import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/di/providers.dart';
import 'auth_controller.dart';

final authControllerProvider = Provider<AuthController>((ref) {
  return AuthController();
});

final authUserProvider = StreamProvider<User?>((ref) {
  if (Firebase.apps.isEmpty) {
    return const Stream<User?>.empty();
  }
  return FirebaseAuth.instance.authStateChanges();
});

final authStateProvider = StreamProvider<bool>((ref) {
  return ref.read(authServiceProvider).authStateChanges();
});

final authStateStreamProvider = Provider<Stream<bool>>((ref) {
  return ref.read(authServiceProvider).authStateChanges();
});
