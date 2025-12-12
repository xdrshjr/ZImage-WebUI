'use client';

import { useTranslation } from 'react-i18next';
import { Textarea } from '@/components/ui/textarea';
import { PromptEnhancer } from './PromptEnhancer';

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  onEnhance?: (enhanced: string) => void;
}

/**
 * 提示词输入组件
 */
export const PromptInput = ({
  value,
  onChange,
  onEnhance,
}: PromptInputProps) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label htmlFor="prompt" className="text-sm font-medium">
          {t('prompt.label')}
        </label>
        <PromptEnhancer
          currentPrompt={value}
          onEnhance={(enhanced) => {
            onChange(enhanced);
            onEnhance?.(enhanced);
          }}
        />
      </div>
      <Textarea
        id="prompt"
        placeholder={t('prompt.placeholder')}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="min-h-[120px] resize-none"
      />
      <p className="text-xs text-muted-foreground">
        {t('prompt.hint')}
      </p>
    </div>
  );
};

