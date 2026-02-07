import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:finq_flutter/services/preferences_service.dart';

void main() {
  late PreferencesService service;

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    service = PreferencesService();
    await service.initialize(null);
  });

  group('PreferencesService', () {
    test('should save and load metrics', () async {
      const ticker = 'AAPL';
      const category = 'IncomeStatement';
      final metrics = ['Revenue', 'Net Income'];

      await service.saveMetrics(ticker, category, metrics);
      final loaded = service.getMetrics(ticker, category);

      expect(loaded, equals(metrics));
    });

    test('should return empty list for unknown ticker/category', () {
      final loaded = service.getMetrics('UNKNOWN', 'Category');
      expect(loaded, isEmpty);
    });

    test('should persist separate preferences for different tickers', () async {
      await service.saveMetrics('AAPL', 'Cat1', ['A', 'B']);
      await service.saveMetrics('GOOGL', 'Cat1', ['X', 'Y']);

      expect(service.getMetrics('AAPL', 'Cat1'), equals(['A', 'B']));
      expect(service.getMetrics('GOOGL', 'Cat1'), equals(['X', 'Y']));
    });

    test('should clear category preferences', () async {
      await service.saveMetrics('AAPL', 'Cat1', ['A']);
      await service.clearCategory('AAPL', 'Cat1');

      expect(service.getMetrics('AAPL', 'Cat1'), isEmpty);
    });

    test('should clear all preferences', () async {
      await service.saveMetrics('AAPL', 'Cat1', ['A']);
      await service.saveMetrics('GOOGL', 'Cat1', ['B']);

      await service.clearAll();

      expect(service.getMetrics('AAPL', 'Cat1'), isEmpty);
      expect(service.getMetrics('GOOGL', 'Cat1'), isEmpty);
    });
  });
}
