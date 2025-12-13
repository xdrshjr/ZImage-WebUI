'use client';

import { useState, useMemo } from 'react';
import { Wand2, Presentation, Image as ImageIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import '@/lib/i18n/config'; // 初始化 i18n
import { ClientOnly } from '@/components/ClientOnly';
import { MobileBlocker } from '@/components/MobileBlocker';
import { SettingsDialog } from '@/components/SettingsDialog';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';
import { PromptInput } from '@/components/PromptInput';
import { ParameterPanel } from '@/components/ParameterPanel';
import { TaskList } from '@/components/TaskList';
import { SlidePromptInput } from '@/components/SlidePromptInput';
import { SlideParameterPanel } from '@/components/SlideParameterPanel';
import { SlideTaskList } from '@/components/SlideTaskList';
import { Button } from '@/components/ui/button';
import { useImageGeneration } from '@/hooks/useImageGeneration';
import { useTaskPolling } from '@/hooks/useTaskPolling';
import { useSlideGeneration } from '@/hooks/useSlideGeneration';
import { useSlideTaskPolling } from '@/hooks/useSlideTaskPolling';
import type { GenerateParams, TaskListItem, SlideGenerateParams, SlideTaskListItem } from '@/types';
import { TaskStatus, TaskType, SlideTaskStatus } from '@/types';
import { INFERENCE_STEPS_RANGE } from '@/lib/constants';

function HomeContent() {
  const { t } = useTranslation();
  
  // 任务类型切换
  const [taskType, setTaskType] = useState<TaskType>(TaskType.IMAGE_GENERATION);
  
  // 图像生成相关状态
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
  
  // Slide生成相关状态
  const [slideBaseText, setSlideBaseText] = useState('');
  const [slideParams, setSlideParams] = useState<SlideGenerateParams>({
    base_text: '',
    num_slides: 6,
    aspect_ratio: '16:9',
    style: 'professional',
    content_richness: 'moderate',
    color_scheme: 'light_blue',
  });
  
  const { 
    generate: generateSlide, 
    isGenerating: isGeneratingSlide, 
    taskIds: slideTaskIds, 
    clearTasks: clearSlideTasks 
  } = useSlideGeneration();
  const { tasks: slideTasks } = useSlideTaskPolling(slideTaskIds);

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
  
  // Slide生成处理函数
  const handleSlideGenerate = async () => {
    if (!slideBaseText.trim()) {
      return;
    }
    
    const generateParams: SlideGenerateParams = {
      ...slideParams,
      base_text: slideBaseText.trim(),
    };
    
    try {
      await generateSlide(generateParams);
    } catch (error) {
      // 错误已在hook中处理
    }
  };
  
  const handleSlideBaseTextChange = (value: string) => {
    setSlideBaseText(value);
    setSlideParams((prev) => ({ ...prev, base_text: value }));
  };
  
  // 将Slide任务数据转换为列表项格式
  const slideTaskListItems: SlideTaskListItem[] = useMemo(() => {
    return Object.entries(slideTasks).map(([taskId, task]) => {
      return {
        taskId: task.task_id,
        baseText: task.base_text,
        status: task.status,
        queuePosition: task.queue_position,
        createdAt: task.created_at,
        slidesGenerated: task.slides_generated,
        pdfAvailable: !!task.pdf_path,
        pptxAvailable: !!task.ppt_path,
        slideImageCount: task.slide_image_paths?.length || 0,
        errorMessage: task.error_message,
        params: {
          numSlides: task.num_slides,
          aspectRatio: task.aspect_ratio,
          style: task.style,
          contentRichness: task.content_richness,
          colorScheme: task.color_scheme,
        },
      };
    });
  }, [slideTasks]);

  return (
    <MobileBlocker>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        {/* 头部 */}
        <header className="border-b bg-card/80 backdrop-blur-sm sticky top-0 z-40">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-primary/10 p-2">
                  {taskType === TaskType.IMAGE_GENERATION ? (
                    <ImageIcon className="h-6 w-6 text-primary" />
                  ) : (
                    <Presentation className="h-6 w-6 text-primary" />
                  )}
                </div>
                <div>
                  <h1 className="text-xl font-semibold" suppressHydrationWarning>
                    {t('header.title')}
                  </h1>
                  <p className="text-xs text-muted-foreground" suppressHydrationWarning>
                    {t('header.subtitle')}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {/* 任务类型切换 */}
                <div className="flex items-center gap-1 bg-muted/50 rounded-lg p-1">
                  <Button
                    variant={taskType === TaskType.IMAGE_GENERATION ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setTaskType(TaskType.IMAGE_GENERATION)}
                    className="gap-2"
                  >
                    <ImageIcon className="h-4 w-4" />
                    {t('taskType.image')}
                  </Button>
                  <Button
                    variant={taskType === TaskType.SLIDE_GENERATION ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setTaskType(TaskType.SLIDE_GENERATION)}
                    className="gap-2"
                  >
                    <Presentation className="h-4 w-4" />
                    {t('taskType.slide')}
                  </Button>
                </div>
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
              {taskType === TaskType.IMAGE_GENERATION ? (
                <>
                  {/* 图像生成：提示词输入 */}
                  <div className="bg-card border rounded-lg p-6">
                    <PromptInput
                      value={prompt}
                      onChange={handlePromptChange}
                    />
                  </div>

                  {/* 图像生成：参数设置 */}
                  <ParameterPanel
                    params={params}
                    imageCount={imageCount}
                    onParamsChange={setParams}
                    onImageCountChange={setImageCount}
                  />

                  {/* 图像生成按钮 */}
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
                </>
              ) : (
                <>
                  {/* Slide生成：内容输入 */}
                  <div className="bg-card border rounded-lg p-6">
                    <SlidePromptInput
                      value={slideBaseText}
                      onChange={handleSlideBaseTextChange}
                    />
                  </div>

                  {/* Slide生成：参数设置 */}
                  <SlideParameterPanel
                    params={slideParams}
                    onParamsChange={setSlideParams}
                  />

                  {/* Slide生成按钮 */}
                  <Button
                    onClick={handleSlideGenerate}
                    disabled={isGeneratingSlide || !slideBaseText.trim()}
                    size="lg"
                    className="w-full h-12 text-base font-semibold"
                  >
                    {isGeneratingSlide ? (
                      <>
                        <span className="animate-spin mr-2">⏳</span>
                        {t('slideToast.generating')}
                      </>
                    ) : (
                      <>
                        <Presentation className="h-5 w-5 mr-2" />
                        {t('button.generate')}
                      </>
                    )}
                  </Button>
                </>
              )}
            </div>

            {/* 右侧：任务列表 (70%) */}
            <div className="lg:col-span-7 p-6 min-h-[calc(100vh-80px)]">
              <div className="bg-card border rounded-lg p-6 sticky top-24 max-h-[calc(100vh-8rem)] overflow-y-auto">
                {taskType === TaskType.IMAGE_GENERATION ? (
                  <>
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
                  </>
                ) : (
                  <>
                    <SlideTaskList tasks={slideTaskListItems} />
                    {slideTaskListItems.length > 0 && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={clearSlideTasks}
                        className="w-full mt-4"
                      >
                        {t('button.clearTasks')}
                      </Button>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </MobileBlocker>
  );
}

export default function Home() {
  return (
    <ClientOnly>
      <HomeContent />
    </ClientOnly>
  );
}

