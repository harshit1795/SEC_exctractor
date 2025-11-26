'use client';

import { useAuth } from '@/lib/hooks/useAuth';
import Image from 'next/image';

export function Header() {
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-10 border-b border-gray-200 bg-white shadow-sm">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <Image
            src="/FInQLogo.png"
            alt="FinQ Logo"
            width={32}
            height={32}
            className="rounded"
          />
          <h1 className="text-xl font-bold text-gray-900">FinQ</h1>
        </div>

        <div className="flex items-center gap-4">
          {user && (
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {user.displayName || user.email?.split('@')[0] || 'User'}
                </p>
                <p className="text-xs text-gray-500">{user.email}</p>
              </div>
              {user.photoURL ? (
                <Image
                  src={user.photoURL}
                  alt="Profile"
                  width={40}
                  height={40}
                  className="rounded-full"
                />
              ) : (
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white">
                  <span className="text-sm font-semibold">
                    {(user.displayName || user.email || 'U')[0].toUpperCase()}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

