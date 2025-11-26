'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '../api';

export function useFinqHealthScores(category?: string, limit: number = 10) {
  return useQuery({
    queryKey: ['health-scores', 'finq', category, limit],
    queryFn: async () => {
      const response = await api.getFinqHealthScores(category, limit);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });
}

export function useCustomHealthScores(metrics: string[], limit: number = 10) {
  return useQuery({
    queryKey: ['health-scores', 'custom', metrics.join(','), limit],
    queryFn: async () => {
      if (metrics.length === 0) {
        return { scores: [], total: 0 };
      }
      const response = await api.getCustomHealthScores(metrics, limit);
      return response.data;
    },
    enabled: metrics.length > 0,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });
}

