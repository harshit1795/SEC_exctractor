'use client';

import { useState, useMemo } from 'react';
import { useTickerData } from '@/lib/hooks/useTickerData';
import { humanFormat, formatPercent } from '@/lib/utils';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface EarningsTabProps {
  ticker: string;
}

interface EarningsData {
  date: string;
  reportedEPS: number | null;
  estimatedEPS: number | null;
  surprise: number | null;
}

export function EarningsTab({ ticker }: EarningsTabProps) {
  const { data, isLoading, error } = useTickerData(ticker, '2y');
  const [chartType, setChartType] = useState<'Line' | 'Bar'>('Line');
  const [aggregation, setAggregation] = useState<'Quarterly' | 'Yearly'>('Quarterly');

  const earningsData = useMemo(() => {
    if (!data?.data) {
      return [];
    }

    // Check for earnings_dates in the data
    const earningsDates = data.data.earnings_dates || [];
    
    
    if (!Array.isArray(earningsDates) || earningsDates.length === 0) {
      return [];
    }

    return earningsDates
      .filter((item: any) => {
        const reported = item['Reported EPS'] ?? item.reportedEPS ?? item.ReportedEPS;
        const estimated = item['EPS Estimate'] ?? item.estimatedEPS ?? item.EPSEstimate;
        return reported !== null && reported !== undefined && estimated !== null && estimated !== undefined;
      })
      .map((item: any) => {
        const date = item['Earnings Date'] ?? item.EarningsDate ?? item.earningsDate ?? item.date ?? item.Date;
        const reported = item['Reported EPS'] ?? item.reportedEPS ?? item.ReportedEPS;
        const estimated = item['EPS Estimate'] ?? item.estimatedEPS ?? item.EPSEstimate;
        const surprise = item['Surprise(%)'] ?? item.surprise ?? item.Surprise;
        
        // Handle date conversion
        let dateStr = '';
        if (date) {
          if (typeof date === 'string') {
            dateStr = date.split('T')[0]; // Extract just the date part
          } else if (date instanceof Date) {
            dateStr = date.toISOString().split('T')[0];
          } else if (typeof date === 'object' && date.toISOString) {
            dateStr = date.toISOString().split('T')[0];
          }
        }
        
        return {
          date: dateStr,
          reportedEPS: typeof reported === 'number' ? reported : parseFloat(reported) || null,
          estimatedEPS: typeof estimated === 'number' ? estimated : parseFloat(estimated) || null,
          surprise: typeof surprise === 'number' ? surprise : parseFloat(surprise) || null,
        };
      })
      .filter((item: EarningsData) => item.date && item.reportedEPS !== null && item.estimatedEPS !== null)
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [data]);

  const chartData = useMemo(() => {
    if (earningsData.length === 0) return [];

    if (aggregation === 'Yearly') {
      // Group by year and average
      const yearlyMap = new Map<number, { reported: number[]; estimated: number[] }>();
      
      earningsData.forEach((item) => {
        const year = new Date(item.date).getFullYear();
        if (!yearlyMap.has(year)) {
          yearlyMap.set(year, { reported: [], estimated: [] });
        }
        const yearData = yearlyMap.get(year)!;
        if (item.reportedEPS !== null) yearData.reported.push(item.reportedEPS);
        if (item.estimatedEPS !== null) yearData.estimated.push(item.estimatedEPS);
      });

      return Array.from(yearlyMap.entries())
        .map(([year, values]) => ({
          period: year.toString(),
          reportedEPS: values.reported.reduce((a, b) => a + b, 0) / values.reported.length,
          estimatedEPS: values.estimated.reduce((a, b) => a + b, 0) / values.estimated.length,
        }))
        .sort((a, b) => a.period.localeCompare(b.period));
    } else {
      // Quarterly - use as is
      return earningsData.map((item) => ({
        period: new Date(item.date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' }),
        reportedEPS: item.reportedEPS,
        estimatedEPS: item.estimatedEPS,
      }));
    }
  }, [earningsData, aggregation]);

  const lastEarnings = useMemo(() => {
    if (earningsData.length === 0) return null;
    const now = new Date();
    const past = earningsData
      .filter((item) => new Date(item.date) < now)
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    return past[0] || null;
  }, [earningsData]);

  const nextEarnings = useMemo(() => {
    if (earningsData.length === 0) return null;
    const now = new Date();
    const future = earningsData
      .filter((item) => new Date(item.date) > now)
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    return future[0] || null;
  }, [earningsData]);

  if (isLoading) {
    return <Loading message="Loading earnings data..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load earnings data" />;
  }

  if (earningsData.length === 0) {
    return (
      <Card>
        <p className="text-gray-600 text-center py-8">
          No earnings data available for {ticker}.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Historical EPS Trend */}
      <Card>
        <div className="mb-4">
          <h3 className="text-lg font-semibold mb-4">Historical EPS Trend</h3>
          <div className="flex gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Aggregation
              </label>
              <select
                value={aggregation}
                onChange={(e) => setAggregation(e.target.value as 'Quarterly' | 'Yearly')}
                className="rounded-md border border-gray-300 px-3 py-2 text-sm"
              >
                <option value="Quarterly">Quarterly</option>
                <option value="Yearly">Yearly</option>
              </select>
            </div>
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
        </div>
        {chartData.length > 0 && (
          <ResponsiveContainer width="100%" height={400}>
            {chartType === 'Line' ? (
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis />
                <Tooltip formatter={(value: number) => value.toFixed(2)} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="reportedEPS"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  name="Reported EPS"
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="estimatedEPS"
                  stroke="#10B981"
                  strokeWidth={2}
                  name="Estimated EPS"
                  strokeDasharray="5 5"
                  dot={{ r: 4 }}
                />
              </LineChart>
            ) : (
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis />
                <Tooltip formatter={(value: number) => value.toFixed(2)} />
                <Legend />
                <Bar dataKey="reportedEPS" fill="#3B82F6" name="Reported EPS" />
                <Bar dataKey="estimatedEPS" fill="#10B981" name="Estimated EPS" />
              </BarChart>
            )}
          </ResponsiveContainer>
        )}
      </Card>

      {/* Last Quarter's Earnings */}
      {lastEarnings && (
        <Card>
          <h3 className="text-lg font-semibold mb-4">Last Quarter's Earnings</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Date</p>
              <p className="text-lg font-semibold">
                {new Date(lastEarnings.date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Reported EPS</p>
              <p className="text-lg font-semibold">{lastEarnings.reportedEPS?.toFixed(2) || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Estimated EPS</p>
              <p className="text-lg font-semibold">{lastEarnings.estimatedEPS?.toFixed(2) || 'N/A'}</p>
            </div>
            {lastEarnings.surprise !== null && (
              <div>
                <p className="text-sm text-gray-600">Surprise (%)</p>
                <p
                  className={`text-lg font-semibold ${
                    lastEarnings.surprise > 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {formatPercent(lastEarnings.surprise)}
                </p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Next Earnings */}
      {nextEarnings && (
        <Card>
          <h3 className="text-lg font-semibold mb-4">Next Earnings</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Date</p>
              <p className="text-lg font-semibold">
                {new Date(nextEarnings.date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Estimated EPS</p>
              <p className="text-lg font-semibold">{nextEarnings.estimatedEPS?.toFixed(2) || 'N/A'}</p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

