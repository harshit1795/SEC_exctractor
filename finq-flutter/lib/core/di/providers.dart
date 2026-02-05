import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio_cache_interceptor/dio_cache_interceptor.dart';

import '../api/api_client.dart';
import '../api/api_client_dio.dart';
import '../auth/auth_service.dart';
import '../auth/firebase_auth_service.dart';

final authServiceProvider = Provider<AuthService>((ref) {
  return FirebaseAuthService();
});

/// Memory cache store for API responses
final cacheStoreProvider = Provider<CacheStore>((ref) {
  return MemCacheStore(maxSize: 10485760); // 10MB
});

/// API client with caching enabled
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClientDio(
    authService: ref.read(authServiceProvider),
    cacheStore: ref.read(cacheStoreProvider),
  );
});
