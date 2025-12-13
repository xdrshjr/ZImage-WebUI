'use client';

import { useEffect, useState } from 'react';

/**
 * ClientOnly组件 - 仅在客户端渲染子组件
 * 用于避免服务端渲染导致的hydration错误
 * 
 * @param children - 需要仅在客户端渲染的内容
 */
export const ClientOnly = ({ children }: { children: React.ReactNode }) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return null;
  }

  return <>{children}</>;
};


