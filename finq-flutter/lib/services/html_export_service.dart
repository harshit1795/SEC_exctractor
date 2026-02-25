import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:intl/intl.dart';
import 'package:universal_html/html.dart' as html;

/// Service for opening HTML reports natively in the browser
class HtmlExportService {
  /// Opens the HTML report in a new browser tab with a Print/Save PDF button injected
  static Future<void> openHtmlReport({
    required String htmlString,
    required String filenamePrefix,
  }) async {
    final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final filename = '${filenamePrefix}_health_report_$timestamp.pdf';

    // Inject a floating print button and hide it during print
    final injectedHtml = '''
      <!DOCTYPE html>
      <html>
      <head>
        <title>$filename</title>
        <style>
          @media print {
            .no-print { display: none !important; }
            body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
          }
          .finq-print-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            background-color: #4F46E5;
            color: white;
            font-family: system-ui, -apple-system, sans-serif;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            z-index: 9999;
            display: flex;
            align-items: center;
            gap: 8px;
          }
          .finq-print-btn:hover { background-color: #4338CA; }
        </style>
      </head>
      <body>
        <button class="finq-print-btn no-print" onclick="window.print()">
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
          Print / Save as PDF
        </button>
        $htmlString
      </body>
      </html>
    ''';

    if (kIsWeb) {
      // Web: Create blob and open in new tab
      final bytes = utf8.encode(injectedHtml);
      final blob = html.Blob([bytes], 'text/html');
      final url = html.Url.createObjectUrlFromBlob(blob);
      html.window.open(url, '_blank');
      
      // We don't revoke immediately so the new tab can load it
      Future.delayed(const Duration(seconds: 5), () {
        html.Url.revokeObjectUrl(url);
      });
    } else {
      // Mobile/Desktop: This requires platform-specific implementation
      debugPrint('HTML export on mobile/desktop would save to: $filename');
      throw UnimplementedError(
        'HTML preview on mobile is not yet implemented. Please use the web version.',
      );
    }
  }
}
