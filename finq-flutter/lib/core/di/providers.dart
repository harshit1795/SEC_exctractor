import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio_cache_interceptor/dio_cache_interceptor.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../api/api_client.dart';
import '../api/api_client_dio.dart';
import '../auth/auth_service.dart';
import '../auth/firebase_auth_service.dart';
import '../config/app_config.dart';

final authServiceProvider = Provider<AuthService>((ref) {
  return FirebaseAuthService();
});

/// Memory cache store for API responses
final cacheStoreProvider = Provider<CacheStore>((ref) {
  return MemCacheStore(maxSize: 10485760); // 10MB
});


/// Provider for the API Base URL
final baseUrlProvider = StateProvider<String>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return prefs.getString('api_base_url') ?? AppConfig.apiBaseUrl;
});

/// Provider for User's BYOK Gemini API Key
final geminiApiKeyProvider = StateProvider<String?>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return prefs.getString('gemini_api_key');
});

/// API client with caching enabled
final apiClientProvider = Provider<ApiClient>((ref) {
  final baseUrl = ref.watch(baseUrlProvider);
  final geminiApiKey = ref.watch(geminiApiKeyProvider);

  return ApiClientDio(
    baseUrl: baseUrl,
    authService: ref.read(authServiceProvider),
    cacheStore: ref.read(cacheStoreProvider),
    geminiApiKey: geminiApiKey,
  );
});

/// Shared Preferences instance (must be overridden in main.dart)
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError();
});
