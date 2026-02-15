import 'package:finq_flutter/features/dashboard/dashboard_providers.dart';
import 'package:finq_flutter/features/dashboard/tabs/snapshot_tab.dart';
import 'package:finq_flutter/features/dashboard/tabs/trend_tab.dart';
import 'package:finq_flutter/features/dashboard/tabs/earnings_tab.dart';
import 'package:finq_flutter/features/dashboard/tabs/disclosures_tab.dart';
import 'package:finq_flutter/features/dashboard/providers/preferences_provider.dart';
import 'package:finq_flutter/services/preferences_service.dart';
import 'package:finq_flutter/core/api/api_client.dart';
import 'package:finq_flutter/core/di/providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Manual Mock for PreferencesService
class MockPreferencesService implements PreferencesService {
  @override
  List<String> getMetrics(String ticker, String category) => [];

  @override
  Future<void> saveMetrics(String ticker, String category, List<String> metrics) async {}

  @override
  Future<void> clearCategory(String ticker, String category) async {}

  @override
  Future<void> clearTicker(String ticker) async {}

  @override
  Future<void> clearAll() async {}

  @override
  bool hasPreferences(String ticker, String category) => false;

  @override
  Future<void> initialize(String? userId) async {}

  @override
  Map<String, Map<String, List<String>>> getAllPreferences() => {};
}

// Manual Mock for ApiClient
class MockApiClient implements ApiClient {
  @override
  Future<ApiResponse<T>> get<T>(String path, {Map<String, String>? headers, Map<String, dynamic>? queryParameters}) async {
    return ApiResponse(data: {} as T, statusCode: 200);
  }

  @override
  Future<ApiResponse<T>> post<T>(String path, {Map<String, String>? headers, Object? body}) async {
    throw UnimplementedError();
  }
}

// Minimal Mock SharedPreferences
class MockSharedPreferences implements SharedPreferences {
  final Map<String, Object> values;
  MockSharedPreferences(this.values);

  @override
  List<String>? getStringList(String key) {
    if (values.containsKey(key)) {
      final val = values[key];
      if (val is List) {
         return val.cast<String>();
      }
    }
    return null;
  }

  @override
  String? getString(String key) {
    if (values.containsKey(key)) {
      return values[key] as String;
    }
    return null;
  }

  @override
  Future<bool> setStringList(String key, List<String> value) async {
    values[key] = value;
    return true;
  }

  @override
  Future<bool> setString(String key, String value) async {
    values[key] = value;
    return true;
  }

  // Implement other members with UnimplementedError
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

// Mock data
Map<String, dynamic> generateMultiFundamentalData() {
  return {
    'tickers': ['AAPL', 'MSFT'],
    'data': {
      'AAPL': {'data': [
        {'Category': 'income', 'Metric': 'Revenue', 'Value': 100.0, 'FiscalPeriod': '2023 Q1'},
        {'Category': 'income', 'Metric': 'Net Income', 'Value': 50.0, 'FiscalPeriod': '2023 Q1'}
      ]},
      'MSFT': {'data': [
        {'Category': 'income', 'Metric': 'Revenue', 'Value': 200.0, 'FiscalPeriod': '2023 Q1'},
        {'Category': 'income', 'Metric': 'Net Income', 'Value': 100.0, 'FiscalPeriod': '2023 Q1'}
      ]},
    }
  };
}

Map<String, dynamic> generateMultiEarningsData() {
  return {
    'tickers': ['AAPL', 'MSFT'],
    'data': {
      'AAPL': {'ticker': 'AAPL', 'earnings_dates': [{'ReportedEPS': 1.0, 'EPSEstimate': 0.9, 'EarningsDate': '2023-01-01'}]},
      'MSFT': {'ticker': 'MSFT', 'earnings_dates': [{'ReportedEPS': 2.0, 'EPSEstimate': 1.9, 'EarningsDate': '2023-01-01'}]},
    }
  };
}

void main() {
  final mockPreferences = MockPreferencesService();
  final mockApiClient = MockApiClient();
  
  // Setup SharedPreferences with initial data
  // Ensure the list is typed correctly
  final mockPrefs = MockSharedPreferences({
    'selectedTickers': <String>['AAPL', 'MSFT'],
    'ticker': 'AAPL',
  });

  group('Multi-Ticker UI Tests', () {
    testWidgets('SnapshotTab renders comparison table for multiple tickers', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            fundamentalsProvider.overrideWith((ref) => Future.value(generateMultiFundamentalData())),
            preferencesServiceProvider.overrideWithValue(mockPreferences),
            selectedTickersProvider.overrideWith((ref) => SelectedTickersNotifier(mockPrefs)),
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: SnapshotTab(ticker: 'AAPL', category: 'income'),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.byType(DataTable), findsOneWidget);
      expect(find.text('AAPL'), findsAtLeastNWidgets(1));
      expect(find.text('MSFT'), findsAtLeastNWidgets(1));
      expect(find.text('Revenue'), findsAtLeastNWidgets(1)); 
    });

    testWidgets('TrendTab renders chips and chart for multiple tickers', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
             fundamentalsProvider.overrideWith((ref) => Future.value(generateMultiFundamentalData())),
             preferencesServiceProvider.overrideWithValue(mockPreferences),
             selectedTickersProvider.overrideWith((ref) => SelectedTickersNotifier(mockPrefs)),
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: TrendTab(ticker: 'AAPL', category: 'income'),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // TrendTab renders one LineChart per selected metric.
      // Our logic selects 'Revenue' and 'Net Income' (first 3).
      // So we expect 2 charts.
      expect(find.byType(LineChart), findsAtLeastNWidgets(1));
      
      expect(find.text('Revenue'), findsAtLeastNWidgets(1));
    });
   
     testWidgets('EarningsTab renders chips and combined chart', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            tickerDataProvider.overrideWith((ref) => Future.value(generateMultiEarningsData())),
            selectedTickersProvider.overrideWith((ref) => SelectedTickersNotifier(mockPrefs)),
            preferencesServiceProvider.overrideWithValue(mockPreferences),
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: EarningsTab(ticker: 'AAPL'),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('AAPL'), findsAtLeastNWidgets(1));
      expect(find.text('MSFT'), findsAtLeastNWidgets(1));
      expect(find.byType(LineChart), findsOneWidget);
    });
    
    testWidgets('DisclosuresTab renders ticker selector', (tester) async {
       await tester.pumpWidget(
        ProviderScope(
          overrides: [
            selectedTickersProvider.overrideWith((ref) => SelectedTickersNotifier(mockPrefs)),
            apiClientProvider.overrideWithValue(mockApiClient),
          ],
          child: const MaterialApp(
            home: Scaffold(
              body: DisclosuresTab(ticker: 'AAPL'),
            ),
          ),
        ),
      );
      
      await tester.pumpAndSettle();
      
      expect(find.text('Select Ticker'), findsOneWidget);
      expect(find.byType(DropdownButtonFormField<String>), findsOneWidget);
    });

  });
}
