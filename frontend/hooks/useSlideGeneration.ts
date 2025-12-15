/**
 * Slide生成相关的React Hook
 */
import { useState, useCallback } from 'react';
import { api } from '@/lib/api';
import type { SlideGenerateParams } from '@/types';
import { logger } from '@/lib/logger';

export interface UseSlideGenerationReturn {
  generate: (params: SlideGenerateParams) => Promise<string | null>;
  isGenerating: boolean;
  taskIds: string[];
  clearTasks: () => void;
}

/**
 * Slide生成Hook
 * 管理Slide生成任务的提交和状态
 */
export const useSlideGeneration = (): UseSlideGenerationReturn => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [taskIds, setTaskIds] = useState<string[]>([]);

  /**
   * 提交Slide生成任务
   */
  const generate = useCallback(async (params: SlideGenerateParams): Promise<string | null> => {
    setIsGenerating(true);
    
    try {
      logger.info('提交Slide生成任务', params);
      
      const result = await api.generateSlide(params);
      
      logger.info('Slide任务已提交', {
        taskId: result.task_id,
        status: result.status,
        queuePosition: result.queue_position,
      });
      
      // 添加任务ID到列表
      setTaskIds((prev) => [result.task_id, ...prev]);
      
      return result.task_id;
    } catch (error) {
      logger.error('提交Slide任务失败', error);
      throw error;
    } finally {
      setIsGenerating(false);
    }
  }, []);

  /**
   * 清空任务列表
   */
  const clearTasks = useCallback(() => {
    logger.info('清空Slide任务列表');
    setTaskIds([]);
  }, []);

  return {
    generate,
    isGenerating,
    taskIds,
    clearTasks,
  };
};




