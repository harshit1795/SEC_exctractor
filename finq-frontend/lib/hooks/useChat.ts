'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api';
import { useAuth } from './useAuth';

export function useChatHistory(limit: number = 50, sessionId?: string) {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';

  return useQuery({
    queryKey: ['chat', 'history', userId, sessionId],
    queryFn: async () => {
      const response = await api.getChatHistory(userId, limit, sessionId);
      return response.data;
    },
    enabled: !!user,
  });
}

export function useChatSessions(limit: number = 50) {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';

  return useQuery({
    queryKey: ['chat', 'sessions', userId],
    queryFn: async () => {
      const response = await api.getChatSessions(userId, limit);
      return response.data;
    },
    enabled: !!user,
  });
}

export function useAnalyzeFinancialData() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const userId = user?.uid || 'anonymous';

  return useMutation({
    mutationFn: async (data: {
      prompt: string;
      context_data?: any;
      session_id?: string;
    }) => {
      try {
        const response = await api.analyzeFinancialData({
          prompt: data.prompt,
          context_data: {
            ...data.context_data,
            user_id: userId,
          },
          session_id: data.session_id,
        });
        // Backend returns { response, insight_id, session_id, timestamp }
        return response.data;
      } catch (error: any) {
        console.error('Chat API error:', error);
        // Re-throw with more context
        throw error;
      }
    },
    onSuccess: () => {
      // Don't invalidate history immediately - let the component manage its own state
      // History will be updated on next mount or manual refresh
      // This prevents history from overwriting new messages
    },
  });
}

