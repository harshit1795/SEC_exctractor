import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

/// Service for managing user preferences for metric selections
/// Storage structure: { ticker: { category: [metrics] } }
/// Example: { "AAPL": { "IncomeStatement": ["Revenue", "Net Income"] } }
class PreferencesService {
  static const String _storageKey = 'finq_metric_preferences';
  
  SharedPreferences? _prefs;
  Map<String, Map<String, List<String>>> _cache = {};
  String? _userId;

  /// Initialize the service with optional user ID for user-specific preferences
  Future<void> initialize(String? userId) async {
    _userId = userId;
    _prefs = await SharedPreferences.getInstance();
    await _loadPreferences();
  }

  String get _key => _userId != null 
      ? '${_storageKey}_$_userId' 
      : _storageKey;

  /// Load preferences from storage
  Future<void> _loadPreferences() async {
    if (_prefs == null) return;
    
    try {
      final jsonString = _prefs!.getString(_key);
      if (jsonString == null) {
        _cache = {};
        return;
      }
      
      final decoded = jsonDecode(jsonString) as Map<String, dynamic>;
      _cache = decoded.map((ticker, value) {
        final categoryMap = (value as Map<String, dynamic>).map((category, metrics) {
          return MapEntry(category, List<String>.from(metrics as List));
        });
        return MapEntry(ticker, categoryMap);
      });
    } catch (e) {
      print('Error loading preferences: $e');
      _cache = {};
    }
  }

  /// Save preferences to storage
  Future<void> _savePreferences() async {
    if (_prefs == null) return;
    
    try {
      final jsonString = jsonEncode(_cache);
      await _prefs!.setString(_key, jsonString);
    } catch (e) {
      print('Error saving preferences: $e');
    }
  }

  /// Get saved metrics for a specific ticker and category
  List<String> getMetrics(String ticker, String category) {
    if (ticker.isEmpty || category.isEmpty) return [];
    final tickerKey = ticker.toUpperCase();
    return _cache[tickerKey]?[category] ?? [];
  }

  /// Save metrics for a specific ticker and category
  Future<void> saveMetrics(
    String ticker,
    String category,
    List<String> metrics,
  ) async {
    if (ticker.isEmpty || category.isEmpty) return;
    
    final tickerKey = ticker.toUpperCase();
    
    if (!_cache.containsKey(tickerKey)) {
      _cache[tickerKey] = {};
    }
    
    _cache[tickerKey]![category] = List<String>.from(metrics);
    await _savePreferences();
  }

  /// Clear preferences for a specific category
  Future<void> clearCategory(String ticker, String category) async {
    if (ticker.isEmpty || category.isEmpty) return;
    
    final tickerKey = ticker.toUpperCase();
    
    if (_cache.containsKey(tickerKey)) {
      _cache[tickerKey]!.remove(category);
      
      // Remove ticker entry if no categories left
      if (_cache[tickerKey]!.isEmpty) {
        _cache.remove(tickerKey);
      }
      
      await _savePreferences();
    }
  }

  /// Clear all preferences for a specific ticker
  Future<void> clearTicker(String ticker) async {
    if (ticker.isEmpty) return;
    
    final tickerKey = ticker.toUpperCase();
    _cache.remove(tickerKey);
    await _savePreferences();
  }

  /// Clear all preferences
  Future<void> clearAll() async {
    _cache = {};
    await _savePreferences();
  }

  /// Check if preferences exist for a specific ticker and category
  bool hasPreferences(String ticker, String category) {
    if (ticker.isEmpty || category.isEmpty) return false;
    final tickerKey = ticker.toUpperCase();
    final metrics = _cache[tickerKey]?[category];
    return metrics != null && metrics.isNotEmpty;
  }

  /// Get all preferences (for debugging or export)
  Map<String, Map<String, List<String>>> getAllPreferences() {
    return Map.from(_cache);
  }
}
