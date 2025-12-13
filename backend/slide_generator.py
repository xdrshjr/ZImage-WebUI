"""
Slide Generation Wrapper
包装slide-gen Agent以供Flask服务调用
"""
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import traceback

# Import main config first
import config

# Set environment variables for slide-gen before importing its modules
# This allows slide-gen to read configuration from the main config.py
os.environ["LLM_API_KEY"] = config.SLIDE_LLM_API_KEY
os.environ["LLM_API_URL"] = config.SLIDE_LLM_API_URL
os.environ["LLM_MODEL"] = config.SLIDE_LLM_MODEL
os.environ["IMAGE_API_KEY"] = config.SLIDE_IMAGE_API_KEY
os.environ["IMAGE_API_URL"] = config.SLIDE_IMAGE_API_URL
os.environ["IMAGE_MODEL"] = config.SLIDE_IMAGE_MODEL
os.environ["DEFAULT_TIMEOUT"] = str(config.SLIDE_DEFAULT_TIMEOUT)
os.environ["MAX_RETRIES"] = str(config.SLIDE_MAX_RETRIES)

# Log configuration status for debugging
_logger = logging.getLogger(__name__)
_logger.debug(f"Slide配置已设置: LLM_API_KEY={'已设置' if config.SLIDE_LLM_API_KEY else '未设置'}, "
              f"IMAGE_API_KEY={'已设置' if config.SLIDE_IMAGE_API_KEY else '未设置'}, "
              f"IMAGE_API_URL={'已设置' if config.SLIDE_IMAGE_API_URL else '未设置'}")

# Add slide-gen to Python path
slide_gen_path = Path(__file__).parent / "agents" / "slide-gen"
if str(slide_gen_path) not in sys.path:
    sys.path.insert(0, str(slide_gen_path))

# Now import slide-gen modules (they will read from the environment variables we just set)
# NOTE: We import slide_config INSIDE the class to ensure env vars are set first
try:
    from src.agent.graph import SlideGenerationAgent
    from src.utils.validators import InputValidator
except ImportError as e:
    logging.error(f"Failed to import slide-gen modules: {e}")
    SlideGenerationAgent = None
    InputValidator = None

logger = logging.getLogger(__name__)


class SlideGenerator:
    """
    Slide生成器类
    封装slide-gen Agent的调用逻辑
    """
    
    def __init__(self):
        """初始化Slide生成器"""
        self.agent = None
        self.is_ready = False
        
        if SlideGenerationAgent is None:
            logger.error("SlideGenerationAgent未能正确导入，Slide生成功能不可用")
            return
        
        try:
            # Import slide_config here (after environment variables have been set)
            from src.utils.config import config as slide_config
            
            # 验证slide-gen配置
            valid, error = slide_config.validate()
            if not valid:
                logger.error(f"Slide生成配置验证失败: {error}")
                logger.error("请在config.py中配置以下必需的环境变量:")
                logger.error("  - SLIDE_LLM_API_KEY: LLM服务的API密钥")
                logger.error("  - SLIDE_IMAGE_API_KEY: 图像生成服务的API密钥")
                logger.error("  - SLIDE_IMAGE_API_URL: 图像生成服务的API地址")
                return
            
            # 初始化Agent
            self.agent = SlideGenerationAgent()
            self.is_ready = True
            logger.info("✓ SlideGenerator初始化成功")
            
        except Exception as e:
            logger.error(f"SlideGenerator初始化失败: {e}")
            logger.debug(traceback.format_exc())
            self.is_ready = False
    
    def is_generator_ready(self) -> bool:
        """
        检查生成器是否就绪
        
        Returns:
            bool: 是否就绪
        """
        return self.is_ready and self.agent is not None
    
    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        验证生成参数
        
        Args:
            params: 参数字典
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not InputValidator:
            return False, "参数验证器未初始化"
        
        try:
            return InputValidator.validate_parameters(params)
        except Exception as e:
            logger.error(f"参数验证异常: {e}")
            return False, str(e)
    
    def generate_slides(
        self,
        base_text: str,
        num_slides: int,
        aspect_ratio: str,
        style: str,
        content_richness: str
    ) -> Dict[str, Any]:
        """
        生成幻灯片
        
        Args:
            base_text: 源内容/主题
            num_slides: 幻灯片数量 (1-50)
            aspect_ratio: 幻灯片比例 ("16:9", "4:3", "16:10")
            style: 视觉风格 ("professional", "creative", "minimal", "academic")
            content_richness: 内容详细程度 ("concise", "moderate", "detailed")
            
        Returns:
            Dict: 生成结果
                - success: bool - 是否成功
                - output_path: str - 输出目录路径
                - pdf_path: str | None - PDF文件路径
                - slides_generated: int - 生成的幻灯片数量
                - errors: List[str] - 错误列表
                - slide_image_paths: List[str] - 单个幻灯片图片路径列表
        """
        if not self.is_generator_ready():
            logger.error("SlideGenerator未就绪，无法生成幻灯片")
            return {
                'success': False,
                'error': 'Slide生成器未就绪',
                'output_path': None,
                'pdf_path': None,
                'slides_generated': 0,
                'errors': ['Slide生成器未初始化或配置错误'],
                'slide_image_paths': []
            }
        
        # 验证参数
        params = {
            'base_text': base_text,
            'num_slides': num_slides,
            'aspect_ratio': aspect_ratio,
            'style': style,
            'content_richness': content_richness
        }
        
        valid, error = self.validate_params(params)
        if not valid:
            logger.error(f"参数验证失败: {error}")
            return {
                'success': False,
                'error': error,
                'output_path': None,
                'pdf_path': None,
                'slides_generated': 0,
                'errors': [error],
                'slide_image_paths': []
            }
        
        # 执行生成
        try:
            logger.info("="*60)
            logger.info("开始生成幻灯片")
            logger.info(f"主题: {base_text[:80]}...")
            logger.info(f"数量: {num_slides} 幻灯片")
            logger.info(f"比例: {aspect_ratio}")
            logger.info(f"风格: {style}")
            logger.info(f"内容详细度: {content_richness}")
            logger.info("="*60)
            
            result = self.agent.generate_slides(
                base_text=base_text,
                num_slides=num_slides,
                aspect_ratio=aspect_ratio,
                style=style,
                content_richness=content_richness
            )
            
            # 收集所有生成的幻灯片图片路径
            slide_image_paths = []
            if result.get('success'):
                output_path = Path(result['output_path'])
                slide_images_dir = output_path / 'slide_images'
                
                if slide_images_dir.exists():
                    # 按顺序收集所有幻灯片图片
                    for i in range(1, num_slides + 1):
                        slide_img = slide_images_dir / f"slide_{i}.png"
                        if slide_img.exists():
                            slide_image_paths.append(str(slide_img))
                            logger.debug(f"找到幻灯片图片: {slide_img.name}")
                
                logger.info(f"✓ 幻灯片生成成功")
                logger.info(f"✓ 生成了 {len(slide_image_paths)} 张幻灯片图片")
                if result.get('pdf_path'):
                    logger.info(f"✓ PDF生成成功: {result['pdf_path']}")
            
            # 添加幻灯片图片路径到结果
            result['slide_image_paths'] = slide_image_paths
            
            return result
            
        except Exception as e:
            error_msg = f"幻灯片生成失败: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            
            return {
                'success': False,
                'error': error_msg,
                'output_path': None,
                'pdf_path': None,
                'slides_generated': 0,
                'errors': [error_msg],
                'slide_image_paths': []
            }


# 全局单例
_slide_generator_instance: Optional[SlideGenerator] = None


def get_slide_generator() -> SlideGenerator:
    """
    获取SlideGenerator单例
    
    Returns:
        SlideGenerator: 生成器实例
    """
    global _slide_generator_instance
    
    if _slide_generator_instance is None:
        _slide_generator_instance = SlideGenerator()
    
    return _slide_generator_instance

