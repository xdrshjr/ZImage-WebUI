"""
任务队列管理模块
负责管理图像生成任务队列和worker线程
"""
import logging
import threading
import queue
import uuid
import time
from datetime import datetime
from typing import Dict, Optional, Any
from enum import Enum
from pathlib import Path
import config
from model_manager import ModelManager

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"  # 排队中
    PROCESSING = "processing"  # 生成中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class Task:
    """任务对象"""
    
    def __init__(
        self,
        task_id: str,
        prompt: str,
        height: int = config.DEFAULT_HEIGHT,
        width: int = config.DEFAULT_WIDTH,
        num_inference_steps: int = config.DEFAULT_NUM_INFERENCE_STEPS,
        seed: Optional[int] = None,
    ):
        """
        初始化任务
        
        Args:
            task_id: 任务ID
            prompt: 文本提示词
            height: 图像高度
            width: 图像宽度
            num_inference_steps: 推理步数
            seed: 随机种子
        """
        self.task_id = task_id
        self.prompt = prompt
        self.height = height
        self.width = width
        self.num_inference_steps = num_inference_steps
        self.seed = seed
        
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.image_path: Optional[str] = None
        self.queue_position: int = 0
        
        self._lock = threading.Lock()
    
    def update_status(self, status: TaskStatus, error_message: Optional[str] = None):
        """
        更新任务状态
        
        Args:
            status: 新状态
            error_message: 错误信息（如果状态为FAILED）
        """
        with self._lock:
            self.status = status
            if status == TaskStatus.PROCESSING:
                self.started_at = datetime.now()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                self.completed_at = datetime.now()
            if error_message:
                self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            dict: 任务信息字典
        """
        with self._lock:
            result = {
                "task_id": self.task_id,
                "status": self.status.value,
                "prompt": self.prompt,
                "height": self.height,
                "width": self.width,
                "num_inference_steps": self.num_inference_steps,
                "seed": self.seed,
                "created_at": self.created_at.isoformat(),
                "queue_position": self.queue_position,
            }
            
            if self.started_at:
                result["started_at"] = self.started_at.isoformat()
            if self.completed_at:
                result["completed_at"] = self.completed_at.isoformat()
            if self.error_message:
                result["error_message"] = self.error_message
            if self.image_path:
                result["image_path"] = self.image_path
                
            return result


class TaskQueueManager:
    """任务队列管理器"""
    
    def __init__(self, model_manager: ModelManager):
        """
        初始化任务队列管理器
        
        Args:
            model_manager: 模型管理器实例
        """
        self.model_manager = model_manager
        self.task_queue: queue.Queue = queue.Queue(maxsize=config.MAX_QUEUE_SIZE)
        self.tasks: Dict[str, Task] = {}
        self.tasks_lock = threading.Lock()
        
        self.worker_thread: Optional[threading.Thread] = None
        self.is_running = False
        self._stop_event = threading.Event()
        
        # 启动worker线程
        self.start_worker()
    
    def start_worker(self):
        """启动worker线程"""
        if self.worker_thread is not None and self.worker_thread.is_alive():
            logger.warning("Worker线程已在运行")
            return
        
        self.is_running = True
        self._stop_event.clear()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("Worker线程已启动")
    
    def stop_worker(self):
        """停止worker线程"""
        self.is_running = False
        self._stop_event.set()
        if self.worker_thread is not None:
            self.worker_thread.join(timeout=5)
        logger.info("Worker线程已停止")
    
    def _worker_loop(self):
        """Worker线程主循环"""
        logger.info("Worker线程开始运行")
        
        while self.is_running and not self._stop_event.is_set():
            try:
                # 从队列获取任务（超时1秒，以便检查停止事件）
                try:
                    task = self.task_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # 更新队列位置
                self.update_queue_positions()
                
                # 处理任务
                self._process_task(task)
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker线程处理任务时出错: {e}", exc_info=True)
        
        logger.info("Worker线程已退出")
    
    def _process_task(self, task: Task):
        """
        处理单个任务
        
        Args:
            task: 要处理的任务
        """
        try:
            logger.info(f"开始处理任务: {task.task_id}")
            task.update_status(TaskStatus.PROCESSING)
            
            # 生成图像
            image = self.model_manager.generate_image(
                prompt=task.prompt,
                height=task.height,
                width=task.width,
                num_inference_steps=task.num_inference_steps,
                seed=task.seed,
            )
            
            # 保存图像
            image_filename = f"{task.task_id}.png"
            image_path = config.OUTPUT_DIR / image_filename
            image.save(image_path)
            
            # 更新任务状态
            task.image_path = str(image_path)
            task.update_status(TaskStatus.COMPLETED)
            
            logger.info(f"任务处理完成: {task.task_id}, 图像保存至: {image_path}")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"任务处理失败: {task.task_id}, 错误: {error_msg}", exc_info=True)
            task.update_status(TaskStatus.FAILED, error_message=error_msg)
    
    def update_queue_positions(self):
        """更新所有待处理任务的队列位置"""
        with self.tasks_lock:
            pending_tasks = [
                (task_id, task) for task_id, task in self.tasks.items()
                if task.status == TaskStatus.PENDING
            ]
            # 按创建时间排序
            pending_tasks.sort(key=lambda x: x[1].created_at)
            
            for position, (task_id, task) in enumerate(pending_tasks, start=1):
                task.queue_position = position
    
    def submit_task(
        self,
        prompt: str,
        height: int = config.DEFAULT_HEIGHT,
        width: int = config.DEFAULT_WIDTH,
        num_inference_steps: int = config.DEFAULT_NUM_INFERENCE_STEPS,
        seed: Optional[int] = None,
    ) -> str:
        """
        提交新任务
        
        Args:
            prompt: 文本提示词
            height: 图像高度
            width: 图像宽度
            num_inference_steps: 推理步数
            seed: 随机种子
            
        Returns:
            str: 任务ID
            
        Raises:
            queue.Full: 如果队列已满
        """
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务对象
        task = Task(
            task_id=task_id,
            prompt=prompt,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            seed=seed,
        )
        
        # 添加到任务字典
        with self.tasks_lock:
            self.tasks[task_id] = task
        
        # 更新队列位置
        self.update_queue_positions()
        
        # 添加到队列
        try:
            self.task_queue.put(task, block=False)
            logger.info(f"任务已提交: {task_id}, 队列长度: {self.task_queue.qsize()}")
        except queue.Full:
            # 从任务字典中移除
            with self.tasks_lock:
                self.tasks.pop(task_id, None)
            raise queue.Full("任务队列已满，请稍后重试")
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Task: 任务对象，如果不存在返回None
        """
        with self.tasks_lock:
            return self.tasks.get(task_id)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        获取队列状态信息
        
        Returns:
            dict: 队列状态字典
        """
        with self.tasks_lock:
            pending_count = sum(1 for task in self.tasks.values() if task.status == TaskStatus.PENDING)
            processing_count = sum(1 for task in self.tasks.values() if task.status == TaskStatus.PROCESSING)
            completed_count = sum(1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED)
            failed_count = sum(1 for task in self.tasks.values() if task.status == TaskStatus.FAILED)
        
        return {
            "queue_size": self.task_queue.qsize(),
            "max_queue_size": config.MAX_QUEUE_SIZE,
            "pending_tasks": pending_count,
            "processing_tasks": processing_count,
            "completed_tasks": completed_count,
            "failed_tasks": failed_count,
            "total_tasks": len(self.tasks),
        }
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """
        清理旧任务（可选功能，用于防止内存泄漏）
        
        Args:
            max_age_hours: 最大保留时间（小时）
        """
        current_time = datetime.now()
        with self.tasks_lock:
            to_remove = []
            for task_id, task in self.tasks.items():
                if task.completed_at:
                    age = (current_time - task.completed_at).total_seconds() / 3600
                    if age > max_age_hours:
                        to_remove.append(task_id)
            
            for task_id in to_remove:
                self.tasks.pop(task_id, None)
            
            if to_remove:
                logger.info(f"清理了 {len(to_remove)} 个旧任务")

