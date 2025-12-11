import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import type { TaskDetail } from '@/types';
import { TASK_POLLING_INTERVAL } from '@/lib/constants';

/**
 * 任务轮询Hook
 */
export const useTaskPolling = (taskIds: string[]) => {
  const [tasks, setTasks] = useState<Record<string, TaskDetail>>({});
  const [isPolling, setIsPolling] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (taskIds.length === 0) {
      setIsPolling(false);
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    setIsPolling(true);

    // 立即查询一次
    const fetchTasks = async () => {
      const taskPromises = taskIds.map(async (taskId) => {
        try {
          const task = await api.getTaskStatus(taskId);
          return { taskId, task };
        } catch (error) {
          console.error(`查询任务 ${taskId} 失败:`, error);
          return null;
        }
      });

      const results = await Promise.all(taskPromises);
      const newTasks: Record<string, TaskDetail> = {};

      results.forEach((result) => {
        if (result) {
          newTasks[result.taskId] = result.task;
        }
      });

      // 更新任务状态并检查是否全部完成
      setTasks((prev) => {
        const updated = { ...prev, ...newTasks };
        
        // 检查是否所有任务都已完成或失败
        const allFinished = taskIds.every((taskId) => {
          const task = updated[taskId];
          return (
            task?.status === 'completed' || task?.status === 'failed'
          );
        });

        if (allFinished && intervalRef.current) {
          setIsPolling(false);
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }

        return updated;
      });
    };

    fetchTasks();

    // 设置轮询
    intervalRef.current = setInterval(fetchTasks, TASK_POLLING_INTERVAL);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [taskIds]);

  // 手动停止轮询
  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  };

  return {
    tasks,
    isPolling,
    stopPolling,
  };
};

