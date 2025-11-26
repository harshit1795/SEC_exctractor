'use client';

import { useState, useMemo } from 'react';
import { useFundamentals } from '@/lib/hooks/useTickerData';
import { useTickerData } from '@/lib/hooks/useTickerData';
import { useFredData } from '@/lib/hooks/useFredData';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { MultiSelect } from '@/components/shared/MultiSelect';
import { ComposedChart, Line, Bar, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

const FRED_INDICATORS = {
  'Real GDP': { id: 'GDPC1', freq: 'q', label: 'Real GDP' },
  'Inflation (CPI)': { id: 'CPIAUCSL', freq: 'm', label: 'Inflation (CPI)' },
  'Unemployment Rate': { id: 'UNRATE', freq: 'm', label: 'Unemployment Rate' },
  '10-Year Treasury Yield': { id: 'DGS10', freq: 'd', label: '10-Year Treasury Yield' },
};

interface FinQ360TabProps {
  ticker: string;
}

export function FinQ360Tab({ ticker }: FinQ360TabProps) {
  const [selectedFundamentals, setSelectedFundamentals] = useState<string[]>([]);
  const [selectedEarnings, setSelectedEarnings] = useState<string[]>(['Reported EPS']);
  const [selectedFred, setSelectedFred] = useState<string[]>([]);
  const [startDate, setStartDate] = useState<string>('2000-01-01');
  const [endDate, setEndDate] = useState<string>(format(new Date(), 'yyyy-MM-dd'));
  const [aggregation, setAggregation] = useState<'Monthly' | 'Quarterly' | 'Yearly'>('Quarterly');
  const [chartType, setChartType] = useState<'Line' | 'Bar' | 'Scatter'>('Line');

  // Fetch data
  const { data: fundamentalsData, isLoading: loadingFundamentals } = useFundamentals(ticker);
  const { data: tickerData, isLoading: loadingTicker } = useTickerData(ticker, '5y');
  
  const fredSeriesIds = useMemo(() => {
    return selectedFred.map(key => FRED_INDICATORS[key as keyof typeof FRED_INDICATORS]?.id).filter(Boolean);
  }, [selectedFred]);

  const { data: fredData, isLoading: loadingFred } = useFredData(fredSeriesIds, startDate, endDate);

  // Process fundamentals data
  const fundamentalsMetrics = useMemo(() => {
    if (!fundamentalsData?.data || !Array.isArray(fundamentalsData.data)) {
      return [];
    }

    const metrics = new Set<string>();
    fundamentalsData.data.forEach((row: any) => {
      if (row.Metric || row.metric) {
        metrics.add(row.Metric || row.metric);
      }
    });
    return Array.from(metrics).sort();
  }, [fundamentalsData]);

  // Auto-select first fundamental if none selected
  useMemo(() => {
    if (fundamentalsMetrics.length > 0 && selectedFundamentals.length === 0) {
      setSelectedFundamentals([fundamentalsMetrics[0]]);
    }
  }, [fundamentalsMetrics, selectedFundamentals.length]);

  // Process earnings data
  const earningsData = useMemo(() => {
    if (!tickerData?.data?.earnings_dates) {
      return [];
    }

    const earnings = tickerData.data.earnings_dates;
    if (!Array.isArray(earnings)) {
      return [];
    }

    return earnings.map((item: any) => {
      const date = item.Date || item.date || item.index;
      let dateStr = '';
      if (date) {
        if (typeof date === 'string') {
          dateStr = date.split('T')[0];
        } else if (date instanceof Date) {
          dateStr = date.toISOString().split('T')[0];
        } else {
          try {
            dateStr = new Date(date).toISOString().split('T')[0];
          } catch {
            return null;
          }
        }
      }
      return {
        date: dateStr,
        'Reported EPS': item.ReportedEPS ?? item.reportedEps ?? item.reported_eps ?? 0,
        'EPS Estimate': item.EPSEstimate ?? item.epsEstimate ?? item.eps_estimate ?? 0,
      };
    }).filter((item: any) => item && item.date);
  }, [tickerData]);

  // Process fundamentals data for charting
  const fundamentalsChartData = useMemo(() => {
    if (!fundamentalsData?.data || !Array.isArray(fundamentalsData.data) || selectedFundamentals.length === 0) {
      return [];
    }

    const dataMap = new Map<string, any>();

    fundamentalsData.data.forEach((row: any) => {
      const metric = row.Metric || row.metric;
      if (!selectedFundamentals.includes(metric)) return;

      const period = row.FiscalPeriod || row.fiscalPeriod || row.period;
      if (!period) return;

      // Convert period to date (e.g., "2023Q1" -> "2023-03-31")
      let dateStr = '';
      try {
        if (period.includes('Q')) {
          const [year, quarter] = period.split('Q');
          const month = parseInt(quarter) * 3;
          dateStr = `${year}-${String(month).padStart(2, '0')}-01`;
        } else {
          dateStr = `${period}-12-31`;
        }
      } catch {
        return;
      }

      if (!dataMap.has(dateStr)) {
        dataMap.set(dateStr, { date: dateStr });
      }

      const value = parseFloat(row.Value || row.value || 0);
      dataMap.get(dateStr)[metric] = value;
    });

    return Array.from(dataMap.values()).sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  }, [fundamentalsData, selectedFundamentals]);

  // Process FRED data
  const fredChartData = useMemo(() => {
    if (!fredData?.data || !Array.isArray(fredData.data) || selectedFred.length === 0) {
      return [];
    }

    const dataMap = new Map<string, any>();

    fredData.data.forEach((row: any) => {
      const date = row.date || row.Date || row.period;
      if (!date) return;

      if (!dataMap.has(date)) {
        dataMap.set(date, { date });
      }

      selectedFred.forEach(key => {
        const indicator = FRED_INDICATORS[key as keyof typeof FRED_INDICATORS];
        if (indicator && row[indicator.id] !== undefined) {
          dataMap.get(date)[indicator.label] = parseFloat(row[indicator.id]) || 0;
        }
      });
    });

    return Array.from(dataMap.values()).sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );
  }, [fredData, selectedFred]);

  // Combine all data
  const combinedData = useMemo(() => {
    const allData: any[] = [];
    const dateMap = new Map<string, any>();

    // Add fundamentals
    fundamentalsChartData.forEach((item: any) => {
      const date = item.date;
      if (!dateMap.has(date)) {
        dateMap.set(date, { date });
      }
      Object.keys(item).forEach(key => {
        if (key !== 'date') {
          dateMap.get(date)[key] = item[key];
        }
      });
    });

    // Add earnings
    earningsData.forEach((item: any) => {
      const date = item.date;
      if (!dateMap.has(date)) {
        dateMap.set(date, { date });
      }
      if (selectedEarnings.includes('Reported EPS')) {
        dateMap.get(date)['Reported EPS'] = item['Reported EPS'];
      }
      if (selectedEarnings.includes('EPS Estimate')) {
        dateMap.get(date)['EPS Estimate'] = item['EPS Estimate'];
      }
    });

    // Add FRED data
    fredChartData.forEach((item: any) => {
      const date = item.date;
      if (!dateMap.has(date)) {
        dateMap.set(date, { date });
      }
      Object.keys(item).forEach(key => {
        if (key !== 'date') {
          dateMap.get(date)[key] = item[key];
        }
      });
    });

    let result = Array.from(dateMap.values())
      .filter(item => {
        const itemDate = new Date(item.date);
        const start = new Date(startDate);
        const end = new Date(endDate);
        return itemDate >= start && itemDate <= end;
      })
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
        const allKeys = new Set<string>();
        items.forEach((item: any) => {
          Object.keys(item).forEach(k => {
            if (k !== 'date') allKeys.add(k);
          });
        });

        allKeys.forEach(k => {
          const values = items.map((item: any) => item[k]).filter((v: any) => v !== undefined && !isNaN(v) && v !== null);
          aggregated[k] = values.length > 0 ? values.reduce((a: number, b: number) => a + b, 0) / values.length : null;
        });
        return aggregated;
      });
    }

    return result;
  }, [fundamentalsChartData, earningsData, fredChartData, selectedEarnings, startDate, endDate, aggregation]);

  const allSelectedMetrics = [...selectedFundamentals, ...selectedEarnings, ...selectedFred];

  const isLoading = loadingFundamentals || loadingTicker || loadingFred;

  if (isLoading) {
    return <Loading message="Loading data for FinQ 360 analysis..." />;
  }

  if (allSelectedMetrics.length === 0) {
    return (
      <Card>
        <div className="text-center py-8 text-gray-500">
          Please select at least one metric from the sections below to create a combined analysis.
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">🔍 FinQ 360</h2>
        <p className="text-gray-600 mb-6">
          Create custom charts by combining company fundamentals, earnings, and macroeconomic data for {ticker}.
        </p>

        {/* Metric Selection */}
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Company Fundamentals
            </label>
            <MultiSelect
              options={fundamentalsMetrics}
              selected={selectedFundamentals}
              onChange={setSelectedFundamentals}
              placeholder="Select fundamental metrics..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Earnings
            </label>
            <MultiSelect
              options={['Reported EPS', 'EPS Estimate']}
              selected={selectedEarnings}
              onChange={setSelectedEarnings}
              placeholder="Select earnings metrics..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Macroeconomic Data
            </label>
            <MultiSelect
              options={Object.keys(FRED_INDICATORS)}
              selected={selectedFred}
              onChange={setSelectedFred}
              placeholder="Select macroeconomic indicators..."
            />
          </div>
        </div>

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
              onChange={(e) => setChartType(e.target.value as 'Line' | 'Bar' | 'Scatter')}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="Line">Line</option>
              <option value="Bar">Bar</option>
              <option value="Scatter">Scatter</option>
            </select>
          </div>
        </div>

        {/* Chart */}
        {combinedData.length > 0 ? (
          <>
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-4">Combined Metric Analysis</h3>
              {chartType === 'Scatter' && allSelectedMetrics.length !== 2 ? (
                <div className="text-center py-8 text-yellow-600">
                  Please select exactly two metrics for a scatter plot.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={400}>
                  {chartType === 'Scatter' ? (
                    <ComposedChart data={combinedData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                      <XAxis
                        dataKey={allSelectedMetrics[0]}
                        type="number"
                        label={{ value: allSelectedMetrics[0], position: 'insideBottom', offset: -5 }}
                      />
                      <YAxis
                        type="number"
                        label={{ value: allSelectedMetrics[1], angle: -90, position: 'insideLeft' }}
                      />
                      <Tooltip />
                      <Legend />
                      <Scatter
                        dataKey={allSelectedMetrics[1]}
                        fill="#3B82F6"
                        name={allSelectedMetrics[1]}
                      />
                    </ComposedChart>
                  ) : (
                    <ComposedChart data={combinedData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
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
                      />
                      <Legend />
                      {allSelectedMetrics.map((metric, index) => {
                        const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#84CC16'];
                        const color = colors[index % colors.length];
                        
                        if (chartType === 'Bar') {
                          return (
                            <Bar
                              key={metric}
                              dataKey={metric}
                              fill={color}
                              name={metric}
                            />
                          );
                        } else {
                          return (
                            <Line
                              key={metric}
                              type="monotone"
                              dataKey={metric}
                              stroke={color}
                              strokeWidth={2}
                              dot={false}
                              name={metric}
                            />
                          );
                        }
                      })}
                    </ComposedChart>
                  )}
                </ResponsiveContainer>
              )}
            </div>
          </>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No data available for the selected metrics and date range.
          </div>
        )}
      </Card>
    </div>
  );
}

