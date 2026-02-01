import '../../core/api/api_client.dart';

class DashboardRepository {
  DashboardRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<Map<String, dynamic>> fetchHealthStatus() async {
    final response = await _apiClient.get<Map<String, dynamic>>('/health');
    final data = response.data;
    if (data is Map<String, dynamic>) {
      return data;
    }
    if (data is Map) {
      return Map<String, dynamic>.from(data);
    }
    throw StateError('Unexpected health response format');
  }
}
