import { useState, useEffect, useCallback } from 'react';
import { ApiConfig } from '@/lib/api';
import { DEFAULT_API_BASE_URL } from '@/lib/constants';

/**
 * API配置Hook
 */
export const useApiConfig = () => {
  const [baseUrl, setBaseUrlState] = useState<string>(DEFAULT_API_BASE_URL);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<boolean | null>(null);

  // 初始化时从localStorage读取
  useEffect(() => {
    const stored = ApiConfig.getBaseUrl();
    setBaseUrlState(stored);
  }, []);

  // 设置URL
  const setBaseUrl = useCallback((url: string) => {
    ApiConfig.setBaseUrl(url);
    setBaseUrlState(url);
    setTestResult(null);
  }, []);

  // 测试连接
  const testConnection = useCallback(async (url?: string) => {
    setIsTesting(true);
    setTestResult(null);
    
    try {
      const result = await ApiConfig.testConnection(url || baseUrl);
      setTestResult(result);
      return result;
    } catch (error) {
      setTestResult(false);
      return false;
    } finally {
      setIsTesting(false);
    }
  }, [baseUrl]);

  return {
    baseUrl,
    setBaseUrl,
    testConnection,
    isTesting,
    testResult,
  };
};


