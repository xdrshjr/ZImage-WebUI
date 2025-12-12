'use client';

import { useState } from 'react';
import { Sparkles, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation();
  const [isEnhancing, setIsEnhancing] = useState(false);

  const handleEnhancePrompt = async () => {
    if (!currentPrompt.trim()) {
      toast.error(t('prompt.emptyError'));
      logger.warn('Prompt enhancement failed: empty prompt');
      return;
    }

    setIsEnhancing(true);
    logger.info('Starting prompt enhancement', { promptLength: currentPrompt.length });

    try {
      const enhanced = await enhancePromptWithLLM(currentPrompt.trim());
      onEnhance(enhanced);
      toast.success(t('prompt.enhanceSuccess'));
      logger.info('Prompt enhancement successful', {
        originalLength: currentPrompt.length,
        enhancedLength: enhanced.length,
      });
    } catch (error: any) {
      logger.error('Prompt enhancement failed', {
        error: error.message,
        promptLength: currentPrompt.length,
      });
      toast.error(error.message || t('prompt.enhanceError'));
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
          {t('prompt.enhancing')}
        </>
      ) : (
        <>
          <Sparkles className="h-4 w-4" />
          {t('prompt.enhance')}
        </>
      )}
    </Button>
  );
};

