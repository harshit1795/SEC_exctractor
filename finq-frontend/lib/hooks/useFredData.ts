'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '../api';

interface FredDataPoint {
  date: string;
  [key: string]: string | number;
}

export function useFredData(seriesIds: string[], startDate: string, endDate: string) {
  return useQuery({
    queryKey: ['fred', seriesIds.join(','), startDate, endDate],
    queryFn: async () => {
      if (seriesIds.length === 0) {
        return { data: [] };
      }
      const response = await api.getFredData(seriesIds, startDate, endDate);
      // Backend returns { data: [...], series_ids: [...] }
      return response.data;
    },
    enabled: seriesIds.length > 0 && !!startDate && !!endDate,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });
}

