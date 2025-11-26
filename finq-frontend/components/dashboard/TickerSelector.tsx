'use client';

import { useState, useMemo } from 'react';
import { useAvailableTickers } from '@/lib/hooks/useTickerData';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';

interface TickerSelectorProps {
  selectedTicker: string;
  onTickerChange: (ticker: string) => void;
}

export function TickerSelector({
  selectedTicker,
  onTickerChange,
}: TickerSelectorProps) {
  const [searchText, setSearchText] = useState('');
  const { data: tickers, isLoading, error } = useAvailableTickers();

  const filteredTickers = useMemo(() => {
    // Handle different response formats
    const tickerList = Array.isArray(tickers) ? tickers : (tickers?.tickers || []);
    
    if (!tickerList || tickerList.length === 0) return [];
    
    if (!searchText.trim()) {
      return [...tickerList].sort();
    }

    const searchLower = searchText.toLowerCase();
    return tickerList
      .filter((ticker: string) => {
        const tickerLower = ticker.toLowerCase();
        return tickerLower.includes(searchLower);
      })
      .sort();
  }, [tickers, searchText]);

  if (isLoading) {
    return <Loading message="Loading tickers..." size="sm" />;
  }

  if (error) {
    return (
      <div>
        <ErrorDisplay error={error} message="Failed to load tickers" />
        <div className="mt-2 text-xs text-gray-500">
          <p>Make sure the backend is running on http://localhost:8000</p>
          <p>API endpoint: /api/financial/tickers/available</p>
        </div>
      </div>
    );
  }

  // Set default to AAPL if available
  const defaultTicker = filteredTickers.includes('AAPL')
    ? 'AAPL'
    : filteredTickers[0] || '';

  // Update selected ticker if current selection is not in filtered list
  if (selectedTicker && !filteredTickers.includes(selectedTicker)) {
    if (defaultTicker && defaultTicker !== selectedTicker) {
      onTickerChange(defaultTicker);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label
          htmlFor="ticker-search"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Search Company or Ticker
        </label>
        <input
          id="ticker-search"
          type="text"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          placeholder="Type to search..."
          className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
        />
      </div>

      <div>
        <label
          htmlFor="ticker-select"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Company (Ticker)
        </label>
        <select
          id="ticker-select"
          value={selectedTicker || defaultTicker}
          onChange={(e) => onTickerChange(e.target.value)}
          className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
        >
          {filteredTickers.length === 0 ? (
            <option value="">No tickers found</option>
          ) : (
            filteredTickers.map((ticker: string) => (
              <option key={ticker} value={ticker}>
                {ticker}
              </option>
            ))
          )}
        </select>
        {filteredTickers.length > 0 && (
          <p className="mt-1 text-xs text-gray-500">
            {filteredTickers.length} ticker{filteredTickers.length !== 1 ? 's' : ''}{' '}
            found
          </p>
        )}
      </div>
    </div>
  );
}

