"""
模型管理模块
负责模型的加载、管理和图像生成
"""
import logging
import torch
from diffusers import ZImagePipeline
from typing import Optional, Dict, Any
import config

logger = logging.getLogger(__name__)


class ModelManager:
    """模型管理器，负责加载和管理Z-Image-Turbo模型"""
    
    def __init__(self):
        """初始化模型管理器"""
        self.pipe: Optional[ZImagePipeline] = None
        self.device = f"cuda:{config.GPU_DEVICE_ID}" if config.CUDA_AVAILABLE and torch.cuda.is_available() else "cpu"
        self.is_loaded = False
        self._load_lock = torch.cuda.Stream() if torch.cuda.is_available() else None
        
    def load_model(self) -> bool:
        """
        加载模型到GPU
        
        Returns:
            bool: 加载是否成功
        """
        if self.is_loaded:
            logger.info("模型已经加载，跳过重复加载")
            return True
            
        try:
            logger.info(f"开始加载模型: {config.MODEL_NAME}")
            logger.info(f"使用设备: {self.device}")
            
            # 确定torch数据类型
            if config.MODEL_TORCH_DTYPE == "bfloat16":
                torch_dtype = torch.bfloat16
            elif config.MODEL_TORCH_DTYPE == "float16":
                torch_dtype = torch.float16
            else:
                torch_dtype = torch.float32
                
            # 加载pipeline
            self.pipe = ZImagePipeline.from_pretrained(
                config.MODEL_NAME,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=config.LOW_CPU_MEM_USAGE,
            )
            
            # 移动到指定设备
            self.pipe.to(self.device)
            
            # 配置Flash Attention（如果启用）
            if config.ENABLE_FLASH_ATTENTION and hasattr(self.pipe, 'transformer'):
                try:
                    self.pipe.transformer.set_attention_backend(config.FLASH_ATTENTION_BACKEND)
                    logger.info(f"已启用Flash Attention后端: {config.FLASH_ATTENTION_BACKEND}")
                except Exception as e:
                    logger.warning(f"启用Flash Attention失败: {e}")
            
            # 模型编译（如果启用）
            if config.ENABLE_MODEL_COMPILE and hasattr(self.pipe, 'transformer'):
                try:
                    self.pipe.transformer.compile()
                    logger.info("已启用模型编译")
                except Exception as e:
                    logger.warning(f"模型编译失败: {e}")
            
            # CPU Offloading（如果启用）
            if config.ENABLE_CPU_OFFLOAD:
                try:
                    self.pipe.enable_model_cpu_offload()
                    logger.info("已启用CPU Offloading")
                except Exception as e:
                    logger.warning(f"启用CPU Offloading失败: {e}")
            
            self.is_loaded = True
            logger.info("模型加载成功")
            
            # 预热模型（执行一次推理以初始化）
            self._warmup_model()
            
            return True
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}", exc_info=True)
            self.is_loaded = False
            return False
    
    def _warmup_model(self):
        """预热模型，执行一次快速推理以初始化"""
        try:
            logger.info("开始模型预热...")
            _ = self.pipe(
                prompt="warmup",
                height=512,
                width=512,
                num_inference_steps=1,
                guidance_scale=config.DEFAULT_GUIDANCE_SCALE,
                generator=torch.Generator(self.device).manual_seed(42),
            ).images[0]
            logger.info("模型预热完成")
        except Exception as e:
            logger.warning(f"模型预热失败: {e}")
    
    def generate_image(
        self,
        prompt: str,
        height: int = config.DEFAULT_HEIGHT,
        width: int = config.DEFAULT_WIDTH,
        num_inference_steps: int = config.DEFAULT_NUM_INFERENCE_STEPS,
        seed: Optional[int] = None,
    ) -> Any:
        """
        生成图像
        
        Args:
            prompt: 文本提示词
            height: 图像高度
            width: 图像宽度
            num_inference_steps: 推理步数
            seed: 随机种子，None表示随机
            
        Returns:
            PIL.Image: 生成的图像对象
            
        Raises:
            RuntimeError: 如果模型未加载或生成失败
        """
        if not self.is_loaded or self.pipe is None:
            raise RuntimeError("模型未加载，请先调用load_model()")
        
        try:
            # 创建生成器
            generator = torch.Generator(self.device)
            if seed is not None:
                generator.manual_seed(seed)
            
            # 生成图像
            logger.info(f"开始生成图像: prompt={prompt[:50]}..., height={height}, width={width}, steps={num_inference_steps}")
            
            result = self.pipe(
                prompt=prompt,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=config.DEFAULT_GUIDANCE_SCALE,
                generator=generator,
            )
            
            image = result.images[0]
            logger.info("图像生成成功")
            
            return image
            
        except Exception as e:
            logger.error(f"图像生成失败: {e}", exc_info=True)
            raise RuntimeError(f"图像生成失败: {str(e)}")
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """
        获取GPU使用信息
        
        Returns:
            dict: GPU信息字典
        """
        if not torch.cuda.is_available():
            return {
                "available": False,
                "message": "CUDA不可用"
            }
        
        try:
            device = torch.device(self.device)
            memory_allocated = torch.cuda.memory_allocated(device) / 1024**3  # GB
            memory_reserved = torch.cuda.memory_reserved(device) / 1024**3  # GB
            memory_total = torch.cuda.get_device_properties(device).total_memory / 1024**3  # GB
            
            return {
                "available": True,
                "device": str(device),
                "memory_allocated_gb": round(memory_allocated, 2),
                "memory_reserved_gb": round(memory_reserved, 2),
                "memory_total_gb": round(memory_total, 2),
                "memory_usage_percent": round((memory_allocated / memory_total) * 100, 2) if memory_total > 0 else 0
            }
        except Exception as e:
            logger.error(f"获取GPU信息失败: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    def is_model_ready(self) -> bool:
        """
        检查模型是否已加载并准备就绪
        
        Returns:
            bool: 模型是否就绪
        """
        return self.is_loaded and self.pipe is not None

