'use client';

import { useState, useMemo } from 'react';
import { useTickerData } from '@/lib/hooks/useTickerData';
import { humanFormat } from '@/lib/utils';
import { addTechnicalIndicators, PriceData } from '@/lib/utils/technicalIndicators';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Cell } from 'recharts';
import { CandlestickChart } from '@/components/shared/CandlestickChart';

interface PriceChartTabProps {
  ticker: string;
}

export function PriceChartTab({ ticker }: PriceChartTabProps) {
  const { data, isLoading, error } = useTickerData(ticker, '2y');
  const [chartType, setChartType] = useState<'Line' | 'Candlestick'>('Candlestick');
  const [aggregation, setAggregation] = useState<'Daily' | 'Weekly' | 'Monthly'>('Daily');
  const [showIndicators, setShowIndicators] = useState({
    bb: true,
    rsi: true,
    macd: true,
  });
  
  // Date range filter
  const [dateRange, setDateRange] = useState<{ start: string; end: string } | null>(null);

  const priceData = useMemo(() => {
    if (!data?.data) {
      return [];
    }

    const history = data.data.history_df || data.data.history || [];
    
    if (!Array.isArray(history) || history.length === 0) {
      const historyDict = data.data.history;
      if (historyDict && typeof historyDict === 'object' && !Array.isArray(historyDict)) {
        const dates = Object.keys(historyDict.Close || historyDict.close || {});
        if (dates.length > 0) {
          return dates.map((date) => ({
            date: date,
            open: historyDict.Open?.[date] || historyDict.open?.[date] || 0,
            high: historyDict.High?.[date] || historyDict.high?.[date] || 0,
            low: historyDict.Low?.[date] || historyDict.low?.[date] || 0,
            close: historyDict.Close?.[date] || historyDict.close?.[date] || 0,
            volume: historyDict.Volume?.[date] || historyDict.volume?.[date] || 0,
          })).filter((item) => item.close > 0)
            .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
        }
      }
      return [];
    }

    return history
      .map((item: any, index: number) => {
        const date = item.Date || item.date || item.index;
        const open = item.Open ?? item.open ?? 0;
        const high = item.High ?? item.high ?? 0;
        const low = item.Low ?? item.low ?? 0;
        const close = item.Close ?? item.close ?? 0;
        const volume = item.Volume ?? item.volume ?? 0;

        let dateStr = '';
        if (date) {
          if (typeof date === 'string') {
            dateStr = date.split('T')[0];
          } else if (date instanceof Date) {
            dateStr = date.toISOString().split('T')[0];
          } else if (typeof date === 'object' && date.toISOString) {
            dateStr = date.toISOString().split('T')[0];
          } else {
            try {
              dateStr = new Date(date).toISOString().split('T')[0];
            } catch {
              dateStr = new Date(Date.now() - (history.length - index) * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
            }
          }
        } else {
          dateStr = new Date(Date.now() - (history.length - index) * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        }

        return {
          date: dateStr,
          open: typeof open === 'number' ? open : parseFloat(open) || 0,
          high: typeof high === 'number' ? high : parseFloat(high) || 0,
          low: typeof low === 'number' ? low : parseFloat(low) || 0,
          close: typeof close === 'number' ? close : parseFloat(close) || 0,
          volume: typeof volume === 'number' ? volume : parseFloat(volume) || 0,
        };
      })
      .filter((item) => item.date && item.close > 0)
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [data]);

  const processedData = useMemo(() => {
    if (priceData.length === 0) return [];

    let processed: PriceData[] = [...priceData];

    // Apply aggregation
    if (aggregation === 'Weekly' || aggregation === 'Monthly') {
      const grouped = new Map<string, PriceData[]>();
      
      processed.forEach((item) => {
        const date = new Date(item.date);
        let key = '';
        
        if (aggregation === 'Weekly') {
          const weekStart = new Date(date);
          weekStart.setDate(date.getDate() - date.getDay());
          key = weekStart.toISOString().split('T')[0];
        } else {
          key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        }
        
        if (!grouped.has(key)) {
          grouped.set(key, []);
        }
        grouped.get(key)!.push(item);
      });

      processed = Array.from(grouped.entries()).map(([key, items]) => {
        const sorted = items.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
        return {
          date: sorted[0].date,
          open: sorted[0].open,
          high: Math.max(...sorted.map((i) => i.high)),
          low: Math.min(...sorted.map((i) => i.low)),
          close: sorted[sorted.length - 1].close,
          volume: sorted.reduce((sum, i) => sum + i.volume, 0),
        };
      });
    }

    // Add technical indicators
    let result = addTechnicalIndicators(processed);
    
    // Apply date range filter if set
    if (dateRange) {
      const startDate = new Date(dateRange.start);
      const endDate = new Date(dateRange.end);
      endDate.setHours(23, 59, 59, 999); // Include the entire end date
      
      result = result.filter((item) => {
        const itemDate = new Date(item.date);
        return itemDate >= startDate && itemDate <= endDate;
      });
    }
    
    return result;
  }, [priceData, aggregation, dateRange]);

  // Prepare candlestick data
  const candlestickData = useMemo(() => {
    return processedData.map((item) => ({
      date: item.date,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    })).filter((item) => item.date && item.close > 0);
  }, [processedData]);

  const latestPrice = processedData.length > 0 ? processedData[processedData.length - 1].close : 0;
  const previousPrice = processedData.length > 1 ? processedData[processedData.length - 2].close : latestPrice;
  const priceChange = latestPrice - previousPrice;
  const priceChangePercent = previousPrice !== 0 ? (priceChange / previousPrice) * 100 : 0;

  const latestRSI = processedData.length > 0 ? processedData[processedData.length - 1].rsi : null;
  const latestMACD = processedData.length > 0 ? processedData[processedData.length - 1].macd : null;

  if (isLoading) {
    return <Loading message="Loading price data..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load price data" />;
  }

  if (processedData.length === 0) {
    return (
      <Card>
        <p className="text-gray-600 text-center py-8">
          No price data available for {ticker}.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <div className="text-sm text-gray-600 mb-1">Latest Price</div>
          <div className="text-2xl font-bold">{humanFormat(latestPrice)}</div>
        </Card>
        <Card>
          <div className="text-sm text-gray-600 mb-1">Change</div>
          <div className={`text-2xl font-bold ${priceChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {priceChange >= 0 ? '+' : ''}{humanFormat(priceChange)}
          </div>
        </Card>
        <Card>
          <div className="text-sm text-gray-600 mb-1">Change %</div>
          <div className={`text-2xl font-bold ${priceChangePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%
          </div>
        </Card>
        {latestRSI !== null && latestRSI !== undefined && (
          <Card>
            <div className="text-sm text-gray-600 mb-1">RSI (14)</div>
            <div className={`text-2xl font-bold ${
              latestRSI > 70 ? 'text-red-600' : latestRSI < 30 ? 'text-green-600' : 'text-gray-600'
            }`}>
              {latestRSI.toFixed(2)}
            </div>
          </Card>
        )}
        {latestMACD !== null && latestMACD !== undefined && (
          <Card>
            <div className="text-sm text-gray-600 mb-1">MACD</div>
            <div className={`text-2xl font-bold ${latestMACD >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {latestMACD.toFixed(4)}
            </div>
          </Card>
        )}
      </div>

      {/* Chart Controls */}
      <Card>
        <div className="mb-4">
          <h3 className="text-lg font-semibold mb-4">Price Chart</h3>
          
          {/* Date Range Filter */}
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date Range Filter
            </label>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <label className="block text-xs text-gray-600 mb-1">Start Date</label>
                <input
                  type="date"
                  value={dateRange?.start || ''}
                  onChange={(e) => {
                    const start = e.target.value;
                    setDateRange((prev) => ({
                      start,
                      end: prev?.end || new Date().toISOString().split('T')[0],
                    }));
                  }}
                  max={dateRange?.end || new Date().toISOString().split('T')[0]}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                />
              </div>
              <div className="flex-1">
                <label className="block text-xs text-gray-600 mb-1">End Date</label>
                <input
                  type="date"
                  value={dateRange?.end || ''}
                  onChange={(e) => {
                    const end = e.target.value;
                    setDateRange((prev) => ({
                      start: prev?.start || '',
                      end,
                    }));
                  }}
                  min={dateRange?.start}
                  max={new Date().toISOString().split('T')[0]}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => setDateRange(null)}
                  className="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Clear Filter
                </button>
              </div>
            </div>
            {dateRange && (
              <div className="mt-2 text-xs text-gray-600">
                Showing data from {new Date(dateRange.start).toLocaleDateString()} to {new Date(dateRange.end).toLocaleDateString()}
              </div>
            )}
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
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
                    onChange={(e) => setChartType(e.target.value as 'Line' | 'Candlestick')}
                    className="mr-2"
                  />
                  Line
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="Candlestick"
                    checked={chartType === 'Candlestick'}
                    onChange={(e) => setChartType(e.target.value as 'Line' | 'Candlestick')}
                    className="mr-2"
                  />
                  Candlestick
                </label>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Aggregation
              </label>
              <select
                value={aggregation}
                onChange={(e) => setAggregation(e.target.value as 'Daily' | 'Weekly' | 'Monthly')}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
              >
                <option value="Daily">Daily</option>
                <option value="Weekly">Weekly</option>
                <option value="Monthly">Monthly</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Indicators
              </label>
              <div className="flex flex-col gap-2">
                <label className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={showIndicators.bb}
                    onChange={(e) => setShowIndicators({ ...showIndicators, bb: e.target.checked })}
                    className="mr-2"
                  />
                  Bollinger Bands
                </label>
                <label className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={showIndicators.rsi}
                    onChange={(e) => setShowIndicators({ ...showIndicators, rsi: e.target.checked })}
                    className="mr-2"
                  />
                  RSI
                </label>
                <label className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={showIndicators.macd}
                    onChange={(e) => setShowIndicators({ ...showIndicators, macd: e.target.checked })}
                    className="mr-2"
                  />
                  MACD
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Main Price Chart */}
        {chartType === 'Candlestick' ? (
          <div>
            <CandlestickChart data={candlestickData} height={400} />
            <div className="mt-2 text-sm text-gray-600 text-center">
              <p>💡 Green = Up Day, Red = Down Day | Showing High-Low wicks and Close price</p>
            </div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={processedData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                angle={-45}
                textAnchor="end"
                height={80}
                interval="preserveStartEnd"
              />
              <YAxis
                yAxisId="price"
                domain={['auto', 'auto']}
                label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                formatter={(value: number, name: string) => [`$${value.toFixed(2)}`, name]}
                labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString('en-US')}`}
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                }}
              />
              <Legend />
              <Line
                yAxisId="price"
                type="monotone"
                dataKey="close"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={false}
                name="Close"
              />
              {/* Bollinger Bands */}
              {showIndicators.bb && (
                <>
                  <Line
                    yAxisId="price"
                    type="monotone"
                    dataKey="bbUpper"
                    stroke="#F59E0B"
                    strokeWidth={1}
                    strokeDasharray="3 3"
                    dot={false}
                    name="Upper BB"
                  />
                  <Line
                    yAxisId="price"
                    type="monotone"
                    dataKey="bbMiddle"
                    stroke="#10B981"
                    strokeWidth={1}
                    strokeDasharray="5 5"
                    dot={false}
                    name="SMA (20)"
                  />
                  <Line
                    yAxisId="price"
                    type="monotone"
                    dataKey="bbLower"
                    stroke="#F59E0B"
                    strokeWidth={1}
                    strokeDasharray="3 3"
                    dot={false}
                    name="Lower BB"
                  />
                </>
              )}
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </Card>

      {/* RSI Chart */}
      {showIndicators.rsi && (
        <Card>
          <h3 className="text-lg font-semibold mb-4">RSI (14) - Relative Strength Index</h3>
          <ResponsiveContainer width="100%" height={200}>
            <ComposedChart data={processedData} margin={{ top: 10, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                angle={-45}
                textAnchor="end"
                height={60}
                interval="preserveStartEnd"
              />
              <YAxis domain={[0, 100]} label={{ value: 'RSI', angle: -90, position: 'insideLeft' }} />
              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Overbought (70)', position: 'right' }} />
              <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" label={{ value: 'Oversold (30)', position: 'right' }} />
              <Tooltip
                formatter={(value: number) => value.toFixed(2)}
                labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString('en-US')}`}
              />
              <Line
                type="monotone"
                dataKey="rsi"
                stroke="#10B981"
                strokeWidth={2}
                dot={false}
                name="RSI"
              />
            </ComposedChart>
          </ResponsiveContainer>
          <div className="mt-2 text-sm text-gray-600">
            <p>RSI above 70 = Overbought (bearish signal), RSI below 30 = Oversold (bullish signal)</p>
          </div>
        </Card>
      )}

      {/* MACD Chart */}
      {showIndicators.macd && (
        <Card>
          <h3 className="text-lg font-semibold mb-4">MACD (12, 26, 9) - Moving Average Convergence Divergence</h3>
          <ResponsiveContainer width="100%" height={200}>
            <ComposedChart data={processedData} margin={{ top: 10, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                angle={-45}
                textAnchor="end"
                height={60}
                interval="preserveStartEnd"
              />
              <YAxis yAxisId="macd" label={{ value: 'MACD', angle: -90, position: 'insideLeft' }} />
              <YAxis yAxisId="histogram" orientation="right" label={{ value: 'Histogram', angle: 90, position: 'insideRight' }} />
              <Tooltip
                formatter={(value: number, name: string) => [value.toFixed(4), name]}
                labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString('en-US')}`}
              />
              <Legend />
              <Line
                yAxisId="macd"
                type="monotone"
                dataKey="macd"
                stroke="#3B82F6"
                strokeWidth={2}
                dot={false}
                name="MACD"
              />
              <Line
                yAxisId="macd"
                type="monotone"
                dataKey="macdSignal"
                stroke="#F59E0B"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Signal"
              />
              <Bar
                yAxisId="histogram"
                dataKey="macdHistogram"
                name="Histogram"
              >
                {processedData.map((entry, index) => (
                  <Cell key={index} fill={entry.macdHistogram && entry.macdHistogram >= 0 ? '#10b981' : '#ef4444'} />
                ))}
              </Bar>
            </ComposedChart>
          </ResponsiveContainer>
          <div className="mt-2 text-sm text-gray-600">
            <p>MACD above Signal = Bullish momentum, MACD below Signal = Bearish momentum. Histogram shows the difference.</p>
          </div>
        </Card>
      )}
    </div>
  );
}
