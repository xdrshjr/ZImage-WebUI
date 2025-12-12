'use client';

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { logger } from '@/lib/logger';

// Import translations
import en from '@/locales/en.json';
import zh from '@/locales/zh.json';

/**
 * 语言配置常量
 */
export const LANGUAGES = {
  EN: 'en',
  ZH: 'zh',
} as const;

export const LANGUAGE_OPTIONS = [
  { value: LANGUAGES.ZH, label: '中文', flag: '🇨🇳' },
  { value: LANGUAGES.EN, label: 'English', flag: '🇺🇸' },
] as const;

export const DEFAULT_LANGUAGE = LANGUAGES.ZH;

/**
 * 获取初始语言
 * 优先使用localStorage保存的语言，确保客户端和服务端使用相同的语言
 */
const getInitialLanguage = (): string => {
  // 服务端始终使用默认语言
  if (typeof window === 'undefined') {
    return DEFAULT_LANGUAGE;
  }
  
  // 客户端读取localStorage
  try {
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage && (savedLanguage === LANGUAGES.EN || savedLanguage === LANGUAGES.ZH)) {
      return savedLanguage;
    }
  } catch (error) {
    // localStorage访问失败时使用默认语言
  }
  
  return DEFAULT_LANGUAGE;
};

/**
 * 初始化 i18n
 * 支持服务端和客户端渲染，确保hydration一致性
 */
if (!i18n.isInitialized) {
  const initialLanguage = getInitialLanguage();
  
  i18n
    .use(initReactI18next)
    .init({
      resources: {
        en: { translation: en },
        zh: { translation: zh },
      },
      lng: initialLanguage,
      fallbackLng: DEFAULT_LANGUAGE,
      interpolation: {
        escapeValue: false,
      },
      react: {
        useSuspense: false,
      },
    })
    .then(() => {
      if (typeof window !== 'undefined') {
        logger.info('i18n initialized successfully', { language: i18n.language });
      }
    })
    .catch((error) => {
      if (typeof window !== 'undefined') {
        logger.error('Failed to initialize i18n', { error: error.message });
      }
    });
}

export default i18n;

