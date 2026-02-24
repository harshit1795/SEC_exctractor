import 'dart:convert';
import 'package:csv/csv.dart';
import 'package:flutter/foundation.dart';
import 'package:intl/intl.dart';
import 'package:universal_html/html.dart' as html;

/// Service for exporting data to CSV files
class CsvExportService {
  /// Export trend data to CSV
  static Future<void> exportTrendData({
    required String ticker,
    required String category,
    required List<String> periods,
    required Map<String, List<double?>> metricsData,
  }) async {
    // Build CSV data
    final csvData = <List<dynamic>>[];

    // Header row
    final header = ['Period', ...metricsData.keys];
    csvData.add(header);

    // Data rows
    for (var i = 0; i < periods.length; i++) {
      final row = <dynamic>[periods[i]];
      for (final metric in metricsData.keys) {
        final values = metricsData[metric];
        if (values != null && i < values.length) {
          row.add(values[i] ?? '');
        } else {
          row.add('');
        }
      }
      csvData.add(row);
    }

    // Convert to CSV string
    final csvString = const ListToCsvConverter().convert(csvData);

    // Generate filename
    final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final filename = '${ticker}_${category}_trend_$timestamp.csv';

    // Download file
    await _downloadCsv(csvString, filename);
  }

  /// Export snapshot data to CSV
  static Future<void> exportSnapshotData({
    required String ticker,
    required String category,
    required List<SnapshotRow> rows,
  }) async {
    // Build CSV data
    final csvData = <List<dynamic>>[];

    // Header row
    csvData.add(['Metric', 'Latest Value', 'Previous Value', 'Change', '% Change']);

    // Data rows
    for (final row in rows) {
      csvData.add([
        row.metric,
        row.latestValue ?? '',
        row.previousValue ?? '',
        row.change ?? '',
        row.percentChange != null ? '${row.percentChange}%' : '',
      ]);
    }

    // Convert to CSV string
    final csvString = const ListToCsvConverter().convert(csvData);

    // Generate filename
    final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
    final filename = '${ticker}_${category}_snapshot_$timestamp.csv';

    // Download file
    await _downloadCsv(csvString, filename);
  }

  /// Download CSV file (web and mobile compatible)
  static Future<void> _downloadCsv(String csvString, String filename) async {
    if (kIsWeb) {
      // Web: Create blob and trigger download
      final bytes = utf8.encode(csvString);
      final blob = html.Blob([bytes]);
      final url = html.Url.createObjectUrlFromBlob(blob);
      html.AnchorElement(href: url)
        ..setAttribute('download', filename)
        ..click();
      html.Url.revokeObjectUrl(url);
    } else {
      // Mobile: This would require platform-specific implementation
      // For now, we'll just print a message
      debugPrint('CSV export on mobile would save to: $filename');
      // TODO: Implement mobile file saving using path_provider + share_plus
      throw UnimplementedError(
        'CSV export on mobile is not yet implemented. Please use the web version.',
      );
    }
  }
}

/// Data class for snapshot rows
class SnapshotRow {
  const SnapshotRow({
    required this.metric,
    this.latestValue,
    this.previousValue,
    this.change,
    this.percentChange,
  });

  final String metric;
  final String? latestValue;
  final String? previousValue;
  final String? change;
  final String? percentChange;
}
