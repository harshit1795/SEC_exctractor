'use client';

import { useState, useMemo, useEffect, useRef } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart } from 'recharts';
import { useFundamentals } from '@/lib/hooks/useTickerData';
import { useMetricPreferences } from '@/lib/hooks/useMetricPreferences';
import { humanFormat, humanFormatForAxis, getMetricUnit } from '@/lib/utils';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { MultiSelect } from '@/components/shared/MultiSelect';
import { MetricTooltip } from '@/components/shared/MetricTooltip';

interface TrendTabProps {
  ticker: string;
  category: string;
}

export function TrendTab({ ticker, category }: TrendTabProps) {
  const { data, isLoading, error } = useFundamentals(ticker);
  const { getMetricsForCategory, setMetricsForCategory, hasPreferencesForCategory, clearCategory } = useMetricPreferences();
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [chartType, setChartType] = useState<'Line' | 'Bar'>('Line');
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'cleared'>('idle');
  const isInitializing = useRef(false);
  const lastCategory = useRef<string>('');

  const { allMetrics, chartData } = useMemo(() => {
    // Handle different response formats
    const dataArray = data?.data?.data || data?.data || [];
    
    if (!dataArray || !Array.isArray(dataArray)) {
      return { allMetrics: [], chartData: [] };
    }

    const filtered = dataArray.filter(
      (item: any) => {
        const itemCategory = item.Category || item.category || '';
        const itemTicker = item.Ticker || item.ticker || '';
        return itemCategory === category && itemTicker.toUpperCase() === ticker.toUpperCase();
      }
    );

    const metrics = Array.from(new Set(filtered.map((item: any) => item.Metric || item.metric))).sort() as string[];
    
    // Group by FiscalPeriod and Metric
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

    const chartData = Array.from(periodMap.entries())
      .map(([period, values]) => ({
        period,
        ...values,
      }))
      .sort((a, b) => {
        const [yearA, quarterA] = parsePeriod(a.period);
        const [yearB, quarterB] = parsePeriod(b.period);
        if (yearA !== yearB) {
          return yearA - yearB; // Ascending by year for chart display
        }
        return quarterA - quarterB; // Ascending by quarter
      });

    return { allMetrics: metrics, chartData };
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
      // Auto-select first 5 if no saved preferences
      const defaultMetrics = allMetrics.slice(0, 5);
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

  if (isLoading) {
    return <Loading message="Loading trend data..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load trend data" />;
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

  const filteredChartData = chartData.map((item: any) => {
    const filtered: any = { period: item.period };
    selectedMetrics.forEach((metric) => {
      filtered[metric] = item[metric] || 0;
    });
    return filtered;
  });

  return (
    <div className="space-y-6">
      <Card>
        <div className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <MultiSelect
                label="Metrics to plot"
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chart Type
            </label>
            <div className="flex gap-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="Line"
                  checked={chartType === 'Line'}
                  onChange={(e) => setChartType(e.target.value as 'Line' | 'Bar')}
                  className="mr-2"
                />
                Line
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="Bar"
                  checked={chartType === 'Bar'}
                  onChange={(e) => setChartType(e.target.value as 'Line' | 'Bar')}
                  className="mr-2"
                />
                Bar
              </label>
            </div>
          </div>
        </div>
      </Card>

      {selectedMetrics.length > 0 && filteredChartData.length > 0 && (
        <Card>
          <div className="space-y-6">
            {selectedMetrics.map((metric) => {
              const metricData = chartData.map((item: any) => ({
                period: item.period,
                value: item[metric] || 0,
              }));

              // Get metric-specific unit information
              const metricInfo = getMetricUnit(metric);
              
              // Determine scaling for axis display
              let scaleFactor = 1;
              let axisUnit = '';
              let tickFormatter: (value: number) => string;
              
              if (metricInfo.isPercentage) {
                // Percentages: show as-is, no scaling
                scaleFactor = 1;
                axisUnit = '%';
                tickFormatter = (value: number) => `${(value * 100).toFixed(1)}%`;
              } else {
                // For currency and other metrics, use human-readable scaling
                const maxValue = Math.max(...metricData.map(d => Math.abs(d.value)));
                const { unit, value: scaledMax } = humanFormatForAxis(maxValue);
                axisUnit = unit;
                scaleFactor = unit === 'B' ? 1e9 : unit === 'M' ? 1e6 : unit === 'K' ? 1e3 : 1;
                tickFormatter = (value: number) => {
                  if (unit === 'B') return `${(value).toFixed(1)}B`;
                  if (unit === 'M') return `${(value).toFixed(1)}M`;
                  if (unit === 'K') return `${(value).toFixed(1)}K`;
                  return value.toFixed(0);
                };
              }

              const scaledData = metricData.map((item) => ({
                ...item,
                value: metricInfo.isPercentage ? item.value : item.value / scaleFactor,
              }));

              const colors = [
                '#3B82F6',
                '#10B981',
                '#F59E0B',
                '#EF4444',
                '#8B5CF6',
                '#EC4899',
                '#06B6D4',
                '#84CC16',
              ];
              const color = colors[selectedMetrics.indexOf(metric) % colors.length];

              // Format Y-axis label
              let yAxisLabel = 'Value';
              if (metricInfo.isPercentage) {
                yAxisLabel = 'Value (%)';
              } else if (axisUnit) {
                yAxisLabel = metricInfo.unit === '$' ? `Value (${axisUnit})` : `Value (${axisUnit})`;
              }

              return (
                <div key={metric}>
                  <h3 className="text-lg font-semibold mb-4 flex items-center">
                    {metric}
                    <MetricTooltip metricName={metric} />
                  </h3>
                  <ResponsiveContainer width="100%" height={300}>
                    {chartType === 'Line' ? (
                      <LineChart data={scaledData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period" />
                        <YAxis
                          label={{
                            value: yAxisLabel,
                            angle: -90,
                            position: 'insideLeft',
                          }}
                          tickFormatter={tickFormatter}
                        />
                        <Tooltip
                          formatter={(value: number) => {
                            // Convert back to original scale for tooltip
                            const originalValue = metricInfo.isPercentage ? value : value * scaleFactor;
                            return metricInfo.formatFn(originalValue);
                          }}
                          labelFormatter={(label) => `Period: ${label}`}
                        />
                        <Line
                          type="monotone"
                          dataKey="value"
                          stroke={color}
                          strokeWidth={2}
                          dot={{ r: 4 }}
                          activeDot={{ r: 6 }}
                        />
                      </LineChart>
                    ) : (
                      <BarChart data={scaledData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period" />
                        <YAxis
                          label={{
                            value: yAxisLabel,
                            angle: -90,
                            position: 'insideLeft',
                          }}
                          tickFormatter={tickFormatter}
                        />
                        <Tooltip
                          formatter={(value: number) => {
                            // Convert back to original scale for tooltip
                            const originalValue = metricInfo.isPercentage ? value : value * scaleFactor;
                            return metricInfo.formatFn(originalValue);
                          }}
                          labelFormatter={(label) => `Period: ${label}`}
                        />
                        <Bar dataKey="value" fill={color} />
                      </BarChart>
                    )}
                  </ResponsiveContainer>
                </div>
              );
            })}
          </div>
        </Card>
      )}
    </div>
  );
}

