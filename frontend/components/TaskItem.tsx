'use client';

import { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, XCircle, Clock, Image as ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ImagePreview } from './ImagePreview';
import { api } from '@/lib/api';
import type { TaskListItem } from '@/types';
import { TaskStatus } from '@/types';
import { truncateText, formatDateTime } from '@/lib/utils';
import { cn } from '@/lib/utils';
import toast from 'react-hot-toast';

interface TaskItemProps {
  task: TaskListItem;
}

/**
 * 任务项组件
 */
export const TaskItem = ({ task }: TaskItemProps) => {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoadingImage, setIsLoadingImage] = useState(false);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  // 当任务完成时，加载图片
  useEffect(() => {
    if (task.status === TaskStatus.COMPLETED && !imageUrl && !isLoadingImage) {
      loadImage();
    }
  }, [task.status, task.taskId]);

  const loadImage = async () => {
    if (imageUrl) return;

    setIsLoadingImage(true);
    try {
      const blob = await api.getTaskResult(task.taskId);
      const url = URL.createObjectURL(blob);
      setImageUrl(url);
    } catch (error: any) {
      console.error('加载图片失败:', error);
      toast.error('加载图片失败');
    } finally {
      setIsLoadingImage(false);
    }
  };

  const getStatusIcon = () => {
    switch (task.status) {
      case TaskStatus.PENDING:
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case TaskStatus.PROCESSING:
        return <Loader2 className="h-5 w-5 text-primary animate-spin" />;
      case TaskStatus.COMPLETED:
        return <CheckCircle2 className="h-5 w-5 text-success" />;
      case TaskStatus.FAILED:
        return <XCircle className="h-5 w-5 text-destructive" />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (task.status) {
      case TaskStatus.PENDING:
        return `等待中 (队列位置: ${task.queuePosition})`;
      case TaskStatus.PROCESSING:
        return '生成中...';
      case TaskStatus.COMPLETED:
        return '已完成';
      case TaskStatus.FAILED:
        return `失败: ${task.errorMessage || '未知错误'}`;
      default:
        return task.status;
    }
  };

  const getStatusColor = () => {
    switch (task.status) {
      case TaskStatus.PENDING:
        return 'border-yellow-200 bg-yellow-50';
      case TaskStatus.PROCESSING:
        return 'border-primary/20 bg-primary/5';
      case TaskStatus.COMPLETED:
        return 'border-success/20 bg-success/5';
      case TaskStatus.FAILED:
        return 'border-destructive/20 bg-destructive/5';
      default:
        return 'border-border bg-card';
    }
  };

  return (
    <>
      <div
        className={cn(
          'border rounded-lg p-4 transition-all duration-200',
          getStatusColor()
        )}
      >
        <div className="flex items-start gap-4">
          {/* 状态图标 */}
          <div className="flex-shrink-0 mt-1">{getStatusIcon()}</div>

          {/* 内容区域 */}
          <div className="flex-1 min-w-0 space-y-2">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground mb-1">
                  {truncateText(task.prompt, 60)}
                </p>
                <p className="text-xs text-muted-foreground">
                  {getStatusText()}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatDateTime(task.createdAt)}
                </p>
              </div>

              {/* 操作按钮 */}
              {task.status === TaskStatus.COMPLETED && imageUrl && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsPreviewOpen(true)}
                  className="flex-shrink-0"
                >
                  <ImageIcon className="h-4 w-4 mr-2" />
                  预览
                </Button>
              )}
            </div>

            {/* 参数信息 */}
            <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
              <span>
                {task.params.width}×{task.params.height}
              </span>
              <span>•</span>
              <span>{task.params.numInferenceSteps} 步</span>
              {task.params.seed !== null && (
                <>
                  <span>•</span>
                  <span>种子: {task.params.seed}</span>
                </>
              )}
            </div>

            {/* 缩略图 */}
            {task.status === TaskStatus.COMPLETED && imageUrl && (
              <div className="mt-3">
                <button
                  onClick={() => setIsPreviewOpen(true)}
                  className="relative w-32 h-32 rounded-md overflow-hidden border border-border hover:opacity-90 transition-opacity"
                >
                  <img
                    src={imageUrl}
                    alt={task.prompt}
                    className="w-full h-full object-cover"
                  />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 图片预览 */}
      {isPreviewOpen && imageUrl && (
        <ImagePreview
          imageUrl={imageUrl}
          task={task}
          onClose={() => setIsPreviewOpen(false)}
        />
      )}
    </>
  );
};

