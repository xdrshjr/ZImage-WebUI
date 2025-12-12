'use client';

import { useState, useEffect } from 'react';
import { Settings } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { useApiConfig } from '@/hooks/useApiConfig';
import { isValidUrl, extractBaseUrl } from '@/lib/utils';
import toast from 'react-hot-toast';

/**
 * 设置对话框组件
 */
export const SettingsDialog = () => {
  const { t } = useTranslation();
  const { baseUrl, setBaseUrl, testConnection, isTesting, testResult } =
    useApiConfig();
  const [url, setUrl] = useState(baseUrl);
  const [isOpen, setIsOpen] = useState(false);

  // 当对话框打开时，同步最新的 baseUrl 到 url 状态
  useEffect(() => {
    if (isOpen) {
      setUrl(baseUrl);
    }
  }, [isOpen, baseUrl]);

  const handleTest = async () => {
    if (!isValidUrl(url)) {
      toast.error(t('settings.invalidUrl'));
      return;
    }

    const result = await testConnection(url);
    if (result) {
      toast.success(t('toast.connectionSuccess'));
    } else {
      toast.error(t('toast.connectionFailed'));
    }
  };

  const handleSave = async () => {
    if (!isValidUrl(url)) {
      toast.error(t('settings.invalidUrl'));
      return;
    }

    // 提取基础URL（去除路径）
    const baseUrlClean = extractBaseUrl(url);
    setBaseUrl(baseUrlClean);
    setIsOpen(false);
    toast.success(t('settings.savedSuccess'));
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" className="h-9 w-9">
          <Settings className="h-5 w-5" />
          <span className="sr-only">{t('settings.title')}</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{t('settings.title')}</DialogTitle>
          <DialogDescription>
            {t('settings.description')}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <label htmlFor="api-url" className="text-sm font-medium">
              {t('settings.serviceUrl')}
            </label>
            <Input
              id="api-url"
              placeholder={t('settings.urlPlaceholder')}
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSave();
                }
              }}
            />
            <p className="text-xs text-muted-foreground">
              {t('settings.urlHint')}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={handleTest}
              disabled={isTesting}
              className="flex-1"
            >
              {isTesting ? t('button.testing') : t('button.test')}
            </Button>
            {testResult !== null && (
              <div
                className={`text-sm ${
                  testResult ? 'text-success' : 'text-destructive'
                }`}
              >
                {testResult ? t('settings.connectionSuccess') : t('settings.connectionFailed')}
              </div>
            )}
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            {t('button.cancel')}
          </Button>
          <Button onClick={handleSave}>{t('button.save')}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

