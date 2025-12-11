/**
 * 任务状态枚举
 */
export enum TaskStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

/**
 * API响应格式
 */
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

/**
 * 健康检查响应
 */
export interface HealthCheckResponse {
  status: string;
  model_loaded: boolean;
}

/**
 * 生成任务请求参数
 */
export interface GenerateParams {
  prompt: string;
  height?: number;
  width?: number;
  num_inference_steps?: number;
  seed?: number | null;
}

/**
 * 生成任务响应
 */
export interface GenerateResponse {
  task_id: string;
  status: TaskStatus;
  queue_position: number;
}

/**
 * 任务详情
 */
export interface TaskDetail {
  task_id: string;
  status: TaskStatus;
  prompt: string;
  height: number;
  width: number;
  num_inference_steps: number;
  seed: number | null;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  image_path?: string;
  error_message?: string;
  queue_position: number;
}

/**
 * 系统状态响应
 */
export interface SystemStatusResponse {
  queue: {
    queue_size: number;
    max_queue_size: number;
    pending_tasks: number;
    processing_tasks: number;
    completed_tasks: number;
    failed_tasks: number;
    total_tasks: number;
  };
  gpu: {
    available: boolean;
    device: string;
    memory_allocated_gb: number;
    memory_reserved_gb: number;
    memory_total_gb: number;
    memory_usage_percent: number;
  };
  model_loaded: boolean;
}

/**
 * 任务列表项（用于UI显示）
 */
export interface TaskListItem {
  taskId: string;
  prompt: string;
  status: TaskStatus;
  queuePosition: number;
  createdAt: string;
  imageUrl?: string;
  errorMessage?: string;
  params: {
    height: number;
    width: number;
    numInferenceSteps: number;
    seed: number | null;
  };
}

/**
 * 提示词模板
 */
export interface PromptTemplate {
  id: string;
  name: string;
  category: string;
  prompt: string;
  description: string;
}

