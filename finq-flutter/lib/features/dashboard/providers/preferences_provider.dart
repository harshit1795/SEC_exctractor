import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../services/preferences_service.dart';
import '../../auth/auth_providers.dart';

/// Provider for the PreferencesService singleton
final preferencesServiceProvider = Provider<PreferencesService>((ref) {
  return PreferencesService();
});

/// Provider that initializes preferences service with current user ID
final initializedPreferencesProvider = FutureProvider<PreferencesService>((ref) async {
  final service = ref.watch(preferencesServiceProvider);
  final user = ref.watch(authUserProvider).valueOrNull;
  await service.initialize(user?.uid);
  return service;
});

/// Provider for checking if preferences exist for a ticker/category
final hasPreferencesProvider = Provider.family<bool, (String, String)>((ref, params) {
  final service = ref.watch(preferencesServiceProvider);
  return service.hasPreferences(params.$1, params.$2);
});

/// Provider for getting saved metrics for a ticker/category
final savedMetricsProvider = Provider.family<List<String>, (String, String)>((ref, params) {
  final service = ref.watch(preferencesServiceProvider);
  return service.getMetrics(params.$1, params.$2);
});
