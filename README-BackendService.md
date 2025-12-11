# Z-Image-Turbo Flask 后台服务

基于Flask框架的Z-Image-Turbo图像生成模型API服务，提供生产级别的图像生成接口。

## 功能特性

- ✅ 模型启动时一次性加载，全局常驻GPU内存
- ✅ 线程安全的任务队列机制
- ✅ 支持任务状态追踪和查询
- ✅ 完善的错误处理和日志记录
- ✅ 统一的JSON API响应格式
- ✅ 支持GPU使用情况监控
- ✅ 任务超时和队列管理

## 环境要求

- Python 3.8+
- CUDA 11.8+ (GPU环境)
- 至少16GB GPU显存
- 8GB+ 系统内存

## 安装部署

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

创建 `.env` 文件或直接设置环境变量：

```bash
# GPU配置
GPU_DEVICE_ID=0
CUDA_AVAILABLE=true

# 模型配置
MODEL_NAME=Tongyi-MAI/Z-Image-Turbo
MODEL_TORCH_DTYPE=bfloat16

# 服务配置
HOST=0.0.0.0
PORT=5000
DEBUG=false

# 队列配置
MAX_QUEUE_SIZE=100
TASK_TIMEOUT=300

# 输出目录
OUTPUT_DIR=./outputs
```

### 3. 启动服务

#### 开发模式

```bash
python app.py
```

#### 生产模式（使用Gunicorn）

```bash
gunicorn -w 1 -b 0.0.0.0:5000 --timeout 600 app:app
```

**注意**: 由于模型需要独占GPU，worker数量应设置为1。

## API接口文档

所有API接口统一返回格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 1. 健康检查

**接口**: `GET /health`

**说明**: 检查服务健康状态

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "healthy",
    "model_loaded": true
  }
}
```

**cURL示例**:

```bash
curl http://localhost:5000/health
```

**Python示例**:

```python
import requests

response = requests.get("http://localhost:5000/health")
print(response.json())
```

---

### 2. 提交生成任务

**接口**: `POST /api/generate`

**说明**: 提交图像生成任务，返回任务ID

**请求参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| prompt | string | 是 | - | 文本提示词 |
| height | integer | 否 | 1024 | 图像高度 (64-2048) |
| width | integer | 否 | 1024 | 图像宽度 (64-2048) |
| num_inference_steps | integer | 否 | 9 | 推理步数 (1-50) |
| seed | integer | 否 | 随机 | 随机种子 |

**请求示例**:

```json
{
  "prompt": "A beautiful sunset over the ocean",
  "height": 1024,
  "width": 1024,
  "num_inference_steps": 9,
  "seed": 42
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending",
    "queue_position": 3
  }
}
```

**错误响应**:

```json
{
  "code": 400,
  "message": "prompt参数必填且不能为空",
  "data": {}
}
```

**cURL示例**:

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over the ocean",
    "height": 1024,
    "width": 1024,
    "num_inference_steps": 9
  }'
```

**Python示例**:

```python
import requests

url = "http://localhost:5000/api/generate"
data = {
    "prompt": "A beautiful sunset over the ocean",
    "height": 1024,
    "width": 1024,
    "num_inference_steps": 9,
    "seed": 42
}

response = requests.post(url, json=data)
result = response.json()
task_id = result["data"]["task_id"]
print(f"任务ID: {task_id}")
```

---

### 3. 查询任务状态

**接口**: `GET /api/task/<task_id>`

**说明**: 查询指定任务的状态和详细信息

**路径参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| task_id | string | 任务ID |

**响应示例** (排队中):

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending",
    "prompt": "A beautiful sunset over the ocean",
    "height": 1024,
    "width": 1024,
    "num_inference_steps": 9,
    "seed": 42,
    "created_at": "2024-01-01T12:00:00",
    "queue_position": 2
  }
}
```

**响应示例** (生成中):

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "prompt": "A beautiful sunset over the ocean",
    "height": 1024,
    "width": 1024,
    "num_inference_steps": 9,
    "seed": 42,
    "created_at": "2024-01-01T12:00:00",
    "started_at": "2024-01-01T12:00:05",
    "queue_position": 0
  }
}
```

**响应示例** (已完成):

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "prompt": "A beautiful sunset over the ocean",
    "height": 1024,
    "width": 1024,
    "num_inference_steps": 9,
    "seed": 42,
    "created_at": "2024-01-01T12:00:00",
    "started_at": "2024-01-01T12:00:05",
    "completed_at": "2024-01-01T12:00:30",
    "image_path": "/path/to/outputs/550e8400-e29b-41d4-a716-446655440000.png",
    "queue_position": 0
  }
}
```

**响应示例** (失败):

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "failed",
    "prompt": "A beautiful sunset over the ocean",
    "error_message": "CUDA out of memory",
    "created_at": "2024-01-01T12:00:00",
    "started_at": "2024-01-01T12:00:05",
    "completed_at": "2024-01-01T12:00:10"
  }
}
```

**cURL示例**:

```bash
curl http://localhost:5000/api/task/550e8400-e29b-41d4-a716-446655440000
```

**Python示例**:

```python
import requests
import time

task_id = "550e8400-e29b-41d4-a716-446655440000"

while True:
    response = requests.get(f"http://localhost:5000/api/task/{task_id}")
    result = response.json()
    status = result["data"]["status"]
    
    print(f"任务状态: {status}")
    
    if status == "completed":
        print("任务完成！")
        break
    elif status == "failed":
        print(f"任务失败: {result['data'].get('error_message')}")
        break
    
    time.sleep(2)  # 等待2秒后再次查询
```

---

### 4. 获取生成结果

**接口**: `GET /api/result/<task_id>`

**说明**: 获取生成的图像文件（任务完成时）或状态信息

**路径参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| task_id | string | 任务ID |

**响应**:

- 如果任务已完成: 返回PNG图像文件
- 如果任务未完成: 返回JSON状态信息

**响应示例** (未完成):

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "message": "任务尚未完成"
  }
}
```

**cURL示例**:

```bash
# 获取图像文件
curl http://localhost:5000/api/result/550e8400-e29b-41d4-a716-446655440000 \
  --output result.png
```

**Python示例**:

```python
import requests

task_id = "550e8400-e29b-41d4-a716-446655440000"
url = f"http://localhost:5000/api/result/{task_id}"

response = requests.get(url)

if response.headers.get('content-type') == 'image/png':
    # 保存图像
    with open('result.png', 'wb') as f:
        f.write(response.content)
    print("图像已保存")
else:
    # 显示状态信息
    print(response.json())
```

---

### 5. 查询系统状态

**接口**: `GET /api/status`

**说明**: 查询系统整体状态，包括队列信息、GPU使用情况等

**响应示例**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "queue": {
      "queue_size": 5,
      "max_queue_size": 100,
      "pending_tasks": 3,
      "processing_tasks": 1,
      "completed_tasks": 10,
      "failed_tasks": 0,
      "total_tasks": 14
    },
    "gpu": {
      "available": true,
      "device": "cuda:0",
      "memory_allocated_gb": 12.5,
      "memory_reserved_gb": 14.0,
      "memory_total_gb": 24.0,
      "memory_usage_percent": 52.08
    },
    "model_loaded": true
  }
}
```

**cURL示例**:

```bash
curl http://localhost:5000/api/status
```

**Python示例**:

```python
import requests

response = requests.get("http://localhost:5000/api/status")
status = response.json()["data"]

print(f"队列长度: {status['queue']['queue_size']}")
print(f"GPU使用率: {status['gpu']['memory_usage_percent']}%")
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在（任务不存在、接口不存在等） |
| 500 | 服务器内部错误 |
| 503 | 服务不可用（模型未加载、队列已满等） |

## 任务状态说明

| 状态 | 说明 |
|------|------|
| pending | 任务在队列中等待处理 |
| processing | 任务正在GPU上生成图像 |
| completed | 任务已完成，图像已生成 |
| failed | 任务处理失败 |

## 完整使用示例

### Python完整示例

```python
import requests
import time
import os

# 1. 检查服务健康状态
response = requests.get("http://localhost:5000/health")
print("服务状态:", response.json())

# 2. 提交生成任务
generate_url = "http://localhost:5000/api/generate"
task_data = {
    "prompt": "A beautiful Chinese landscape with mountains and rivers",
    "height": 1024,
    "width": 1024,
    "num_inference_steps": 9,
    "seed": 42
}

response = requests.post(generate_url, json=task_data)
result = response.json()

if result["code"] != 200:
    print(f"提交任务失败: {result['message']}")
    exit(1)

task_id = result["data"]["task_id"]
print(f"任务已提交，任务ID: {task_id}")

# 3. 轮询查询任务状态
task_url = f"http://localhost:5000/api/task/{task_id}"
max_wait_time = 300  # 最大等待5分钟
start_time = time.time()

while True:
    response = requests.get(task_url)
    result = response.json()
    status = result["data"]["status"]
    
    print(f"任务状态: {status}")
    
    if status == "completed":
        print("任务完成！")
        break
    elif status == "failed":
        print(f"任务失败: {result['data'].get('error_message')}")
        exit(1)
    
    # 检查超时
    if time.time() - start_time > max_wait_time:
        print("任务超时")
        exit(1)
    
    time.sleep(2)

# 4. 获取生成的图像
result_url = f"http://localhost:5000/api/result/{task_id}"
response = requests.get(result_url)

if response.headers.get('content-type') == 'image/png':
    output_path = f"output_{task_id}.png"
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"图像已保存至: {output_path}")
else:
    print("获取图像失败:", response.json())
```

### cURL完整示例

```bash
#!/bin/bash

# 1. 检查服务状态
echo "检查服务状态..."
curl http://localhost:5000/health

# 2. 提交任务
echo -e "\n提交生成任务..."
TASK_RESPONSE=$(curl -s -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful Chinese landscape",
    "height": 1024,
    "width": 1024,
    "num_inference_steps": 9
  }')

echo $TASK_RESPONSE | jq '.'

TASK_ID=$(echo $TASK_RESPONSE | jq -r '.data.task_id')
echo "任务ID: $TASK_ID"

# 3. 查询任务状态
echo -e "\n查询任务状态..."
while true; do
  STATUS_RESPONSE=$(curl -s http://localhost:5000/api/task/$TASK_ID)
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.data.status')
  
  echo "当前状态: $STATUS"
  
  if [ "$STATUS" == "completed" ]; then
    echo "任务完成！"
    break
  elif [ "$STATUS" == "failed" ]; then
    echo "任务失败"
    exit 1
  fi
  
  sleep 2
done

# 4. 下载图像
echo -e "\n下载生成的图像..."
curl http://localhost:5000/api/result/$TASK_ID \
  --output "result_${TASK_ID}.png"

echo "图像已保存"
```

## 性能优化建议

1. **模型编译**: 在配置中启用 `ENABLE_MODEL_COMPILE=true` 可以加速推理，但首次运行会较慢
2. **Flash Attention**: 默认启用Flash Attention-2，可提升性能
3. **队列管理**: 根据GPU显存调整 `MAX_QUEUE_SIZE`，避免内存溢出
4. **批量处理**: 虽然当前版本不支持批量，但可以通过并发提交多个任务来提高吞吐量

## 故障排查

### 模型加载失败

- 检查CUDA是否可用: `python -c "import torch; print(torch.cuda.is_available())"`
- 检查GPU显存是否足够（至少16GB）
- 检查模型路径是否正确

### 任务队列已满

- 增加 `MAX_QUEUE_SIZE` 配置
- 等待队列中的任务完成
- 检查是否有任务卡住

### GPU内存不足

- 启用CPU Offloading: `ENABLE_CPU_OFFLOAD=true`
- 减少并发任务数量
- 降低图像分辨率

### 任务超时

- 增加 `TASK_TIMEOUT` 配置
- 检查GPU性能
- 减少 `num_inference_steps`

## 项目结构

```
flask_backend/
├── app.py              # Flask应用主文件
├── model_manager.py    # 模型加载和管理
├── task_queue.py       # 任务队列管理
├── config.py           # 配置文件
├── requirements.txt    # 依赖清单
├── outputs/            # 生成图像存储目录
└── README.md           # 接口文档
```

## 许可证

本项目基于Z-Image-Turbo模型，请遵循相应的许可证要求。

## 联系方式

如有问题或建议，请提交Issue或Pull Request。

