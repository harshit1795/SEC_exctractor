import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';

class FirebaseInitializer {
  FirebaseInitializer._();

  static Future<void> ensureInitialized() async {
    if (Firebase.apps.isNotEmpty) {
      return;
    }

    if (kIsWeb) {
      final options = _webOptions();
      if (!_hasRequiredOptions(options)) {
        throw StateError(
          'Missing Firebase web config. Provide FIREBASE_* via --dart-define-from-file=.dart-define.json',
        );
      }
      await Firebase.initializeApp(options: options);
      return;
    }

    await Firebase.initializeApp();
  }

  static FirebaseOptions _webOptions() {
    return FirebaseOptions(
      apiKey: const String.fromEnvironment('FIREBASE_API_KEY'),
      appId: const String.fromEnvironment('FIREBASE_APP_ID'),
      projectId: const String.fromEnvironment('FIREBASE_PROJECT_ID'),
      authDomain: const String.fromEnvironment('FIREBASE_AUTH_DOMAIN'),
      storageBucket: const String.fromEnvironment('FIREBASE_STORAGE_BUCKET'),
      messagingSenderId:
          const String.fromEnvironment('FIREBASE_MESSAGING_SENDER_ID'),
      measurementId:
          const String.fromEnvironment('FIREBASE_MEASUREMENT_ID', defaultValue: ''),
    );
  }

  static bool _hasRequiredOptions(FirebaseOptions options) {
    final hasAuthDomain = options.authDomain?.isNotEmpty ?? false;
    return options.apiKey.isNotEmpty &&
        options.appId.isNotEmpty &&
        options.projectId.isNotEmpty &&
        hasAuthDomain;
  }
}
