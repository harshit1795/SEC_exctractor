import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../core/config/app_config.dart';
import '../../core/di/providers.dart';
import 'dashboard_repository.dart';

final dashboardRepositoryProvider = Provider<DashboardRepository>((ref) {
  return DashboardRepository(ref.read(apiClientProvider));
});

final healthStatusProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.read(dashboardRepositoryProvider);
  return repository.fetchHealthStatus();
});

// --- Persistent Providers ---

class TickerNotifier extends StateNotifier<String> {
  TickerNotifier(this.prefs) : super(prefs.getString('ticker') ?? 'AAPL');
  final SharedPreferences prefs;

  void setTicker(String ticker) {
    state = ticker;
    prefs.setString('ticker', ticker);
  }
}

final tickerProvider = StateNotifierProvider<TickerNotifier, String>((ref) {
  return TickerNotifier(ref.read(sharedPreferencesProvider));
});


class PeriodNotifier extends StateNotifier<String> {
  PeriodNotifier(this.prefs) : super(prefs.getString('period') ?? '1y');
  final SharedPreferences prefs;

  void setPeriod(String period) {
    state = period;
    prefs.setString('period', period);
  }
}

final periodProvider = StateNotifierProvider<PeriodNotifier, String>((ref) {
  return PeriodNotifier(ref.read(sharedPreferencesProvider));
});


class CategoryNotifier extends StateNotifier<String> {
  CategoryNotifier(this.prefs) : super(prefs.getString('category') ?? 'IncomeStatement');
  final SharedPreferences prefs;

  void setCategory(String category) {
    state = category;
    prefs.setString('category', category);
  }
}

final categoryProvider = StateNotifierProvider<CategoryNotifier, String>((ref) {
  return CategoryNotifier(ref.read(sharedPreferencesProvider));
});

// --- Data Providers ---

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

final logoUrlProvider = FutureProvider.family<String?, String>((ref, ticker) async {
  if (ticker.isEmpty) return null;
  
  // Use Financial Modeling Prep's free logo API
  // This works directly with stock tickers and has good CORS support
  // Format: https://financialmodelingprep.com/image-stock/{TICKER}.png
  
  return 'https://financialmodelingprep.com/image-stock/${ticker.toUpperCase()}.png';
});
