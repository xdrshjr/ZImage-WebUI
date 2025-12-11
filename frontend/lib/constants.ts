/**
 * 应用常量定义
 */

// 从环境变量读取默认API地址，如果没有则使用默认值
// Next.js 中客户端可访问的环境变量需要以 NEXT_PUBLIC_ 开头
export const DEFAULT_API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

export const STORAGE_KEYS = {
  API_CONFIG: 'api_config',
  TASK_HISTORY: 'task_history',
} as const;

export const TASK_POLLING_INTERVAL = 2000; // 2秒

export const MAX_TASK_HISTORY = 50; // 最多保存50条历史记录

export const IMAGE_COUNT_OPTIONS = [1, 2, 3, 4] as const;

export const IMAGE_SIZE_PRESETS = [
  { label: '正方形 (1024×1024)', width: 1024, height: 1024 },
  { label: '横向 (1280×768)', width: 1280, height: 768 },
  { label: '纵向 (768×1280)', width: 768, height: 1280 },
  { label: '宽屏 (1920×1080)', width: 1920, height: 1080 },
] as const;

export const INFERENCE_STEPS_RANGE = {
  min: 1,
  max: 50,
  default: 9,
} as const;

export const IMAGE_SIZE_RANGE = {
  min: 64,
  max: 2048,
} as const;

/**
 * 提示词模板库
 */
export const PROMPT_TEMPLATES: Array<{
  id: string;
  name: string;
  category: string;
  prompt: string;
  description: string;
}> = [
  {
    id: 'landscape-1',
    name: '山水风景',
    category: '风景',
    prompt: 'A beautiful Chinese landscape painting with mountains, rivers, and mist, traditional ink painting style, highly detailed, 4k, masterpiece',
    description: '传统中国山水画风格',
  },
  {
    id: 'portrait-1',
    name: '人物肖像',
    category: '人物',
    prompt: 'Portrait of a person, professional photography, soft lighting, high quality, detailed, 8k, sharp focus',
    description: '专业人物肖像',
  },
  {
    id: 'fantasy-1',
    name: '奇幻场景',
    category: '奇幻',
    prompt: 'Fantasy landscape with magical elements, ethereal atmosphere, vibrant colors, highly detailed, digital art, concept art',
    description: '奇幻风格场景',
  },
  {
    id: 'anime-1',
    name: '动漫风格',
    category: '动漫',
    prompt: 'Anime style illustration, vibrant colors, detailed background, high quality, 4k, beautiful art',
    description: '日式动漫风格',
  },
  {
    id: 'cyberpunk-1',
    name: '赛博朋克',
    category: '科幻',
    prompt: 'Cyberpunk cityscape at night, neon lights, futuristic architecture, rain, highly detailed, 4k, cinematic lighting',
    description: '赛博朋克风格城市',
  },
  {
    id: 'nature-1',
    name: '自然风光',
    category: '自然',
    prompt: 'Beautiful nature scene, lush forest, sunlight filtering through trees, peaceful atmosphere, highly detailed, 4k, photorealistic',
    description: '自然风光摄影',
  },
];

/**
 * 提示词增强词库
 */
export const PROMPT_ENHANCEMENTS = {
  quality: [
    'high quality',
    'highly detailed',
    '4k',
    '8k',
    'masterpiece',
    'best quality',
    'ultra detailed',
  ],
  style: [
    'digital art',
    'concept art',
    'photorealistic',
    'cinematic',
    'professional photography',
    'illustration',
  ],
  lighting: [
    'soft lighting',
    'dramatic lighting',
    'cinematic lighting',
    'golden hour',
    'natural lighting',
  ],
  composition: [
    'sharp focus',
    'depth of field',
    'rule of thirds',
    'balanced composition',
  ],
} as const;

