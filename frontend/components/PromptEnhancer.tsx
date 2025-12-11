'use client';

import { useState } from 'react';
import { Sparkles, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { enhancePromptWithLLM } from '@/lib/llm';
import { logger } from '@/lib/logger';
import toast from 'react-hot-toast';

interface PromptEnhancerProps {
  currentPrompt: string;
  onEnhance: (enhanced: string) => void;
}

/**
 * 提示词润色组件
 */
export const PromptEnhancer = ({
  currentPrompt,
  onEnhance,
}: PromptEnhancerProps) => {
  const [isEnhancing, setIsEnhancing] = useState(false);

  const handleEnhancePrompt = async () => {
    if (!currentPrompt.trim()) {
      toast.error('请先输入提示词');
      logger.warn('润色失败：提示词为空');
      return;
    }

    setIsEnhancing(true);
    logger.info('开始润色提示词', { promptLength: currentPrompt.length });

    try {
      const enhanced = await enhancePromptWithLLM(currentPrompt.trim());
      onEnhance(enhanced);
      toast.success('提示词已润色');
      logger.info('润色成功', {
        originalLength: currentPrompt.length,
        enhancedLength: enhanced.length,
      });
    } catch (error: any) {
      logger.error('润色失败', {
        error: error.message,
        promptLength: currentPrompt.length,
      });
      toast.error(error.message || '润色失败，请稍后重试');
    } finally {
      setIsEnhancing(false);
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      className="gap-2"
      onClick={handleEnhancePrompt}
      disabled={isEnhancing || !currentPrompt.trim()}
    >
      {isEnhancing ? (
        <>
          <Loader2 className="h-4 w-4 animate-spin" />
          润色中...
        </>
      ) : (
        <>
          <Sparkles className="h-4 w-4" />
          润色
        </>
      )}
    </Button>
  );
};

