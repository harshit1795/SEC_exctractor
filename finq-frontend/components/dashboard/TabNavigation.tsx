'use client';

import { useMemo } from 'react';
import { TabTooltip } from '@/components/shared/TabTooltip';

interface Tab {
  id: string;
  label: string;
  icon: string;
}

interface TabNavigationProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export function TabNavigation({
  tabs,
  activeTab,
  onTabChange,
}: TabNavigationProps) {
  // Split tabs into two rows (approximately half in each row)
  const { firstRow, secondRow } = useMemo(() => {
    const midPoint = Math.ceil(tabs.length / 2);
    return {
      firstRow: tabs.slice(0, midPoint),
      secondRow: tabs.slice(midPoint),
    };
  }, [tabs]);

  const renderTab = (tab: Tab) => {
    const isActive = activeTab === tab.id;
    const isFinQBot = tab.id === 'bot';
    
    return (
      <div key={tab.id} className="flex items-center flex-shrink-0">
        <button
          onClick={() => onTabChange(tab.id)}
          className={`
            flex items-center gap-2 whitespace-nowrap border-b-2 px-4 py-4 text-base font-bold transition-all duration-200
            ${
              isActive
                ? 'border-green-500 text-green-700 bg-green-50'
                : 'border-transparent text-gray-600 hover:border-gray-300 hover:text-gray-800 hover:bg-gray-50'
            }
            ${isFinQBot ? 'animate-pulse hover:animate-none' : ''}
          `}
        >
          <span className={`text-xl ${isFinQBot && !isActive ? 'animate-bounce' : ''}`}>{tab.icon}</span>
          <span>{tab.label}</span>
        </button>
        <TabTooltip tabId={tab.id} tabLabel={tab.label} />
      </div>
    );
  };

  return (
    <div className="border-b border-gray-200 mb-6">
      {/* Guidance Message */}
      <div className="mb-3 px-2">
        <p className="text-sm text-gray-600 flex items-center gap-2">
          <span className="text-blue-600">💡</span>
          <span>Select a tab or hover over the <span className="inline-flex items-center text-gray-400"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-3.5 h-3.5 mx-1"><path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" /></svg></span> icon to learn more about each tab's capabilities</span>
        </p>
      </div>
      
      <nav className="-mb-px flex flex-col" aria-label="Tabs">
        {/* First Row */}
        <div className="flex space-x-4 overflow-x-auto pb-1">
          {firstRow.map(renderTab)}
        </div>
        {/* Second Row */}
        {secondRow.length > 0 && (
          <div className="flex space-x-4 overflow-x-auto pt-1">
            {secondRow.map(renderTab)}
          </div>
        )}
      </nav>
    </div>
  );
}

