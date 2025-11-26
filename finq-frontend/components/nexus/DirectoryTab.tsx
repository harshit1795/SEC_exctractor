'use client';

import { useState } from 'react';
import { useUserDirectory, useSendFriendRequest, useAcceptFriendRequest } from '@/lib/hooks/useNexus';
import { useAuth } from '@/lib/hooks/useAuth';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';

export function DirectoryTab() {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';
  const [searchTerm, setSearchTerm] = useState('');
  const { data, isLoading, error } = useUserDirectory(100, 0);
  const sendRequestMutation = useSendFriendRequest();
  const acceptRequestMutation = useAcceptFriendRequest();

  if (isLoading) {
    return <Loading message="Loading user directory..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load user directory" />;
  }

  const users = data?.users || [];
  
  // Filter users by search term
  const filteredUsers = users.filter((u: any) =>
    u.user_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSendFriendRequest = async (friendId: string) => {
    try {
      await sendRequestMutation.mutateAsync(friendId);
    } catch (error) {
      console.error('Failed to send friend request:', error);
    }
  };

  const handleAcceptRequest = async (friendId: string) => {
    try {
      await acceptRequestMutation.mutateAsync(friendId);
    } catch (error) {
      console.error('Failed to accept friend request:', error);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <h3 className="text-lg font-semibold mb-4">User Directory</h3>
        
        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search users by ID..."
            className="w-full rounded-md border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
          />
        </div>

        {/* User List */}
        {filteredUsers.length === 0 ? (
          <div className="text-center py-8 text-gray-600">
            <p>No users found.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredUsers.map((userItem: any) => {
              if (userItem.user_id === userId) return null; // Don't show current user
              
              return (
                <div
                  key={userItem.user_id}
                  className="flex items-center justify-between border-b border-gray-200 pb-4 last:border-b-0"
                >
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <img
                        src={`https://ui-avatars.com/api/?name=${userItem.user_id}`}
                        alt={userItem.user_id}
                        className="h-12 w-12 rounded-full"
                      />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{userItem.user_id}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span>{userItem.posts_count} posts</span>
                        <span>{userItem.friends_count} friends</span>
                        <span>{userItem.insights_count} insights</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    {userItem.is_friend ? (
                      <span className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-md">
                        Friends
                      </span>
                    ) : userItem.has_pending_request ? (
                      <button
                        onClick={() => handleAcceptRequest(userItem.user_id)}
                        disabled={acceptRequestMutation.isPending}
                        className="px-4 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                      >
                        {acceptRequestMutation.isPending ? 'Accepting...' : 'Accept Request'}
                      </button>
                    ) : (
                      <button
                        onClick={() => handleSendFriendRequest(userItem.user_id)}
                        disabled={sendRequestMutation.isPending}
                        className="px-4 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                      >
                        {sendRequestMutation.isPending ? 'Sending...' : 'Add Friend'}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
}

