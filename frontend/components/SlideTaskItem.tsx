/**
 * Slide任务项组件
 */
'use client';

import { useState, useCallback } from 'react';
import { Download, FileText, Image as ImageIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import type { SlideTaskListItem } from '@/types';
import { SlideTaskStatus } from '@/types';
import { api } from '@/lib/api';
import { logger } from '@/lib/logger';

interface SlideTaskItemProps {
  task: SlideTaskListItem;
}

export const SlideTaskItem = ({ task }: SlideTaskItemProps) => {
  const { t } = useTranslation();
  const [downloading, setDownloading] = useState<string | null>(null);

  /**
   * 下载PDF
   */
  const handleDownloadPdf = useCallback(async () => {
    setDownloading('pdf');
    
    try {
      logger.info('下载Slide PDF', { taskId: task.taskId });
      
      const blob = await api.getSlidePdfResult(task.taskId);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `presentation_${task.taskId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      logger.info('✓ PDF下载成功');
    } catch (error) {
      logger.error('✗ PDF下载失败', error);
      alert(t('slideToast.downloadFailed'));
    } finally {
      setDownloading(null);
    }
  }, [task.taskId, t]);

  /**
   * 下载PPTX (PowerPoint)
   */
  const handleDownloadPptx = useCallback(async () => {
    setDownloading('pptx');
    
    try {
      logger.info('下载Slide PPTX', { taskId: task.taskId });
      
      const blob = await api.getSlidePptxResult(task.taskId);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `presentation_${task.taskId}.pptx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      logger.info('✓ PPTX下载成功');
    } catch (error) {
      logger.error('✗ PPTX下载失败', error);
      alert(t('slideToast.downloadFailed'));
    } finally {
      setDownloading(null);
    }
  }, [task.taskId, t]);

  /**
   * 下载单张幻灯片图片
   */
  const handleDownloadSlide = useCallback(async (slideNumber: number) => {
    setDownloading(`slide-${slideNumber}`);
    
    try {
      logger.info('下载幻灯片图片', { taskId: task.taskId, slideNumber });
      
      const blob = await api.getSlideImage(task.taskId, slideNumber);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `slide_${slideNumber}.png`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      logger.info('✓ 幻灯片图片下载成功');
    } catch (error) {
      logger.error('✗ 幻灯片图片下载失败', error);
      alert(t('slideToast.downloadFailed'));
    } finally {
      setDownloading(null);
    }
  }, [task.taskId, t]);

  /**
   * 渲染状态徽章
   */
  const renderStatusBadge = () => {
    const statusConfig = {
      [SlideTaskStatus.PENDING]: {
        color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        text: t('slideTaskStatus.pending', { position: task.queuePosition }),
      },
      [SlideTaskStatus.PROCESSING]: {
        color: 'bg-blue-100 text-blue-800 border-blue-200',
        text: t('slideTaskStatus.processing'),
      },
      [SlideTaskStatus.COMPLETED]: {
        color: 'bg-green-100 text-green-800 border-green-200',
        text: t('slideTaskStatus.completed'),
      },
      [SlideTaskStatus.FAILED]: {
        color: 'bg-red-100 text-red-800 border-red-200',
        text: t('slideTaskStatus.failed', {
          message: task.errorMessage || t('taskStatus.unknownError'),
        }),
      },
    };

    const config = statusConfig[task.status];

    return (
      <span
        className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border ${config.color}`}
      >
        {config.text}
      </span>
    );
  };

  return (
    <div className="border rounded-lg p-4 bg-card hover:shadow-md transition-shadow">
      {/* 头部 */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-foreground truncate">
            {task.baseText}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {new Date(task.createdAt).toLocaleString()}
          </p>
        </div>
        {renderStatusBadge()}
      </div>

      {/* 参数信息 */}
      <div className="flex flex-wrap gap-2 mb-3 text-xs text-muted-foreground">
        <span>
          {task.params.numSlides} {t('slide.numSlidesUnit')}
        </span>
        <span>•</span>
        <span>{task.params.aspectRatio}</span>
        <span>•</span>
        <span>{t(`slideStyle.${task.params.style}`)}</span>
        <span>•</span>
        <span>{t(`slideContentRichness.${task.params.contentRichness}`)}</span>
        <span>•</span>
        <span>{t(`slideColorScheme.${task.params.colorScheme}`)}</span>
      </div>

      {/* 完成状态：显示下载按钮 */}
      {task.status === SlideTaskStatus.COMPLETED && (
        <div className="space-y-2">
          {/* 生成结果信息 */}
          <p className="text-sm text-muted-foreground">
            {t('slideTaskList.slidesGenerated', {
              count: task.slidesGenerated || 0,
            })}
          </p>

          {/* 下载按钮组 */}
          <div className="flex flex-wrap gap-2">
            {/* 下载PDF */}
            {task.pdfAvailable && (
              <Button
                size="sm"
                variant="outline"
                onClick={handleDownloadPdf}
                disabled={downloading === 'pdf'}
                className="gap-2"
              >
                <FileText className="h-4 w-4" />
                {downloading === 'pdf'
                  ? t('button.downloading')
                  : t('slideTaskList.downloadPdf')}
              </Button>
            )}

            {/* 下载PPTX */}
            {task.pptxAvailable && (
              <Button
                size="sm"
                variant="outline"
                onClick={handleDownloadPptx}
                disabled={downloading === 'pptx'}
                className="gap-2"
              >
                <Download className="h-4 w-4" />
                {downloading === 'pptx'
                  ? t('button.downloading')
                  : t('slideTaskList.downloadPptx')}
              </Button>
            )}

            {/* 下载单张幻灯片 */}
            {task.slideImageCount > 0 &&
              Array.from({ length: Math.min(task.slideImageCount, 6) }).map(
                (_, index) => {
                  const slideNumber = index + 1;
                  return (
                    <Button
                      key={slideNumber}
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDownloadSlide(slideNumber)}
                      disabled={downloading === `slide-${slideNumber}`}
                      className="gap-1"
                    >
                      <ImageIcon className="h-3 w-3" />
                      {slideNumber}
                    </Button>
                  );
                }
              )}

            {/* 如果幻灯片数量超过6张，显示省略号 */}
            {task.slideImageCount > 6 && (
              <span className="text-xs text-muted-foreground self-center">
                ... +{task.slideImageCount - 6}
              </span>
            )}
          </div>
        </div>
      )}

      {/* 处理中状态：显示进度指示 */}
      {task.status === SlideTaskStatus.PROCESSING && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
          <span>{t('slideTaskStatus.processing')}</span>
        </div>
      )}
    </div>
  );
};

