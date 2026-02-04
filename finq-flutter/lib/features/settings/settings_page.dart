import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../auth/auth_providers.dart';

class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(authUserProvider);
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Settings',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            userAsync.when(
              data: (user) => _AuthSection(user: user),
              loading: () => const Text('Loading user...'),
              error: (error, _) => Text('Error: $error'),
            ),
          ],
        ),
      ),
    );
  }
}

class _AuthSection extends ConsumerWidget {
  const _AuthSection({required this.user});

  final User? user;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (user == null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Not signed in.'),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () async {
              final result =
                  await ref.read(authControllerProvider).signInWithGoogle();
              if (result.error != null) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(result.error!)),
                );
              }
            },
            icon: const Icon(Icons.login),
            label: const Text('Continue with Google'),
          ),
          const SizedBox(height: 8),
          TextButton(
            onPressed: () => context.go('/login'),
            child: const Text('Use email/password instead'),
          ),
        ],
      );
    }

    final currentUser = user;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('User ID: ${currentUser?.uid ?? "Unknown"}'),
        if (currentUser?.email != null) Text('Email: ${currentUser!.email}'),
        const SizedBox(height: 20),
        ElevatedButton(
          onPressed: () => ref.read(authControllerProvider).signOut(),
          child: const Text('Sign Out'),
        ),
      ],
    );
  }
}
