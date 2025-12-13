"""
Image generation API client for Z-Image-Turbo Flask backend
"""

import logging
import time
from pathlib import Path
from typing import Optional, Tuple
import requests
from PIL import Image, ImageOps
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
        
        # Check if we should use internal bridge based on config
        # This is controlled by USE_BRIDGE environment variable
        self.use_internal_bridge = config.use_bridge
        self.internal_bridge = None
        
        # Only attempt to initialize bridge if USE_BRIDGE is True
        if self.use_internal_bridge:
            logger.info("Bridge mode enabled (USE_BRIDGE=true)")
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
                    logger.info("✓ Internal image bridge initialized successfully")
                else:
                    logger.warning("Internal bridge task queue manager not registered")
                    logger.warning("  Ensure app.py correctly initializes the internal bridge")
                    logger.warning("  Falling back to HTTP calls")
                    self.use_internal_bridge = False
            except Exception as e:
                logger.warning(f"Failed to initialize internal bridge: {e}")
                logger.warning("Falling back to HTTP calls")
                self.use_internal_bridge = False
        else:
            logger.info("HTTP mode enabled (USE_BRIDGE=false) - Using direct API calls")
    
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
        prompt_preview = prompt[:80] + "..." if len(prompt) > 80 else prompt
        logger.info(f"Generating image: {width}x{height}")
        logger.debug(f"Prompt: {prompt_preview}")
        logger.debug(f"Output path: {output_path}")
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Image generation attempt {attempt + 1}/{self.max_retries}")
                
                # Step 1: Submit task
                logger.debug("Step 1: Submitting image generation task")
                task_id = self._submit_task(prompt, width, height)
                if not task_id:
                    raise Exception("Failed to submit task - no task ID returned")
                
                logger.info(f"✓ Task submitted successfully: {task_id}")
                
                # Step 2: Poll for completion
                logger.debug("Step 2: Waiting for image generation to complete")
                success, error = self._wait_for_completion(task_id)
                if not success:
                    raise Exception(error or "Task failed without error message")
                
                logger.info(f"✓ Image generation completed for task {task_id}")
                
                # Step 3: Download image
                logger.debug("Step 3: Downloading generated image")
                success = self._download_image(task_id, output_path, width, height)
                if success:
                    logger.info(f"✓ Image saved successfully to {output_path.name}")
                    return True, None
                else:
                    raise Exception("Failed to download image - no image data received")
                
            except Exception as e:
                last_error = e
                logger.warning(f"Image generation attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    backoff_time = 2 ** attempt
                    logger.info(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)  # Exponential backoff
        
        error_msg = f"Image generation failed after {self.max_retries} attempts: {str(last_error)}"
        logger.error(error_msg)
        
        # Create placeholder image on failure
        logger.warning("Creating placeholder image due to generation failure")
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
                logger.info(f"Adjusted dimensions: {width}x{height} → {adjusted_width}x{adjusted_height} (multiple of 16 required)")
            else:
                logger.debug(f"Dimensions already valid: {width}x{height}")
            
            # Use internal bridge if available
            if self.use_internal_bridge and self.internal_bridge:
                logger.debug("Submitting task via internal bridge (bypassing HTTP)")
                task_id = self.internal_bridge.submit_task(
                    prompt=prompt,
                    width=adjusted_width,
                    height=adjusted_height,
                    num_inference_steps=9
                )
                logger.debug(f"Internal bridge returned task ID: {task_id}")
                return task_id
            
            # Fall back to HTTP
            url = f"{self.api_url}/api/generate"
            logger.debug(f"Submitting task via HTTP to {url}")
            payload = {
                "prompt": prompt,
                "width": adjusted_width,
                "height": adjusted_height,
                "num_inference_steps": 9
            }
            
            response = requests.post(url, json=payload, timeout=30)
            logger.debug(f"HTTP response status: {response.status_code}")
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("code") == 200:
                task_id = result.get("data", {}).get("task_id")
                logger.debug(f"Task submission successful, task ID: {task_id}")
                return task_id
            else:
                error_msg = result.get('message', 'Unknown error')
                logger.error(f"API returned error code: {result.get('code')} - {error_msg}")
                return None
                
        except requests.exceptions.Timeout as e:
            logger.error(f"Task submission timeout: {str(e)}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Task submission HTTP error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Task submission failed: {str(e)}", exc_info=True)
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
            logger.debug(f"Waiting for task {task_id} completion via internal bridge")
            result = self.internal_bridge.wait_for_completion(task_id)
            if result[0]:
                logger.debug(f"Task {task_id} completed successfully via internal bridge")
            else:
                logger.warning(f"Task {task_id} failed via internal bridge: {result[1]}")
            return result
        
        # Fall back to HTTP
        logger.debug(f"Polling task {task_id} status via HTTP (max wait: {self.max_wait_time}s)")
        start_time = time.time()
        poll_count = 0
        
        while True:
            try:
                poll_count += 1
                elapsed = time.time() - start_time
                
                # Check timeout
                if elapsed > self.max_wait_time:
                    error_msg = f"Task timeout after {elapsed:.1f}s (max: {self.max_wait_time}s)"
                    logger.error(error_msg)
                    return False, error_msg
                
                # Query task status
                url = f"{self.api_url}/api/task/{task_id}"
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("code") != 200:
                    error_msg = result.get("message", "Unknown error")
                    logger.error(f"Task query returned error: {error_msg}")
                    return False, error_msg
                
                status = result.get("data", {}).get("status")
                
                if status == "completed":
                    logger.info(f"✓ Task {task_id} completed after {elapsed:.1f}s ({poll_count} polls)")
                    return True, None
                elif status == "failed":
                    error_msg = result.get("data", {}).get("error_message", "Task failed without error message")
                    logger.error(f"Task {task_id} failed: {error_msg}")
                    return False, error_msg
                elif status in ["pending", "processing"]:
                    # Still processing, wait and retry
                    if poll_count % 5 == 0:  # Log every 5th poll
                        logger.debug(f"Task {task_id} status: {status} (elapsed: {elapsed:.1f}s, poll #{poll_count})")
                    time.sleep(self.poll_interval)
                else:
                    error_msg = f"Unknown status: {status}"
                    logger.warning(error_msg)
                    return False, error_msg
                    
            except requests.exceptions.Timeout as e:
                logger.warning(f"Task status query timeout: {str(e)}")
                return False, f"Status query timeout: {str(e)}"
            except requests.exceptions.RequestException as e:
                logger.error(f"Error polling task status: {str(e)}")
                return False, f"Polling error: {str(e)}"
            except Exception as e:
                logger.error(f"Unexpected error polling task status: {str(e)}", exc_info=True)
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
                logger.debug(f"Downloading image for task {task_id} via internal bridge")
                image_bytes = self.internal_bridge.get_task_result(task_id)
                
                if image_bytes:
                    logger.debug(f"Received {len(image_bytes)} bytes from internal bridge")
                    # Save and resize image
                    image = Image.open(BytesIO(image_bytes))
                    logger.debug(f"Image opened successfully, original size: {image.size}")
                    image = self._resize_image(image, target_width, target_height)
                    image.save(output_path)
                    logger.debug(f"Image saved to {output_path}")
                    return True
                else:
                    logger.error("Failed to get image data from internal bridge (received None)")
                    return False
            
            # Fall back to HTTP
            url = f"{self.api_url}/api/result/{task_id}"
            logger.debug(f"Downloading image via HTTP from {url}")
            response = requests.get(url, timeout=60)
            logger.debug(f"Download response status: {response.status_code}")
            response.raise_for_status()
            
            # Check if response is image
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            logger.debug(f"Content type: {content_type}, size: {content_length} bytes")
            
            if 'image' in content_type:
                # Save and resize image
                image = Image.open(BytesIO(response.content))
                logger.debug(f"Image opened successfully, original size: {image.size}")
                image = self._resize_image(image, target_width, target_height)
                image.save(output_path)
                logger.debug(f"Image saved to {output_path}")
                return True
            else:
                # Not an image, probably still processing or error
                logger.error(f"Expected image content but received: {content_type}")
                if logger.isEnabledFor(logging.DEBUG):
                    preview = response.text[:200] if hasattr(response, 'text') else str(response.content[:200])
                    logger.debug(f"Response preview: {preview}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to download image for task {task_id}: {str(e)}", exc_info=True)
            return False
    
    def _resize_image(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Resize image to target dimensions using smart cropping (fit)
        
        Args:
            image: PIL Image object
            target_width: Target width
            target_height: Target height
            
        Returns:
            Resized and cropped image
        """
        current_size = image.size
        target_size = (target_width, target_height)
        
        if current_size == target_size:
            logger.debug(f"Image already at target size: {target_size}")
            return image
        
        logger.debug(f"Smart resizing image: {current_size} → {target_size}")
        # ImageOps.fit crops and resizes the image to fill the requested size 
        # while maintaining aspect ratio, centering the crop.
        resized = ImageOps.fit(
            image, 
            target_size, 
            method=Image.Resampling.LANCZOS, 
            centering=(0.5, 0.5)
        )
        logger.debug("Image resized and cropped successfully")
        return resized
    
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

        logger.info(f"Creating placeholder image: {width}x{height}")
        logger.debug(f"Placeholder will be saved to: {output_path}")
        logger.debug(f"Error message: {error_msg[:100]}...")
        
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
        logger.debug(f"Placeholder image saved successfully")
