import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/di/providers.dart';
import '../../../core/widgets/empty_state.dart';
import '../../auth/auth_providers.dart';

class FeedTab extends ConsumerStatefulWidget {
  const FeedTab({super.key});

  @override
  ConsumerState<FeedTab> createState() => _FeedTabState();
}

class _FeedTabState extends ConsumerState<FeedTab> {
  final _contentController = TextEditingController();
  var _isPosting = false;

  @override
  void dispose() {
    _contentController.dispose();
    super.dispose();
  }

  Future<void> _createPost() async {
    final content = _contentController.text.trim();
    if (content.isEmpty) return;

    setState(() => _isPosting = true);

    try {
      final apiClient = ref.read(apiClientProvider);
      final user = ref.read(authUserProvider).valueOrNull;
      if (user == null) return;

      await apiClient.post(
        '/nexus/posts',
        body: {
          'content': content,
          'media_urls': [],
          'media_type': null,
          'is_shared_insight': false,
          'insight_id': null,
          'tags': [],
        },
        queryParameters: {'user_id': user.uid},
      );

      _contentController.clear();
      // Refresh feed
      ref.invalidate(_feedProvider);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Post created successfully!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error creating post: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isPosting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authUserProvider).valueOrNull;
    final feed = ref.watch(_feedProvider);

    if (user == null) {
      return const Center(
        child: Text('Please sign in to view the feed'),
      );
    }

    return Column(
      children: [
        // Create Post Section
        Card(
          margin: const EdgeInsets.all(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Share with the community',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _contentController,
                  decoration: const InputDecoration(
                    hintText: 'What\'s on your mind?',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 3,
                  enabled: !_isPosting,
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    ElevatedButton.icon(
                      onPressed: _isPosting ? null : _createPost,
                      icon: _isPosting
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.send),
                      label: Text(_isPosting ? 'Posting...' : 'Post'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        // Feed List
        Expanded(
          child: feed.when(
            data: (data) {
              final posts = data['posts'] as List? ?? [];
              
              if (posts.isEmpty) {
                return const EmptyState(
                  icon: Icons.speaker_notes_off,
                  title: 'Nothing to see here',
                  message: 'No posts yet. Be the first to share your insights!',
                );
              }

              return RefreshIndicator(
                onRefresh: () async {
                  ref.invalidate(_feedProvider);
                },
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: posts.length,
                  itemBuilder: (context, index) {
                    final post = posts[index] as Map<String, dynamic>;
                    return _PostCard(post: post);
                  },
                ),
              );
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, _) => Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 48, color: Colors.red),
                  const SizedBox(height: 16),
                  Text('Error loading feed: $error'),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => ref.invalidate(_feedProvider),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _PostCard extends StatelessWidget {
  const _PostCard({required this.post});

  final Map<String, dynamic> post;

  @override
  Widget build(BuildContext context) {
    final author = post['author'] as Map<String, dynamic>?;
    final displayName = author?['display_name'] ?? 'Anonymous';
    final profilePictureUrl = author?['profile_picture_url'] as String?;
    final content = post['content'] ?? '';
    final createdAt = post['created_at'] as String?;
    final likesCount = post['likes_count'] ?? 0;
    final commentsCount = post['comments_count'] ?? 0;

    DateTime? postDate;
    if (createdAt != null) {
      try {
        postDate = DateTime.parse(createdAt).toLocal();
      } catch (_) {}
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  child: profilePictureUrl != null && profilePictureUrl.isNotEmpty
                      ? ClipOval(
                          child: Image.network(
                            profilePictureUrl,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) =>
                                Text(displayName[0].toUpperCase()),
                          ),
                        )
                      : Text(displayName[0].toUpperCase()),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        displayName,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (postDate != null)
                        Text(
                          _formatDate(postDate),
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade600,
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(content),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(Icons.favorite_border, size: 20, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text('$likesCount', style: TextStyle(color: Colors.grey.shade600)),
                const SizedBox(width: 16),
                Icon(Icons.comment_outlined, size: 20, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text('$commentsCount', style: TextStyle(color: Colors.grey.shade600)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.isNegative || difference.inSeconds < 60) {
      return 'just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      // Use locale-aware date formatting
      return DateFormat.yMMMd().add_jm().format(date);
    }
  }
}

// Provider for feed data
final _feedProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  final user = await ref.watch(authUserProvider.future);
  
  if (user == null) {
    throw Exception('User not authenticated');
  }
  
  final response = await apiClient.get(
    '/nexus/posts/feed',
    queryParameters: {'user_id': user.uid},
  );
  return response.data as Map<String, dynamic>;
});
