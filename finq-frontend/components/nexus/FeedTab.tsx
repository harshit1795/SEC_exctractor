'use client';

import { useState } from 'react';
import { useFeed, useCreatePost, useLikePost, useUnlikePost, useAddComment } from '@/lib/hooks/useNexus';
import { useAuth } from '@/lib/hooks/useAuth';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { Card } from '@/components/shared/Card';
import { getRelativeTime } from '@/lib/utils';

export function FeedTab() {
  const { user } = useAuth();
  const { data, isLoading, error } = useFeed(20);
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
    } catch (error) {
      console.error('Failed to toggle like:', error);
    }
  };

  const handleAddComment = async (postId: string) => {
    const content = commentContent[postId];
    if (!content?.trim()) return;
    
    try {
      await addCommentMutation.mutateAsync({ postId, content });
      setCommentContent({ ...commentContent, [postId]: '' });
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };

  if (isLoading) {
    return <Loading message="Loading feed..." />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load feed" />;
  }

  const posts = data?.posts || [];

  return (
    <div className="space-y-6">
      <Card>
        <h3 className="text-lg font-semibold mb-4">My Feed</h3>
        
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
          <div className="text-center py-8 text-gray-600">
            <p>Your feed is empty. Add some friends to see their posts!</p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {posts.map((post: any) => {
            const isLiked = post.likes?.some((like: any) => like.user_id === user?.uid) || false;
            const likeCount = post.likes?.length || 0;
            const commentCount = post.comments?.length || 0;
            
            return (
              <Card key={post.id}>
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <img
                      src={post.author?.profile_picture_url || `https://ui-avatars.com/api/?name=${post.author?.display_name || 'User'}`}
                      alt={post.author?.display_name || 'User'}
                      className="h-10 w-10 rounded-full"
                    />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-semibold text-gray-900">
                        {post.author?.display_name || 'Unknown User'}
                      </span>
                      <span className="text-sm text-gray-500">
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
                        className={`flex items-center space-x-1 text-sm ${
                          isLiked ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'
                        }`}
                      >
                        <span>{isLiked ? '❤️' : '🤍'}</span>
                        <span>{likeCount}</span>
                      </button>
                      
                      <span className="text-sm text-gray-600">{commentCount} comments</span>
                    </div>
                    
                    {/* Comments */}
                    {post.comments && post.comments.length > 0 && (
                      <div className="mt-4 space-y-2 border-t border-gray-200 pt-3">
                        {post.comments.map((comment: any) => (
                          <div key={comment.id} className="flex items-start space-x-2">
                            <img
                              src={comment.author?.profile_picture_url || `https://ui-avatars.com/api/?name=${comment.author?.display_name || 'User'}`}
                              alt={comment.author?.display_name || 'User'}
                              className="h-6 w-6 rounded-full"
                            />
                            <div className="flex-1">
                              <span className="font-semibold text-sm text-gray-900">
                                {comment.author?.display_name || 'Unknown User'}
                              </span>
                              <span className="text-sm text-gray-700 ml-2">{comment.content}</span>
                            </div>
                          </div>
                        ))}
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
                      >
                        Comment
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

