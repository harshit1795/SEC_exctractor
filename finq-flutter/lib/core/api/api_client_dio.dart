import 'package:dio/dio.dart';

import '../auth/auth_service.dart';
import '../config/app_config.dart';
import 'api_client.dart';

class ApiClientDio implements ApiClient {
  ApiClientDio({
    required AuthService authService,
    Dio? dio,
  })  : _authService = authService,
        _dio = dio ??
            Dio(
              BaseOptions(
                baseUrl: AppConfig.apiBaseUrl,
                connectTimeout: const Duration(seconds: 15),
                receiveTimeout: const Duration(seconds: 30),
              ),
            ) {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _authService.getIdToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
      ),
    );
  }

  final AuthService _authService;
  final Dio _dio;

  @override
  Future<ApiResponse<T>> get<T>(
    String path, {
    Map<String, String>? headers,
    Map<String, dynamic>? queryParameters,
  }) async {
    final response = await _dio.get<T>(
      path,
      options: Options(headers: headers),
      queryParameters: queryParameters,
    );
    return ApiResponse<T>(
      data: response.data as T,
      statusCode: response.statusCode ?? 0,
    );
  }

  @override
  Future<ApiResponse<T>> post<T>(
    String path, {
    Map<String, String>? headers,
    Object? body,
  }) async {
    final response = await _dio.post<T>(
      path,
      data: body,
      options: Options(headers: headers),
    );
    return ApiResponse<T>(
      data: response.data as T,
      statusCode: response.statusCode ?? 0,
    );
  }
}
