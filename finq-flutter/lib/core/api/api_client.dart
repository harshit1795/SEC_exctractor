class ApiResponse<T> {
  ApiResponse({
    required this.data,
    required this.statusCode,
  });

  final T data;
  final int statusCode;
}

abstract class ApiClient {
  Future<ApiResponse<T>> get<T>(
    String path, {
    Map<String, String>? headers,
    Map<String, dynamic>? queryParameters,
  });

  Future<ApiResponse<T>> post<T>(
    String path, {
    Map<String, String>? headers,
    Object? body,
  });
}
