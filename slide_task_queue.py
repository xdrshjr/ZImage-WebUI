"""
Slide任务队列管理器
管理幻灯片生成任务的队列、状态和执行
"""
import logging
import threading
import queue
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List
from pathlib import Path

from slide_generator import SlideGenerator

logger = logging.getLogger(__name__)


class SlideTaskStatus(Enum):
    """Slide任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SlideTask:
    """Slide任务数据类"""
    task_id: str
    status: SlideTaskStatus
    base_text: str
    num_slides: int
    aspect_ratio: str
    style: str
    content_richness: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    queue_position: int = 0
    
    # 输出结果
    output_path: Optional[str] = None
    pdf_path: Optional[str] = None
    slide_image_paths: List[str] = field(default_factory=list)
    slides_generated: int = 0
    
    # 错误信息
    error_message: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        data = asdict(self)
        data['status'] = self.status.value
        return data


class SlideTaskQueueManager:
    """
    Slide任务队列管理器
    管理slide生成任务的提交、执行和状态追踪
    """
    
    def __init__(self, slide_generator: SlideGenerator, max_queue_size: int = 50):
        """
        初始化任务队列管理器
        
        Args:
            slide_generator: Slide生成器实例
            max_queue_size: 最大队列长度
        """
        self.slide_generator = slide_generator
        self.max_queue_size = max_queue_size
        
        # 任务队列和存储
        self.task_queue = queue.Queue(maxsize=max_queue_size)
        self.tasks: Dict[str, SlideTask] = {}
        self.lock = threading.RLock()
        
        # 工作线程
        self.worker_thread = None
        self.is_running = False
        
        # 启动工作线程
        self._start_worker()
        
        logger.info(f"✓ SlideTaskQueueManager初始化完成 (最大队列: {max_queue_size})")
    
    def _start_worker(self):
        """启动工作线程"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.is_running = True
            self.worker_thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name="SlideTaskWorker"
            )
            self.worker_thread.start()
            logger.info("✓ Slide任务工作线程已启动")
    
    def _worker_loop(self):
        """工作线程主循环"""
        logger.info("Slide任务工作线程开始运行")
        
        while self.is_running:
            try:
                # 从队列获取任务 (超时1秒以便检查is_running)
                try:
                    task_id = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # 获取任务
                with self.lock:
                    task = self.tasks.get(task_id)
                    if not task:
                        logger.warning(f"任务 {task_id} 不存在，跳过")
                        continue
                    
                    # 更新任务状态为处理中
                    task.status = SlideTaskStatus.PROCESSING
                    task.started_at = datetime.now().isoformat()
                    task.queue_position = 0
                
                logger.info(f"开始处理Slide任务: {task_id}")
                logger.info(f"  主题: {task.base_text[:80]}...")
                logger.info(f"  幻灯片数量: {task.num_slides}")
                
                # 执行生成
                try:
                    result = self.slide_generator.generate_slides(
                        base_text=task.base_text,
                        num_slides=task.num_slides,
                        aspect_ratio=task.aspect_ratio,
                        style=task.style,
                        content_richness=task.content_richness
                    )
                    
                    # 更新任务状态
                    with self.lock:
                        task.completed_at = datetime.now().isoformat()
                        
                        if result.get('success'):
                            task.status = SlideTaskStatus.COMPLETED
                            task.output_path = result.get('output_path')
                            task.pdf_path = result.get('pdf_path')
                            task.slides_generated = result.get('slides_generated', 0)
                            task.slide_image_paths = result.get('slide_image_paths', [])
                            task.errors = result.get('errors', [])
                            
                            logger.info(f"✓ 任务完成: {task_id}")
                            logger.info(f"  生成了 {task.slides_generated} 张幻灯片")
                            if task.pdf_path:
                                logger.info(f"  PDF: {Path(task.pdf_path).name}")
                        else:
                            task.status = SlideTaskStatus.FAILED
                            error = result.get('error', '未知错误')
                            task.error_message = error
                            task.errors = result.get('errors', [error])
                            
                            logger.error(f"✗ 任务失败: {task_id}")
                            logger.error(f"  错误: {error}")
                
                except Exception as e:
                    # 处理异常
                    with self.lock:
                        task.status = SlideTaskStatus.FAILED
                        task.completed_at = datetime.now().isoformat()
                        error_msg = f"执行异常: {str(e)}"
                        task.error_message = error_msg
                        task.errors = [error_msg]
                    
                    logger.error(f"✗ 任务执行异常: {task_id}")
                    logger.error(f"  异常: {e}", exc_info=True)
                
                finally:
                    # 标记任务完成
                    self.task_queue.task_done()
                    
                    # 更新队列位置
                    self.update_queue_positions()
            
            except Exception as e:
                logger.error(f"工作线程异常: {e}", exc_info=True)
        
        logger.info("Slide任务工作线程已停止")
    
    def submit_task(
        self,
        base_text: str,
        num_slides: int,
        aspect_ratio: str,
        style: str,
        content_richness: str
    ) -> str:
        """
        提交slide生成任务
        
        Args:
            base_text: 源内容/主题
            num_slides: 幻灯片数量
            aspect_ratio: 幻灯片比例
            style: 视觉风格
            content_richness: 内容详细程度
            
        Returns:
            str: 任务ID
            
        Raises:
            queue.Full: 队列已满
        """
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务
        task = SlideTask(
            task_id=task_id,
            status=SlideTaskStatus.PENDING,
            base_text=base_text,
            num_slides=num_slides,
            aspect_ratio=aspect_ratio,
            style=style,
            content_richness=content_richness,
            created_at=datetime.now().isoformat()
        )
        
        # 添加到存储和队列
        with self.lock:
            self.tasks[task_id] = task
            
            try:
                # 尝试将任务ID加入队列 (非阻塞)
                self.task_queue.put(task_id, block=False)
                
                # 更新队列位置
                self.update_queue_positions()
                
                logger.info(f"✓ Slide任务已提交: {task_id}")
                logger.debug(f"  主题: {base_text[:80]}...")
                logger.debug(f"  幻灯片数量: {num_slides}")
                logger.debug(f"  队列位置: {task.queue_position}")
                
                return task_id
                
            except queue.Full:
                # 队列已满，删除任务
                del self.tasks[task_id]
                logger.warning(f"任务队列已满，拒绝任务: {task_id}")
                raise
    
    def get_task(self, task_id: str) -> Optional[SlideTask]:
        """
        获取任务详情
        
        Args:
            task_id: 任务ID
            
        Returns:
            SlideTask: 任务对象，不存在则返回None
        """
        with self.lock:
            return self.tasks.get(task_id)
    
    def update_queue_positions(self):
        """更新所有pending任务的队列位置"""
        with self.lock:
            # 获取队列中的任务ID列表（不移除）
            queue_items = []
            temp_list = []
            
            # 从队列中取出所有项
            while not self.task_queue.empty():
                try:
                    item = self.task_queue.get_nowait()
                    temp_list.append(item)
                except queue.Empty:
                    break
            
            # 放回队列
            for item in temp_list:
                try:
                    self.task_queue.put_nowait(item)
                    queue_items.append(item)
                except queue.Full:
                    break
            
            # 更新队列位置（从1开始）
            for position, task_id in enumerate(queue_items, start=1):
                task = self.tasks.get(task_id)
                if task and task.status == SlideTaskStatus.PENDING:
                    task.queue_position = position
            
            # 处理中的任务位置为0
            for task in self.tasks.values():
                if task.status == SlideTaskStatus.PROCESSING:
                    task.queue_position = 0
    
    def get_queue_status(self) -> Dict:
        """
        获取队列状态统计
        
        Returns:
            Dict: 队列状态信息
        """
        with self.lock:
            pending_count = sum(1 for t in self.tasks.values() if t.status == SlideTaskStatus.PENDING)
            processing_count = sum(1 for t in self.tasks.values() if t.status == SlideTaskStatus.PROCESSING)
            completed_count = sum(1 for t in self.tasks.values() if t.status == SlideTaskStatus.COMPLETED)
            failed_count = sum(1 for t in self.tasks.values() if t.status == SlideTaskStatus.FAILED)
            
            return {
                "queue_size": self.task_queue.qsize(),
                "max_queue_size": self.max_queue_size,
                "pending_tasks": pending_count,
                "processing_tasks": processing_count,
                "completed_tasks": completed_count,
                "failed_tasks": failed_count,
                "total_tasks": len(self.tasks)
            }
    
    def shutdown(self):
        """关闭任务队列管理器"""
        logger.info("正在关闭SlideTaskQueueManager...")
        
        self.is_running = False
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
        
        logger.info("✓ SlideTaskQueueManager已关闭")

