"""
配置文件
定义所有系统配置项
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.absolute()

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

