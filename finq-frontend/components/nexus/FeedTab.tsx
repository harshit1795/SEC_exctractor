'use client';

import { useState, useEffect } from 'react';
import { useFeed, useCreatePost, useLikePost, useUnlikePost, useAddComment } from '@/lib/hooks/useNexus';
import { useAuth } from '@/lib/hooks/useAuth';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { getRelativeTime } from '@/lib/utils';

export function FeedTab() {
  const { user, loading: authLoading } = useAuth();
  const { data, isLoading, error, isError } = useFeed(20);
  const createPostMutation = useCreatePost();
  const likePostMutation = useLikePost();
  const unlikePostMutation = useUnlikePost();
  const addCommentMutation = useAddComment();
  
  const [postContent, setPostContent] = useState('');
  const [commentContent, setCommentContent] = useState<Record<string, string>>({});

  const handleCreatePost = async () => {
    if (!postContent.trim()) return;
    
    try {
      await createPostMutation.mutateAsync({ content: postContent });
      setPostContent('');
    } catch (error) {
      console.error('Failed to create post:', error);
    }
  };

  const handleLike = async (postId: string, isLiked: boolean) => {
    try {
      if (isLiked) {
        await unlikePostMutation.mutateAsync(postId);
      } else {
        await likePostMutation.mutateAsync(postId);
      }
    } catch (error: any) {
      console.error('Failed to toggle like:', error);
      alert(error?.response?.data?.detail || 'Failed to update like. Please try again.');
    }
  };

  const handleAddComment = async (postId: string) => {
    const content = commentContent[postId];
    if (!content?.trim()) return;
    
    try {
      await addCommentMutation.mutateAsync({ postId, content });
      setCommentContent({ ...commentContent, [postId]: '' });
    } catch (error: any) {
      console.error('Failed to add comment:', error);
      alert(error?.response?.data?.detail || 'Failed to add comment. Please try again.');
    }
  };

  // If no user, show message
  if (!authLoading && !user) {
    return (
      <Card>
        <div className="text-center py-8 text-gray-600">
          <p>Please log in to view your feed.</p>
        </div>
      </Card>
    );
  }

  // Show loading if auth is still loading or feed is loading
  if (authLoading || isLoading) {
    return <Loading message="Loading feed..." />;
  }

  // Show error if there's an error
  if (isError || error) {
    console.error('Feed error details:', error);
    return <ErrorDisplay error={error} message="Failed to load feed. Please try refreshing the page." />;
  }

  // Get posts from data, default to empty array
  const posts = data?.posts || [];

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">My Feed</h3>
          <p className="text-sm text-gray-500">
            Posts from your friends and your own posts
          </p>
        </div>
        
        {/* Create Post Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleCreatePost();
          }}
          className="mb-6"
        >
          <textarea
            value={postContent}
            onChange={(e) => setPostContent(e.target.value)}
            placeholder="What's on your mind?"
            className="w-full rounded-md border border-gray-300 px-4 py-2 mb-2 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
            rows={3}
          />
          <button
            type="submit"
            disabled={!postContent.trim() || createPostMutation.isPending}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {createPostMutation.isPending ? 'Posting...' : 'Post'}
          </button>
        </form>
      </Card>

      {/* Feed Posts */}
      {posts.length === 0 ? (
        <Card>
          <div className="text-center py-8">
            <p className="text-gray-600 mb-2">Your feed is empty.</p>
            <p className="text-sm text-gray-500 mb-4">
              Add some friends from the User Directory to see their posts here!
            </p>
            <a
              href="#directory"
              onClick={(e) => {
                e.preventDefault();
                window.location.hash = 'directory';
                // Trigger a custom event to switch tabs
                window.dispatchEvent(new CustomEvent('switchNexusTab', { detail: 'directory' }));
              }}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium underline"
            >
              Go to User Directory →
            </a>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {posts.map((post: any) => {
            const isLiked = post.liked || false;
            const likeCount = post.likes_count || 0;
            const commentCount = post.comments_count || 0;
            
            // Use author info from backend - backend provides display_name which respects user preferences
            // For own posts, show "You", otherwise use the display_name from backend
            const authorName = post.author_id === user?.uid 
              ? 'You'
              : (post.author?.display_name 
                || post.author?.firebase_display_name 
                || post.author_id 
                || 'Unknown User');
            
            const authorPhoto = post.author?.profile_picture_url 
              || post.author?.firebase_photo_url
              || (post.author_id === user?.uid
                ? user?.photoURL 
                : null)
              || `https://ui-avatars.com/api/?name=${encodeURIComponent(authorName)}`;
            
            return (
              <Card key={post.id}>
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <img
                      src={authorPhoto}
                      alt={authorName}
                      className="h-10 w-10 rounded-full"
                    />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-semibold text-gray-900">
                        {authorName}
                      </span>
                      <span className="text-xs text-gray-400">•</span>
                      <span className="text-sm text-gray-500" title={new Date(post.created_at).toLocaleString()}>
                        {getRelativeTime(new Date(post.created_at))}
                      </span>
                    </div>
                    
                    <p className="text-gray-700 mb-4">{post.content}</p>
                    
                    {/* Media */}
                    {post.media_urls && post.media_urls.length > 0 && (
                      <div className="mb-4 space-y-2">
                        {post.media_urls.map((url: string, idx: number) => (
                          <img
                            key={idx}
                            src={url}
                            alt={`Post media ${idx + 1}`}
                            className="max-w-full h-auto rounded-lg"
                          />
                        ))}
                      </div>
                    )}
                    
                    {/* Actions */}
                    <div className="flex items-center space-x-4 border-t border-gray-200 pt-3">
                      <button
                        onClick={() => handleLike(post.id, isLiked)}
                        disabled={likePostMutation.isPending || unlikePostMutation.isPending}
                        className={`flex items-center space-x-1 text-sm transition-colors ${
                          isLiked 
                            ? 'text-red-600 hover:text-red-700' 
                            : 'text-gray-600 hover:text-red-600'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                        title={isLiked ? 'Unlike this post' : 'Like this post'}
                      >
                        <span className="text-lg">{isLiked ? '❤️' : '🤍'}</span>
                        <span className="font-medium">{likeCount}</span>
                      </button>
                      
                      <span className="text-sm text-gray-600 flex items-center space-x-1">
                        <span>💬</span>
                        <span>{commentCount} {commentCount === 1 ? 'comment' : 'comments'}</span>
                      </span>
                    </div>
                    
                    {/* Comments */}
                    {post.comments && post.comments.length > 0 && (
                      <div className="mt-4 space-y-2 border-t border-gray-200 pt-3">
                        {post.comments.map((comment: any) => {
                          // Use author info from backend (priority: display_name > firebase_display_name > user_id)
                          const commentAuthorName = comment.author?.display_name
                            || comment.author?.firebase_display_name
                            || (comment.user_id === user?.uid ? 'You' : comment.user_id || 'Unknown User');
                          
                          const commentAuthorPhoto = comment.author?.profile_picture_url
                            || comment.author?.firebase_photo_url
                            || (comment.user_id === user?.uid ? user?.photoURL : null)
                            || `https://ui-avatars.com/api/?name=${encodeURIComponent(commentAuthorName)}`;
                          
                          return (
                            <div key={comment.id} className="flex items-start space-x-2">
                              <img
                                src={commentAuthorPhoto}
                                alt={commentAuthorName}
                                className="h-6 w-6 rounded-full"
                              />
                              <div className="flex-1">
                                <div className="flex items-center space-x-2">
                                  <span className="font-semibold text-sm text-gray-900">
                                    {commentAuthorName}
                                  </span>
                                  {comment.created_at && (
                                    <>
                                      <span className="text-xs text-gray-400">•</span>
                                      <span 
                                        className="text-xs text-gray-500"
                                        title={new Date(comment.created_at).toLocaleString()}
                                      >
                                        {getRelativeTime(new Date(comment.created_at))}
                                      </span>
                                    </>
                                  )}
                                </div>
                                <span className="text-sm text-gray-700 block mt-1">{comment.content}</span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                    
                    {/* Add Comment */}
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        handleAddComment(post.id);
                      }}
                      className="mt-3 flex space-x-2"
                    >
                      <input
                        type="text"
                        value={commentContent[post.id] || ''}
                        onChange={(e) => setCommentContent({ ...commentContent, [post.id]: e.target.value })}
                        placeholder="Add a comment..."
                        className="flex-1 rounded-md border border-gray-300 px-3 py-1 text-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                      />
                      <button
                        type="submit"
                        disabled={!commentContent[post.id]?.trim() || addCommentMutation.isPending}
                        className="rounded-md bg-blue-600 px-3 py-1 text-sm text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                        title="Add a comment to this post"
                      >
                        {addCommentMutation.isPending ? 'Posting...' : 'Comment'}
                      </button>
                    </form>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}

