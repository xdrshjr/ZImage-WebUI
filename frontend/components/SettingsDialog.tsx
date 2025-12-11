'use client';

import { useState } from 'react';
import { Settings } from 'lucide-react';
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
  const { baseUrl, setBaseUrl, testConnection, isTesting, testResult } =
    useApiConfig();
  const [url, setUrl] = useState(baseUrl);
  const [isOpen, setIsOpen] = useState(false);

  const handleTest = async () => {
    if (!isValidUrl(url)) {
      toast.error('请输入有效的URL地址');
      return;
    }

    const result = await testConnection(url);
    if (result) {
      toast.success('连接成功！');
    } else {
      toast.error('连接失败，请检查配置');
    }
  };

  const handleSave = async () => {
    if (!isValidUrl(url)) {
      toast.error('请输入有效的URL地址');
      return;
    }

    // 提取基础URL（去除路径）
    const baseUrlClean = extractBaseUrl(url);
    setBaseUrl(baseUrlClean);
    setIsOpen(false);
    toast.success('配置已保存');
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" className="h-9 w-9">
          <Settings className="h-5 w-5" />
          <span className="sr-only">设置</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>后台服务配置</DialogTitle>
          <DialogDescription>
            配置图像生成服务的IP地址和端口
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <label htmlFor="api-url" className="text-sm font-medium">
              服务地址
            </label>
            <Input
              id="api-url"
              placeholder="http://localhost:5000"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSave();
                }
              }}
            />
            <p className="text-xs text-muted-foreground">
              请输入完整的URL地址，例如: http://192.168.1.100:5000
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={handleTest}
              disabled={isTesting}
              className="flex-1"
            >
              {isTesting ? '测试中...' : '测试连接'}
            </Button>
            {testResult !== null && (
              <div
                className={`text-sm ${
                  testResult ? 'text-success' : 'text-destructive'
                }`}
              >
                {testResult ? '✓ 连接成功' : '✗ 连接失败'}
              </div>
            )}
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            取消
          </Button>
          <Button onClick={handleSave}>保存</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

