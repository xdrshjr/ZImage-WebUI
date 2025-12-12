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
        from PIL import ImageDraw, ImageFont
        
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

