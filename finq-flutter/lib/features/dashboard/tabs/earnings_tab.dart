import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';

import '../dashboard_providers.dart';

class EarningsTab extends ConsumerStatefulWidget {
  const EarningsTab({
    required this.ticker,
    super.key,
  });

  final String ticker;

  @override
  ConsumerState<EarningsTab> createState() => _EarningsTabState();
}

class _EarningsTabState extends ConsumerState<EarningsTab> {
  var _chartType = _ChartType.line;
  var _aggregation = _Aggregation.quarterly;

  @override
  Widget build(BuildContext context) {
    final tickerData = ref.watch(tickerDataProvider);

    return tickerData.when(
      data: (data) {
        final earningsData = _parseEarningsData(data);
        
        if (earningsData.isEmpty) {
          return Center(
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Text(
                  'No earnings data available for ${widget.ticker}.',
                  style: TextStyle(color: Colors.grey.shade600),
                ),
              ),
            ),
          );
        }

        final chartData = _aggregateData(earningsData);
        final lastEarnings = _getLastEarnings(earningsData);
        final nextEarnings = _getNextEarnings(earningsData);

        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Historical EPS Trend Chart
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Historical EPS Trend',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          // Aggregation selector
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Aggregation',
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                SegmentedButton<_Aggregation>(
                                  segments: const [
                                    ButtonSegment(
                                      value: _Aggregation.quarterly,
                                      label: Text('Quarterly'),
                                    ),
                                    ButtonSegment(
                                      value: _Aggregation.yearly,
                                      label: Text('Yearly'),
                                    ),
                                  ],
                                  selected: {_aggregation},
                                  onSelectionChanged: (values) {
                                    setState(() => _aggregation = values.first);
                                  },
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 16),
                          // Chart type selector
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Chart Type',
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                const SizedBox(height: 8),
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
                          ),
                        ],
                      ),
                      const SizedBox(height: 24),
                      if (chartData.isNotEmpty)
                        SizedBox(
                          height: 300,
                          child: _chartType == _ChartType.line
                              ? _buildLineChart(chartData)
                              : _buildBarChart(chartData),
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              // Last Quarter's Earnings
              if (lastEarnings != null)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Last Quarter\'s Earnings',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Wrap(
                          spacing: 32,
                          runSpacing: 16,
                          children: [
                            _buildStatItem(
                              'Date',
                              DateFormat.yMMMMd().format(lastEarnings.date),
                            ),
                            _buildStatItem(
                              'Reported EPS',
                              '\$${lastEarnings.reportedEPS.toStringAsFixed(2)}',
                            ),
                            _buildStatItem(
                              'Estimated EPS',
                              '\$${lastEarnings.estimatedEPS.toStringAsFixed(2)}',
                            ),
                            if (lastEarnings.surprise != null)
                              _buildStatItem(
                                'Surprise (%)',
                                '${lastEarnings.surprise! > 0 ? '+' : ''}${lastEarnings.surprise!.toStringAsFixed(2)}%',
                                color: lastEarnings.surprise! > 0
                                    ? Colors.green
                                    : Colors.red,
                              ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              if (lastEarnings != null) const SizedBox(height: 16),
              // Next Earnings
              if (nextEarnings != null)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Next Earnings',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Wrap(
                          spacing: 32,
                          runSpacing: 16,
                          children: [
                            _buildStatItem(
                              'Date',
                              DateFormat.yMMMMd().format(nextEarnings.date),
                            ),
                            _buildStatItem(
                              'Estimated EPS',
                              '\$${nextEarnings.estimatedEPS.toStringAsFixed(2)}',
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
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
                  'Failed to load earnings data',
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

  Widget _buildStatItem(String label, String value, {Color? color}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildLineChart(List<_ChartDataPoint> data) {
    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: true,
          horizontalInterval: 1,
          verticalInterval: 1,
        ),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 40,
              getTitlesWidget: (value, meta) {
                return Text(
                  value.toStringAsFixed(2),
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
          // Reported EPS line
          LineChartBarData(
            spots: data
                .asMap()
                .entries
                .map((e) => FlSpot(e.key.toDouble(), e.value.reportedEPS))
                .toList(),
            isCurved: true,
            color: Colors.blue,
            barWidth: 2,
            dotData: FlDotData(show: true),
            belowBarData: BarAreaData(show: false),
          ),
          // Estimated EPS line
          LineChartBarData(
            spots: data
                .asMap()
                .entries
                .map((e) => FlSpot(e.key.toDouble(), e.value.estimatedEPS))
                .toList(),
            isCurved: true,
            color: Colors.green,
            barWidth: 2,
            dotData: FlDotData(show: true),
            dashArray: [5, 5],
            belowBarData: BarAreaData(show: false),
          ),
        ],
      ),
    );
  }

  Widget _buildBarChart(List<_ChartDataPoint> data) {
    return BarChart(
      BarChartData(
        gridData: FlGridData(show: true),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 40,
              getTitlesWidget: (value, meta) {
                return Text(
                  value.toStringAsFixed(2),
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
                toY: e.value.reportedEPS,
                color: Colors.blue,
                width: 12,
              ),
              BarChartRodData(
                toY: e.value.estimatedEPS,
                color: Colors.green,
                width: 12,
              ),
            ],
          );
        }).toList(),
      ),
    );
  }

  List<_EarningsDataPoint> _parseEarningsData(Map<String, dynamic> data) {
    final earningsDates = data['earnings_dates'];
    if (earningsDates == null || earningsDates is! List) {
      return [];
    }

    final parsed = <_EarningsDataPoint>[];
    for (final item in earningsDates) {
      if (item is! Map) continue;

      final reportedEPS = _getDouble(
        item['Reported EPS'] ?? item['reportedEPS'] ?? item['ReportedEPS'],
      );
      final estimatedEPS = _getDouble(
        item['EPS Estimate'] ?? item['estimatedEPS'] ?? item['EPSEstimate'],
      );
      final surprise = _getDouble(
        item['Surprise(%)'] ?? item['surprise'] ?? item['Surprise'],
      );

      if (reportedEPS == null || estimatedEPS == null) continue;

      final dateValue =
          item['Earnings Date'] ?? item['EarningsDate'] ?? item['earningsDate'] ?? item['date'] ?? item['Date'];
      if (dateValue == null) continue;

      DateTime? date;
      if (dateValue is String) {
        date = DateTime.tryParse(dateValue);
      } else if (dateValue is DateTime) {
        date = dateValue;
      }

      if (date == null) continue;

      parsed.add(_EarningsDataPoint(
        date: date,
        reportedEPS: reportedEPS,
        estimatedEPS: estimatedEPS,
        surprise: surprise,
      ));
    }

    parsed.sort((a, b) => a.date.compareTo(b.date));
    return parsed;
  }

  double? _getDouble(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }

  List<_ChartDataPoint> _aggregateData(List<_EarningsDataPoint> data) {
    if (_aggregation == _Aggregation.quarterly) {
      return data.map((e) {
        return _ChartDataPoint(
          period: DateFormat('MMM yyyy').format(e.date),
          reportedEPS: e.reportedEPS,
          estimatedEPS: e.estimatedEPS,
        );
      }).toList();
    } else {
      // Yearly aggregation
      final yearlyMap = <int, _YearlyData>{};
      for (final item in data) {
        final year = item.date.year;
        yearlyMap.putIfAbsent(year, () => _YearlyData());
        yearlyMap[year]!.reported.add(item.reportedEPS);
        yearlyMap[year]!.estimated.add(item.estimatedEPS);
      }

      final result = <_ChartDataPoint>[];
      final sortedYears = yearlyMap.keys.toList()..sort();
      for (final year in sortedYears) {
        final data = yearlyMap[year]!;
        result.add(_ChartDataPoint(
          period: year.toString(),
          reportedEPS: data.reported.reduce((a, b) => a + b) / data.reported.length,
          estimatedEPS: data.estimated.reduce((a, b) => a + b) / data.estimated.length,
        ));
      }
      return result;
    }
  }

  _EarningsDataPoint? _getLastEarnings(List<_EarningsDataPoint> data) {
    final now = DateTime.now();
    final past = data.where((e) => e.date.isBefore(now)).toList();
    if (past.isEmpty) return null;
    past.sort((a, b) => b.date.compareTo(a.date));
    return past.first;
  }

  _EarningsDataPoint? _getNextEarnings(List<_EarningsDataPoint> data) {
    final now = DateTime.now();
    final future = data.where((e) => e.date.isAfter(now)).toList();
    if (future.isEmpty) return null;
    future.sort((a, b) => a.date.compareTo(b.date));
    return future.first;
  }
}

class _EarningsDataPoint {
  const _EarningsDataPoint({
    required this.date,
    required this.reportedEPS,
    required this.estimatedEPS,
    this.surprise,
  });

  final DateTime date;
  final double reportedEPS;
  final double estimatedEPS;
  final double? surprise;
}

class _ChartDataPoint {
  const _ChartDataPoint({
    required this.period,
    required this.reportedEPS,
    required this.estimatedEPS,
  });

  final String period;
  final double reportedEPS;
  final double estimatedEPS;
}

class _YearlyData {
  final reported = <double>[];
  final estimated = <double>[];
}

enum _ChartType { line, bar }

enum _Aggregation { quarterly, yearly }
