/**
 * Slide任务轮询Hook
 * 定期查询任务状态
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '@/lib/api';
import type { SlideTaskDetail } from '@/types';
import { SlideTaskStatus } from '@/types';
import { logger } from '@/lib/logger';

const POLLING_INTERVAL = 2000; // 2秒
const MAX_POLLING_DURATION = 1800000; // 30分钟

export interface UseSlideTaskPollingReturn {
  tasks: Record<string, SlideTaskDetail>;
  isPolling: boolean;
}

/**
 * Slide任务轮询Hook
 * 自动轮询任务状态直到完成或失败
 */
export const useSlideTaskPolling = (
  taskIds: string[]
): UseSlideTaskPollingReturn => {
  const [tasks, setTasks] = useState<Record<string, SlideTaskDetail>>({});
  const [isPolling, setIsPolling] = useState(false);
  const pollingTimerRef = useRef<NodeJS.Timeout | null>(null);
  const taskStartTimesRef = useRef<Record<string, number>>({});

  /**
   * 查询单个任务状态
   */
  const fetchTaskStatus = useCallback(async (taskId: string) => {
    try {
      const taskDetail = await api.getSlideTaskStatus(taskId);
      
      logger.debug('Slide任务状态更新', {
        taskId,
        status: taskDetail.status,
        queuePosition: taskDetail.queue_position,
        slidesGenerated: taskDetail.slides_generated,
      });
      
      setTasks((prev) => ({
        ...prev,
        [taskId]: taskDetail,
      }));
      
      return taskDetail;
    } catch (error) {
      logger.error('查询Slide任务状态失败', { taskId, error });
      return null;
    }
  }, []);

  /**
   * 检查任务是否需要继续轮询
   */
  const shouldContinuePolling = useCallback((taskDetail: SlideTaskDetail, taskId: string): boolean => {
    // 如果任务已完成或失败，停止轮询
    if (
      taskDetail.status === SlideTaskStatus.COMPLETED ||
      taskDetail.status === SlideTaskStatus.FAILED
    ) {
      return false;
    }
    
    // 检查是否超时
    const startTime = taskStartTimesRef.current[taskId];
    if (startTime && Date.now() - startTime > MAX_POLLING_DURATION) {
      logger.warn('Slide任务轮询超时', { taskId });
      return false;
    }
    
    return true;
  }, []);

  /**
   * 轮询所有任务
   */
  const pollTasks = useCallback(async () => {
    if (taskIds.length === 0) {
      setIsPolling(false);
      return;
    }
    
    setIsPolling(true);
    
    // 查询所有任务状态
    const results = await Promise.all(
      taskIds.map((taskId) => fetchTaskStatus(taskId))
    );
    
    // 检查是否还有需要继续轮询的任务
    const hasActiveTask = results.some((taskDetail, index) => {
      if (!taskDetail) return false;
      return shouldContinuePolling(taskDetail, taskIds[index]);
    });
    
    if (!hasActiveTask) {
      setIsPolling(false);
      logger.info('所有Slide任务已完成或失败，停止轮询');
    }
  }, [taskIds, fetchTaskStatus, shouldContinuePolling]);

  /**
   * 初始化任务开始时间
   */
  useEffect(() => {
    taskIds.forEach((taskId) => {
      if (!taskStartTimesRef.current[taskId]) {
        taskStartTimesRef.current[taskId] = Date.now();
      }
    });
  }, [taskIds]);

  /**
   * 设置轮询定时器
   */
  useEffect(() => {
    if (taskIds.length === 0) {
      // 清除定时器
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
        pollingTimerRef.current = null;
      }
      setIsPolling(false);
      return;
    }
    
    // 立即执行一次
    pollTasks();
    
    // 设置定时器
    pollingTimerRef.current = setInterval(pollTasks, POLLING_INTERVAL);
    
    // 清理函数
    return () => {
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
        pollingTimerRef.current = null;
      }
    };
  }, [taskIds, pollTasks]);

  return {
    tasks,
    isPolling,
  };
};

