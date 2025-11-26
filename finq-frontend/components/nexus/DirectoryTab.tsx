'use client';

import { useState } from 'react';
import { useUserDirectory, useSendFriendRequest, useAcceptFriendRequest } from '@/lib/hooks/useNexus';
import { useAuth } from '@/lib/hooks/useAuth';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { UserProfileView } from './UserProfileView';

export function DirectoryTab() {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
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
  
  // Filter users by search term (search both user_id, display_name, and firebase_display_name)
  const filteredUsers = users.filter((u: any) => {
    if (u.user_id === userId) return false; // Don't show current user
    const searchLower = searchTerm.toLowerCase();
    return (
      u.user_id.toLowerCase().includes(searchLower) ||
      (u.display_name && u.display_name.toLowerCase().includes(searchLower)) ||
      (u.firebase_display_name && u.firebase_display_name.toLowerCase().includes(searchLower))
    );
  });

  const handleSendFriendRequest = async (friendId: string) => {
    try {
      await sendRequestMutation.mutateAsync(friendId);
      // Show success feedback (you could add a toast notification here)
      alert('Friend request sent!');
    } catch (error: any) {
      console.error('Failed to send friend request:', error);
      alert(error?.response?.data?.detail || 'Failed to send friend request. Please try again.');
    }
  };

  const handleAcceptRequest = async (friendId: string) => {
    try {
      await acceptRequestMutation.mutateAsync(friendId);
      alert('Friend request accepted! You can now see their posts in your feed.');
    } catch (error: any) {
      console.error('Failed to accept friend request:', error);
      alert(error?.response?.data?.detail || 'Failed to accept friend request. Please try again.');
    }
  };

  // If a user is selected, show their profile
  if (selectedUserId) {
    return (
      <div>
        <UserProfileView 
          userId={selectedUserId} 
          onClose={() => setSelectedUserId(null)}
        />
      </div>
    );
  }

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
            placeholder="Search users by name or ID..."
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
              
              // Use display_name (alias) if set, otherwise use firebase_display_name, otherwise user_id
              const displayName = userItem.display_name || userItem.firebase_display_name || userItem.user_id;
              const profilePicture = userItem.profile_picture_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}`;
              
              return (
                <div
                  key={userItem.user_id}
                  className="flex items-center justify-between border-b border-gray-200 pb-4 last:border-b-0 hover:bg-gray-50 p-2 rounded-md transition-colors cursor-pointer"
                  onClick={() => setSelectedUserId(userItem.user_id)}
                >
                  <div className="flex items-center space-x-4 flex-1">
                    <div className="flex-shrink-0">
                      <img
                        src={profilePicture}
                        alt={displayName}
                        className="h-12 w-12 rounded-full"
                      />
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900 hover:text-blue-600 transition-colors">
                        {displayName}
                      </p>
                      {!userItem.display_name && (
                        <p className="text-xs text-gray-500">User ID: {userItem.user_id}</p>
                      )}
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span>{userItem.posts_count} posts</span>
                        <span>{userItem.friends_count} friends</span>
                        <span>{userItem.insights_count} insights</span>
                      </div>
                    </div>
                  </div>
                  <div onClick={(e) => e.stopPropagation()} className="flex items-center space-x-2">
                    {userItem.is_friend ? (
                      <span className="px-4 py-2 text-sm text-green-700 bg-green-100 rounded-md flex items-center space-x-1">
                        <span>✓</span>
                        <span>Friends</span>
                      </span>
                    ) : userItem.has_pending_request ? (
                      userItem.pending_request_sent_by_me ? (
                        <span className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md flex items-center space-x-1">
                          <span>⏳</span>
                          <span>Request sent</span>
                        </span>
                      ) : (
                        <button
                          onClick={() => handleAcceptRequest(userItem.user_id)}
                          disabled={acceptRequestMutation.isPending}
                          className="px-4 py-2 text-sm text-white bg-green-600 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                        >
                          {acceptRequestMutation.isPending ? 'Accepting...' : 'Accept Request'}
                        </button>
                      )
                    ) : (
                      <button
                        onClick={() => handleSendFriendRequest(userItem.user_id)}
                        disabled={sendRequestMutation.isPending}
                        className="px-4 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
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

