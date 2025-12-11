import axios, { AxiosInstance } from 'axios';
import type {
  ApiResponse,
  GenerateParams,
  GenerateResponse,
  TaskDetail,
  HealthCheckResponse,
  SystemStatusResponse,
} from '@/types';
import { DEFAULT_API_BASE_URL, STORAGE_KEYS } from './constants';

/**
 * API配置管理类
 */
export class ApiConfig {
  private static STORAGE_KEY = STORAGE_KEYS.API_CONFIG;

  /**
   * 获取API基础URL
   * 优先级：localStorage（用户保存的配置）> 环境变量 > 默认值
   * 初始时读取.env，用户修改后遵循用户修改的配置
   */
  static getBaseUrl(): string {
    // 优先使用localStorage中的用户配置（仅在客户端）
    // 如果用户保存过配置，则优先使用用户配置
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        return stored;
      }
    }
    
    // 其次使用环境变量（在客户端和服务端都可用）
    const envUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    if (envUrl) {
      return envUrl;
    }
    
    // 最后使用默认值
    return DEFAULT_API_BASE_URL;
  }

  /**
   * 设置API基础URL
   */
  static setBaseUrl(url: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(this.STORAGE_KEY, url);
  }

  /**
   * 测试连接
   */
  static async testConnection(url?: string): Promise<boolean> {
    try {
      const baseUrl = url || this.getBaseUrl();
      const response = await axios.get<ApiResponse<HealthCheckResponse>>(
        `${baseUrl}/health`,
        { timeout: 5000 }
      );
      
      return (
        response.data.code === 200 &&
        response.data.data.model_loaded === true
      );
    } catch {
      return false;
    }
  }
}

/**
 * 创建axios实例
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: ApiConfig.getBaseUrl(),
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 请求拦截器：动态更新baseURL
  client.interceptors.request.use((config) => {
    config.baseURL = ApiConfig.getBaseUrl();
    return config;
  });

  return client;
};

const apiClient = createApiClient();

/**
 * API调用函数
 */
export const api = {
  /**
   * 健康检查
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await apiClient.get<ApiResponse<HealthCheckResponse>>(
      '/health'
    );
    if (response.data.code !== 200) {
      throw new Error(response.data.message);
    }
    return response.data.data;
  },

  /**
   * 提交生成任务
   */
  async generateImage(params: GenerateParams): Promise<GenerateResponse> {
    const response = await apiClient.post<ApiResponse<GenerateResponse>>(
      '/api/generate',
      params
    );
    if (response.data.code !== 200) {
      throw new Error(response.data.message);
    }
    return response.data.data;
  },

  /**
   * 查询任务状态
   */
  async getTaskStatus(taskId: string): Promise<TaskDetail> {
    const response = await apiClient.get<ApiResponse<TaskDetail>>(
      `/api/task/${taskId}`
    );
    if (response.data.code !== 200) {
      throw new Error(response.data.message);
    }
    return response.data.data;
  },

  /**
   * 获取任务结果（图片）
   */
  async getTaskResult(taskId: string): Promise<Blob> {
    const response = await apiClient.get(`/api/result/${taskId}`, {
      responseType: 'blob',
    });
    
    // 检查是否是JSON错误响应
    if (response.headers['content-type']?.includes('application/json')) {
      const text = await response.data.text();
      const json = JSON.parse(text);
      throw new Error(json.message || '获取图片失败');
    }
    
    return response.data;
  },

  /**
   * 获取系统状态
   */
  async getSystemStatus(): Promise<SystemStatusResponse> {
    const response = await apiClient.get<ApiResponse<SystemStatusResponse>>(
      '/api/status'
    );
    if (response.data.code !== 200) {
      throw new Error(response.data.message);
    }
    return response.data.data;
  },
};

/**
 * 批量生成图片
 */
export const generateMultipleImages = async (
  params: GenerateParams,
  count: number
): Promise<string[]> => {
  const taskIds: string[] = [];
  
  for (let i = 0; i < count; i++) {
    try {
      // 如果没有指定种子，为每张图片生成不同的随机种子
      const generateParams: GenerateParams = { ...params };
      if (generateParams.seed === null || generateParams.seed === undefined) {
        // 生成一个随机种子（0 到 2147483647 之间的整数）
        generateParams.seed = Math.floor(Math.random() * 2147483647);
      }
      
      const result = await api.generateImage(generateParams);
      taskIds.push(result.task_id);
    } catch (error) {
      console.error(`生成第 ${i + 1} 个任务失败:`, error);
      throw error;
    }
  }
  
  return taskIds;
};

