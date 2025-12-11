'use client';

import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { IMAGE_COUNT_OPTIONS, IMAGE_SIZE_PRESETS, INFERENCE_STEPS_RANGE } from '@/lib/constants';
import type { GenerateParams } from '@/types';

interface ParameterPanelProps {
  params: GenerateParams;
  imageCount: number;
  onParamsChange: (params: GenerateParams) => void;
  onImageCountChange: (count: number) => void;
}

/**
 * 参数设置面板
 */
export const ParameterPanel = ({
  params,
  imageCount,
  onParamsChange,
  onImageCountChange,
}: ParameterPanelProps) => {
  const handleSizePreset = (preset: typeof IMAGE_SIZE_PRESETS[number]) => {
    onParamsChange({
      ...params,
      width: preset.width,
      height: preset.height,
    });
  };

  return (
    <div className="space-y-4 p-6 bg-card border rounded-lg">
      <h3 className="text-lg font-semibold mb-4">生成参数</h3>

      {/* 图片数量 */}
      <div className="space-y-2">
        <Label htmlFor="image-count">图片数量</Label>
        <Select
          value={imageCount.toString()}
          onValueChange={(value) => onImageCountChange(parseInt(value))}
        >
          <SelectTrigger id="image-count">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {IMAGE_COUNT_OPTIONS.map((count) => (
              <SelectItem key={count} value={count.toString()}>
                {count} 张
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* 图片尺寸预设 */}
      <div className="space-y-2">
        <Label>图片尺寸</Label>
        <Select
          value={`${params.width}x${params.height}`}
          onValueChange={(value) => {
            const preset = IMAGE_SIZE_PRESETS.find(
              (p) => `${p.width}x${p.height}` === value
            );
            if (preset) {
              handleSizePreset(preset);
            }
          }}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {IMAGE_SIZE_PRESETS.map((preset) => (
              <SelectItem
                key={preset.label}
                value={`${preset.width}x${preset.height}`}
              >
                {preset.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* 自定义尺寸 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="width">宽度</Label>
          <Input
            id="width"
            type="number"
            min={64}
            max={2048}
            value={params.width || 1024}
            onChange={(e) =>
              onParamsChange({
                ...params,
                width: parseInt(e.target.value) || 1024,
              })
            }
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="height">高度</Label>
          <Input
            id="height"
            type="number"
            min={64}
            max={2048}
            value={params.height || 1024}
            onChange={(e) =>
              onParamsChange({
                ...params,
                height: parseInt(e.target.value) || 1024,
              })
            }
          />
        </div>
      </div>

      {/* 推理步数 */}
      <div className="space-y-2">
        <Label htmlFor="steps">推理步数</Label>
        <Input
          id="steps"
          type="number"
          min={INFERENCE_STEPS_RANGE.min}
          max={INFERENCE_STEPS_RANGE.max}
          value={params.num_inference_steps || INFERENCE_STEPS_RANGE.default}
          onChange={(e) =>
            onParamsChange({
              ...params,
              num_inference_steps:
                parseInt(e.target.value) || INFERENCE_STEPS_RANGE.default,
            })
          }
        />
        <p className="text-xs text-muted-foreground">
          范围: {INFERENCE_STEPS_RANGE.min}-{INFERENCE_STEPS_RANGE.max}，数值越大质量越好但速度越慢
        </p>
      </div>

      {/* 随机种子 */}
      <div className="space-y-2">
        <Label htmlFor="seed">随机种子（可选）</Label>
        <Input
          id="seed"
          type="number"
          min={0}
          placeholder="留空则随机生成"
          value={params.seed || ''}
          onChange={(e) =>
            onParamsChange({
              ...params,
              seed: e.target.value ? parseInt(e.target.value) : null,
            })
          }
        />
        <p className="text-xs text-muted-foreground">
          相同的种子和提示词会生成相同的图像
        </p>
      </div>
    </div>
  );
};

