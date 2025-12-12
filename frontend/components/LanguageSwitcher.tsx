'use client';

import { useEffect, useState } from 'react';
import { Languages } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { LANGUAGE_OPTIONS } from '@/lib/i18n/config';
import { logger } from '@/lib/logger';

/**
 * 语言切换器组件
 * 优雅的语言选择界面，支持中英文切换
 */
export const LanguageSwitcher = () => {
  const { i18n, t } = useTranslation();
  const [currentLanguage, setCurrentLanguage] = useState(i18n.language);

  // 同步i18n的语言变化到组件状态
  useEffect(() => {
    const handleLanguageChanged = (lng: string) => {
      setCurrentLanguage(lng);
    };
    
    i18n.on('languageChanged', handleLanguageChanged);
    
    return () => {
      i18n.off('languageChanged', handleLanguageChanged);
    };
  }, [i18n]);

  const handleLanguageChange = (language: string) => {
    logger.info('Changing language', { from: currentLanguage, to: language });
    
    i18n.changeLanguage(language);
    setCurrentLanguage(language);
    
    // 保存到 localStorage
    localStorage.setItem('language', language);
    
    logger.info('Language changed successfully', { language });
  };

  const getCurrentLanguageOption = () => {
    return LANGUAGE_OPTIONS.find((opt) => opt.value === currentLanguage);
  };

  return (
    <div className="flex items-center gap-2">
      <Languages className="h-4 w-4 text-muted-foreground" />
      <Select value={currentLanguage} onValueChange={handleLanguageChange}>
        <SelectTrigger 
          className="w-[140px] h-9 border-none bg-transparent hover:bg-accent transition-colors"
          aria-label={t('language.switch')}
        >
          <SelectValue>
            <span className="flex items-center gap-2">
              <span>{getCurrentLanguageOption()?.flag}</span>
              <span className="font-medium">{getCurrentLanguageOption()?.label}</span>
            </span>
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {LANGUAGE_OPTIONS.map((option) => (
            <SelectItem 
              key={option.value} 
              value={option.value}
              className="cursor-pointer"
            >
              <span className="flex items-center gap-2">
                <span>{option.flag}</span>
                <span>{option.label}</span>
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

