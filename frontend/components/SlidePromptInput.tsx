/**
 * Slide内容输入组件
 */
'use client';

import { useTranslation } from 'react-i18next';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface SlidePromptInputProps {
  value: string;
  onChange: (value: string) => void;
}

export const SlidePromptInput = ({ value, onChange }: SlidePromptInputProps) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label className="text-base font-semibold">
          {t('slide.baseText')}
        </Label>
      </div>

      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={t('slide.baseTextPlaceholder')}
        className="min-h-[120px] resize-none"
      />

      <p className="text-xs text-muted-foreground">
        {t('slide.baseTextHint')}
      </p>
    </div>
  );
};



