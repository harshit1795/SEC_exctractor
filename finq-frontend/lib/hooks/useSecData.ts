'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '../api';

export function useSecFilings(ticker: string) {
  return useQuery({
    queryKey: ['sec', 'filings', ticker],
    queryFn: async () => {
      const response = await api.getSecData(ticker);
      // Response structure: { ticker: string, filings: { "10-k": {...}, "10-q": {...} } }
      return response.data;
    },
    enabled: !!ticker,
    staleTime: 10 * 60 * 1000, // 10 minutes - SEC filings don't change often
  });
}

export function useSec10K(ticker: string, sections: string[] = ['business', 'risk', 'mda']) {
  return useQuery({
    queryKey: ['sec', '10k', ticker, sections.join(',')],
    queryFn: async () => {
      const sectionsParam = sections.join(',');
      const response = await api.getSec10K(ticker, sectionsParam);
      return response.data;
    },
    enabled: !!ticker && sections.length > 0,
    staleTime: 10 * 60 * 1000,
  });
}

export function useSec10Q(ticker: string, sections: string[] = ['risk', 'mda']) {
  return useQuery({
    queryKey: ['sec', '10q', ticker, sections.join(',')],
    queryFn: async () => {
      const sectionsParam = sections.join(',');
      const response = await api.getSec10Q(ticker, sectionsParam);
      return response.data;
    },
    enabled: !!ticker && sections.length > 0,
    staleTime: 10 * 60 * 1000,
  });
}

