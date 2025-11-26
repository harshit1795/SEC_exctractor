'use client';

import { useState, useMemo } from 'react';
import { useFredData } from '@/lib/hooks/useFredData';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { MultiSelect } from '@/components/shared/MultiSelect';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

const INDICATORS = {
  'GDP': { id: 'GDP', freq: 'q', label: 'GDP' },
  'Real GDP': { id: 'GDPC1', freq: 'q', label: 'Real GDP' },
  'Inflation (CPI)': { id: 'CPIAUCSL', freq: 'm', label: 'Inflation (CPI)' },
  'Unemployment Rate': { id: 'UNRATE', freq: 'm', label: 'Unemployment Rate' },
  '10-Year Treasury Yield': { id: 'DGS10', freq: 'd', label: '10-Year Treasury Yield' },
  'Federal Funds Rate': { id: 'FEDFUNDS', freq: 'd', label: 'Federal Funds Rate' },
};

const DEFAULT_INDICATORS = ['Real GDP', 'Inflation (CPI)', 'Unemployment Rate'];

export function MacroeconomicTab() {
  const [selectedIndicators, setSelectedIndicators] = useState<string[]>(DEFAULT_INDICATORS);
  const [startDate, setStartDate] = useState<string>('2000-01-01');
  const [endDate, setEndDate] = useState<string>(format(new Date(), 'yyyy-MM-dd'));
  const [aggregation, setAggregation] = useState<'Monthly' | 'Quarterly' | 'Yearly'>('Quarterly');
  const [chartType, setChartType] = useState<'Line' | 'Bar'>('Line');

  const seriesIds = useMemo(() => {
    return selectedIndicators.map(key => INDICATORS[key as keyof typeof INDICATORS]?.id).filter(Boolean);
  }, [selectedIndicators]);

  const { data, isLoading, error } = useFredData(seriesIds, startDate, endDate);

  const processedData = useMemo(() => {
    // Backend returns { data: [...], series_ids: [...] }
    const dataArray = data?.data || [];
    if (!Array.isArray(dataArray) || dataArray.length === 0) {
      return [];
    }

    // Convert API response to chart format
    const dateMap = new Map<string, any>();

    dataArray.forEach((row: any) => {
      const date = row.date || row.Date || row.period || row.index;
      if (!date) return;

      // Handle date conversion
      let dateStr = '';
      if (typeof date === 'string') {
        dateStr = date.split('T')[0]; // Extract just the date part
      } else if (date instanceof Date) {
        dateStr = date.toISOString().split('T')[0];
      } else {
        try {
          dateStr = new Date(date).toISOString().split('T')[0];
        } catch {
          return;
        }
      }

      if (!dateMap.has(dateStr)) {
        dateMap.set(dateStr, { date: dateStr });
      }

      // Add each indicator value
      selectedIndicators.forEach(key => {
        const indicator = INDICATORS[key as keyof typeof INDICATORS];
        if (indicator) {
          // Try multiple possible column names
          const value = row[indicator.id] ?? row[indicator.label] ?? row[key];
          if (value !== undefined && value !== null) {
            dateMap.get(dateStr)[indicator.label] = parseFloat(value) || 0;
          }
        }
      });
    });

    let result = Array.from(dateMap.values())
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

    // Apply aggregation
    if (aggregation !== 'Monthly') {
      const grouped = new Map<string, any[]>();
      
      result.forEach((item) => {
        const date = new Date(item.date);
        let key = '';
        
        if (aggregation === 'Quarterly') {
          const quarter = Math.floor(date.getMonth() / 3);
          key = `${date.getFullYear()}-Q${quarter + 1}`;
        } else { // Yearly
          key = `${date.getFullYear()}`;
        }
        
        if (!grouped.has(key)) {
          grouped.set(key, []);
        }
        grouped.get(key)!.push(item);
      });

      result = Array.from(grouped.entries()).map(([key, items]) => {
        const aggregated: any = { date: key };
        selectedIndicators.forEach(key => {
          const indicator = INDICATORS[key as keyof typeof INDICATORS];
          if (indicator) {
            const values = items.map((item: any) => item[indicator.label]).filter((v: any) => v !== undefined && !isNaN(v));
            aggregated[indicator.label] = values.length > 0 ? values.reduce((a: number, b: number) => a + b, 0) / values.length : null;
          }
        });
        return aggregated;
      });
    }

    return result;
  }, [data, selectedIndicators, aggregation]);

  if (isLoading) {
    return <Loading message="Loading macroeconomic data..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load macroeconomic data" />;
  }

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">📊 Macroeconomic Data</h2>
        <p className="text-gray-600 mb-6">
          View and analyze key economic indicators from the Federal Reserve Economic Data (FRED).
        </p>

        {/* Indicator Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Economic Indicators
          </label>
          <MultiSelect
            options={Object.keys(INDICATORS)}
            selected={selectedIndicators}
            onChange={setSelectedIndicators}
            placeholder="Select indicators..."
          />
        </div>

        {selectedIndicators.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Please select at least one economic indicator to display.
          </div>
        ) : (
          <>
            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  max={format(new Date(), 'yyyy-MM-dd')}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Aggregation</label>
                <select
                  value={aggregation}
                  onChange={(e) => setAggregation(e.target.value as 'Monthly' | 'Quarterly' | 'Yearly')}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                >
                  <option value="Monthly">Monthly</option>
                  <option value="Quarterly">Quarterly</option>
                  <option value="Yearly">Yearly</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Chart Type</label>
                <select
                  value={chartType}
                  onChange={(e) => setChartType(e.target.value as 'Line' | 'Bar')}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                >
                  <option value="Line">Line</option>
                  <option value="Bar">Bar</option>
                </select>
              </div>
            </div>

            {/* Chart */}
            {processedData.length > 0 ? (
              <>
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-4">Macroeconomic Trends</h3>
                  <ResponsiveContainer width="100%" height={400}>
                    <ComposedChart data={processedData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                      <XAxis
                        dataKey="date"
                        angle={-45}
                        textAnchor="end"
                        height={80}
                        interval="preserveStartEnd"
                      />
                      <YAxis />
                      <Tooltip
                        formatter={(value: number) => typeof value === 'number' ? value.toFixed(2) : value}
                        labelFormatter={(label) => `Date: ${label}`}
                        contentStyle={{
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          border: '1px solid #ccc',
                          borderRadius: '4px',
                        }}
                      />
                      <Legend />
                      {selectedIndicators.map((key, index) => {
                        const indicator = INDICATORS[key as keyof typeof INDICATORS];
                        if (!indicator) return null;
                        
                        const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
                        const color = colors[index % colors.length];
                        
                        if (chartType === 'Bar') {
                          return (
                            <Bar
                              key={indicator.label}
                              dataKey={indicator.label}
                              fill={color}
                              name={indicator.label}
                            />
                          );
                        } else {
                          return (
                            <Line
                              key={indicator.label}
                              type="monotone"
                              dataKey={indicator.label}
                              stroke={color}
                              strokeWidth={2}
                              dot={false}
                              name={indicator.label}
                            />
                          );
                        }
                      })}
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>

                {/* Data Table */}
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">Aggregated Data ({aggregation})</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 border border-gray-300">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-r border-gray-300">
                            Period
                          </th>
                          {selectedIndicators.map((key) => {
                            const indicator = INDICATORS[key as keyof typeof INDICATORS];
                            return indicator ? (
                              <th
                                key={indicator.label}
                                className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase tracking-wider"
                              >
                                {indicator.label}
                              </th>
                            ) : null;
                          })}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {processedData.map((row, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 border-r border-gray-300">
                              {row.date}
                            </td>
                            {selectedIndicators.map((key) => {
                              const indicator = INDICATORS[key as keyof typeof INDICATORS];
                              if (!indicator) return null;
                              const value = row[indicator.label];
                              return (
                                <td
                                  key={indicator.label}
                                  className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-700"
                                >
                                  {value !== null && value !== undefined ? value.toFixed(2) : 'N/A'}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No data available for the selected indicators and date range.
              </div>
            )}
          </>
        )}
      </Card>
    </div>
  );
}

