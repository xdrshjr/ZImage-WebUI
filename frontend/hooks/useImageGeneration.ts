import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { generateMultipleImages } from '@/lib/api';
import type { GenerateParams } from '@/types';
import { IMAGE_COUNT_OPTIONS } from '@/lib/constants';
import toast from 'react-hot-toast';

/**
 * 图片生成Hook
 */
export const useImageGeneration = () => {
  const { t } = useTranslation();
  const [isGenerating, setIsGenerating] = useState(false);
  const [taskIds, setTaskIds] = useState<string[]>([]);

  const generate = useCallback(
    async (params: GenerateParams, count: number = 1) => {
      if (isGenerating) {
        toast.error(t('toast.generating'));
        return;
      }

      if (!params.prompt || params.prompt.trim().length === 0) {
        toast.error(t('toast.promptRequired'));
        return;
      }

      if (!IMAGE_COUNT_OPTIONS.includes(count as any)) {
        toast.error(t('toast.imageCountError'));
        return;
      }

      setIsGenerating(true);
      setTaskIds([]);

      try {
        const newTaskIds = await generateMultipleImages(params, count);
        setTaskIds(newTaskIds);
        toast.success(t('toast.generateSuccess', { count: newTaskIds.length }));
        return newTaskIds;
      } catch (error: any) {
        const errorMessage =
          error?.response?.data?.message ||
          error?.message ||
          t('toast.generateError');
        toast.error(errorMessage);
        setTaskIds([]);
        throw error;
      } finally {
        setIsGenerating(false);
      }
    },
    [isGenerating, t]
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

