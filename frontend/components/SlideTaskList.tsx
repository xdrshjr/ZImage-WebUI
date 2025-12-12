/**
 * Slide任务列表组件
 */
'use client';

import { useTranslation } from 'react-i18next';
import { Presentation } from 'lucide-react';
import { SlideTaskItem } from './SlideTaskItem';
import type { SlideTaskListItem } from '@/types';

interface SlideTaskListProps {
  tasks: SlideTaskListItem[];
}

export const SlideTaskList = ({ tasks }: SlideTaskListProps) => {
  const { t } = useTranslation();

  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="rounded-full bg-muted/50 p-6 mb-4">
          <Presentation className="h-12 w-12 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold mb-2">
          {t('slideTaskList.empty')}
        </h3>
        <p className="text-sm text-muted-foreground max-w-sm">
          {t('slideTaskList.emptyHint')}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          {t('slideTaskList.title')}
        </h2>
        <span className="text-sm text-muted-foreground">
          {tasks.length} {t('slide.numSlidesUnit')}
        </span>
      </div>
      
      <div className="space-y-3">
        {tasks.map((task) => (
          <SlideTaskItem key={task.taskId} task={task} />
        ))}
      </div>
    </div>
  );
};

