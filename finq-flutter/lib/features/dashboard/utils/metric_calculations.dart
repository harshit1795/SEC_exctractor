/// Utility functions for calculating financial metrics, trends, and derived values
import '../../../data/financial_hierarchies.dart';

enum TrendDirection { up, down, flat, noData }

class MetricData {
  const MetricData({
    required this.currentValue,
    this.previousValue,
    this.percentChange,
    required this.trend,
    required this.period,
    this.isCalculated = false,
    this.isPartial = false,
  });

  final double currentValue;
  final double? previousValue;
  final double? percentChange;
  final TrendDirection trend;
  final String period; // e.g., "2025Q1"
  final bool isCalculated; // True if derived from other metrics
  final bool isPartial; // True if some child metrics are missing

  /// Format value as currency
  String formatValue({bool compact = false}) {
    if (compact) {
      if (currentValue.abs() >= 1e12) {
        return '\$${(currentValue / 1e12).toStringAsFixed(2)}T';
      } else if (currentValue.abs() >= 1e9) {
        return '\$${(currentValue / 1e9).toStringAsFixed(2)}B';
      } else if (currentValue.abs() >= 1e6) {
        return '\$${(currentValue / 1e6).toStringAsFixed(2)}M';
      } else if (currentValue.abs() >= 1e3) {
        return '\$${(currentValue / 1e3).toStringAsFixed(2)}K';
      }
    }
    return '\$${currentValue.toStringAsFixed(2)}';
  }

  /// Format percentage change
  String formatPercentChange() {
    if (percentChange == null) return 'N/A';
    final sign = percentChange! >= 0 ? '+' : '';
    return '$sign${percentChange!.toStringAsFixed(2)}%';
  }

  /// Get trend icon
  String getTrendIcon() {
    switch (trend) {
      case TrendDirection.up:
        return '▲';
      case TrendDirection.down:
        return '▼';
      case TrendDirection.flat:
        return '─';
      case TrendDirection.noData:
        return '?';
    }
  }
}

class MetricCalculations {
  /// Calculate metric data from period data
  /// 
  /// Extracts current and previous values, calculates percentage change,
  /// and determines trend direction
  static MetricData? calculateMetricData(
    List<PeriodData> periods,
    String metricName,
    List<String> alternativeNames,
  ) {
    if (periods.isEmpty) return null;

    // Find metric in latest period (first in list, assuming sorted desc)
    final latestPeriod = periods.first;
    double? currentValue;
    
    // Try to find the metric by name or alternative names
    currentValue = latestPeriod.metrics[metricName];
    if (currentValue == null) {
      for (final altName in alternativeNames) {
        currentValue = latestPeriod.metrics[altName];
        if (currentValue != null) break;
      }
    }

    if (currentValue == null) return null;

    // Find previous period value (if available)
    double? previousValue;
    if (periods.length > 1) {
      final prevPeriod = periods[1];
      previousValue = prevPeriod.metrics[metricName];
      if (previousValue == null) {
        for (final altName in alternativeNames) {
          previousValue = prevPeriod.metrics[altName];
          if (previousValue != null) break;
        }
      }
    }

    // Calculate percentage change
    double? percentChange;
    if (previousValue != null && previousValue != 0) {
      percentChange = ((currentValue - previousValue) / previousValue.abs()) * 100;
    }

    // Determine trend direction
    final trend = _determineTrend(percentChange);

    return MetricData(
      currentValue: currentValue,
      previousValue: previousValue,
      percentChange: percentChange,
      trend: trend,
      period: latestPeriod.period,
    );
  }

  /// Calculate derived metric from a formula
  /// 
  /// Handles calculations like:
  /// - Gross Profit = Revenue - COGS
  /// - Operating Income = Gross Profit - Operating Expenses
  /// - Net Income = Income Before Tax - Tax Expense
  static MetricData? calculateDerivedMetric(
    FinancialNode node,
    Map<String, MetricData> metricsData,
    List<PeriodData> periods,
  ) {
    if (node.calculationType == CalculationType.none) {
      return null;
    }

    if (periods.isEmpty) return null;

    switch (node.calculationType) {
      case CalculationType.sum:
        return _calculateSum(node, metricsData, periods.first.period);
      
      case CalculationType.subtract:
        return _calculateSubtraction(node, metricsData, periods);
      
      case CalculationType.custom:
        return _calculateCustom(node, metricsData, periods);
      
      case CalculationType.none:
        return null;
    }
  }

  /// Roll up child metrics to parent total
  static MetricData? rollupChildMetrics(
    List<FinancialNode> children,
    Map<String, MetricData> metricsData,
    String period,
  ) {
    double sum = 0.0;
    double? previousSum;
    bool hasAnyValue = false;
    bool hasAllValues = true;
    int foundCount = 0;

    for (final child in children) {
      final childData = metricsData[child.id];
      if (childData != null) {
        sum += childData.currentValue;
        hasAnyValue = true;
        foundCount++;
        
        if (previousSum != null && childData.previousValue != null) {
          previousSum = previousSum + childData.previousValue!;
        } else if (childData.previousValue != null) {
          previousSum = childData.previousValue;
        } else {
          previousSum = null;
        }
      } else {
        hasAllValues = false;
      }
    }

    if (!hasAnyValue) return null;

    // Calculate percentage change
    double? percentChange;
    if (previousSum != null && previousSum != 0) {
      percentChange = ((sum - previousSum) / previousSum.abs()) * 100;
    }

    final trend = _determineTrend(percentChange);

    return MetricData(
      currentValue: sum,
      previousValue: previousSum,
      percentChange: percentChange,
      trend: trend,
      period: period,
      isCalculated: true,
      isPartial: !hasAllValues && foundCount > 0,
    );
  }

  /// Calculate sum of child metrics
  static MetricData? _calculateSum(
    FinancialNode node,
    Map<String, MetricData> metricsData,
    String period,
  ) {
    return rollupChildMetrics(node.children, metricsData, period);
  }

  /// Calculate subtraction (A - B)
  static MetricData? _calculateSubtraction(
    FinancialNode node,
    Map<String, MetricData> metricsData,
    List<PeriodData> periods,
  ) {
    // For subtraction, use childMetricNames
    if (node.childMetricNames.length < 2) return null;

    final minuendName = node.childMetricNames[0]; // A
    final subtrahendName = node.childMetricNames[1]; // B

    // Find minuend in metricsData
    MetricData? minuendData;
    MetricData? subtrahendData;

    for (final entry in metricsData.entries) {
      final nodeData = entry.value;
      // Check if this metric matches minuend or subtrahend
      if (entry.key.contains(minuendName) || 
          minuendName.contains(entry.key)) {
        minuendData = nodeData;
      }
      if (entry.key.contains(subtrahendName) || 
          subtrahendName.contains(entry.key)) {
        subtrahendData = nodeData;
      }
    }

    if (minuendData == null || subtrahendData == null) return null;

    final currentValue = minuendData.currentValue - subtrahendData.currentValue;
    
    double? previousValue;
    if (minuendData.previousValue != null && subtrahendData.previousValue != null) {
      previousValue = minuendData.previousValue! - subtrahendData.previousValue!;
    }

    double? percentChange;
    if (previousValue != null && previousValue != 0) {
      percentChange = ((currentValue - previousValue) / previousValue.abs()) * 100;
    }

    final trend = _determineTrend(percentChange);

    return MetricData(
      currentValue: currentValue,
      previousValue: previousValue,
      percentChange: percentChange,
      trend: trend,
      period: periods.first.period,
      isCalculated: true,
    );
  }

  /// Calculate custom formulas (e.g., Income Before Tax)
  static MetricData? _calculateCustom(
    FinancialNode node,
    Map<String, MetricData> metricsData,
    List<PeriodData> periods,
  ) {
    // Handle specific custom calculations
    if (node.id == 'income_before_tax') {
      // Income Before Tax = Operating Income + Other Income/Expenses
      final opIncome = metricsData['operating_income'];
      final otherIncome = metricsData['other_items'];
      
      if (opIncome == null) return null;

      double currentValue = opIncome.currentValue;
      double? previousValue = opIncome.previousValue;

      if (otherIncome != null) {
        currentValue += otherIncome.currentValue;
        if (previousValue != null && otherIncome.previousValue != null) {
          previousValue = previousValue + otherIncome.previousValue!;
        }
      }

      double? percentChange;
      if (previousValue != null && previousValue != 0) {
        percentChange = ((currentValue - previousValue) / previousValue.abs()) * 100;
      }

      final trend = _determineTrend(percentChange);

      return MetricData(
        currentValue: currentValue,
        previousValue: previousValue,
        percentChange: percentChange,
        trend: trend,
        period: periods.first.period,
        isCalculated: true,
      );
    }

    return null;
  }

  /// Determine trend direction from percentage change
  static TrendDirection _determineTrend(double? percentChange) {
    if (percentChange == null) return TrendDirection.noData;
    
    const threshold = 1.0; // 1% threshold for "flat"
    
    if (percentChange > threshold) {
      return TrendDirection.up;
    } else if (percentChange < -threshold) {
      return TrendDirection.down;
    } else {
      return TrendDirection.flat;
    }
  }

  /// Calculate financial ratios
  static Map<String, MetricData?> calculateRatios(
    Map<String, MetricData> metricsData,
    String period,
  ) {
    final ratios = <String, MetricData?>{};

    // Debt-to-Equity Ratio = Total Debt / Shareholder Equity
    final totalLiabilities = metricsData['total_liabilities'];
    final shareholderEquity = metricsData['shareholders_equity'];
    if (totalLiabilities != null && shareholderEquity != null && shareholderEquity.currentValue != 0) {
      final debtToEquity = totalLiabilities.currentValue / shareholderEquity.currentValue;
      double? prevDebtToEquity;
      if (totalLiabilities.previousValue != null && 
          shareholderEquity.previousValue != null && 
          shareholderEquity.previousValue != 0) {
        prevDebtToEquity = totalLiabilities.previousValue! / shareholderEquity.previousValue!;
      }
      
      double? percentChange;
      if (prevDebtToEquity != null && prevDebtToEquity != 0) {
        percentChange = ((debtToEquity - prevDebtToEquity) / prevDebtToEquity.abs()) * 100;
      }

      ratios['debt_to_equity'] = MetricData(
        currentValue: debtToEquity,
        previousValue: prevDebtToEquity,
        percentChange: percentChange,
        trend: _determineTrend(percentChange),
        period: period,
        isCalculated: true,
      );
    }

    // Current Ratio = Current Assets / Current Liabilities
    final currentAssets = metricsData['current_assets'];
    final currentLiabilities = metricsData['current_liabilities'];
    if (currentAssets != null && currentLiabilities != null && currentLiabilities.currentValue != 0) {
      final currentRatio = currentAssets.currentValue / currentLiabilities.currentValue;
      double? prevCurrentRatio;
      if (currentAssets.previousValue != null && 
          currentLiabilities.previousValue != null && 
          currentLiabilities.previousValue != 0) {
        prevCurrentRatio = currentAssets.previousValue! / currentLiabilities.previousValue!;
      }
      
      double? percentChange;
      if (prevCurrentRatio != null && prevCurrentRatio != 0) {
        percentChange = ((currentRatio - prevCurrentRatio) / prevCurrentRatio.abs()) * 100;
      }

      ratios['current_ratio'] = MetricData(
        currentValue: currentRatio,
        previousValue: prevCurrentRatio,
        percentChange: percentChange,
        trend: _determineTrend(percentChange),
        period: period,
        isCalculated: true,
      );
    }

    // Working Capital = Current Assets - Current Liabilities
    if (currentAssets != null && currentLiabilities != null) {
      final workingCapital = currentAssets.currentValue - currentLiabilities.currentValue;
      double? prevWorkingCapital;
      if (currentAssets.previousValue != null && currentLiabilities.previousValue != null) {
        prevWorkingCapital = currentAssets.previousValue! - currentLiabilities.previousValue!;
      }
      
      double? percentChange;
      if (prevWorkingCapital != null && prevWorkingCapital != 0) {
        percentChange = ((workingCapital - prevWorkingCapital) / prevWorkingCapital.abs()) * 100;
      }

      ratios['working_capital'] = MetricData(
        currentValue: workingCapital,
        previousValue: prevWorkingCapital,
        percentChange: percentChange,
        trend: _determineTrend(percentChange),
        period: period,
        isCalculated: true,
      );
    }

    // ROE = Net Income / Shareholder Equity
    final netIncome = metricsData['net_income'];
    if (netIncome != null && shareholderEquity != null && shareholderEquity.currentValue != 0) {
      final roe = (netIncome.currentValue / shareholderEquity.currentValue) * 100;
      double? prevRoe;
      if (netIncome.previousValue != null && 
          shareholderEquity.previousValue != null && 
          shareholderEquity.previousValue != 0) {
        prevRoe = (netIncome.previousValue! / shareholderEquity.previousValue!) * 100;
      }
      
      double? percentChange;
      if (prevRoe != null && prevRoe != 0) {
        percentChange = ((roe - prevRoe) / prevRoe.abs()) * 100;
      }

      ratios['roe'] = MetricData(
        currentValue: roe,
        previousValue: prevRoe,
        percentChange: percentChange,
        trend: _determineTrend(percentChange),
        period: period,
        isCalculated: true,
      );
    }

    // ROA = Net Income / Total Assets
    final totalAssets = metricsData['total_assets'];
    if (netIncome != null && totalAssets != null && totalAssets.currentValue != 0) {
      final roa = (netIncome.currentValue / totalAssets.currentValue) * 100;
      double? prevRoa;
      if (netIncome.previousValue != null && 
          totalAssets.previousValue != null && 
          totalAssets.previousValue != 0) {
        prevRoa = (netIncome.previousValue! / totalAssets.previousValue!) * 100;
      }
      
      double? percentChange;
      if (prevRoa != null && prevRoa != 0) {
        percentChange = ((roa - prevRoa) / prevRoa.abs()) * 100;
      }

      ratios['roa'] = MetricData(
        currentValue: roa,
        previousValue: prevRoa,
        percentChange: percentChange,
        trend: _determineTrend(percentChange),
        period: period,
        isCalculated: true,
      );
    }

    return ratios;
  }
}

/// Data class for a period's metrics
class PeriodData {
  const PeriodData({
    required this.period,
    required this.metrics,
  });

  final String period;
  final Map<String, double> metrics;
}
