'use client';

import { useState } from 'react';
import { AuthGuard } from '@/components/shared/AuthGuard';
import { MainLayout } from '@/components/layout/MainLayout';
import { FeedTab } from '@/components/nexus/FeedTab';
import { ProfileTab } from '@/components/nexus/ProfileTab';
import { DirectoryTab } from '@/components/nexus/DirectoryTab';
import { FriendsTab } from '@/components/nexus/FriendsTab';

export default function NexusPage() {
  const [activeTab, setActiveTab] = useState<'feed' | 'profile' | 'directory' | 'friends'>('feed');

  const tabs = [
    { id: 'feed', label: 'Feed', icon: '📰' },
    { id: 'profile', label: 'My Profile', icon: '👤' },
    { id: 'directory', label: 'User Directory', icon: '👥' },
    { id: 'friends', label: 'Friends', icon: '🤝' },
  ];

  return (
    <AuthGuard>
      <MainLayout>
        <h1 className="mb-6 text-3xl font-bold text-gray-900">Nexus Community</h1>
        
        {/* Tab Navigation */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-4 text-base font-bold border-b-2 transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'border-green-500 text-green-700 bg-green-50'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'feed' && <FeedTab />}
          {activeTab === 'profile' && <ProfileTab />}
          {activeTab === 'directory' && <DirectoryTab />}
          {activeTab === 'friends' && <FriendsTab />}
        </div>
      </MainLayout>
    </AuthGuard>
  );
}

