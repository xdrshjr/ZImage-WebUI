'use client';

import { useMemo } from 'react';
import { ImageIcon } from 'lucide-react';
import { TaskItem } from './TaskItem';
import type { TaskListItem } from '@/types';
import { TaskStatus } from '@/types';

interface TaskListProps {
  tasks: TaskListItem[];
}

/**
 * 任务列表组件
 */
export const TaskList = ({ tasks }: TaskListProps) => {
  const sortedTasks = useMemo(() => {
    return [...tasks].sort((a, b) => {
      // 按状态排序：processing > pending > completed > failed
      const statusOrder = {
        [TaskStatus.PROCESSING]: 0,
        [TaskStatus.PENDING]: 1,
        [TaskStatus.COMPLETED]: 2,
        [TaskStatus.FAILED]: 3,
      };
      const orderDiff = statusOrder[a.status] - statusOrder[b.status];
      if (orderDiff !== 0) return orderDiff;
      // 相同状态按创建时间倒序
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    });
  }, [tasks]);

  if (tasks.length === 0) {
    return (
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">任务列表</h2>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="rounded-full bg-primary/10 p-4 mb-4">
            <ImageIcon className="h-8 w-8 text-primary" />
          </div>
          <p className="text-sm text-muted-foreground">
            这里会产生图像生成结果
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            提交生成任务后，结果将显示在这里
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">任务列表</h2>
      <div className="space-y-3">
        {sortedTasks.map((task) => (
          <TaskItem key={task.taskId} task={task} />
        ))}
      </div>
    </div>
  );
};

