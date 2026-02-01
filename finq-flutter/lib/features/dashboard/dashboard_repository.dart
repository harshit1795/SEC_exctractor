import '../../core/api/api_client.dart';

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
    final response = await _apiClient.get<Map<String, dynamic>>(
      '/financial/ticker/$ticker',
      queryParameters: {'period': period},
    );
    return _asMap(response.data, 'ticker data');
  }

  Future<Map<String, dynamic>> fetchFundamentals(String ticker) async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      '/financial/fundamentals/$ticker',
    );
    return _asMap(response.data, 'fundamentals');
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
