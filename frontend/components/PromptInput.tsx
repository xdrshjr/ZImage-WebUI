'use client';

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
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label htmlFor="prompt" className="text-sm font-medium">
          提示词
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
        placeholder="输入您想要生成的图像描述，例如：A beautiful sunset over the ocean..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="min-h-[120px] resize-none"
      />
      <p className="text-xs text-muted-foreground">
        描述越详细，生成的图像质量越好
      </p>
    </div>
  );
};

