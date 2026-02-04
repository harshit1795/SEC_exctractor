import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/di/providers.dart';
import 'dashboard_repository.dart';

final dashboardRepositoryProvider = Provider<DashboardRepository>((ref) {
  return DashboardRepository(ref.read(apiClientProvider));
});

final healthStatusProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.read(dashboardRepositoryProvider);
  return repository.fetchHealthStatus();
});

final tickerProvider = StateProvider<String>((ref) => 'AAPL');
final periodProvider = StateProvider<String>((ref) => '1y');
final categoryProvider = StateProvider<String>((ref) => 'IncomeStatement');

final tickerDataProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.read(dashboardRepositoryProvider);
  final ticker = ref.watch(tickerProvider).trim();
  final period = ref.watch(periodProvider).trim();
  return repository.fetchTickerData(ticker, period);
});

final fundamentalsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.read(dashboardRepositoryProvider);
  final ticker = ref.watch(tickerProvider).trim();
  return repository.fetchFundamentals(ticker);
});
