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


// --- Persistent Providers ---

class TickerNotifier extends StateNotifier<String> {
  TickerNotifier(this.prefs) : super(prefs.getString('ticker') ?? 'AAPL');
  final SharedPreferences prefs;

  void setTicker(String ticker) {
    state = ticker;
    prefs.setString('ticker', ticker);
  }
}

// Keeping legacy provider for backward compatibility, but it will essentially track the "primary" ticker
final tickerProvider = StateNotifierProvider<TickerNotifier, String>((ref) {
  return TickerNotifier(ref.read(sharedPreferencesProvider));
});


class SelectedTickersNotifier extends StateNotifier<List<String>> {
  SelectedTickersNotifier(this.prefs) : super(_loadTickers(prefs));
  final SharedPreferences prefs;

  static List<String> _loadTickers(SharedPreferences prefs) {
    final list = prefs.getStringList('selectedTickers');
    if (list != null && list.isNotEmpty) return list;
    // Fallback to single ticker if no list
    final single = prefs.getString('ticker');
    return [single ?? 'AAPL'];
  }

  void setTickers(List<String> tickers) {
    if (tickers.isEmpty) return;
    // Enforce max 3
    final limited = tickers.take(3).toList();
    state = limited;
    prefs.setStringList('selectedTickers', limited);
    
    // Sync single ticker provider for compatibility
    if (limited.isNotEmpty) {
      prefs.setString('ticker', limited.first);
      // We don't direct update the other provider to avoid loops, 
      // but UI should prefer this provider.
    }
  }

  void addTicker(String ticker) {
    if (state.contains(ticker)) return;
    if (state.length >= 3) {
      // Option: Remove first? Or just don't add? user req says "Allow Users to select at most 3"
      // Let's replace the last one if full? Or just block? 
      // Plan said "Try adding a 4th. Should be blocked or replace specific one".
      // Let's block for now, UI should handle "remove to add".
      return;
    }
    setTickers([...state, ticker]);
  }

  void removeTicker(String ticker) {
    if (state.length <= 1) return; // Don't allow empty
    setTickers(state.where((t) => t != ticker).toList());
  }
}

final selectedTickersProvider = StateNotifierProvider<SelectedTickersNotifier, List<String>>((ref) {
  return SelectedTickersNotifier(ref.read(sharedPreferencesProvider));
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
  // Use selected tickers
  final mn = ref.watch(selectedTickersProvider.notifier);
  // Ensure we sync with legacy provider if it changes externally? 
  // For now let's just observe selectedTickers
  final tickers = ref.watch(selectedTickersProvider);
  final period = ref.watch(periodProvider).trim();
  
  if (tickers.isEmpty) {
      // Falback
      return repository.fetchTickerData('AAPL', period);
  }
  
  if (tickers.length == 1) {
      return repository.fetchTickerData(tickers.first, period);
  }
  
  // Multiple tickers
  return repository.fetchMultipleTickerData(tickers, period);
});

final fundamentalsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.read(dashboardRepositoryProvider);
  final tickers = ref.watch(selectedTickersProvider);
  
  if (tickers.isEmpty) {
     return repository.fetchFundamentals('AAPL');
  }
  
  if (tickers.length == 1) {
     return repository.fetchFundamentals(tickers.first);
  }

  // Multiple tickers
  final data = await repository.fetchMultipleFundamentals(tickers);
  return {
    'tickers': tickers,
    'data': data,
  };
});

final logoUrlProvider = FutureProvider.family<String?, String>((ref, ticker) async {
  if (ticker.isEmpty) return null;
  return 'https://financialmodelingprep.com/image-stock/${ticker.toUpperCase()}.png';
});

final dashboardHealthScoresProvider = FutureProvider<List<dynamic>>((ref) async {
  final repository = ref.read(dashboardRepositoryProvider);
  final tickers = ref.watch(selectedTickersProvider);
  
  if (tickers.isEmpty) return [];
  
  final data = await repository.fetchDashboardHealthScores(tickers);
  return data['scores'] as List<dynamic>? ?? [];
});


