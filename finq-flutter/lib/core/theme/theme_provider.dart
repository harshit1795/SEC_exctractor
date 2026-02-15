import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flex_color_scheme/flex_color_scheme.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../di/providers.dart';

/// Manages the app's color scheme selection with persistence
class ThemeNotifier extends StateNotifier<FlexScheme> {
  ThemeNotifier(this._prefs) : super(_loadTheme(_prefs));

  final SharedPreferences _prefs;

  static const String _themeKey = 'theme_scheme';
  static const FlexScheme _defaultTheme = FlexScheme.green;

  /// Load theme from SharedPreferences
  static FlexScheme _loadTheme(SharedPreferences prefs) {
    final themeName = prefs.getString(_themeKey);
    if (themeName == null) return _defaultTheme;

    try {
      return FlexScheme.values.firstWhere(
        (scheme) => scheme.name == themeName,
        orElse: () => _defaultTheme,
      );
    } catch (e) {
      return _defaultTheme;
    }
  }

  /// Set new theme and persist to SharedPreferences
  Future<void> setTheme(FlexScheme scheme) async {
    await _prefs.setString(_themeKey, scheme.name);
    state = scheme;
  }

  /// Get display name for a theme
  static String getThemeName(FlexScheme scheme) {
    // Convert camelCase to Title Case
    final name = scheme.name;
    final result = name.replaceAllMapped(
      RegExp(r'([A-Z])'),
      (match) => ' ${match.group(0)}',
    );
    return result[0].toUpperCase() + result.substring(1);
  }
}

/// Provider for the current theme scheme
final themeProvider = StateNotifierProvider<ThemeNotifier, FlexScheme>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return ThemeNotifier(prefs);
});
