import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api_client.dart';
import '../api/api_client_dio.dart';
import '../auth/auth_service.dart';
import '../auth/firebase_auth_service.dart';

final authServiceProvider = Provider<AuthService>((ref) {
  return FirebaseAuthService();
});

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClientDio(authService: ref.read(authServiceProvider));
});
