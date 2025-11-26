'use client';

import { useFriends, useFriendRequests, useAcceptFriendRequest, useUserProfile } from '@/lib/hooks/useNexus';
import { useAuth } from '@/lib/hooks/useAuth';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { useState } from 'react';

function FriendItem({ friend, userId }: { friend: any; userId: string }) {
  // Get the friend's user ID (could be in friend_id or user_id depending on direction)
  const friendId = friend.friend_id === userId ? friend.user_id : friend.friend_id;
  // Use display info from backend if available, otherwise fetch profile
  const displayName = friend.display_name || friend.firebase_display_name || friendId;
  const profilePicture = friend.profile_picture_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}`;
  
  return (
    <div
      className="flex items-center justify-between border-b border-gray-200 pb-4 last:border-b-0 hover:bg-gray-50 p-2 rounded-md transition-colors cursor-pointer"
      onClick={() => {
        // Navigate to friend's profile
        window.location.hash = 'directory';
        window.dispatchEvent(new CustomEvent('switchNexusTab', { detail: 'directory' }));
        // Store friend ID for profile view
        setTimeout(() => {
          window.dispatchEvent(new CustomEvent('viewUserProfile', { detail: friendId }));
        }, 100);
      }}
    >
      <div className="flex items-center space-x-4">
        <div className="flex-shrink-0">
          <img
            src={profilePicture}
            alt={displayName}
            className="h-12 w-12 rounded-full"
          />
        </div>
        <div>
          <p className="font-semibold text-gray-900">{displayName}</p>
          <p className="text-sm text-gray-600">
            Friends since {new Date(friend.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>
    </div>
  );
}

export function FriendsTab() {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';
  const [activeTab, setActiveTab] = useState<'friends' | 'requests'>('friends');
  const { data: friendsData, isLoading: friendsLoading, error: friendsError } = useFriends();
  const { data: requestsData, isLoading: requestsLoading, error: requestsError } = useFriendRequests();
  const acceptRequestMutation = useAcceptFriendRequest();

  const handleAcceptRequest = async (friendId: string) => {
    try {
      await acceptRequestMutation.mutateAsync(friendId);
    } catch (error) {
      console.error('Failed to accept friend request:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex space-x-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('friends')}
          className={`px-4 py-2 font-semibold border-b-2 transition-colors ${
            activeTab === 'friends'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Friends ({friendsData?.count || 0})
        </button>
        <button
          onClick={() => setActiveTab('requests')}
          className={`px-4 py-2 font-semibold border-b-2 transition-colors ${
            activeTab === 'requests'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Requests ({requestsData?.count || 0})
        </button>
      </div>

      {/* Friends List */}
      {activeTab === 'friends' && (
        <Card>
          <h3 className="text-lg font-semibold mb-4">My Friends</h3>
          {friendsLoading ? (
            <Loading message="Loading friends..." />
          ) : friendsError ? (
            <ErrorDisplay error={friendsError} message="Failed to load friends" />
          ) : friendsData?.friends && friendsData.friends.length > 0 ? (
            <div className="space-y-4">
              {friendsData.friends.map((friend: any) => (
                <FriendItem 
                  key={friend.id} 
                  friend={friend}
                  userId={userId}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-600">
              <p>You don't have any friends yet. Check out the User Directory to add some!</p>
            </div>
          )}
        </Card>
      )}

      {/* Friend Requests */}
      {activeTab === 'requests' && (
        <Card>
          <h3 className="text-lg font-semibold mb-4">Friend Requests</h3>
          {requestsLoading ? (
            <Loading message="Loading friend requests..." />
          ) : requestsError ? (
            <ErrorDisplay error={requestsError} message="Failed to load friend requests" />
          ) : requestsData?.friends && requestsData.friends.length > 0 ? (
            <div className="space-y-4">
              {requestsData.friends.map((request: any) => {
                // Get display info from backend (user_id is the requester)
                const requesterId = request.user_id;
                const displayName = request.display_name || request.firebase_display_name || requesterId;
                const profilePicture = request.profile_picture_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}`;
                
                return (
                  <div
                    key={request.id}
                    className="flex items-center justify-between border-b border-gray-200 pb-4 last:border-b-0 hover:bg-gray-50 p-2 rounded-md transition-colors"
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
                        <p className="font-semibold text-gray-900">{displayName}</p>
                        {request.firebase_display_name && displayName !== request.firebase_display_name && (
                          <p className="text-xs text-gray-500">{request.firebase_display_name}</p>
                        )}
                        <p className="text-sm text-gray-600">
                          Sent {new Date(request.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleAcceptRequest(requesterId)}
                      disabled={acceptRequestMutation.isPending}
                      className="px-4 py-2 text-sm text-white bg-green-600 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                    >
                      {acceptRequestMutation.isPending ? 'Accepting...' : 'Accept'}
                    </button>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-600">
              <p>No pending friend requests.</p>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

