/**
 * Slide参数面板组件
 */
'use client';

import { useTranslation } from 'react-i18next';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { SlideGenerateParams } from '@/types';

interface SlideParameterPanelProps {
  params: SlideGenerateParams;
  onParamsChange: (params: SlideGenerateParams) => void;
}

export const SlideParameterPanel = ({
  params,
  onParamsChange,
}: SlideParameterPanelProps) => {
  const { t } = useTranslation();

  const handleNumSlidesChange = (value: string) => {
    const numSlides = parseInt(value, 10);
    if (!isNaN(numSlides) && numSlides >= 1 && numSlides <= 50) {
      onParamsChange({ ...params, num_slides: numSlides });
    }
  };

  const handleAspectRatioChange = (value: '16:9' | '4:3' | '16:10') => {
    onParamsChange({ ...params, aspect_ratio: value });
  };

  const handleStyleChange = (
    value: 'professional' | 'creative' | 'minimal' | 'academic'
  ) => {
    onParamsChange({ ...params, style: value });
  };

  const handleContentRichnessChange = (
    value: 'concise' | 'moderate' | 'detailed'
  ) => {
    onParamsChange({ ...params, content_richness: value });
  };

  return (
    <div className="bg-card border rounded-lg p-6 space-y-6">
      <div>
        <h3 className="text-base font-semibold mb-4">
          {t('slide.parameters')}
        </h3>
      </div>

      {/* 幻灯片数量 */}
      <div className="space-y-2">
        <Label>{t('slide.numSlides')}</Label>
        <div className="flex items-center gap-3">
          <Input
            type="number"
            min={1}
            max={50}
            value={params.num_slides || 6}
            onChange={(e) => handleNumSlidesChange(e.target.value)}
            className="flex-1"
          />
          <span className="text-sm text-muted-foreground whitespace-nowrap">
            {t('slide.numSlidesUnit')}
          </span>
        </div>
        <p className="text-xs text-muted-foreground">
          Range: 1-50
        </p>
      </div>

      {/* 幻灯片比例 */}
      <div className="space-y-2">
        <Label>{t('slide.aspectRatio')}</Label>
        <Select
          value={params.aspect_ratio || '16:9'}
          onValueChange={handleAspectRatioChange}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="16:9">
              {t('slideAspectRatio.16:9')}
            </SelectItem>
            <SelectItem value="4:3">
              {t('slideAspectRatio.4:3')}
            </SelectItem>
            <SelectItem value="16:10">
              {t('slideAspectRatio.16:10')}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* 视觉风格 */}
      <div className="space-y-2">
        <Label>{t('slide.style')}</Label>
        <Select
          value={params.style || 'professional'}
          onValueChange={handleStyleChange}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="professional">
              {t('slideStyle.professional')}
            </SelectItem>
            <SelectItem value="creative">
              {t('slideStyle.creative')}
            </SelectItem>
            <SelectItem value="minimal">
              {t('slideStyle.minimal')}
            </SelectItem>
            <SelectItem value="academic">
              {t('slideStyle.academic')}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* 内容详细度 */}
      <div className="space-y-2">
        <Label>{t('slide.contentRichness')}</Label>
        <Select
          value={params.content_richness || 'moderate'}
          onValueChange={handleContentRichnessChange}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="concise">
              {t('slideContentRichness.concise')}
            </SelectItem>
            <SelectItem value="moderate">
              {t('slideContentRichness.moderate')}
            </SelectItem>
            <SelectItem value="detailed">
              {t('slideContentRichness.detailed')}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};



