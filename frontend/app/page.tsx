'use client';

import { useState, useMemo } from 'react';
import { Wand2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n/config'; // 初始化 i18n
import { MobileBlocker } from '@/components/MobileBlocker';
import { SettingsDialog } from '@/components/SettingsDialog';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';
import { PromptInput } from '@/components/PromptInput';
import { ParameterPanel } from '@/components/ParameterPanel';
import { TaskList } from '@/components/TaskList';
import { Button } from '@/components/ui/button';
import { useImageGeneration } from '@/hooks/useImageGeneration';
import { useTaskPolling } from '@/hooks/useTaskPolling';
import type { GenerateParams, TaskListItem } from '@/types';
import { TaskStatus } from '@/types';
import { INFERENCE_STEPS_RANGE } from '@/lib/constants';

export default function Home() {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState('');
  const [imageCount, setImageCount] = useState(1);
  const [params, setParams] = useState<GenerateParams>({
    prompt: '',
    width: 1024,
    height: 1024,
    num_inference_steps: INFERENCE_STEPS_RANGE.default,
    seed: null,
  });

  const { generate, isGenerating, taskIds, clearTasks } = useImageGeneration();
  const { tasks } = useTaskPolling(taskIds);

  // 将任务数据转换为列表项格式
  const taskListItems: TaskListItem[] = useMemo(() => {
    return Object.entries(tasks).map(([taskId, task]) => {
      // 如果任务已完成，尝试获取图片URL
      let imageUrl: string | undefined;
      if (task.status === TaskStatus.COMPLETED && task.image_path) {
        // 这里会在TaskItem组件中动态加载
        imageUrl = undefined;
      }

      return {
        taskId: task.task_id,
        prompt: task.prompt,
        status: task.status,
        queuePosition: task.queue_position,
        createdAt: task.created_at,
        imageUrl,
        errorMessage: task.error_message,
        params: {
          height: task.height,
          width: task.width,
          numInferenceSteps: task.num_inference_steps,
          seed: task.seed,
        },
      };
    });
  }, [tasks]);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      return;
    }

    const generateParams: GenerateParams = {
      ...params,
      prompt: prompt.trim(),
    };

    try {
      await generate(generateParams, imageCount);
    } catch (error) {
      // 错误已在hook中处理
    }
  };

  const handlePromptChange = (value: string) => {
    setPrompt(value);
    setParams((prev) => ({ ...prev, prompt: value }));
  };

  return (
    <MobileBlocker>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        {/* 头部 */}
        <header className="border-b bg-card/80 backdrop-blur-sm sticky top-0 z-40">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-primary/10 p-2">
                  <Wand2 className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h1 className="text-xl font-semibold">{t('header.title')}</h1>
                  <p className="text-xs text-muted-foreground">
                    {t('header.subtitle')}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <LanguageSwitcher />
                <SettingsDialog />
              </div>
            </div>
          </div>
        </header>

        {/* 主内容 */}
        <main className="w-full">
          <div className="grid grid-cols-1 lg:grid-cols-10 gap-0">
            {/* 左侧：输入区域 (30%) */}
            <div className="lg:col-span-3 p-6 space-y-6 border-r border-border min-h-[calc(100vh-80px)]">
              {/* 提示词输入 */}
              <div className="bg-card border rounded-lg p-6">
                <PromptInput
                  value={prompt}
                  onChange={handlePromptChange}
                />
              </div>

              {/* 参数设置 */}
              <ParameterPanel
                params={params}
                imageCount={imageCount}
                onParamsChange={setParams}
                onImageCountChange={setImageCount}
              />

              {/* 生成按钮 */}
              <Button
                onClick={handleGenerate}
                disabled={isGenerating || !prompt.trim()}
                size="lg"
                className="w-full h-12 text-base font-semibold"
              >
                {isGenerating ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    {t('button.generating')}
                  </>
                ) : (
                  <>
                    <Wand2 className="h-5 w-5 mr-2" />
                    {t('button.generate')}
                  </>
                )}
              </Button>
            </div>

            {/* 右侧：任务列表 (70%) */}
            <div className="lg:col-span-7 p-6 min-h-[calc(100vh-80px)]">
              <div className="bg-card border rounded-lg p-6 sticky top-24 max-h-[calc(100vh-8rem)] overflow-y-auto">
                <TaskList tasks={taskListItems} />
                {taskListItems.length > 0 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={clearTasks}
                    className="w-full mt-4"
                  >
                    {t('button.clearTasks')}
                  </Button>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </MobileBlocker>
  );
}

