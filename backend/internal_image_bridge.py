"""
Internal Image Generation Bridge

Provides direct access to the image generation task queue for internal calls,
bypassing HTTP to avoid deadlock when slide generation calls image generation
on the same Flask server.

使用注册模式避免循环导入和重复加载模型的问题。
"""
import logging
import time
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class InternalImageBridge:
    """
    Bridge for internal image generation calls that bypasses HTTP.
    
    This allows the slide generation worker thread to call the image generation
    task queue directly without making HTTP requests to the same Flask server,
    avoiding deadlock issues.
    
    使用注册模式：app.py在初始化时主动注册task_queue_manager，
    避免在这里import app导致循环依赖和重复初始化。
    """
    
    def __init__(self):
        """Initialize the bridge"""
        self._task_queue_manager = None
        self.poll_interval = 2  # Poll every 2 seconds
        self.max_wait_time = 300  # Maximum wait time: 5 minutes
    
    def register_task_queue_manager(self, task_queue_manager):
        """
        注册task queue manager实例。
        由app.py在初始化时调用，避免循环导入。
        
        Args:
            task_queue_manager: TaskQueueManager实例
        """
        self._task_queue_manager = task_queue_manager
        logger.info("✓ Task queue manager已注册到internal image bridge")
    
    def _get_task_queue_manager(self):
        """
        Get the registered task queue manager instance.
        """
        if self._task_queue_manager is None:
            logger.error("Task queue manager未注册。请确保app.py在初始化时调用register_task_queue_manager()")
            return None
        
        return self._task_queue_manager
    
    def is_ready(self) -> bool:
        """
        Check if the internal bridge is ready to use.
        
        Returns:
            bool: True if task queue manager is registered and ready
        """
        return self._task_queue_manager is not None
    
    def submit_task(
        self,
        prompt: str,
        width: int,
        height: int,
        num_inference_steps: int = 9
    ) -> Optional[str]:
        """
        Submit image generation task directly to the queue.
        
        Args:
            prompt: Image generation prompt
            width: Image width
            height: Image height
            num_inference_steps: Number of inference steps
            
        Returns:
            task_id if successful, None otherwise
        """
        try:
            queue_manager = self._get_task_queue_manager()
            if not queue_manager:
                logger.error("Cannot submit task: queue manager not available")
                return None
            
            # Submit task directly to the queue
            task_id = queue_manager.submit_task(
                prompt=prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps
            )
            
            logger.debug(f"Internal task submitted: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to submit internal task: {e}")
            return None
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task status directly from the queue.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status dict or None
        """
        try:
            queue_manager = self._get_task_queue_manager()
            if not queue_manager:
                return None
            
            task = queue_manager.get_task(task_id)
            if not task:
                return None
            
            return {
                'status': task.status.value,
                'error_message': task.error_message
            }
            
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return None
    
    def wait_for_completion(self, task_id: str) -> Tuple[bool, Optional[str]]:
        """
        Poll task status until completion.
        
        Args:
            task_id: Task ID
            
        Returns:
            tuple: (success, error_message)
        """
        start_time = time.time()
        
        while True:
            try:
                # Check timeout
                if time.time() - start_time > self.max_wait_time:
                    return False, "Task timeout"
                
                # Get task status
                task_status = self.get_task_status(task_id)
                
                if not task_status:
                    return False, "Task not found"
                
                status = task_status.get('status')
                
                if status == "completed":
                    return True, None
                elif status == "failed":
                    error_msg = task_status.get('error_message', 'Task failed')
                    return False, error_msg
                elif status in ["pending", "processing"]:
                    # Still processing, wait and retry
                    logger.debug(f"Internal task {task_id} status: {status}")
                    time.sleep(self.poll_interval)
                else:
                    return False, f"Unknown status: {status}"
                    
            except Exception as e:
                logger.error(f"Error polling internal task status: {e}")
                return False, str(e)
    
    def get_task_result(self, task_id: str) -> Optional[bytes]:
        """
        Get task result image data directly.
        
        Args:
            task_id: Task ID
            
        Returns:
            Image bytes or None
        """
        try:
            queue_manager = self._get_task_queue_manager()
            if not queue_manager:
                return None
            
            task = queue_manager.get_task(task_id)
            if not task or not task.image_path:
                return None
            
            # Read image file
            output_path = Path(task.image_path)
            if not output_path.exists():
                logger.error(f"Output file not found: {output_path}")
                return None
            
            with open(output_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to get task result: {e}")
            return None


# Global singleton
_internal_bridge_instance: Optional[InternalImageBridge] = None


def get_internal_bridge() -> InternalImageBridge:
    """
    Get the InternalImageBridge singleton instance.
    
    Returns:
        InternalImageBridge instance
    """
    global _internal_bridge_instance
    
    if _internal_bridge_instance is None:
        _internal_bridge_instance = InternalImageBridge()
    
    return _internal_bridge_instance

