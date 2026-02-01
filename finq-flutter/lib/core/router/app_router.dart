import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app_shell.dart';
import '../../features/auth/auth_providers.dart';
import '../../features/auth/login_page.dart';
import '../../features/dashboard/dashboard_page.dart';
import '../../features/health/health_page.dart';
import '../../features/nexus/nexus_page.dart';
import '../../features/settings/settings_page.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    refreshListenable: GoRouterRefreshStream(
      ref.read(authStateStreamProvider),
    ),
    redirect: (context, state) {
      final authState = ref.read(authStateProvider);
      final isLoggingIn = state.matchedLocation == '/login';
      final isLoading = authState.isLoading;
      final isAuthenticated = authState.asData?.value ?? false;

      if (isLoading) {
        return isLoggingIn ? null : '/login';
      }

      if (!isAuthenticated && !isLoggingIn) {
        return '/login';
      }

      if (isAuthenticated && isLoggingIn) {
        return '/';
      }

      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginPage(),
      ),
      ShellRoute(
        builder: (context, state, child) => AppShell(
          child: child,
          location: state.uri.toString(),
        ),
        routes: [
          GoRoute(
            path: '/',
            builder: (context, state) => const DashboardPage(),
          ),
          GoRoute(
            path: '/nexus',
            builder: (context, state) => const NexusPage(),
          ),
          GoRoute(
            path: '/health',
            builder: (context, state) => const HealthPage(),
          ),
          GoRoute(
            path: '/settings',
            builder: (context, state) => const SettingsPage(),
          ),
        ],
      ),
    ],
  );
});

class GoRouterRefreshStream extends ChangeNotifier {
  GoRouterRefreshStream(Stream<dynamic> stream) {
    _subscription = stream.asBroadcastStream().listen((_) {
      notifyListeners();
    });
  }

  late final StreamSubscription<dynamic> _subscription;

  @override
  void dispose() {
    _subscription.cancel();
    super.dispose();
  }
}
