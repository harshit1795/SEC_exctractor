'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api';

export function useDataStatus(ticker?: string) {
  return useQuery({
    queryKey: ['data-pipeline', 'status', ticker],
    queryFn: async () => {
      const response = await api.getDataStatus(ticker);
      return response.data;
    },
    staleTime: 60 * 1000, // 1 minute
  });
}

export function useUpdateTickerData() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ ticker, forceRefresh }: { ticker: string; forceRefresh?: boolean }) => {
      const response = await api.updateTickerData(ticker, forceRefresh);
      return response.data;
    },
    onSuccess: (data, variables) => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['fundamentals', variables.ticker] });
      queryClient.invalidateQueries({ queryKey: ['data-pipeline', 'status'] });
      queryClient.invalidateQueries({ queryKey: ['tickers', 'available'] });
    },
  });
}

export function useUpdateLatestData() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (tickers?: string[]) => {
      const response = await api.updateLatestData(tickers);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate all fundamentals and status queries
      queryClient.invalidateQueries({ queryKey: ['fundamentals'] });
      queryClient.invalidateQueries({ queryKey: ['data-pipeline', 'status'] });
      queryClient.invalidateQueries({ queryKey: ['tickers', 'available'] });
    },
  });
}

