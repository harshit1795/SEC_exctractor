'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api';
import { useAuth } from './useAuth';

export function useFeed(limit: number = 20) {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';

  return useQuery({
    queryKey: ['nexus', 'feed', userId],
    queryFn: async () => {
      const response = await api.getFeed(userId, limit);
      return response.data;
    },
    enabled: !!user,
    refetchInterval: 30000, // Refetch every 30 seconds for real-time feel
  });
}

export function useCreatePost() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const userId = user?.uid || 'anonymous';

  return useMutation({
    mutationFn: async (data: { content: string; media_url?: string }) => {
      const response = await api.createPost({
        ...data,
        user_id: userId,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nexus', 'feed', userId] });
    },
  });
}

export function useLikePost() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const userId = user?.uid || 'anonymous';

  return useMutation({
    mutationFn: async (postId: string) => {
      const response = await api.likePost(postId, userId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nexus', 'feed', userId] });
    },
  });
}

export function useUnlikePost() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const userId = user?.uid || 'anonymous';

  return useMutation({
    mutationFn: async (postId: string) => {
      const response = await api.unlikePost(postId, userId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nexus', 'feed', userId] });
    },
  });
}

export function useAddComment() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const userId = user?.uid || 'anonymous';

  return useMutation({
    mutationFn: async (data: { postId: string; content: string }) => {
      const response = await api.addComment(data.postId, {
        user_id: userId,
        content: data.content,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nexus', 'feed', userId] });
    },
  });
}

export function useFriends() {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';

  return useQuery({
    queryKey: ['nexus', 'friends', userId],
    queryFn: async () => {
      const response = await api.getFriends(userId);
      return response.data;
    },
    enabled: !!user,
  });
}

export function useFriendRequests() {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';

  return useQuery({
    queryKey: ['nexus', 'friend-requests', userId],
    queryFn: async () => {
      const response = await api.getFriendRequests(userId);
      return response.data;
    },
    enabled: !!user,
  });
}

export function useSendFriendRequest() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const userId = user?.uid || 'anonymous';

  return useMutation({
    mutationFn: async (friend_id: string) => {
      const response = await api.sendFriendRequest({
        user_id: userId,
        friend_id,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nexus', 'friends', userId] });
      queryClient.invalidateQueries({ queryKey: ['nexus', 'directory', userId] });
      queryClient.invalidateQueries({ queryKey: ['nexus', 'profile'] });
    },
  });
}

export function useAcceptFriendRequest() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const userId = user?.uid || 'anonymous';

  return useMutation({
    mutationFn: async (friend_id: string) => {
      const response = await api.acceptFriendRequest(friend_id, userId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['nexus', 'friends', userId] });
      queryClient.invalidateQueries({ queryKey: ['nexus', 'friend-requests', userId] });
      queryClient.invalidateQueries({ queryKey: ['nexus', 'directory', userId] });
      queryClient.invalidateQueries({ queryKey: ['nexus', 'profile'] });
    },
  });
}

export function useUserDirectory(limit: number = 100, offset: number = 0) {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';

  return useQuery({
    queryKey: ['nexus', 'directory', userId, limit, offset],
    queryFn: async () => {
      const response = await api.getUserDirectory(userId, limit, offset);
      return response.data;
    },
    enabled: !!user,
  });
}

export function useUserProfile(targetUserId: string) {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';

  return useQuery({
    queryKey: ['nexus', 'profile', targetUserId, userId],
    queryFn: async () => {
      const response = await api.getUserProfile(targetUserId, userId);
      return response.data;
    },
    enabled: !!user && !!targetUserId,
  });
}

