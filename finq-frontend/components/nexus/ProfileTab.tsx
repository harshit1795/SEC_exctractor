'use client';

import { useState, useEffect } from 'react';
import { useUserProfile, useSendFriendRequest, useAcceptFriendRequest, useUserProfilePreferences, useUpdateUserProfile } from '@/lib/hooks/useNexus';
import { useAuth } from '@/lib/hooks/useAuth';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { getRelativeTime } from '@/lib/utils';

export function ProfileTab() {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';
  const { data, isLoading, error } = useUserProfile(userId);
  const { data: profilePrefs, isLoading: prefsLoading } = useUserProfilePreferences(userId);
  const updateProfileMutation = useUpdateUserProfile();
  const sendRequestMutation = useSendFriendRequest();
  const acceptRequestMutation = useAcceptFriendRequest();
  
  const [isEditing, setIsEditing] = useState(false);
  const [displayName, setDisplayName] = useState('');
  const [profilePictureUrl, setProfilePictureUrl] = useState('');
  const [useAliasAsDisplay, setUseAliasAsDisplay] = useState(false);

  // Sync form state with profile preferences when they load or change
  useEffect(() => {
    if (profilePrefs && !isEditing) {
      setDisplayName(profilePrefs.display_name || '');
      setProfilePictureUrl(profilePrefs.profile_picture_url || '');
      setUseAliasAsDisplay(profilePrefs.use_alias_as_display || false);
    }
  }, [profilePrefs, isEditing]);

  if (isLoading || prefsLoading) {
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

  const handleSaveProfile = async () => {
    try {
      await updateProfileMutation.mutateAsync({
        display_name: displayName.trim() || undefined,
        profile_picture_url: profilePictureUrl.trim() || undefined,
        use_alias_as_display: useAliasAsDisplay,
      });
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Failed to update profile. Please try again.');
    }
  };

  const handleCancelEdit = () => {
    if (profilePrefs) {
      setDisplayName(profilePrefs.display_name || '');
      setProfilePictureUrl(profilePrefs.profile_picture_url || '');
      setUseAliasAsDisplay(profilePrefs.use_alias_as_display || false);
    }
    setIsEditing(false);
  };

  // Determine display name and picture to show
  // Priority: alias (if enabled) > Firebase display name > email prefix
  const effectiveDisplayName = profilePrefs?.use_alias_as_display && profilePrefs?.display_name
    ? profilePrefs.display_name
    : (profilePrefs?.display_name || user?.displayName || user?.email?.split('@')[0] || 'User');
  const effectiveProfilePicture = profilePrefs?.profile_picture_url || user?.photoURL || `https://ui-avatars.com/api/?name=${encodeURIComponent(effectiveDisplayName)}`;

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <Card>
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-6 flex-1">
            <div className="flex-shrink-0">
              <img
                src={effectiveProfilePicture}
                alt={effectiveDisplayName}
                className="h-24 w-24 rounded-full"
              />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900">
                {effectiveDisplayName}
              </h2>
              <p className="text-gray-600">{user?.email}</p>
              {profilePrefs?.display_name && !profilePrefs.use_alias_as_display && (
                <p className="text-sm text-gray-500">Alias: {profilePrefs.display_name}</p>
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
          {!isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
            >
              Edit Profile
            </button>
          )}
        </div>
      </Card>

      {/* Profile Editing Form */}
      {isEditing && (
        <Card>
          <h3 className="text-lg font-semibold mb-4">Edit Profile</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Display Name (Alias)
              </label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Enter an alias name"
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              />
              <p className="mt-1 text-xs text-gray-500">
                This will be shown as your display name if enabled below
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Profile Picture URL
              </label>
              <input
                type="url"
                value={profilePictureUrl}
                onChange={(e) => setProfilePictureUrl(e.target.value)}
                placeholder="https://example.com/your-picture.jpg"
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              />
              <p className="mt-1 text-xs text-gray-500">
                Enter a URL to your profile picture
              </p>
              {profilePictureUrl && (
                <div className="mt-2">
                  <img
                    src={profilePictureUrl}
                    alt="Preview"
                    className="h-16 w-16 rounded-full border border-gray-300"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                </div>
              )}
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="useAlias"
                checked={useAliasAsDisplay}
                onChange={(e) => setUseAliasAsDisplay(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="useAlias" className="ml-2 text-sm text-gray-700">
                Use alias as display name (instead of real name)
              </label>
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                onClick={handleSaveProfile}
                disabled={updateProfileMutation.isPending}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {updateProfileMutation.isPending ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                onClick={handleCancelEdit}
                disabled={updateProfileMutation.isPending}
                className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </Card>
      )}

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

