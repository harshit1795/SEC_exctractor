import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../nexus_providers.dart';

class PrivacySettingsPage extends ConsumerWidget {
  const PrivacySettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final preferences = ref.watch(nexusProfilePreferencesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Privacy Settings'),
      ),
      body: preferences.when(
        data: (data) {
          final useAlias = data['use_alias_as_display'] ?? false;
          
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const Text(
                'Identity',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              SwitchListTile(
                title: const Text('Use Alias as Display Name'),
                subtitle: const Text(
                  'Show your custom alias instead of your real name from Google/Firebase.',
                ),
                value: useAlias,
                onChanged: (value) async {
                  try {
                    await NexusProfileService.updateProfile(
                      ref,
                      useAliasAsDisplay: value,
                    );
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            value ? 'Now using alias' : 'Now using real name',
                          ),
                        ),
                      );
                    }
                  } catch (e) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Error: $e')),
                      );
                    }
                  }
                },
              ),
              const Divider(),
              const SizedBox(height: 16),
              const Text(
                'Visibility',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ListTile(
                title: const Text('Profile Visibility'),
                subtitle: const Text('Who can see your profile and posts'),
                trailing: const Text('Everyone', style: TextStyle(color: Colors.grey)),
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('More privacy options coming soon!')),
                  );
                },
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Error: $error')),
      ),
    );
  }
}
