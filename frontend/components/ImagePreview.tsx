'use client';

import { useEffect } from 'react';
import { X, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import type { TaskListItem } from '@/types';
import { downloadFile } from '@/lib/utils';
import toast from 'react-hot-toast';

interface ImagePreviewProps {
  imageUrl: string;
  task: TaskListItem;
  onClose: () => void;
}

/**
 * 图片预览模态框组件
 */
export const ImagePreview = ({
  imageUrl,
  task,
  onClose,
}: ImagePreviewProps) => {
  // 键盘快捷键：ESC关闭
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);

  const handleDownload = async () => {
    try {
      const blob = await api.getTaskResult(task.taskId);
      const url = URL.createObjectURL(blob);
      const filename = `${task.prompt.slice(0, 30).replace(/[^a-z0-9]/gi, '_')}_${task.taskId.slice(0, 8)}.png`;
      downloadFile(url, filename);
      URL.revokeObjectURL(url);
      toast.success('图片已下载');
    } catch (error: any) {
      console.error('下载失败:', error);
      toast.error('下载失败');
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative max-w-7xl max-h-[90vh] w-full mx-4 bg-card rounded-lg shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold truncate">{task.prompt}</h3>
            <p className="text-sm text-muted-foreground mt-1">
              {task.params.width}×{task.params.height} •{' '}
              {task.params.numInferenceSteps} 步
              {task.params.seed !== null && ` • 种子: ${task.params.seed}`}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleDownload}>
              <Download className="h-4 w-4 mr-2" />
              下载
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-9 w-9"
            >
              <X className="h-5 w-5" />
              <span className="sr-only">关闭</span>
            </Button>
          </div>
        </div>

        {/* 图片区域 */}
        <div className="p-4 overflow-auto max-h-[calc(90vh-120px)] flex items-center justify-center">
          <img
            src={imageUrl}
            alt={task.prompt}
            className="max-w-full max-h-full object-contain rounded-md"
          />
        </div>
      </div>
    </div>
  );
};

