import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'tabs/feed_tab.dart';
import 'tabs/profile_tab.dart';
import 'tabs/friends_tab.dart';
import 'tabs/directory_tab.dart';

class NexusPageEnhanced extends ConsumerStatefulWidget {
  const NexusPageEnhanced({super.key});

  @override
  ConsumerState<NexusPageEnhanced> createState() => _NexusPageEnhancedState();
}

class _NexusPageEnhancedState extends ConsumerState<NexusPageEnhanced> {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: DefaultTabController(
        length: 4,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  Icon(Icons.people, size: 28, color: Colors.purple.shade700),
                  const SizedBox(width: 12),
                  const Text(
                    'Nexus Community',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            TabBar(
              labelColor: Theme.of(context).colorScheme.primary,
              unselectedLabelColor: Theme.of(context).colorScheme.onSurfaceVariant,
              indicatorColor: Theme.of(context).colorScheme.primary,
              tabs: const [
                Tab(text: 'Feed', icon: Icon(Icons.dynamic_feed)),
                Tab(text: 'Profile', icon: Icon(Icons.person)),
                Tab(text: 'Friends', icon: Icon(Icons.group)),
                Tab(text: 'Directory', icon: Icon(Icons.explore)),
              ],
            ),
            const Expanded(
              child: TabBarView(
                children: [
                  FeedTab(),
                  ProfileTab(),
                  FriendsTab(),
                  DirectoryTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
