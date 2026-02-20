import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/di/providers.dart';
import '../../auth/auth_providers.dart';

class FriendsTab extends ConsumerWidget {
  const FriendsTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authUserProvider).valueOrNull;

    if (user == null) {
      return const Center(
        child: Text('Please sign in to view friends'),
      );
    }

    final friends = ref.watch(_friendsProvider);
    final requests = ref.watch(_friendRequestsProvider);

    return DefaultTabController(
      length: 2,
      child: Column(
        children: [
          const TabBar(
            labelColor: Colors.indigo,
            unselectedLabelColor: Colors.black54,
            tabs: [
              Tab(text: 'Friends'),
              Tab(text: 'Requests'),
            ],
          ),
          Expanded(
            child: TabBarView(
              children: [
                // Friends List
                friends.when(
                  data: (data) {
                    final friendsList = data['friends'] as List? ?? [];
                    
                    if (friendsList.isEmpty) {
                      return const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.people_outline, size: 64, color: Colors.grey),
                            SizedBox(height: 16),
                            Text(
                              'No friends yet',
                              style: TextStyle(
                                fontSize: 18,
                                color: Colors.grey,
                              ),
                            ),
                            SizedBox(height: 8),
                            Text(
                              'Visit the Directory to find people',
                              style: TextStyle(color: Colors.grey),
                            ),
                          ],
                        ),
                      );
                    }

                    return RefreshIndicator(
                      onRefresh: () async {
                        ref.invalidate(_friendsProvider);
                      },
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: friendsList.length,
                        itemBuilder: (context, index) {
                          final friend = friendsList[index] as Map<String, dynamic>;
                          final displayName = friend['display_name'] ?? 'User';
                          final profilePictureUrl = friend['profile_picture_url'] as String?;
                          
                          return Card(
                            margin: const EdgeInsets.only(bottom: 8),
                            child: ListTile(
                              leading: CircleAvatar(
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
                              title: Text(displayName),
                              trailing: IconButton(
                                icon: const Icon(Icons.message),
                                onPressed: () {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('Messaging coming soon!'),
                                    ),
                                  );
                                },
                              ),
                            ),
                          );
                        },
                      ),
                    );
                  },
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (error, _) => Center(
                    child: Text('Error loading friends: $error'),
                  ),
                ),
                // Friend Requests
                requests.when(
                  data: (data) {
                    final requestsList = data['requests'] as List? ?? [];
                    
                    if (requestsList.isEmpty) {
                      return const Center(
                        child: Text('No friend requests'),
                      );
                    }

                    return RefreshIndicator(
                      onRefresh: () async {
                        ref.invalidate(_friendRequestsProvider);
                      },
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: requestsList.length,
                        itemBuilder: (context, index) {
                          final request = requestsList[index] as Map<String, dynamic>;
                          final displayName = request['display_name'] ?? 'User';
                          final friendId = request['id'] ?? request['friend_id'];
                          final profilePictureUrl = request['profile_picture_url'] as String?;
                          
                          return Card(
                            margin: const EdgeInsets.only(bottom: 8),
                            child: ListTile(
                              leading: CircleAvatar(
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
                              title: Text(displayName),
                              trailing: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  IconButton(
                                    icon: const Icon(Icons.check, color: Colors.green),
                                    onPressed: () async {
                                      try {
                                        final apiClient = ref.read(apiClientProvider);
                                        await apiClient.post('/nexus/friends/$friendId/accept');
                                        ref.invalidate(_friendRequestsProvider);
                                        ref.invalidate(_friendsProvider);
                                      } catch (e) {
                                        if (context.mounted) {
                                          ScaffoldMessenger.of(context).showSnackBar(
                                            SnackBar(content: Text('Error: $e')),
                                          );
                                        }
                                      }
                                    },
                                  ),
                                  IconButton(
                                    icon: const Icon(Icons.close, color: Colors.red),
                                    onPressed: () {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        const SnackBar(
                                          content: Text('Decline coming soon!'),
                                        ),
                                      );
                                    },
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    );
                  },
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (error, _) => Center(
                    child: Text('Error loading requests: $error'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Providers
final _friendsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final user = ref.watch(authUserProvider).valueOrNull;
  if (user == null) return {'friends': []};
  
  final apiClient = ref.watch(apiClientProvider);
  final response = await apiClient.get(
    '/nexus/friends',
    queryParameters: {'user_id': user.uid},
  );
  return response.data as Map<String, dynamic>;
});

final _friendRequestsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final user = ref.watch(authUserProvider).valueOrNull;
  if (user == null) return {'requests': []};
  
  final apiClient = ref.watch(apiClientProvider);
  final response = await apiClient.get(
    '/nexus/friends/requests',
    queryParameters: {'user_id': user.uid},
  );
  return response.data as Map<String, dynamic>;
});
