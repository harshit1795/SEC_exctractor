import 'package:flutter_test/flutter_test.dart';
import 'package:finq_flutter/features/dashboard/utils/metric_calculations.dart';
import 'package:finq_flutter/data/financial_hierarchies.dart';

void main() {
  group('MetricCalculations', () {
    test('calculateMetricData should return correct metric data', () {
      final periods = [
        PeriodData(
          period: '2024Q1',
          metrics: {'Revenue': 100.0},
        ),
        PeriodData(
          period: '2023Q4',
          metrics: {'Revenue': 80.0},
        ),
      ];

      final result = MetricCalculations.calculateMetricData(
        periods,
        'Revenue',
        [],
      );

      expect(result, isNotNull);
      expect(result!.currentValue, 100.0);
      expect(result.previousValue, 80.0);
      expect(result.percentChange, 25.0); // (100 - 80) / 80 * 100 = 25%
      expect(result.trend, TrendDirection.up);
    });

    test('calculateMetricData should handle missing previous value', () {
      final periods = [
        PeriodData(
          period: '2024Q1',
          metrics: {'Revenue': 100.0},
        ),
      ];

      final result = MetricCalculations.calculateMetricData(
        periods,
        'Revenue',
        [],
      );

      expect(result, isNotNull);
      expect(result!.currentValue, 100.0);
      expect(result.previousValue, isNull);
      expect(result.percentChange, isNull);
      expect(result.trend, TrendDirection.noData);
    });

    test('calculateDerivedMetric should calculate subtraction correctly', () {
      final periods = [
        PeriodData(period: '2024Q1', metrics: {}), // Metrics not used for subtraction logic directly from periods list in this helper, but passed via metricsData map usually.
        // Wait, calculateDerivedMetric USES periods list for date, but implementation details check metricsData map.
        // Let's verify implementation of calculateDerivedMetric in source.
        // It calls _calculateSubtraction(node, metricsData, periods). 
      ];

      final node = FinancialNode(
        id: 'gross_profit',
        displayName: 'Gross Profit',
        category: NodeCategory.profit,
        type: NodeType.calculated,
        calculationType: CalculationType.subtract,
        childMetricNames: ['Total Revenue', 'Cost of Revenue'],
      );

      final metricsData = {
        'total_revenue': MetricData(
          currentValue: 1000.0,
          trend: TrendDirection.up,
          period: '2024Q1',
          previousValue: 800.0,
        ),
        'cost_of_revenue': MetricData(
          currentValue: 400.0,
          trend: TrendDirection.up,
          period: '2024Q1',
          previousValue: 300.0,
        ),
      };

      final result = MetricCalculations.calculateDerivedMetric(
        node,
        metricsData,
        periods,
      );

      expect(result, isNotNull);
      expect(result!.currentValue, 600.0); // 1000 - 400
      expect(result.previousValue, 500.0); // 800 - 300
      expect(result.percentChange, 20.0); // (600 - 500) / 500 * 100
      expect(result.trend, TrendDirection.up);
    });
  });
}
