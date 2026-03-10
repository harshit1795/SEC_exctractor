import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:intl/intl.dart';
import 'package:universal_html/html.dart' as html;

/// Service for opening HTML reports natively in the browser
class HtmlExportService {
  /// Safely executes an async report generation and opens it in a new tab.
  /// Bypasses browser popup blockers by opening a blank tab synchronously
  /// before awaiting the [htmlGenerator] future.
  static Future<void> generateAndOpenReport({
    required Future<String> Function() htmlGenerator,
    required String filenamePrefix,
  }) async {
    html.WindowBase? newTab;

    if (kIsWeb) {
      // Open immediately to bypass popup blockers
      final loadingHtml = '''
        <!DOCTYPE html>
        <html>
        <head>
          <title>Generating Report...</title>
          <style>
            body { font-family: system-ui, -apple-system, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; background-color: #f9fafb; color: #1f2937; }
            .spinner { width: 40px; height: 40px; border: 4px solid #e5e7eb; border-top-color: #4f46e5; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }
            @keyframes spin { to { transform: rotate(360deg); } }
          </style>
        </head>
        <body>
          <div class="spinner"></div>
          <h2>Generating your AI Health Report</h2>
          <p>Please wait while we crunch the numbers. This usually takes 5-10 seconds...</p>
        </body>
        </html>
      ''';
      final loadingBlob = html.Blob([utf8.encode(loadingHtml)], 'text/html');
      final loadingUrl = html.Url.createObjectUrlFromBlob(loadingBlob);
      newTab = html.window.open(loadingUrl, '_blank');
      html.Url.revokeObjectUrl(loadingUrl);
    } else {
      debugPrint('HTML export on mobile/desktop is not yet implemented.');
      throw UnimplementedError('HTML preview on mobile is not yet implemented. Please use the web version.');
    }

    try {
      final htmlString = await htmlGenerator();
      final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
      final filename = '${filenamePrefix}_health_report_$timestamp.pdf';

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

      final bytes = utf8.encode(injectedHtml);
      final blob = html.Blob([bytes], 'text/html');
      final url = html.Url.createObjectUrlFromBlob(blob);
      newTab.location.href = url;
      
      Future.delayed(const Duration(seconds: 5), () {
        html.Url.revokeObjectUrl(url);
      });
    } catch (e) {
      newTab.close(); // Close tab on error
      rethrow;
    }
  }
}


