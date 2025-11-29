'use client';

import { useState, useEffect } from 'react';
import { AuthGuard } from '@/components/shared/AuthGuard';
import { MainLayout } from '@/components/layout/MainLayout';
import { TickerSelector } from '@/components/dashboard/TickerSelector';
import { CompanyHeader } from '@/components/dashboard/CompanyHeader';
import { TabNavigation } from '@/components/dashboard/TabNavigation';
import { CategoryFilter } from '@/components/dashboard/CategoryFilter';
import { Card } from '@/components/shared/Card';
import { TrendTab } from '@/components/dashboard/tabs/TrendTab';
import { SnapshotTab } from '@/components/dashboard/tabs/SnapshotTab';
import { ChatbotTab } from '@/components/dashboard/tabs/ChatbotTab';
import { EarningsTab } from '@/components/dashboard/tabs/EarningsTab';
import { PriceChartTab } from '@/components/dashboard/tabs/PriceChartTab';
import { DisclosuresTab } from '@/components/dashboard/tabs/DisclosuresTab';
import { MacroeconomicTab } from '@/components/dashboard/tabs/MacroeconomicTab';
import { FinQ360Tab } from '@/components/dashboard/tabs/FinQ360Tab';
import { PlaceholderTab } from '@/components/dashboard/tabs/PlaceholderTab';
import { DataUpdateButton } from '@/components/dashboard/DataUpdateButton';
import { useDataStatus } from '@/lib/hooks/useDataPipeline';

const DASHBOARD_TABS = [
  { id: 'trend', label: 'Metrics Trend Analysis', icon: '📈' },
  { id: 'snapshot', label: 'Snapshot & Changes', icon: '📷' },
  { id: 'earnings', label: 'Earning Summary', icon: '💰' },
  { id: 'price', label: 'Price Chart', icon: '📊' },
  { id: 'disclosures', label: 'Disclosures', icon: '📄' },
  { id: 'macro', label: 'Macroeconomic Data', icon: '🌐' },
  { id: 'finq360', label: 'FinQ 360', icon: '🔍' },
  { id: 'bot', label: 'FinQ Bot', icon: '🤖' },
];

export default function DashboardPage() {
  const [selectedTicker, setSelectedTicker] = useState<string>('AAPL');
  const [activeTab, setActiveTab] = useState<string>('trend');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const { data: dataStatus } = useDataStatus(selectedTicker);

  // Load ticker from URL or localStorage on mount
  useEffect(() => {
    const savedTicker = localStorage.getItem('selectedTicker');
    if (savedTicker) {
      setSelectedTicker(savedTicker);
    }
  }, []);

  // Save ticker to localStorage when it changes
  useEffect(() => {
    if (selectedTicker) {
      localStorage.setItem('selectedTicker', selectedTicker);
    }
  }, [selectedTicker]);

  const handleDataUpdate = () => {
    // Force refetch of fundamentals data
    window.location.reload();
  };

  return (
    <AuthGuard>
      <MainLayout>
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Filters */}
          <div className="lg:col-span-1">
            <Card title="Filters">
              <div className="space-y-6">
                <TickerSelector
                  selectedTicker={selectedTicker}
                  onTickerChange={setSelectedTicker}
                />
                {selectedTicker && (
                  <CategoryFilter
                    ticker={selectedTicker}
                    selectedCategory={selectedCategory}
                    onCategoryChange={setSelectedCategory}
                  />
                )}
              </div>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {selectedTicker ? (
              <>
                <div className="mb-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-sm font-semibold text-blue-900 mb-1">
                          📊 Data Pipeline Management
                        </h3>
                        <p className="text-xs text-blue-700 mb-3">
                          Update quarterly financial data from Yahoo Finance. Real-time data (prices, FRED, SEC filings) is always current.
                        </p>
                        {dataStatus?.latest_period && (
                          <p className="text-xs text-blue-600">
                            Current data: <span className="font-medium">{dataStatus.latest_period}</span>
                            {dataStatus.total_records && (
                              <> • {dataStatus.total_records.toLocaleString()} records</>
                            )}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="mt-3">
                      <DataUpdateButton
                        ticker={selectedTicker}
                        onUpdateComplete={handleDataUpdate}
                        showUpdateAll={true}
                      />
                    </div>
                  </div>
                </div>
                <CompanyHeader ticker={selectedTicker} />
                <TabNavigation
                  tabs={DASHBOARD_TABS}
                  activeTab={activeTab}
                  onTabChange={setActiveTab}
                />
                {(() => {
                  switch (activeTab) {
                    case 'trend':
                      return selectedCategory ? (
                        <TrendTab ticker={selectedTicker} category={selectedCategory} />
                      ) : (
                        <Card>
                          <p className="text-gray-600 text-center py-8">
                            Please select a category to view trend analysis.
                          </p>
                        </Card>
                      );
                    case 'snapshot':
                      return selectedCategory ? (
                        <SnapshotTab ticker={selectedTicker} category={selectedCategory} />
                      ) : (
                        <Card>
                          <p className="text-gray-600 text-center py-8">
                            Please select a category to view snapshot data.
                          </p>
                        </Card>
                      );
                    case 'bot':
                      return <ChatbotTab ticker={selectedTicker} />;
                    case 'earnings':
                      return <EarningsTab ticker={selectedTicker} />;
                    case 'price':
                      return <PriceChartTab ticker={selectedTicker} />;
                            case 'disclosures':
                              return <DisclosuresTab ticker={selectedTicker} />;
                    case 'macro':
                      return <MacroeconomicTab />;
                    case 'finq360':
                      return <FinQ360Tab ticker={selectedTicker} />;
                    default:
                      return (
                        <Card>
                          <p className="text-gray-600 text-center py-8">
                            Select a tab to view content.
                          </p>
                        </Card>
                      );
                  }
                })()}
              </>
            ) : (
              <Card>
                <p className="text-gray-600 text-center py-12">
                  Please select a ticker to view dashboard
                </p>
              </Card>
            )}
          </div>
        </div>
      </MainLayout>
    </AuthGuard>
  );
}

