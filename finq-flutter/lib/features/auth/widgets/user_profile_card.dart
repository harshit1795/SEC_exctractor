import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../auth_providers.dart';
import '../auth_controller.dart';

class UserProfileCard extends ConsumerWidget {
  const UserProfileCard({
    super.key,
    required this.user,
    this.showSignOut = true,
  });

  final User user;
  final bool showSignOut;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final displayName = user.displayName ?? 'User';
    final email = user.email ?? '';
    final photoUrl = user.photoURL;
    final creationTime = user.metadata.creationTime;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                if (photoUrl != null && photoUrl.isNotEmpty)
                  CircleAvatar(
                    backgroundImage: NetworkImage(photoUrl),
                    backgroundColor: Colors.grey.shade200,
                    radius: 32,
                  )
                else
                  CircleAvatar(
                    backgroundColor: Colors.grey.shade200,
                    radius: 32,
                    child: Text(
                      displayName.isNotEmpty ? displayName[0].toUpperCase() : '?',
                      style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                    ),
                  ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        displayName,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (email.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          email,
                          style: TextStyle(
                            color: Colors.grey.shade600,
                            fontSize: 14,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                      if (creationTime != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          'Member since ${DateFormat.yMMMd().format(creationTime)}',
                          style: TextStyle(
                            color: Colors.grey.shade500,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
            if (showSignOut) ...[
                const SizedBox(height: 16),
                const Divider(),
                const SizedBox(height: 8),
                SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                    onPressed: () => ref.read(authControllerProvider).signOut(),
                    icon: const Icon(Icons.logout),
                    label: const Text('Sign Out'),
                    style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.red.shade700,
                    side: BorderSide(color: Colors.red.shade200),
                    ),
                ),
                ),
            ],
          ],
        ),
      ),
    );
  }
}
