'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/hooks/useAuth';
import Image from 'next/image';

const PAGES = [
  { name: 'Dashboard', path: '/dashboard', icon: '📊' },
  { name: 'Financial Health Monitoring', path: '/health', icon: '❤️' },
  { name: 'Nexus', path: '/nexus', icon: '🌐' },
  { name: 'Settings', path: '/settings', icon: '⚙️' },
];

export function Sidebar() {
  const pathname = usePathname();
  const { logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    window.location.href = '/';
  };

  return (
    <div className="flex h-screen w-64 flex-col bg-gray-900 text-white">
      <div className="flex items-center gap-3 p-6">
        <Image
          src="/FInQLogo.png"
          alt="FinQ Logo"
          width={40}
          height={40}
          className="rounded"
        />
        <h1 className="text-xl font-bold">FinQ Modules</h1>
      </div>

      <nav className="flex-1 space-y-2 px-4">
        {PAGES.map((page) => {
          const isActive = pathname?.startsWith(page.path);
          return (
            <Link
              key={page.path}
              href={page.path}
              className={`flex items-center gap-3 rounded-lg px-4 py-3 transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <span className="text-xl">{page.icon}</span>
              <span>{page.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-gray-700 p-4">
        <button
          onClick={handleLogout}
          className="w-full rounded-lg bg-red-600 px-4 py-2 text-white transition-colors hover:bg-red-700"
        >
          Log Out
        </button>
      </div>
    </div>
  );
}

