import { useState, useCallback } from 'react';
import { generateMultipleImages } from '@/lib/api';
import type { GenerateParams } from '@/types';
import { IMAGE_COUNT_OPTIONS } from '@/lib/constants';
import toast from 'react-hot-toast';

/**
 * 图片生成Hook
 */
export const useImageGeneration = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [taskIds, setTaskIds] = useState<string[]>([]);

  const generate = useCallback(
    async (params: GenerateParams, count: number = 1) => {
      if (isGenerating) {
        toast.error('正在生成中，请稍候...');
        return;
      }

      if (!params.prompt || params.prompt.trim().length === 0) {
        toast.error('请输入提示词');
        return;
      }

      if (!IMAGE_COUNT_OPTIONS.includes(count as any)) {
        toast.error('图片数量必须在1-4之间');
        return;
      }

      setIsGenerating(true);
      setTaskIds([]);

      try {
        const newTaskIds = await generateMultipleImages(params, count);
        setTaskIds(newTaskIds);
        toast.success(`成功提交 ${newTaskIds.length} 个生成任务`);
        return newTaskIds;
      } catch (error: any) {
        const errorMessage =
          error?.response?.data?.message ||
          error?.message ||
          '生成任务提交失败';
        toast.error(errorMessage);
        setTaskIds([]);
        throw error;
      } finally {
        setIsGenerating(false);
      }
    },
    [isGenerating]
  );

  const clearTasks = useCallback(() => {
    setTaskIds([]);
  }, []);

  return {
    generate,
    isGenerating,
    taskIds,
    clearTasks,
  };
};

