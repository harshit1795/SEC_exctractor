'use client';

import { useState } from 'react';
import { useUserProfile, useSendFriendRequest, useAcceptFriendRequest } from '@/lib/hooks/useNexus';
import { useAuth } from '@/lib/hooks/useAuth';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { getRelativeTime } from '@/lib/utils';

interface UserProfileViewProps {
  userId: string;
  onClose?: () => void;
}

export function UserProfileView({ userId, onClose }: UserProfileViewProps) {
  const { user: currentUser } = useAuth();
  const currentUserId = currentUser?.uid || 'anonymous';
  const isOwnProfile = userId === currentUserId;
  
  const { data, isLoading, error } = useUserProfile(userId);
  const sendRequestMutation = useSendFriendRequest();
  const acceptRequestMutation = useAcceptFriendRequest();

  if (isLoading) {
    return <Loading message="Loading profile..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load profile" />;
  }

  if (!data) {
    return (
      <Card>
        <div className="text-center py-8 text-gray-600">
          <p>Profile not found.</p>
        </div>
      </Card>
    );
  }

  const handleSendFriendRequest = async () => {
    try {
      await sendRequestMutation.mutateAsync(userId);
      alert('Friend request sent! Once they accept, you can see their posts in your feed.');
    } catch (error: any) {
      console.error('Failed to send friend request:', error);
      alert(error?.response?.data?.detail || 'Failed to send friend request. Please try again.');
    }
  };

  const handleAcceptRequest = async () => {
    try {
      await acceptRequestMutation.mutateAsync(userId);
      alert('Friend request accepted! You can now see their posts in your feed.');
    } catch (error: any) {
      console.error('Failed to accept friend request:', error);
      alert(error?.response?.data?.detail || 'Failed to accept friend request. Please try again.');
    }
  };

  // Determine display name and picture
  const displayName = data.display_name || data.firebase_display_name || userId;
  const profilePicture = data.profile_picture_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}`;

  return (
    <div className="space-y-6">
      {/* Back button */}
      {onClose && (
        <button
          onClick={onClose}
          className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
        >
          <span className="mr-2">←</span>
          Back
        </button>
      )}

      {/* Profile Header */}
      <Card>
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-6 flex-1">
            <div className="flex-shrink-0">
              <img
                src={profilePicture}
                alt={displayName}
                className="h-24 w-24 rounded-full"
              />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900">
                {displayName}
              </h2>
              {data.firebase_display_name && data.display_name && data.display_name !== data.firebase_display_name && (
                <p className="text-sm text-gray-500">Also known as: {data.firebase_display_name}</p>
              )}
              <div className="mt-4 flex items-center space-x-6">
                <div>
                  <span className="text-2xl font-bold text-gray-900">{data.posts_count}</span>
                  <p className="text-sm text-gray-600">Posts</p>
                </div>
                <div>
                  <span className="text-2xl font-bold text-gray-900">{data.friends_count}</span>
                  <p className="text-sm text-gray-600">Friends</p>
                </div>
                <div>
                  <span className="text-2xl font-bold text-gray-900">{data.insights_count}</span>
                  <p className="text-sm text-gray-600">Insights</p>
                </div>
              </div>
            </div>
          </div>
          {!isOwnProfile && (
            <div>
              {data.is_friend ? (
                <span className="px-4 py-2 text-sm text-green-700 bg-green-100 rounded-md flex items-center space-x-1">
                  <span>✓</span>
                  <span>Friends</span>
                </span>
              ) : data.has_pending_request ? (
                <button
                  onClick={handleAcceptRequest}
                  disabled={acceptRequestMutation.isPending}
                  className="px-4 py-2 text-sm text-white bg-green-600 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {acceptRequestMutation.isPending ? 'Accepting...' : 'Accept Request'}
                </button>
              ) : (
                <button
                  onClick={handleSendFriendRequest}
                  disabled={sendRequestMutation.isPending}
                  className="px-4 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {sendRequestMutation.isPending ? 'Sending...' : 'Add Friend'}
                </button>
              )}
            </div>
          )}
        </div>
      </Card>

      {/* Recent Posts */}
      <Card>
        <h3 className="text-lg font-semibold mb-4">Recent Posts</h3>
        {data.recent_posts && data.recent_posts.length > 0 ? (
          <div className="space-y-4">
            {data.recent_posts.map((post: any) => (
              <div key={post.id} className="border-b border-gray-200 pb-4 last:border-b-0">
                <p className="text-gray-700 mb-2">{post.content}</p>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span title={new Date(post.created_at).toLocaleString()}>
                    {getRelativeTime(new Date(post.created_at))}
                  </span>
                  <span>{post.likes_count || 0} likes</span>
                  <span>{post.comments_count || 0} comments</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-600">
            <p>No posts yet.</p>
          </div>
        )}
      </Card>
    </div>
  );
}

