import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app.dart';
import 'core/auth/firebase_initializer.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await FirebaseInitializer.ensureInitialized();
  } catch (error) {
    debugPrint('Firebase initialization skipped: $error');
  }
  runApp(const ProviderScope(child: FinqApp()));
}
