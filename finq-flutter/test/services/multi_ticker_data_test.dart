import 'package:finq_flutter/core/api/api_client.dart';
import 'package:finq_flutter/features/dashboard/dashboard_repository.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';

// Manual Mock for ApiClient matching the abstract class definition
class MockApiClient implements ApiClient {
  final Map<String, dynamic> responses = {};
  final Map<String, dynamic> errors = {};
  
  // Track calls
  final Map<String, int> callCounts = {};

  void whenGet(String path, dynamic data) {
    responses[path] = data;
  }
  
  void whenGetThrow(String path, dynamic error) {
    errors[path] = error;
  }

  @override
  Future<ApiResponse<T>> get<T>(
    String path, {
    bool forceRefresh = false,
    Map<String, String>? headers,
    Map<String, dynamic>? queryParameters,
  }) async {
    callCounts[path] = (callCounts[path] ?? 0) + 1;
    
    if (errors.containsKey(path)) {
      throw errors[path];
    }
    
    if (responses.containsKey(path)) {
      // Cast the response data to T. 
      // In the tests we expect Map<String, dynamic> usually.
      return ApiResponse<T>(
        data: responses[path] as T,
        statusCode: 200,
      );
    }
    
    throw Exception('No mock defined for $path');
  }

  @override
  Future<ApiResponse<T>> post<T>(
    String path, {
    Map<String, String>? headers,
    Map<String, dynamic>? queryParameters,
    Object? body,
  }) async {
    throw UnimplementedError(); 
  }

  @override
  Future<ApiResponse<T>> put<T>(
    String path, {
    Map<String, String>? headers,
    Map<String, dynamic>? queryParameters,
    Object? body,
  }) async {
    throw UnimplementedError(); 
  }

  @override
  Future<ApiResponse<T>> patch<T>(
    String path, {
    Map<String, String>? headers,
    Map<String, dynamic>? queryParameters,
    Object? body,
  }) async {
    throw UnimplementedError(); 
  }
}

void main() {
  late MockApiClient mockApiClient;
  late DashboardRepository repository;

  setUp(() {
    mockApiClient = MockApiClient();
    repository = DashboardRepository(mockApiClient);
  });

  group('Multi-Ticker Data Fetching', () {
    test('fetchMultipleFundamentals calls API correctly and aggregates results', () async {
      final tickers = ['AAPL', 'MSFT'];
      
      // Mock responses
      mockApiClient.whenGet('/financial/fundamentals/AAPL', {'data': [{'Metric': 'Revenue', 'Value': 100}]});
      mockApiClient.whenGet('/financial/fundamentals/MSFT', {'data': [{'Metric': 'Revenue', 'Value': 200}]});

      final result = await repository.fetchMultipleFundamentals(tickers);

      expect(result.length, 2);
      expect(result['AAPL'], isNotNull);
      expect(result['MSFT'], isNotNull);
      
      expect(mockApiClient.callCounts['/financial/fundamentals/AAPL'], 1);
      expect(mockApiClient.callCounts['/financial/fundamentals/MSFT'], 1);
    });

    test('fetchMultipleFundamentals handles partial failures gracefully', () async {
      final tickers = ['AAPL', 'INVALID'];
      
      mockApiClient.whenGet('/financial/fundamentals/AAPL', {'data': []});
      // Simulate failure for INVALID
      mockApiClient.whenGetThrow('/financial/fundamentals/INVALID', DioException(requestOptions: RequestOptions(path: '')));

      final result = await repository.fetchMultipleFundamentals(tickers);

      expect(result.length, 2);
      expect(result['AAPL'], isNotNull);
      expect(result['INVALID'], isNull); // Should be null on failure
      
      expect(mockApiClient.callCounts['/financial/fundamentals/AAPL'], 1);
      expect(mockApiClient.callCounts['/financial/fundamentals/INVALID'], 1);
    });
  });
}
