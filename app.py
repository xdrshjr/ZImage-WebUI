"""
Flask主应用
提供图像生成API服务
"""
import logging
import os
import queue
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import config
from model_manager import ModelManager
from task_queue import TaskQueueManager, TaskStatus
from slide_generator import get_slide_generator
from slide_task_queue import SlideTaskQueueManager, SlideTaskStatus

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量
model_manager: ModelManager = None
task_queue_manager: TaskQueueManager = None
slide_generator = None
slide_task_queue_manager: SlideTaskQueueManager = None


def create_response(code: int = 200, message: str = "success", data: dict = None):
    """
    创建统一的API响应格式
    
    Args:
        code: 状态码
        message: 消息
        data: 数据字典
        
    Returns:
        dict: 响应字典
    """
    if data is None:
        data = {}
    return jsonify({
        "code": code,
        "message": message,
        "data": data
    })


def create_error_response(code: int = 400, message: str = "error", data: dict = None):
    """
    创建错误响应
    
    Args:
        code: 错误码
        message: 错误消息
        data: 额外数据
        
    Returns:
        dict: 错误响应字典
    """
    return create_response(code, message, data)


@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    Returns:
        JSON: 健康状态
    """
    try:
        model_ready = model_manager.is_model_ready() if model_manager else False
        return create_response(data={
            "status": "healthy",
            "model_loaded": model_ready
        })
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return create_error_response(500, "服务异常", {"status": "unhealthy"})


@app.route('/api/generate', methods=['POST'])
def generate_image():
    """
    提交图像生成任务
    
    请求参数:
        prompt (必填): 文本提示词
        height (可选): 图像高度，默认1024
        width (可选): 图像宽度，默认1024
        num_inference_steps (可选): 推理步数，默认9
        seed (可选): 随机种子，默认随机
        
    Returns:
        JSON: 任务ID和状态
    """
    try:
        # 检查模型是否就绪
        if not model_manager or not model_manager.is_model_ready():
            return create_error_response(503, "模型未加载，服务不可用")
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return create_error_response(400, "请求体不能为空")
        
        # 验证必填参数
        prompt = data.get('prompt')
        if not prompt or not isinstance(prompt, str) or len(prompt.strip()) == 0:
            return create_error_response(400, "prompt参数必填且不能为空")
        
        # 获取可选参数
        height = data.get('height', config.DEFAULT_HEIGHT)
        width = data.get('width', config.DEFAULT_WIDTH)
        num_inference_steps = data.get('num_inference_steps', config.DEFAULT_NUM_INFERENCE_STEPS)
        seed = data.get('seed')
        
        # 参数验证
        if not isinstance(height, int) or height < 64 or height > 2048:
            return create_error_response(400, "height参数必须是64-2048之间的整数")
        if not isinstance(width, int) or width < 64 or width > 2048:
            return create_error_response(400, "width参数必须是64-2048之间的整数")
        if not isinstance(num_inference_steps, int) or num_inference_steps < 1 or num_inference_steps > 50:
            return create_error_response(400, "num_inference_steps参数必须是1-50之间的整数")
        if seed is not None and (not isinstance(seed, int) or seed < 0):
            return create_error_response(400, "seed参数必须是非负整数")
        
        # 提交任务
        try:
            task_id = task_queue_manager.submit_task(
                prompt=prompt.strip(),
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                seed=seed,
            )
            
            # 获取任务信息
            task = task_queue_manager.get_task(task_id)
            
            return create_response(data={
                "task_id": task_id,
                "status": task.status.value,
                "queue_position": task.queue_position
            })
            
        except queue.Full:
            return create_error_response(503, "任务队列已满，请稍后重试")
            
    except Exception as e:
        logger.error(f"提交任务失败: {e}", exc_info=True)
        return create_error_response(500, f"服务器内部错误: {str(e)}")


@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id: str):
    """
    查询任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        JSON: 任务状态信息
    """
    try:
        task = task_queue_manager.get_task(task_id)
        
        if not task:
            return create_error_response(404, "任务不存在")
        
        # 更新队列位置
        task_queue_manager.update_queue_positions()
        
        return create_response(data=task.to_dict())
        
    except Exception as e:
        logger.error(f"查询任务状态失败: {e}", exc_info=True)
        return create_error_response(500, f"服务器内部错误: {str(e)}")


@app.route('/api/result/<task_id>', methods=['GET'])
def get_task_result(task_id: str):
    """
    获取生成结果
    
    Args:
        task_id: 任务ID
        
    Returns:
        图像文件（如果完成）或状态信息
    """
    try:
        task = task_queue_manager.get_task(task_id)
        
        if not task:
            return create_error_response(404, "任务不存在")
        
        # 如果任务未完成，返回状态信息
        if task.status != TaskStatus.COMPLETED:
            return create_response(data={
                "task_id": task_id,
                "status": task.status.value,
                "message": "任务尚未完成" if task.status == TaskStatus.PROCESSING else "任务处理失败" if task.status == TaskStatus.FAILED else "任务排队中"
            })
        
        # 检查文件是否存在
        if not task.image_path or not Path(task.image_path).exists():
            return create_error_response(404, "生成结果文件不存在")
        
        # 返回图像文件
        return send_file(
            task.image_path,
            mimetype='image/png',
            as_attachment=False,
            download_name=f"{task_id}.png"
        )
        
    except Exception as e:
        logger.error(f"获取任务结果失败: {e}", exc_info=True)
        return create_error_response(500, f"服务器内部错误: {str(e)}")


@app.route('/api/status', methods=['GET'])
def get_system_status():
    """
    查询系统状态
    
    Returns:
        JSON: 系统状态信息
    """
    try:
        # 获取队列状态
        queue_status = task_queue_manager.get_queue_status()
        
        # 获取GPU信息
        gpu_info = model_manager.get_gpu_info() if model_manager else {"available": False}
        
        # 获取模型状态
        model_ready = model_manager.is_model_ready() if model_manager else False
        
        return create_response(data={
            "queue": queue_status,
            "gpu": gpu_info,
            "model_loaded": model_ready,
        })
        
    except Exception as e:
        logger.error(f"查询系统状态失败: {e}", exc_info=True)
        return create_error_response(500, f"服务器内部错误: {str(e)}")


@app.route('/api/slide/generate', methods=['POST'])
def generate_slide():
    """
    提交幻灯片生成任务
    
    请求参数:
        base_text (必填): 源内容/主题
        num_slides (可选): 幻灯片数量，默认6，范围1-50
        aspect_ratio (可选): 幻灯片比例，默认16:9，可选4:3, 16:10
        style (可选): 视觉风格，默认professional，可选creative, minimal, academic
        content_richness (可选): 内容详细程度，默认moderate，可选concise, detailed
        
    Returns:
        JSON: 任务ID和状态
    """
    try:
        # 检查slide生成功能是否启用
        if not config.ENABLE_SLIDE_GENERATION:
            return create_error_response(503, "Slide生成功能未启用")
        
        # 检查生成器是否就绪
        if not slide_generator or not slide_generator.is_generator_ready():
            logger.warning("Slide生成器未就绪")
            return create_error_response(503, "Slide生成服务不可用，请检查配置")
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return create_error_response(400, "请求体不能为空")
        
        # 验证必填参数
        base_text = data.get('base_text')
        if not base_text or not isinstance(base_text, str) or len(base_text.strip()) == 0:
            return create_error_response(400, "base_text参数必填且不能为空")
        
        # 获取可选参数
        num_slides = data.get('num_slides', 6)
        aspect_ratio = data.get('aspect_ratio', '16:9')
        style = data.get('style', 'professional')
        content_richness = data.get('content_richness', 'moderate')
        
        # 参数验证
        if not isinstance(num_slides, int) or num_slides < 1 or num_slides > 50:
            return create_error_response(400, "num_slides参数必须是1-50之间的整数")
        
        if aspect_ratio not in ['16:9', '4:3', '16:10']:
            return create_error_response(400, "aspect_ratio参数必须是16:9, 4:3或16:10")
        
        if style not in ['professional', 'creative', 'minimal', 'academic']:
            return create_error_response(400, "style参数必须是professional, creative, minimal或academic")
        
        if content_richness not in ['concise', 'moderate', 'detailed']:
            return create_error_response(400, "content_richness参数必须是concise, moderate或detailed")
        
        # 提交任务
        try:
            task_id = slide_task_queue_manager.submit_task(
                base_text=base_text.strip(),
                num_slides=num_slides,
                aspect_ratio=aspect_ratio,
                style=style,
                content_richness=content_richness
            )
            
            # 获取任务信息
            task = slide_task_queue_manager.get_task(task_id)
            
            logger.info(f"✓ Slide生成任务已提交: {task_id}")
            
            return create_response(data={
                "task_id": task_id,
                "status": task.status.value,
                "queue_position": task.queue_position
            })
            
        except queue.Full:
            return create_error_response(503, "任务队列已满，请稍后重试")
            
    except Exception as e:
        logger.error(f"提交Slide任务失败: {e}", exc_info=True)
        return create_error_response(500, f"服务器内部错误: {str(e)}")


@app.route('/api/slide/task/<task_id>', methods=['GET'])
def get_slide_task_status(task_id: str):
    """
    查询Slide任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        JSON: 任务状态信息
    """
    try:
        task = slide_task_queue_manager.get_task(task_id)
        
        if not task:
            return create_error_response(404, "任务不存在")
        
        # 更新队列位置
        slide_task_queue_manager.update_queue_positions()
        
        logger.debug(f"查询Slide任务状态: {task_id} - {task.status.value}")
        
        return create_response(data=task.to_dict())
        
    except Exception as e:
        logger.error(f"查询Slide任务状态失败: {e}", exc_info=True)
        return create_error_response(500, f"服务器内部错误: {str(e)}")


@app.route('/api/slide/result/<task_id>', methods=['GET'])
def get_slide_result(task_id: str):
    """
    获取Slide生成结果PDF
    
    Args:
        task_id: 任务ID
        
    Returns:
        PDF文件（如果完成）或状态信息
    """
    try:
        task = slide_task_queue_manager.get_task(task_id)
        
        if not task:
            return create_error_response(404, "任务不存在")
        
        # 如果任务未完成，返回状态信息
        if task.status != SlideTaskStatus.COMPLETED:
            status_msg = {
                SlideTaskStatus.PENDING: "任务排队中",
                SlideTaskStatus.PROCESSING: "任务处理中",
                SlideTaskStatus.FAILED: "任务处理失败"
            }.get(task.status, "未知状态")
            
            return create_response(data={
                "task_id": task_id,
                "status": task.status.value,
                "message": status_msg
            })
        
        # 检查PDF文件是否存在
        if not task.pdf_path or not Path(task.pdf_path).exists():
            logger.warning(f"任务 {task_id} 的PDF文件不存在: {task.pdf_path}")
            return create_error_response(404, "PDF文件不存在")
        
        # 返回PDF文件
        logger.info(f"下载Slide PDF: {task_id}")
        return send_file(
            task.pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"presentation_{task_id}.pdf"
        )
        
    except Exception as e:
        logger.error(f"获取Slide结果失败: {e}", exc_info=True)
        return create_error_response(500, f"服务器内部错误: {str(e)}")


@app.route('/api/slide/result/<task_id>/image/<int:slide_number>', methods=['GET'])
def get_slide_image(task_id: str, slide_number: int):
    """
    获取单个幻灯片图片
    
    Args:
        task_id: 任务ID
        slide_number: 幻灯片编号（从1开始）
        
    Returns:
        PNG图片文件或错误信息
    """
    try:
        task = slide_task_queue_manager.get_task(task_id)
        
        if not task:
            return create_error_response(404, "任务不存在")
        
        # 如果任务未完成
        if task.status != SlideTaskStatus.COMPLETED:
            return create_error_response(400, "任务尚未完成")
        
        # 验证幻灯片编号
        if slide_number < 1 or slide_number > task.slides_generated:
            return create_error_response(400, f"幻灯片编号必须在1-{task.slides_generated}之间")
        
        # 查找对应的图片文件
        if not task.slide_image_paths:
            return create_error_response(404, "幻灯片图片不存在")
        
        # 幻灯片编号从1开始，数组索引从0开始
        image_index = slide_number - 1
        
        if image_index >= len(task.slide_image_paths):
            return create_error_response(404, f"幻灯片 {slide_number} 的图片不存在")
        
        image_path = Path(task.slide_image_paths[image_index])
        
        if not image_path.exists():
            logger.warning(f"幻灯片图片文件不存在: {image_path}")
            return create_error_response(404, "图片文件不存在")
        
        # 返回图片文件
        logger.debug(f"下载幻灯片图片: {task_id} - slide_{slide_number}")
        return send_file(
            str(image_path),
            mimetype='image/png',
            as_attachment=False,
            download_name=f"slide_{slide_number}.png"
        )
        
    except Exception as e:
        logger.error(f"获取幻灯片图片失败: {e}", exc_info=True)
        return create_error_response(500, f"服务器内部错误: {str(e)}")


@app.route('/api/slide/status', methods=['GET'])
def get_slide_system_status():
    """
    查询Slide系统状态
    
    Returns:
        JSON: Slide系统状态信息
    """
    try:
        # 获取队列状态
        queue_status = slide_task_queue_manager.get_queue_status()
        
        # 获取生成器状态
        generator_ready = slide_generator.is_generator_ready() if slide_generator else False
        
        logger.debug(f"Slide系统状态: 队列={queue_status['queue_size']}, 就绪={generator_ready}")
        
        return create_response(data={
            "queue": queue_status,
            "generator_ready": generator_ready,
            "enabled": config.ENABLE_SLIDE_GENERATION
        })
        
    except Exception as e:
        logger.error(f"查询Slide系统状态失败: {e}", exc_info=True)
        return create_error_response(500, f"服务器内部错误: {str(e)}")


@app.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return create_error_response(404, "接口不存在")


@app.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    logger.error(f"服务器内部错误: {error}", exc_info=True)
    return create_error_response(500, "服务器内部错误")


def initialize_app():
    """初始化应用"""
    global model_manager, task_queue_manager, slide_generator, slide_task_queue_manager
    
    logger.info("开始初始化应用...")
    
    # 初始化模型管理器
    model_manager = ModelManager()
    if not model_manager.load_model():
        logger.error("模型加载失败，应用无法正常启动")
        raise RuntimeError("模型加载失败")
    
    # 初始化任务队列管理器
    task_queue_manager = TaskQueueManager(model_manager)
    
    # 初始化Slide生成器（如果启用）
    if config.ENABLE_SLIDE_GENERATION:
        logger.info("初始化Slide生成服务...")
        try:
            slide_generator = get_slide_generator()
            
            if slide_generator.is_generator_ready():
                # 初始化Slide任务队列管理器
                slide_task_queue_manager = SlideTaskQueueManager(
                    slide_generator,
                    max_queue_size=config.SLIDE_MAX_QUEUE_SIZE
                )
                logger.info("✓ Slide生成服务初始化成功")
            else:
                logger.warning("⚠ Slide生成器未就绪，功能将不可用")
                logger.warning("  请检查slide-gen目录下的.env配置")
        except Exception as e:
            logger.error(f"✗ Slide生成服务初始化失败: {e}")
            logger.warning("  Slide生成功能将不可用，但图像生成功能正常")
    else:
        logger.info("Slide生成功能未启用")
    
    logger.info("应用初始化完成")


if __name__ == '__main__':
    # 初始化应用
    initialize_app()
    
    # 启动Flask服务
    logger.info(f"启动Flask服务: http://{config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        threaded=True
    )
else:
    # 使用gunicorn等WSGI服务器时
    initialize_app()

