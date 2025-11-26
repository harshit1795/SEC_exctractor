'use client';

import { useUserProfile, useSendFriendRequest, useAcceptFriendRequest } from '@/lib/hooks/useNexus';
import { useAuth } from '@/lib/hooks/useAuth';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { getRelativeTime } from '@/lib/utils';

export function ProfileTab() {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';
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
          <p>No profile data available.</p>
        </div>
      </Card>
    );
  }

  const handleSendFriendRequest = async () => {
    try {
      await sendRequestMutation.mutateAsync(userId);
    } catch (error) {
      console.error('Failed to send friend request:', error);
    }
  };

  const handleAcceptRequest = async () => {
    try {
      await acceptRequestMutation.mutateAsync(userId);
    } catch (error) {
      console.error('Failed to accept friend request:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <Card>
        <div className="flex items-center space-x-6">
          <div className="flex-shrink-0">
            <img
              src={user?.photoURL || `https://ui-avatars.com/api/?name=${user?.displayName || user?.email || 'User'}`}
              alt={user?.displayName || 'User'}
              className="h-24 w-24 rounded-full"
            />
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900">
              {user?.displayName || user?.email || 'User'}
            </h2>
            <p className="text-gray-600">{user?.email}</p>
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
                  <span>{getRelativeTime(new Date(post.created_at))}</span>
                  <span>{post.likes_count} likes</span>
                  <span>{post.comments_count} comments</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-600">
            <p>No posts yet. Start sharing your insights!</p>
          </div>
        )}
      </Card>
    </div>
  );
}

