import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/di/providers.dart';
import '../../auth/auth_providers.dart';

class DirectoryTab extends ConsumerStatefulWidget {
  const DirectoryTab({super.key});

  @override
  ConsumerState<DirectoryTab> createState() => _DirectoryTabState();
}

class _DirectoryTabState extends ConsumerState<DirectoryTab> {
  final _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authUserProvider).valueOrNull;

    if (user == null) {
      return const Center(
        child: Text('Please sign in to browse the directory'),
      );
    }

    final directory = ref.watch(_directoryProvider(_searchQuery));

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: 'Search users...',
              prefixIcon: const Icon(Icons.search),
              border: const OutlineInputBorder(),
              suffixIcon: _searchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        _searchController.clear();
                        setState(() => _searchQuery = '');
                      },
                    )
                  : null,
            ),
            onChanged: (value) {
              setState(() => _searchQuery = value);
            },
          ),
        ),
        Expanded(
          child: directory.when(
            data: (data) {
              final users = data['users'] as List? ?? [];
              
              if (users.isEmpty) {
                return Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.person_search, size: 64, color: Colors.grey),
                      const SizedBox(height: 16),
                      Text(
                        _searchQuery.isEmpty
                            ? 'No users in directory'
                            : 'No users found matching "$_searchQuery"',
                        style: const TextStyle(
                          fontSize: 16,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                );
              }

              return RefreshIndicator(
                onRefresh: () async {
                  ref.invalidate(_directoryProvider(_searchQuery));
                },
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: users.length,
                  itemBuilder: (context, index) {
                    final userItem = users[index] as Map<String, dynamic>;
                    return _UserCard(user: userItem);
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
                  Text('Error loading directory: $error'),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => ref.invalidate(_directoryProvider(_searchQuery)),
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

class _UserCard extends ConsumerStatefulWidget {
  const _UserCard({required this.user});

  final Map<String, dynamic> user;

  @override
  ConsumerState<_UserCard> createState() => _UserCardState();
}

class _UserCardState extends ConsumerState<_UserCard> {
  var _isSendingRequest = false;

  Future<void> _sendFriendRequest() async {
    setState(() => _isSendingRequest = true);

    try {
      final apiClient = ref.read(apiClientProvider);
      final friendUserId = widget.user['user_id'] ?? widget.user['id'];
      
      await apiClient.post(
        '/nexus/friends/request',
        body: {'friend_user_id': friendUserId},
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Friend request sent!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSendingRequest = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final displayName = widget.user['display_name'] ?? 'User';
    final isFriend = widget.user['is_friend'] ?? false;
    final hasPendingRequest = widget.user['has_pending_request'] ?? false;
    final profilePictureUrl = widget.user['profile_picture_url'] as String?;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.purple.shade100,
          child: profilePictureUrl != null && profilePictureUrl.isNotEmpty
              ? ClipOval(
                  child: Image.network(
                    profilePictureUrl,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) => Text(
                      displayName[0].toUpperCase(),
                      style: TextStyle(color: Colors.purple.shade700),
                    ),
                  ),
                )
              : Text(
                  displayName[0].toUpperCase(),
                  style: TextStyle(color: Colors.purple.shade700),
                ),
        ),
        title: Text(displayName),
        subtitle: isFriend
            ? const Text('Friends', style: TextStyle(color: Colors.green))
            : hasPendingRequest
                ? const Text('Request Pending', style: TextStyle(color: Colors.orange))
                : null,
        trailing: isFriend
            ? const Icon(Icons.check_circle, color: Colors.green)
            : hasPendingRequest
                ? const Icon(Icons.pending, color: Colors.orange)
                : IconButton(
                    icon: _isSendingRequest
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.person_add),
                    onPressed: _isSendingRequest ? null : _sendFriendRequest,
                  ),
      ),
    );
  }
}

// Provider for directory
final _directoryProvider = FutureProvider.family<Map<String, dynamic>, String>(
  (ref, searchQuery) async {
    final user = ref.watch(authUserProvider).valueOrNull;
    if (user == null) return {'users': []};
    
    final apiClient = ref.watch(apiClientProvider);
    final queryParams = <String, dynamic>{
      'user_id': user.uid,
    };
    
    if (searchQuery.isNotEmpty) {
      queryParams['search'] = searchQuery;
    }
    
    final response = await apiClient.get(
      '/nexus/users/directory',
      queryParameters: queryParams,
    );
    return response.data as Map<String, dynamic>;
  },
);
