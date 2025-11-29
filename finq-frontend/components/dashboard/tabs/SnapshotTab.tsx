'use client';

import { useState, useMemo, useEffect, useRef } from 'react';
import { useFundamentals } from '@/lib/hooks/useTickerData';
import { useMetricPreferences } from '@/lib/hooks/useMetricPreferences';
import { humanFormat, formatPercent, getValueColor } from '@/lib/utils';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { MultiSelect } from '@/components/shared/MultiSelect';
import { MetricTooltip } from '@/components/shared/MetricTooltip';

interface SnapshotTabProps {
  ticker: string;
  category: string;
}

type DisplayMode = 'Latest' | 'QoQ Δ' | 'YoY Δ';

export function SnapshotTab({ ticker, category }: SnapshotTabProps) {
  const { data, isLoading, error } = useFundamentals(ticker);
  const { getMetricsForCategory, setMetricsForCategory, hasPreferencesForCategory, clearCategory } = useMetricPreferences();
  const [mode, setMode] = useState<DisplayMode>('Latest');
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'cleared'>('idle');
  const isInitializing = useRef(false);
  const lastCategory = useRef<string>('');

  const { allMetrics, periodData } = useMemo(() => {
    // Handle different response formats
    const dataArray = data?.data?.data || data?.data || [];
    
    if (!dataArray || !Array.isArray(dataArray)) {
      return { allMetrics: [], periodData: new Map() };
    }

    const filtered = dataArray.filter(
      (item: any) => {
        const itemCategory = item.Category || item.category || '';
        const itemTicker = item.Ticker || item.ticker || '';
        return itemCategory === category && itemTicker.toUpperCase() === ticker.toUpperCase();
      }
    );

    const metrics = Array.from(new Set(filtered.map((item: any) => item.Metric || item.metric))).sort() as string[];
    
    // Group by FiscalPeriod
    const periodMap = new Map<string, Record<string, number>>();
    
    filtered.forEach((item: any) => {
      const period = item.FiscalPeriod || item.fiscalPeriod || item.Date || item.date || '';
      const metric = item.Metric || item.metric || '';
      const value = item.Value !== undefined ? item.Value : (item.value !== undefined ? item.value : 0);
      
      if (!periodMap.has(period)) {
        periodMap.set(period, {});
      }
      periodMap.get(period)![metric] = value;
    });

    return { allMetrics: metrics, periodData: periodMap };
  }, [data, category, ticker]);

  // Load saved preferences when category changes
  useEffect(() => {
    // Only run if category actually changed
    if (lastCategory.current === category && allMetrics.length > 0) {
      return;
    }
    
    if (!category || allMetrics.length === 0) {
      setSelectedMetrics([]);
      lastCategory.current = category;
      return;
    }
    
    isInitializing.current = true;
    lastCategory.current = category;
    
    const savedMetrics = getMetricsForCategory(ticker, category);
    
    // Filter saved metrics to only include those available in current data
    const validSavedMetrics = savedMetrics.filter((m: string) => (allMetrics as string[]).includes(m));
    
    if (validSavedMetrics.length > 0) {
      // Restore saved selections
      setSelectedMetrics(validSavedMetrics);
    } else {
      // Auto-select first 10 if no saved preferences
      const defaultMetrics = allMetrics.slice(0, 10);
      setSelectedMetrics(defaultMetrics);
      // Save defaults, but mark as initializing to prevent loop
      setMetricsForCategory(ticker, category, defaultMetrics);
    }
    
    // Reset initialization flag after a brief delay
    setTimeout(() => {
      isInitializing.current = false;
    }, 100);
  }, [ticker, category, allMetrics, getMetricsForCategory, setMetricsForCategory]);

  // Auto-save preferences when selections change (but not during initialization)
  // Note: Manual save button is also available for explicit user control
  useEffect(() => {
    if (isInitializing.current) {
      return;
    }
    
    if (category && selectedMetrics.length > 0 && allMetrics.length > 0) {
      // Only auto-save if selections are valid for current category
      const validMetrics = selectedMetrics.filter((m: string) => (allMetrics as string[]).includes(m));
      if (validMetrics.length > 0 && category === lastCategory.current) {
        // Auto-save silently (user can also use manual save button)
        setMetricsForCategory(ticker, category, validMetrics);
      }
    }
  }, [ticker, selectedMetrics, category, allMetrics, setMetricsForCategory]);

  // Helper function to parse period for sorting
  const parsePeriod = (period: string): [number, number] => {
    try {
      // Handle formats like "2025 Q3", "2025Q3", "2025-03", etc.
      if (period.includes('Q') || period.includes('q')) {
        const parts = period.toUpperCase().split('Q');
        const year = parseInt(parts[0].trim()) || 0;
        const quarter = parseInt(parts[1]?.trim()) || 0;
        return [year, quarter];
      } else if (period.includes('-')) {
        // Handle "2025-03" format
        const parts = period.split('-');
        const year = parseInt(parts[0]) || 0;
        const month = parseInt(parts[1]) || 0;
        const quarter = Math.ceil(month / 3);
        return [year, quarter];
      } else {
        // Try to extract year from beginning
        const year = parseInt(period.substring(0, 4)) || 0;
        return [year, 0];
      }
    } catch {
      return [0, 0];
    }
  };

  const periods = useMemo(() => {
    const periodArray = Array.from(periodData.keys());
    // Sort by year and quarter (descending - latest first)
    return periodArray.sort((a, b) => {
      const [yearA, quarterA] = parsePeriod(a);
      const [yearB, quarterB] = parsePeriod(b);
      if (yearA !== yearB) {
        return yearB - yearA; // Descending by year
      }
      return quarterB - quarterA; // Descending by quarter
    });
  }, [periodData]);

  // Latest period is the first one after sorting (descending)
  const latestPeriod = periods[0] || '';
  const latestData = periodData.get(latestPeriod) || {};

  const snapshotData = useMemo(() => {
    if (!latestPeriod) return [];

    return selectedMetrics.map((metric) => {
      const latestValue = latestData[metric] || 0;
      let delta = null;
      let deltaPercent = null;

      if (mode === 'QoQ Δ' && periods.length >= 2) {
        // Previous period is the second one (since periods are sorted descending)
        const prevPeriod = periods[1];
        const prevData = periodData.get(prevPeriod) || {};
        const prevValue = prevData[metric] || 0;
        delta = latestValue - prevValue;
        deltaPercent = prevValue !== 0 ? (delta / Math.abs(prevValue)) * 100 : 0;
      } else if (mode === 'YoY Δ') {
        // Find period from same quarter last year
        const [latestYear, latestQuarter] = parsePeriod(latestPeriod);
        const targetYear = latestYear - 1;
        
        // Find the period that matches target year and quarter
        const yearAgoPeriod = periods.find(p => {
          const [y, q] = parsePeriod(p);
          return y === targetYear && q === latestQuarter;
        });
        
        if (yearAgoPeriod) {
          const yearAgoData = periodData.get(yearAgoPeriod) || {};
          const yearAgoValue = yearAgoData[metric] || 0;
          delta = latestValue - yearAgoValue;
          deltaPercent = yearAgoValue !== 0 ? (delta / Math.abs(yearAgoValue)) * 100 : 0;
        }
      }

      return {
        metric,
        value: latestValue,
        delta,
        deltaPercent,
      };
    });
  }, [selectedMetrics, latestPeriod, latestData, mode, periods, periodData]);

  if (isLoading) {
    return <Loading message="Loading snapshot data..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load snapshot data" />;
  }

  if (allMetrics.length === 0) {
    return (
      <Card>
        <p className="text-gray-600 text-center py-8">
          No metrics available for this category.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Display Mode (Period: {latestPeriod})
            </label>
            <div className="flex gap-4">
              {(['Latest', 'QoQ Δ', 'YoY Δ'] as DisplayMode[]).map((m) => (
                <label key={m} className="flex items-center">
                  <input
                    type="radio"
                    value={m}
                    checked={mode === m}
                    onChange={(e) => setMode(e.target.value as DisplayMode)}
                    className="mr-2"
                  />
                  {m}
                </label>
              ))}
            </div>
          </div>

          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <MultiSelect
                label="Metrics to show"
                options={allMetrics}
                selected={selectedMetrics}
                onChange={setSelectedMetrics}
                placeholder="Search and select metrics..."
              />
            </div>
            <div className="flex flex-col gap-2 pt-7">
              <button
                onClick={() => {
                  if (selectedMetrics.length > 0) {
                    setSaveStatus('saving');
                    setMetricsForCategory(ticker, category, selectedMetrics);
                    setTimeout(() => {
                      setSaveStatus('saved');
                      setTimeout(() => setSaveStatus('idle'), 2000);
                    }, 100);
                  }
                }}
                disabled={selectedMetrics.length === 0 || saveStatus === 'saving'}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {saveStatus === 'saving' ? (
                  <>💾 Saving...</>
                ) : saveStatus === 'saved' ? (
                  <>✅ Saved</>
                ) : hasPreferencesForCategory(ticker, category) ? (
                  <>💾 Update Preference</>
                ) : (
                  <>💾 Save Preference</>
                )}
              </button>
              {hasPreferencesForCategory(ticker, category) && (
                <button
                  onClick={() => {
                    clearCategory(ticker, category);
                    setSelectedMetrics([]);
                    setSaveStatus('cleared');
                    setTimeout(() => setSaveStatus('idle'), 2000);
                  }}
                  className="rounded-md border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
                >
                  🗑️ Clear Saved
                </button>
              )}
            </div>
          </div>
          {hasPreferencesForCategory(ticker, category) && saveStatus === 'idle' && (
            <div className="rounded-md bg-green-50 border border-green-200 px-3 py-2 text-sm text-green-800">
              ✓ Preferences saved for this category
            </div>
          )}
        </div>
      </Card>

      {selectedMetrics.length > 0 && (
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Metric
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {mode === 'Latest' ? 'Value' : `Latest Value (${latestPeriod})`}
                  </th>
                  {mode !== 'Latest' && (
                    <>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Change
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Change %
                      </th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {snapshotData.map((row) => (
                  <tr key={row.metric}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      <div className="flex items-center">
                        {row.metric}
                        <MetricTooltip metricName={row.metric} />
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                      {humanFormat(row.value)}
                    </td>
                    {mode !== 'Latest' && (
                      <>
                        <td
                          className={`px-6 py-4 whitespace-nowrap text-sm text-right ${getValueColor(row.delta)}`}
                        >
                          {row.delta !== null ? humanFormat(row.delta) : 'N/A'}
                        </td>
                        <td
                          className={`px-6 py-4 whitespace-nowrap text-sm text-right ${getValueColor(row.deltaPercent)}`}
                        >
                          {row.deltaPercent !== null
                            ? formatPercent(row.deltaPercent)
                            : 'N/A'}
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}

