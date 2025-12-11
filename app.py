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
    global model_manager, task_queue_manager
    
    logger.info("开始初始化应用...")
    
    # 初始化模型管理器
    model_manager = ModelManager()
    if not model_manager.load_model():
        logger.error("模型加载失败，应用无法正常启动")
        raise RuntimeError("模型加载失败")
    
    # 初始化任务队列管理器
    task_queue_manager = TaskQueueManager(model_manager)
    
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

