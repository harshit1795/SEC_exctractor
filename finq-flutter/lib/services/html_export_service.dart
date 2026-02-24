import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:intl/intl.dart';
import 'package:universal_html/html.dart' as html;

/// Service for downloading HTML reports to the user's device
class HtmlExportService {
  /// Download HTML report (web compatible)
  static Future<void> downloadHtmlReport({
    required String htmlString,
    required String filenamePrefix,
  }) async {
    final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final filename = '${filenamePrefix}_health_report_$timestamp.html';

    if (kIsWeb) {
      // Web: Create blob and trigger download
      final bytes = utf8.encode(htmlString);
      final blob = html.Blob([bytes], 'text/html');
      final url = html.Url.createObjectUrlFromBlob(blob);
      html.AnchorElement(href: url)
        ..setAttribute('download', filename)
        ..click();
      html.Url.revokeObjectUrl(url);
    } else {
      // Mobile/Desktop: This requires platform-specific implementation
      // Usually via path_provider + standard dart:io File writes.
      debugPrint('HTML export on mobile/desktop would save to: $filename');
      // For now, throw UnimplementedError until file_saver or path_provider logic is built.
      throw UnimplementedError(
        'HTML export on mobile is not yet implemented. Please use the web version.',
      );
    }
  }
}
