'use client';

import { useState } from 'react';
import { AuthGuard } from '@/components/shared/AuthGuard';
import { MainLayout } from '@/components/layout/MainLayout';
import { FinqHealthScoresTab } from '@/components/health/FinqHealthScoresTab';
import { CustomHealthScoresTab } from '@/components/health/CustomHealthScoresTab';
import { Card } from '@/components/shared/Card';

export default function HealthPage() {
  const [activeTab, setActiveTab] = useState<'finq' | 'custom'>('finq');

  return (
    <AuthGuard>
      <MainLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Financial Health Monitoring
            </h1>
            <p className="text-gray-600">
              Analyze and compare financial health scores across companies
            </p>
          </div>

          <Card>
            <div className="border-b border-gray-200 mb-6">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab('finq')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'finq'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  📊 FinQ Suggestions
                </button>
                <button
                  onClick={() => setActiveTab('custom')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'custom'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  ⚙️ Custom Health Score
                </button>
              </nav>
            </div>

            {activeTab === 'finq' ? <FinqHealthScoresTab /> : <CustomHealthScoresTab />}
          </Card>
        </div>
      </MainLayout>
    </AuthGuard>
  );
}

