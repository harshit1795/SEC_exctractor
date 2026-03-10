import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app_shell.dart';
import '../../features/auth/auth_providers.dart';
import '../../features/auth/login_page.dart';
import '../../features/dashboard/dashboard_page.dart';
import '../../features/dashboard/dashboard_providers.dart';
import '../../features/health/health_page.dart';
import '../../features/nexus/nexus_page_enhanced.dart';
import '../../features/settings/settings_page.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final notifier = AuthStateRefreshNotifier(ref);
  ref.onDispose(() {
    notifier.dispose();
  });

  return GoRouter(
    initialLocation: '/',
    refreshListenable: notifier,
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
            builder: (context, state) {
              // Parse deep-link query params: ?ticker=META&period=1y
              // or ?tickers=META,AAPL&period=3m for multi-ticker
              final ticker = state.uri.queryParameters['ticker'];
              final tickers = state.uri.queryParameters['tickers'];
              final period = state.uri.queryParameters['period'];
              return _DeepLinkedDashboard(
                tickerParam: ticker,
                tickersParam: tickers,
                periodParam: period,
              );
            },
          ),
          GoRoute(
            path: '/nexus',
            builder: (context, state) => const NexusPageEnhanced(),
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

/// Wrapper that applies deep-link query parameters to providers before
/// rendering the dashboard. Params are only applied when non-null so
/// normal navigations (no params) preserve the persisted provider state.
class _DeepLinkedDashboard extends ConsumerStatefulWidget {
  const _DeepLinkedDashboard({
    this.tickerParam,
    this.tickersParam,
    this.periodParam,
  });

  final String? tickerParam;
  final String? tickersParam;
  final String? periodParam;

  @override
  ConsumerState<_DeepLinkedDashboard> createState() =>
      _DeepLinkedDashboardState();
}

class _DeepLinkedDashboardState extends ConsumerState<_DeepLinkedDashboard> {
  @override
  void initState() {
    super.initState();
    // Apply query params after first frame so providers are ready
    WidgetsBinding.instance.addPostFrameCallback((_) => _applyParams());
  }

  void _applyParams() {
    // Multi-ticker: ?tickers=META,AAPL,NVDA
    if (widget.tickersParam != null && widget.tickersParam!.isNotEmpty) {
      final list = widget.tickersParam!
          .split(',')
          .map((t) => t.trim().toUpperCase())
          .where((t) => t.isNotEmpty)
          .toList();
      if (list.isNotEmpty) {
        ref.read(selectedTickersProvider.notifier).setTickers(list);
      }
    } else if (widget.tickerParam != null && widget.tickerParam!.isNotEmpty) {
      // Single ticker: ?ticker=META
      ref
          .read(selectedTickersProvider.notifier)
          .setTickers([widget.tickerParam!.toUpperCase()]);
    }

    if (widget.periodParam != null && widget.periodParam!.isNotEmpty) {
      ref
          .read(periodProvider.notifier)
          .setPeriod(widget.periodParam!);
    }
  }

  @override
  Widget build(BuildContext context) => const DashboardPage();
}

class AuthStateRefreshNotifier extends ChangeNotifier {
  AuthStateRefreshNotifier(this._ref) {
    _ref.listen<AsyncValue<bool>>(
      authStateProvider,
      (previous, next) {
        notifyListeners();
      },
    );
  }

  final Ref _ref;

  @override
  void dispose() {
    super.dispose();
  }
}

