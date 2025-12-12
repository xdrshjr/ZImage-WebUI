'use client';

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { isMobileDevice } from '@/lib/utils';
import { Monitor } from 'lucide-react';

/**
 * 移动端阻止组件
 */
export const MobileBlocker = ({ children }: { children: React.ReactNode }) => {
  const { t } = useTranslation();
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(isMobileDevice());
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    return () => {
      window.removeEventListener('resize', checkMobile);
    };
  }, []);

  if (isMobile) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 px-4">
        <div className="max-w-md w-full text-center space-y-6">
          <div className="flex justify-center">
            <div className="rounded-full bg-primary/10 p-6">
              <Monitor className="h-16 w-16 text-primary" />
            </div>
          </div>
          <div className="space-y-2">
            <h1 className="text-2xl font-semibold text-foreground">
              {t('mobile.title')}
            </h1>
            <p className="text-muted-foreground">
              {t('mobile.description')}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

