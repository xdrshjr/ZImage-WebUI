"""
配置文件
定义所有系统配置项
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 项目根目录
BASE_DIR = Path(__file__).parent.absolute()

# 加载.env文件（如果存在）
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ 已加载配置文件: {env_path}")
else:
    print(f"⚠ 未找到.env文件: {env_path}，将使用环境变量或默认值")

# GPU配置
GPU_DEVICE_ID = int(os.getenv("GPU_DEVICE_ID", "0"))
CUDA_AVAILABLE = os.getenv("CUDA_AVAILABLE", "true").lower() == "true"

# 模型配置
MODEL_NAME = os.getenv("MODEL_NAME", "Tongyi-MAI/Z-Image-Turbo")
MODEL_TORCH_DTYPE = os.getenv("MODEL_TORCH_DTYPE", "bfloat16")  # float16, bfloat16, float32
LOW_CPU_MEM_USAGE = os.getenv("LOW_CPU_MEM_USAGE", "false").lower() == "true"

# 模型优化选项
ENABLE_FLASH_ATTENTION = os.getenv("ENABLE_FLASH_ATTENTION", "true").lower() == "true"
FLASH_ATTENTION_BACKEND = os.getenv("FLASH_ATTENTION_BACKEND", "flash")  # flash, _flash_3
ENABLE_MODEL_COMPILE = os.getenv("ENABLE_MODEL_COMPILE", "false").lower() == "true"
ENABLE_CPU_OFFLOAD = os.getenv("ENABLE_CPU_OFFLOAD", "false").lower() == "true"

# 图像输出配置
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 任务队列配置
MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", "100"))
TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", "300"))  # 秒

# Flask服务配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 默认生成参数
DEFAULT_HEIGHT = int(os.getenv("DEFAULT_HEIGHT", "1024"))
DEFAULT_WIDTH = int(os.getenv("DEFAULT_WIDTH", "1024"))
DEFAULT_NUM_INFERENCE_STEPS = int(os.getenv("DEFAULT_NUM_INFERENCE_STEPS", "9"))
DEFAULT_GUIDANCE_SCALE = float(os.getenv("DEFAULT_GUIDANCE_SCALE", "0.0"))

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ========================================
# Slide生成配置
# ========================================
# 注意：Slide生成功能需要配置以下API密钥才能正常工作
# 请通过环境变量设置或直接修改默认值

# 基础配置
SLIDE_MAX_QUEUE_SIZE = int(os.getenv("SLIDE_MAX_QUEUE_SIZE", "50"))
SLIDE_OUTPUT_DIR = Path(os.getenv("SLIDE_OUTPUT_DIR", BASE_DIR / "slide-gen" / "output"))
ENABLE_SLIDE_GENERATION = os.getenv("ENABLE_SLIDE_GENERATION", "true").lower() == "true"

# LLM配置（用于生成幻灯片内容）
# 必需：SLIDE_LLM_API_KEY - LLM服务的API密钥（如OpenAI API Key）
SLIDE_LLM_API_KEY = os.getenv("SLIDE_LLM_API_KEY", "")
SLIDE_LLM_API_URL = os.getenv("SLIDE_LLM_API_URL", "https://api.openai.com/v1/chat/completions")
SLIDE_LLM_MODEL = os.getenv("SLIDE_LLM_MODEL", "gpt-4")

# 图像生成配置（用于生成幻灯片中的图片）
# 必需：SLIDE_IMAGE_API_KEY - 图像生成服务的API密钥
# 必需：SLIDE_IMAGE_API_URL - 图像生成服务的API地址
# 注意：如果使用本地服务，设置为 http://localhost:5000 或保持空字符串使用internal bridge
SLIDE_IMAGE_API_KEY = os.getenv("SLIDE_IMAGE_API_KEY", "dummy-key-for-internal-bridge")
SLIDE_IMAGE_API_URL = os.getenv("SLIDE_IMAGE_API_URL", "http://localhost:5000")
SLIDE_IMAGE_MODEL = os.getenv("SLIDE_IMAGE_MODEL", "stable-diffusion-xl")

# 其他设置
SLIDE_DEFAULT_TIMEOUT = int(os.getenv("SLIDE_DEFAULT_TIMEOUT", "60"))  # API请求超时时间（秒）
SLIDE_MAX_RETRIES = int(os.getenv("SLIDE_MAX_RETRIES", "3"))  # API请求重试次数

