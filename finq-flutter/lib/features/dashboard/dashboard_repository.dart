import '../../core/api/api_client.dart';
import '../../services/report_cache_service.dart';

class DashboardRepository {
  DashboardRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<Map<String, dynamic>> fetchHealthStatus() async {
    final response = await _apiClient.get<Map<String, dynamic>>('/health');
    return _asMap(response.data, 'health');
  }

  Future<Map<String, dynamic>> fetchTickerData(
    String ticker,
    String period,
  ) async {
    print('DEBUG: Fetching ticker data for $ticker');
    try {
        final response = await _apiClient.get<Map<String, dynamic>>(
        '/financial/ticker/$ticker',
        queryParameters: {'period': period},
        );
        return _asMap(response.data, 'ticker data');
    } catch (e) {
        print('DEBUG: Error fetching ticker data: $e');
        rethrow;
    }
  }

  Future<Map<String, dynamic>> fetchFundamentals(String ticker) async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      '/financial/fundamentals/$ticker',
    );
    return _asMap(response.data, 'fundamentals');
  }

  Future<Map<String, dynamic>> fetchMultipleFundamentals(List<String> tickers) async {
    // If we had a bulk endpoint we'd use it, for now parallel requests
    if (tickers.isEmpty) return {};
    
    final results = <String, dynamic>{};
    final futures = tickers.map((ticker) async {
      try {
        final data = await fetchFundamentals(ticker);
        results[ticker] = data;
      } catch (e) {
        // Log error but continue
        print('Error fetching fundamentals for $ticker: $e');
        results[ticker] = null;
      }
    });
    
    await Future.wait(futures);
    return results;
  }

  Future<List<Map<String, dynamic>>> searchTickers(String query) async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      '/financial/search',
      queryParameters: {'q': query, 'limit': 10},
    );
    
    final data = response.data;
    if (data == null) return [];
    
    // Response structure: { query: "...", results: [...], count: ... }
    final results = data['results'] as List<dynamic>?;
    if (results == null) return [];
    
    return results.cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> fetchMultipleTickerData(
    List<String> tickers,
    String period,
  ) async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      '/financial/tickers',
      queryParameters: {
        'tickers': tickers.join(','),
        'period': period,
      },
    );
    return _asMap(response.data, 'multiple tickers data');
  }

  Future<Map<String, dynamic>> fetchDashboardHealthScores(List<String> tickers) async {
    if (tickers.isEmpty) return {'scores': [], 'count': 0};
    final response = await _apiClient.get<Map<String, dynamic>>(
      '/health-scores/finq',
      queryParameters: {'ticker': tickers.join(',')},
    );
    return _asMap(response.data, 'health scores');
  }

  Future<String> generateHealthReportHtml(List<Map<String, dynamic>> tickersData) async {
    if (tickersData.isEmpty) return 'No data provided';

    final tickers = tickersData.map((e) => e['ticker'].toString()).toList();
    final cachedHtml = await ReportCacheService.getCachedReport(tickers);
    if (cachedHtml != null) {
      return cachedHtml;
    }

    final response = await _apiClient.post<Map<String, dynamic>>(
      '/health-scores/report',
      // In Dio, setting 'data' payload for POST:
      body: {'tickers': tickersData},
    );
    final data = _asMap(response.data, 'health report');
    final html = data['report'] as String? ?? 'No report generated';
    
    if (html != 'No report generated') {
      await ReportCacheService.saveReport(tickers, html);
    }
    return html;
  }

  Map<String, dynamic> _asMap(Object? data, String label) {
    if (data is Map<String, dynamic>) {
      return data;
    }
    if (data is Map) {
      return Map<String, dynamic>.from(data);
    }
    throw StateError('Unexpected $label response format');
  }
}
