import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_providers.dart';
import 'nexus_feed_controller.dart';
import 'nexus_feed_state.dart';

final nexusFeedControllerProvider =
    StateNotifierProvider<NexusFeedController, NexusFeedState>((ref) {
  final user = ref.watch(authUserProvider).valueOrNull;
  return NexusFeedController(userId: user?.uid ?? 'anonymous');
});

class NexusPage extends ConsumerStatefulWidget {
  const NexusPage({super.key});

  @override
  ConsumerState<NexusPage> createState() => _NexusPageState();
}

class _NexusPageState extends ConsumerState<NexusPage> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(nexusFeedControllerProvider.notifier).connect();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(nexusFeedControllerProvider);
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Nexus Feed',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _StatusChip(isConnected: state.isConnected),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: state.isConnected
                      ? ref.read(nexusFeedControllerProvider.notifier).disconnect
                      : ref.read(nexusFeedControllerProvider.notifier).connect,
                  child: Text(state.isConnected ? 'Disconnect' : 'Connect'),
                ),
                const SizedBox(width: 8),
                OutlinedButton(
                  onPressed: state.isConnected
                      ? ref.read(nexusFeedControllerProvider.notifier).sendPing
                      : null,
                  child: const Text('Ping'),
                ),
              ],
            ),
            if (state.error != null) ...[
              const SizedBox(height: 12),
              Text(
                state.error!,
                style: TextStyle(color: Colors.red.shade700),
              ),
            ],
            const SizedBox(height: 16),
            Expanded(
              child: state.messages.isEmpty
                  ? const Center(child: Text('No messages yet.'))
                  : ListView.builder(
                      itemCount: state.messages.length,
                      itemBuilder: (context, index) {
                        final message = state.messages[index];
                        return _MessageCard(message: message);
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.isConnected});

  final bool isConnected;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isConnected ? Colors.green.shade100 : Colors.red.shade100,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Text(
        isConnected ? 'Connected' : 'Disconnected',
        style: TextStyle(
          color: isConnected ? Colors.green.shade800 : Colors.red.shade800,
        ),
      ),
    );
  }
}

class _MessageCard extends StatelessWidget {
  const _MessageCard({required this.message});

  final NexusMessage message;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.type,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 6),
            Text(
              message.payload.toString(),
              style: const TextStyle(fontSize: 12),
            ),
            const SizedBox(height: 6),
            Text(
              message.receivedAt.toIso8601String(),
              style: const TextStyle(fontSize: 11, color: Colors.black54),
            ),
          ],
        ),
      ),
    );
  }
}
