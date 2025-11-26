'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '../api';

export function useTickerData(ticker: string, period: string = '1y') {
  return useQuery({
    queryKey: ['ticker', ticker, period],
    queryFn: async () => {
      const response = await api.getTickerData(ticker, period);
      return response.data;
    },
    enabled: !!ticker,
  });
}

export function useFundamentals(ticker: string) {
  return useQuery({
    queryKey: ['fundamentals', ticker],
    queryFn: async () => {
      const response = await api.getFundamentals(ticker);
      return response.data;
    },
    enabled: !!ticker,
  });
}

export function useSecData(ticker: string) {
  return useQuery({
    queryKey: ['sec', ticker],
    queryFn: async () => {
      const response = await api.getSecData(ticker);
      return response.data;
    },
    enabled: !!ticker,
  });
}

export function useAvailableTickers() {
  return useQuery({
    queryKey: ['tickers', 'available'],
    queryFn: async () => {
      const response = await api.getAvailableTickers();
      // API returns {tickers: [...], count: N}, extract just the tickers array
      return response.data?.tickers || response.data || [];
    },
    staleTime: 5 * 60 * 1000, // 5 minutes - ticker list doesn't change often
  });
}

