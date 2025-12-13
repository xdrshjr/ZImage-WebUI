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

/**
 * Slide任务状态枚举
 */
export enum SlideTaskStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

/**
 * Slide生成参数
 */
export interface SlideGenerateParams {
  base_text: string;
  num_slides?: number;
  aspect_ratio?: '16:9' | '4:3' | '16:10';
  style?: 'professional' | 'creative' | 'minimal' | 'academic';
  content_richness?: 'concise' | 'moderate' | 'detailed';
  color_scheme?: 'light_blue' | 'dark_slate' | 'warm_cream' | 'dark_navy' | 'soft_green';
}

/**
 * Slide生成任务响应
 */
export interface SlideGenerateResponse {
  task_id: string;
  status: SlideTaskStatus;
  queue_position: number;
}

/**
 * Slide任务详情
 */
export interface SlideTaskDetail {
  task_id: string;
  status: SlideTaskStatus;
  base_text: string;
  num_slides: number;
  aspect_ratio: string;
  style: string;
  content_richness: string;
  color_scheme: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  queue_position: number;
  output_path?: string;
  pdf_path?: string;
  ppt_path?: string;
  slide_image_paths?: string[];
  slides_generated?: number;
  error_message?: string;
  errors?: string[];
}

/**
 * Slide任务列表项（用于UI显示）
 */
export interface SlideTaskListItem {
  taskId: string;
  baseText: string;
  status: SlideTaskStatus;
  queuePosition: number;
  createdAt: string;
  slidesGenerated?: number;
  pdfAvailable: boolean;
  pptxAvailable: boolean;
  slideImageCount: number;
  errorMessage?: string;
  params: {
    numSlides: number;
    aspectRatio: string;
    style: string;
    contentRichness: string;
    colorScheme: string;
  };
}

/**
 * Slide系统状态响应
 */
export interface SlideSystemStatusResponse {
  queue: {
    queue_size: number;
    max_queue_size: number;
    pending_tasks: number;
    processing_tasks: number;
    completed_tasks: number;
    failed_tasks: number;
    total_tasks: number;
  };
  generator_ready: boolean;
  enabled: boolean;
}

/**
 * 任务类型枚举
 */
export enum TaskType {
  IMAGE_GENERATION = 'image',
  SLIDE_GENERATION = 'slide',
}

