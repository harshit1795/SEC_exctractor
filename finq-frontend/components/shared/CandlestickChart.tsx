'use client';

import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface CandlestickData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface CandlestickChartProps {
  data: CandlestickData[];
  height?: number;
}

export function CandlestickChart({ data, height = 400 }: CandlestickChartProps) {
  // Prepare data for visualization
  const chartData = data.map((item) => {
    const isUp = item.close >= item.open;
    return {
      ...item,
      dateFormatted: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      isUp,
      // For visual representation
      range: item.high - item.low,
      bodyRange: Math.abs(item.close - item.open),
    };
  });

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis
          dataKey="dateFormatted"
          angle={-45}
          textAnchor="end"
          height={80}
          interval="preserveStartEnd"
        />
        <YAxis
          domain={['auto', 'auto']}
          label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }}
        />
        <Tooltip
          formatter={(value: number, name: string) => {
            if (name === 'isUp' || name === 'range' || name === 'bodyRange') return '';
            return [`$${value.toFixed(2)}`, name];
          }}
          labelFormatter={(label) => `Date: ${label}`}
          contentStyle={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            border: '1px solid #ccc',
            borderRadius: '4px',
          }}
        />
        
        {/* High-Low range visualization */}
        <Line
          type="monotone"
          dataKey="high"
          stroke="#666"
          strokeWidth={1}
          dot={false}
          name="High"
          strokeOpacity={0.4}
        />
        <Line
          type="monotone"
          dataKey="low"
          stroke="#666"
          strokeWidth={1}
          dot={false}
          name="Low"
          strokeOpacity={0.4}
        />
        
        {/* Close price line */}
        <Line
          type="monotone"
          dataKey="close"
          stroke="#3B82F6"
          strokeWidth={2}
          dot={false}
          name="Close"
        />
        
        {/* Open price line */}
        <Line
          type="monotone"
          dataKey="open"
          stroke="#F59E0B"
          strokeWidth={1.5}
          strokeDasharray="3 3"
          dot={false}
          name="Open"
          strokeOpacity={0.6}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
