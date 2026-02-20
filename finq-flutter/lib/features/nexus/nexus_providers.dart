import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/di/providers.dart';
import '../auth/auth_providers.dart';

final nexusProfileProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  final user = await ref.watch(authUserProvider.future);

  if (user == null) {
    throw Exception('User not authenticated');
  }

  try {
    // 1. Try to get existing profile
    final response = await apiClient.get('/nexus/users/${user.uid}/profile');
    final data = response.data as Map<String, dynamic>;

    // 2. Check if we need to initialize/sync (e.g. if photo is missing in backend but exists in Firebase)
    final backendPhoto = data['profile_picture_url'] as String?;
    final firebasePhoto = user.photoURL;

    if (backendPhoto == null && firebasePhoto != null && firebasePhoto.isNotEmpty) {
      // Sync Firebase data to backend
      final initResponse = await apiClient.post(
        '/nexus/users/${user.uid}/profile/initialize',
        body: {
          'firebase_display_name': user.displayName,
          'firebase_photo_url': firebasePhoto,
          'firebase_email': user.email,
        },
        queryParameters: {'user_id': user.uid},
      );
      return initResponse.data as Map<String, dynamic>;
    }

    return data;
  } catch (e) {
    // If profile doesn't exist (404), try to initialize it
    if (e.toString().contains('404')) {
      final initResponse = await apiClient.post(
        '/nexus/users/${user.uid}/profile/initialize',
        body: {
          'firebase_display_name': user.displayName,
          'firebase_photo_url': user.photoURL,
          'firebase_email': user.email,
        },
        queryParameters: {'user_id': user.uid},
      );
      return initResponse.data as Map<String, dynamic>;
    }
    rethrow;
  }
});

final nexusProfilePreferencesProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  final user = await ref.watch(authUserProvider.future);

  if (user == null) {
    throw Exception('User not authenticated');
  }

  final response = await apiClient.get('/nexus/users/${user.uid}/profile/preferences');
  return response.data as Map<String, dynamic>;
});

abstract class NexusProfileService {
  static Future<void> updateProfile(WidgetRef ref, {
    String? displayName,
    String? profilePictureUrl,
    bool? useAliasAsDisplay,
  }) async {
    final apiClient = ref.read(apiClientProvider);
    final user = ref.read(authUserProvider).valueOrNull;
    if (user == null) return;

    final data = <String, dynamic>{};
    if (displayName != null) data['display_name'] = displayName;
    if (profilePictureUrl != null) data['profile_picture_url'] = profilePictureUrl;
    if (useAliasAsDisplay != null) data['use_alias_as_display'] = useAliasAsDisplay;

    await apiClient.put(
      '/nexus/users/${user.uid}/profile/preferences',
      body: data,
      queryParameters: {'user_id': user.uid},
    );
    
    // Invalidate providers to refresh UI
    ref.invalidate(nexusProfileProvider);
    ref.invalidate(nexusProfilePreferencesProvider);
  }
}
