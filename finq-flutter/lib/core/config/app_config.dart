class AppConfig {
  AppConfig._();

  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api',
  );

  static String websocketUrl({
    required String path,
    Map<String, String>? queryParameters,
    String? baseUrl,
  }) {
    final targetBase = baseUrl ?? apiBaseUrl;
    final base = targetBase.startsWith('https://')
        ? targetBase.replaceFirst('https://', 'wss://')
        : targetBase.replaceFirst('http://', 'ws://');
    final buffer = StringBuffer('$base$path');
    if (queryParameters != null && queryParameters.isNotEmpty) {
      buffer.write('?');
      buffer.write(queryParameters.entries
          .map((entry) =>
              '${Uri.encodeQueryComponent(entry.key)}=${Uri.encodeQueryComponent(entry.value)}')
          .join('&'));
    }
    return buffer.toString();
  }
  static const String apiNinjaKey = String.fromEnvironment(
    'API_NINJA_KEY',
    defaultValue: 'livTDbNkoOMN7yeNkNIhNA==4OpEMBaOVHwqOn8g',
  );
}
