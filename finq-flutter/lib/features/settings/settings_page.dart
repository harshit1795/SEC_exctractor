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
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.settings, size: 28, color: Colors.grey.shade700),
                const SizedBox(width: 12),
                const Text(
                  'Settings',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 24),
            userAsync.when(
              data: (user) => Column(
                children: [
                  _AuthSection(user: user),
                  if (user != null) ...[
                    const SizedBox(height: 24),
                    _PreferencesSection(),
                    const SizedBox(height: 24),
                    _AppInfoSection(),
                  ],
                ],
              ),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Text('Error: $error'),
            ),
          ],
        ),
      ),
    );
  }
}

class _PreferencesSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          ListTile(
            leading: const Icon(Icons.palette),
            title: const Text('Theme'),
            subtitle: const Text('Light'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Theme switching coming soon!')),
              );
            },
          ),
          const Divider(height: 1),
          ListTile(
            leading: const Icon(Icons.notifications),
            title: const Text('Notifications'),
            subtitle: const Text('Manage notification preferences'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Notification settings coming soon!')),
              );
            },
          ),
          const Divider(height: 1),
          ListTile(
            leading: const Icon(Icons.data_usage),
            title: const Text('Data Preferences'),
            subtitle: const Text('Default ticker, period, category'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Data preferences coming soon!')),
              );
            },
          ),
        ],
      ),
    );
  }
}

class _AppInfoSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          const ListTile(
            leading: Icon(Icons.info),
            title: Text('About'),
            subtitle: Text('FinQ v1.0.0 (Flutter)'),
          ),
          const Divider(height: 1),
          ListTile(
            leading: const Icon(Icons.privacy_tip),
            title: const Text('Privacy Policy'),
            trailing: const Icon(Icons.open_in_new),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Opening privacy policy...')),
              );
            },
          ),
          const Divider(height: 1),
          ListTile(
            leading: const Icon(Icons.description),
            title: const Text('Terms of Service'),
            trailing: const Icon(Icons.open_in_new),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Opening terms of service...')),
              );
            },
          ),
        ],
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
