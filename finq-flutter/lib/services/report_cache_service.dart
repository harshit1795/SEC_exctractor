import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Service to cache generated AI Health Reports locally using platform storage.
class ReportCacheService {
  static const _prefix = 'finq_health_report_';

  /// Generate a unique cache key based on the list of tickers
  static String _generateKey(List<String> tickers) {
    final sortedTickers = List<String>.from(tickers)..sort();
    final keyStr = sortedTickers.join('_');
    // Use md5 to keep the key short and safe for shared preferences
    return md5.convert(utf8.encode(keyStr)).toString();
  }

  /// Get a cached report for a list of tickers
  static Future<String?> getCachedReport(List<String> tickers) async {
    if (tickers.isEmpty) return null;
    final prefs = await SharedPreferences.getInstance();
    final key = '$_prefix${_generateKey(tickers)}';
    return prefs.getString(key);
  }

  /// Save a generated report to the local cache
  static Future<void> saveReport(List<String> tickers, String htmlContent) async {
    if (tickers.isEmpty) return;
    final prefs = await SharedPreferences.getInstance();
    final key = '$_prefix${_generateKey(tickers)}';
    // Optionally, we could store a timestamp to expire the cache, 
    // but for now we'll just store the raw HTML string
    await prefs.setString(key, htmlContent);
  }

  /// Delete a cached report for a list of tickers
  static Future<void> deleteReport(List<String> tickers) async {
    if (tickers.isEmpty) return;
    final prefs = await SharedPreferences.getInstance();
    final key = '$_prefix${_generateKey(tickers)}';
    await prefs.remove(key);
  }
}
