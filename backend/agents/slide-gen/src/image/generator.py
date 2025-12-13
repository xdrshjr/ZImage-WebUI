"""
Image generation API client for Z-Image-Turbo Flask backend
"""

import logging
import time
from pathlib import Path
from typing import Optional, Tuple
import requests
from PIL import Image
from io import BytesIO
from src.utils.config import config
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Client for generating images via Z-Image-Turbo async API"""
    
    def __init__(self):
        """Initialize image generator with configuration"""
        self.api_key = config.image_api_key  # Not used for Z-Image-Turbo
        self.api_url = config.image_api_url  # Base URL like http://localhost:5000
        self.model = config.image_model
        self.timeout = config.default_timeout
        self.max_retries = config.max_retries
        self.poll_interval = 2  # Poll every 2 seconds
        self.max_wait_time = 300  # Maximum wait time: 5 minutes
        
        # Check if we should use internal bridge (for localhost calls)
        self.use_internal_bridge = self._should_use_internal_bridge()
        self.internal_bridge = None
        
        if self.use_internal_bridge:
            try:
                # Import internal_image_bridge directly from backend directory
                import sys
                from pathlib import Path
                # Path structure: .../backend/agents/slide-gen/src/image/generator.py
                # Go up 3 levels to reach backend directory
                backend_dir = Path(__file__).resolve().parents[3]  # Go up to backend directory
                if str(backend_dir) not in sys.path:
                    sys.path.insert(0, str(backend_dir))
                
                # Import internal_image_bridge module directly
                import internal_image_bridge
                self.internal_bridge = internal_image_bridge.get_internal_bridge()
                
                # Check if task queue manager is registered
                if self.internal_bridge.is_ready():
                    logger.info("✓ Using internal image bridge (bypassing HTTP to avoid deadlock)")
                else:
                    logger.warning("Internal bridge task queue manager未注册，将使用HTTP调用")
                    logger.warning("  如果遇到502错误，请确保app.py正确初始化了internal bridge")
                    self.use_internal_bridge = False
            except Exception as e:
                logger.warning(f"Failed to initialize internal bridge: {e}")
                logger.warning("Will fall back to HTTP calls")
                self.use_internal_bridge = False
    
    def _should_use_internal_bridge(self) -> bool:
        """
        Check if we should use internal bridge instead of HTTP calls.
        Returns True if api_url points to localhost/127.0.0.1.
        """
        try:
            parsed = urlparse(self.api_url)
            hostname = parsed.hostname or ''
            
            # Check if it's localhost or 127.0.0.1
            is_localhost = hostname.lower() in ['localhost', '127.0.0.1', '0.0.0.0', '']
            
            if is_localhost:
                logger.debug(f"Detected localhost URL ({self.api_url}), will use internal bridge")
            
            return is_localhost
        except Exception as e:
            logger.debug(f"Failed to parse URL {self.api_url}: {e}")
            return False
    
    def generate_image(
        self,
        prompt: str,
        width: int,
        height: int,
        output_path: Path
    ) -> Tuple[bool, Optional[str]]:
        """
        Generate image from prompt using Z-Image-Turbo async API
        
        Args:
            prompt: Image generation prompt
            width: Desired image width
            height: Desired image height
            output_path: Path to save generated image
            
        Returns:
            tuple: (success, error_message)
        """
        logger.info(f"Generating image: {width}x{height} - {prompt[:50]}...")
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Image generation attempt {attempt + 1}/{self.max_retries}")
                
                # Step 1: Submit task
                task_id = self._submit_task(prompt, width, height)
                if not task_id:
                    raise Exception("Failed to submit task")
                
                logger.debug(f"Task submitted: {task_id}")
                
                # Step 2: Poll for completion
                success, error = self._wait_for_completion(task_id)
                if not success:
                    raise Exception(error or "Task failed")
                
                # Step 3: Download image
                success = self._download_image(task_id, output_path, width, height)
                if success:
                    logger.info(f"Image saved to {output_path}")
                    return True, None
                else:
                    raise Exception("Failed to download image")
                
            except Exception as e:
                last_error = e
                logger.warning(f"Image generation failed (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        error_msg = f"Image generation failed after {self.max_retries} attempts: {str(last_error)}"
        logger.error(error_msg)
        
        # Create placeholder image on failure
        self._create_placeholder_image(output_path, width, height, str(last_error))
        return False, error_msg
    
    def _submit_task(self, prompt: str, width: int, height: int) -> Optional[str]:
        """
        Submit image generation task
        
        Returns:
            task_id if successful, None otherwise
        """
        try:
            # Z-Image-Turbo requires dimensions divisible by 16
            adjusted_width = self._round_to_multiple(width, 16)
            adjusted_height = self._round_to_multiple(height, 16)
            
            if adjusted_width != width or adjusted_height != height:
                logger.info(f"Adjusted dimensions from {width}x{height} to {adjusted_width}x{adjusted_height} (multiple of 16)")
            
            # Use internal bridge if available
            if self.use_internal_bridge and self.internal_bridge:
                logger.debug("Submitting task via internal bridge")
                task_id = self.internal_bridge.submit_task(
                    prompt=prompt,
                    width=adjusted_width,
                    height=adjusted_height,
                    num_inference_steps=9
                )
                return task_id
            
            # Fall back to HTTP
            url = f"{self.api_url}/api/generate"
            payload = {
                "prompt": prompt,
                "width": adjusted_width,
                "height": adjusted_height,
                "num_inference_steps": 9
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("code") == 200:
                task_id = result.get("data", {}).get("task_id")
                return task_id
            else:
                logger.error(f"API error: {result.get('message')}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to submit task: {str(e)}")
            return None
    
    def _round_to_multiple(self, value: int, multiple: int) -> int:
        """
        Round value to nearest multiple
        
        Args:
            value: Original value
            multiple: Multiple to round to (e.g., 16)
            
        Returns:
            Rounded value
        """
        return round(value / multiple) * multiple
    
    def _wait_for_completion(self, task_id: str) -> Tuple[bool, Optional[str]]:
        """
        Poll task status until completion
        
        Returns:
            tuple: (success, error_message)
        """
        # Use internal bridge if available
        if self.use_internal_bridge and self.internal_bridge:
            logger.debug("Waiting for completion via internal bridge")
            return self.internal_bridge.wait_for_completion(task_id)
        
        # Fall back to HTTP
        start_time = time.time()
        
        while True:
            try:
                # Check timeout
                if time.time() - start_time > self.max_wait_time:
                    return False, "Task timeout"
                
                # Query task status
                url = f"{self.api_url}/api/task/{task_id}"
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("code") != 200:
                    return False, result.get("message", "Unknown error")
                
                status = result.get("data", {}).get("status")
                
                if status == "completed":
                    return True, None
                elif status == "failed":
                    error_msg = result.get("data", {}).get("error_message", "Task failed")
                    return False, error_msg
                elif status in ["pending", "processing"]:
                    # Still processing, wait and retry
                    logger.debug(f"Task {task_id} status: {status}")
                    time.sleep(self.poll_interval)
                else:
                    return False, f"Unknown status: {status}"
                    
            except Exception as e:
                logger.error(f"Error polling task status: {str(e)}")
                return False, str(e)
    
    def _download_image(
        self, 
        task_id: str, 
        output_path: Path,
        target_width: int,
        target_height: int
    ) -> bool:
        """
        Download generated image
        
        Returns:
            Success status
        """
        try:
            # Use internal bridge if available
            if self.use_internal_bridge and self.internal_bridge:
                logger.debug("Downloading image via internal bridge")
                image_bytes = self.internal_bridge.get_task_result(task_id)
                
                if image_bytes:
                    # Save and resize image
                    image = Image.open(BytesIO(image_bytes))
                    image = self._resize_image(image, target_width, target_height)
                    image.save(output_path)
                    return True
                else:
                    logger.error("Failed to get image data from internal bridge")
                    return False
            
            # Fall back to HTTP
            url = f"{self.api_url}/api/result/{task_id}"
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Check if response is image
            content_type = response.headers.get('content-type', '')
            
            if 'image' in content_type:
                # Save and resize image
                image = Image.open(BytesIO(response.content))
                image = self._resize_image(image, target_width, target_height)
                image.save(output_path)
                return True
            else:
                # Not an image, probably still processing
                logger.error(f"Expected image but got: {content_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to download image: {str(e)}")
            return False
    
    def _resize_image(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Resize image to target dimensions while maintaining quality
        
        Args:
            image: PIL Image object
            target_width: Target width
            target_height: Target height
            
        Returns:
            Resized image
        """
        if image.size == (target_width, target_height):
            return image
        
        logger.debug(f"Resizing image from {image.size} to {target_width}x{target_height}")
        return image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    def _create_placeholder_image(
        self, 
        output_path: Path, 
        width: int, 
        height: int,
        error_msg: str
    ) -> None:
        """
        Create a placeholder image when generation fails
        
        Args:
            output_path: Path to save placeholder
            width: Image width
            height: Image height
            error_msg: Error message to display
        """
        from PIL import ImageDraw

        logger.info(f"Creating placeholder image at {output_path}")
        
        # Create gray placeholder
        image = Image.new('RGB', (width, height), color='#E0E0E0')
        draw = ImageDraw.Draw(image)
        
        # Draw border
        draw.rectangle(
            [(10, 10), (width - 10, height - 10)],
            outline='#BDBDBD',
            width=3
        )
        
        # Add text
        text = "Image Generation Failed"
        
        # Calculate text position (center)
        bbox = draw.textbbox((0, 0), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='#757575')
        
        image.save(output_path)

