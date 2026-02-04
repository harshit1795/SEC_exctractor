import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';

import '../dashboard_providers.dart';

class TrendTab extends ConsumerStatefulWidget {
  const TrendTab({
    required this.ticker,
    required this.category,
    super.key,
  });

  final String ticker;
  final String category;

  @override
  ConsumerState<TrendTab> createState() => _TrendTabState();
}

class _TrendTabState extends ConsumerState<TrendTab> {
  var _chartType = _ChartType.line;
  final _selectedMetrics = <String>{};

  @override
  Widget build(BuildContext context) {
    if (widget.category.isEmpty) {
      return const Center(
        child: Card(
          child: Padding(
            padding: EdgeInsets.all(32),
            child: Text('Select a category to view trend analysis.'),
          ),
        ),
      );
    }

    final fundamentals = ref.watch(fundamentalsProvider);

    return fundamentals.when(
      data: (data) {
        final parsed = _parseFundamentalsData(data);
        final allMetrics = parsed.metrics.toList()..sort();

        if (allMetrics.isEmpty) {
          return const Center(
            child: Card(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: Text('No metrics available for this category.'),
              ),
            ),
          );
        }

        // Auto-select first 3 metrics if none selected
        if (_selectedMetrics.isEmpty && allMetrics.isNotEmpty) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            setState(() {
              _selectedMetrics.addAll(allMetrics.take(3));
            });
          });
        }

        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Metrics to Plot',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: allMetrics.map((metric) {
                          return FilterChip(
                            label: Text(metric),
                            selected: _selectedMetrics.contains(metric),
                            onSelected: (selected) {
                              setState(() {
                                if (selected) {
                                  _selectedMetrics.add(metric);
                                } else {
                                  _selectedMetrics.remove(metric);
                                }
                              });
                            },
                          );
                        }).toList(),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          const Text(
                            'Chart Type:',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(width: 8),
                          SegmentedButton<_ChartType>(
                            segments: const [
                              ButtonSegment(
                                value: _ChartType.line,
                                label: Text('Line'),
                              ),
                              ButtonSegment(
                                value: _ChartType.bar,
                                label: Text('Bar'),
                              ),
                            ],
                            selected: {_chartType},
                            onSelectionChanged: (values) {
                              setState(() => _chartType = values.first);
                            },
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              ..._selectedMetrics.map((metric) {
                final metricData = parsed.data
                    .map((period) => _MetricDataPoint(
                          period: period.period,
                          value: period.metrics[metric] ?? 0,
                        ))
                    .toList();

                return Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            metric,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 16),
                          SizedBox(
                            height: 250,
                            child: _chartType == _ChartType.line
                                ? _buildLineChart(metricData)
                                : _buildBarChart(metricData),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              }),
            ],
          ),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline, size: 48, color: Colors.red),
                const SizedBox(height: 16),
                Text(
                  'Failed to load trend data',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey.shade700,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  error.toString(),
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade600,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLineChart(List<_MetricDataPoint> data) {
    return LineChart(
      LineChartData(
        gridData: FlGridData(show: true),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 60,
              getTitlesWidget: (value, meta) {
                return Text(
                  _formatValue(value),
                  style: const TextStyle(fontSize: 10),
                );
              },
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 30,
              getTitlesWidget: (value, meta) {
                final index = value.toInt();
                if (index >= 0 && index < data.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      data[index].period,
                      style: const TextStyle(fontSize: 10),
                    ),
                  );
                }
                return const Text('');
              },
            ),
          ),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: true),
        lineBarsData: [
          LineChartBarData(
            spots: data
                .asMap()
                .entries
                .map((e) => FlSpot(e.key.toDouble(), e.value.value))
                .toList(),
            isCurved: true,
            color: Colors.blue,
            barWidth: 2,
            dotData: FlDotData(show: true),
          ),
        ],
      ),
    );
  }

  Widget _buildBarChart(List<_MetricDataPoint> data) {
    return BarChart(
      BarChartData(
        gridData: FlGridData(show: true),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 60,
              getTitlesWidget: (value, meta) {
                return Text(
                  _formatValue(value),
                  style: const TextStyle(fontSize: 10),
                );
              },
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 30,
              getTitlesWidget: (value, meta) {
                final index = value.toInt();
                if (index >= 0 && index < data.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      data[index].period,
                      style: const TextStyle(fontSize: 10),
                    ),
                  );
                }
                return const Text('');
              },
            ),
          ),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: true),
        barGroups: data.asMap().entries.map((e) {
          return BarChartGroupData(
            x: e.key,
            barRods: [
              BarChartRodData(
                toY: e.value.value,
                color: Colors.blue,
                width: 20,
              ),
            ],
          );
        }).toList(),
      ),
    );
  }

  String _formatValue(double value) {
    if (value.abs() >= 1e9) {
      return '\$${(value / 1e9).toStringAsFixed(1)}B';
    } else if (value.abs() >= 1e6) {
      return '\$${(value / 1e6).toStringAsFixed(1)}M';
    } else if (value.abs() >= 1e3) {
      return '\$${(value / 1e3).toStringAsFixed(1)}K';
    }
    return value.toStringAsFixed(0);
  }

  _FundamentalsData _parseFundamentalsData(Map<String, dynamic> data) {
    final dataArray = data['data'] ?? data;
    if (dataArray is! List) {
      return _FundamentalsData(metrics: {}, data: []);
    }

    final filtered = dataArray.where((item) {
      if (item is! Map) return false;
      final itemCategory = item['Category'] ?? item['category'] ?? '';
      final itemTicker = item['Ticker'] ?? item['ticker'] ?? '';
      return itemCategory == widget.category &&
          itemTicker.toString().toUpperCase() == widget.ticker.toUpperCase();
    }).toList();

    final metrics = <String>{};
    final periodMap = <String, Map<String, double>>{};

    for (final item in filtered) {
      if (item is! Map) continue;

      final period = item['FiscalPeriod'] ??
          item['fiscalPeriod'] ??
          item['Date'] ??
          item['date'] ??
          '';
      final metric = item['Metric'] ?? item['metric'] ?? '';
      final value = (item['Value'] ?? item['value'] ?? 0).toDouble();

      if (period.isEmpty || metric.isEmpty) continue;

      metrics.add(metric);
      periodMap.putIfAbsent(period, () => {});
      periodMap[period]![metric] = value;
    }

    final periods = periodMap.keys.toList()
      ..sort((a, b) {
        // Sort by year and quarter
        final aParts = _parsePeriod(a);
        final bParts = _parsePeriod(b);
        if (aParts.$1 != bParts.$1) return aParts.$1.compareTo(bParts.$1);
        return aParts.$2.compareTo(bParts.$2);
      });

    final periodData = periods
        .map((period) => _PeriodData(
              period: period,
              metrics: periodMap[period]!,
            ))
        .toList();

    return _FundamentalsData(metrics: metrics, data: periodData);
  }

  (int, int) _parsePeriod(String period) {
    // Parse period like "2025 Q3" or "2025-03"
    if (period.contains('Q') || period.contains('q')) {
      final parts = period.toUpperCase().split('Q');
      final year = int.tryParse(parts[0].trim()) ?? 0;
      final quarter = int.tryParse(parts[1].trim()) ?? 0;
      return (year, quarter);
    } else if (period.contains('-')) {
      final parts = period.split('-');
      final year = int.tryParse(parts[0]) ?? 0;
      final month = int.tryParse(parts[1]) ?? 0;
      final quarter = (month / 3).ceil();
      return (year, quarter);
    }
    final year = int.tryParse(period.substring(0, 4)) ?? 0;
    return (year, 0);
  }
}

class _FundamentalsData {
  const _FundamentalsData({
    required this.metrics,
    required this.data,
  });

  final Set<String> metrics;
  final List<_PeriodData> data;
}

class _PeriodData {
  const _PeriodData({
    required this.period,
    required this.metrics,
  });

  final String period;
  final Map<String, double> metrics;
}

class _MetricDataPoint {
  const _MetricDataPoint({
    required this.period,
    required this.value,
  });

  final String period;
  final double value;
}

enum _ChartType { line, bar }
