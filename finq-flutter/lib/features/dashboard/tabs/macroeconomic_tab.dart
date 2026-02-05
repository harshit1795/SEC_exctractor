import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';

import '../../../core/api/api_client.dart';
import '../../../core/di/providers.dart';
import '../widgets/tab_description_tooltip.dart';

class MacroeconomicTab extends ConsumerStatefulWidget {
  const MacroeconomicTab({super.key});

  @override
  ConsumerState<MacroeconomicTab> createState() => _MacroeconomicTabState();
}

class _MacroeconomicTabState extends ConsumerState<MacroeconomicTab> {
  final _selectedIndicators = <String>{'Real GDP', 'Inflation (CPI)', 'Unemployment Rate'};
  var _chartType = _ChartType.line;

  static const _indicators = {
    'GDP': _Indicator(id: 'GDP', freq: 'q', label: 'GDP'),
    'Real GDP': _Indicator(id: 'GDPC1', freq: 'q', label: 'Real GDP'),
    'Inflation (CPI)': _Indicator(id: 'CPIAUCSL', freq: 'm', label: 'Inflation (CPI)'),
    'Unemployment Rate': _Indicator(id: 'UNRATE', freq: 'm', label: 'Unemployment Rate'),
    '10-Year Treasury Yield': _Indicator(id: 'DGS10', freq: 'd', label: '10-Year Treasury Yield'),
    'Federal Funds Rate': _Indicator(id: 'FEDFUNDS', freq: 'd', label: 'Federal Funds Rate'),
  };

  @override
  Widget build(BuildContext context) {
    final seriesIds = _selectedIndicators
        .map((key) => _indicators[key]?.id)
        .where((id) => id != null)
        .join(',');

    final startDate = DateTime.now().subtract(const Duration(days: 1825)); // 5 years ago
    final endDate = DateTime.now();

    final fredDataFuture = ref.watch(
      _fredDataProvider((
        seriesIds: seriesIds,
        startDate: DateFormat('yyyy-MM-dd').format(startDate),
        endDate: DateFormat('yyyy-MM-dd').format(endDate),
      )),
    );

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Tab description tooltip
          Padding(
            padding: const EdgeInsets.only(left: 4, bottom: 8),
            child: Row(
              children: [
                Text(
                  'Macroeconomic Analysis',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
                const SizedBox(width: 8),
                const TabDescriptionTooltip(tabId: 'macro'),
              ],
            ),
          ),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.public, size: 28),
                      SizedBox(width: 12),
                      Text(
                        'Macroeconomic Data',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'View and analyze key economic indicators from the Federal Reserve Economic Data (FRED).',
                    style: TextStyle(
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(height: 24),
                  // Indicator Selection
                  const Text(
                    'Select Economic Indicators',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _indicators.keys.map((indicator) {
                      return FilterChip(
                        label: Text(indicator, style: const TextStyle(fontSize: 12)),
                        selected: _selectedIndicators.contains(indicator),
                        onSelected: (selected) {
                          setState(() {
                            if (selected) {
                              _selectedIndicators.add(indicator);
                            } else {
                              _selectedIndicators.remove(indicator);
                            }
                          });
                        },
                      );
                    }).toList(),
                  ),
                  if (_selectedIndicators.isEmpty) ...[
                    const SizedBox(height: 16),
                    const Center(
                      child: Text(
                        'Please select at least one economic indicator to display.',
                        style: TextStyle(color: Colors.grey),
                      ),
                    ),
                  ] else ...[
                    const SizedBox(height: 24),
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
                ],
              ),
            ),
          ),
          if (_selectedIndicators.isNotEmpty) ...[
            const SizedBox(height: 16),
            fredDataFuture.when(
              data: (data) {
                final processedData = _processData(data);
                
                if (processedData.isEmpty) {
                  return const Card(
                    child: Padding(
                      padding: EdgeInsets.all(32),
                      child: Center(
                        child: Text('No data available for selected indicators.'),
                      ),
                    ),
                  );
                }

                return Column(
                  children: _selectedIndicators.map((indicator) {
                    final indicatorData = processedData
                        .map((item) => _DataPoint(
                              date: item['date'] as String,
                              value: (item[indicator] as num?)?.toDouble() ?? 0,
                            ))
                        .where((point) => point.value != 0)
                        .toList();

                    if (indicatorData.isEmpty) {
                      return const SizedBox.shrink();
                    }

                    return Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                indicator,
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 16),
                              SizedBox(
                                height: 250,
                                child: _chartType == _ChartType.line
                                    ? _buildLineChart(indicatorData)
                                    : _buildBarChart(indicatorData),
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                );
              },
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: CircularProgressIndicator(),
                ),
              ),
              error: (error, _) => Card(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    children: [
                      const Icon(
                        Icons.error_outline,
                        size: 48,
                        color: Colors.red,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Failed to load macroeconomic data',
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
          ],
        ],
      ),
    );
  }

  Widget _buildLineChart(List<_DataPoint> data) {
    return LineChart(
      LineChartData(
        gridData: FlGridData(show: true),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 50,
              getTitlesWidget: (value, meta) {
                return Text(
                  value.toStringAsFixed(0),
                  style: const TextStyle(fontSize: 10),
                );
              },
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 30,
              interval: (data.length / 5).ceil().toDouble(),
              getTitlesWidget: (value, meta) {
                final index = value.toInt();
                if (index >= 0 && index < data.length) {
                  try {
                    final date = DateTime.parse(data[index].date);
                    return Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        DateFormat('MMM\nyy').format(date),
                        style: const TextStyle(fontSize: 9),
                        textAlign: TextAlign.center,
                      ),
                    );
                  } catch (_) {
                    return const Text('');
                  }
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
            dotData: FlDotData(show: false),
          ),
        ],
      ),
    );
  }

  Widget _buildBarChart(List<_DataPoint> data) {
    // Sample data for better performance - show every 5th data point
    final sampledData = <_DataPoint>[];
    for (var i = 0; i < data.length; i += 5) {
      sampledData.add(data[i]);
    }

    return BarChart(
      BarChartData(
        gridData: FlGridData(show: true),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 50,
              getTitlesWidget: (value, meta) {
                return Text(
                  value.toStringAsFixed(0),
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
                if (index >= 0 && index < sampledData.length) {
                  try {
                    final date = DateTime.parse(sampledData[index].date);
                    return Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        DateFormat('MMM\nyy').format(date),
                        style: const TextStyle(fontSize: 9),
                        textAlign: TextAlign.center,
                      ),
                    );
                  } catch (_) {
                    return const Text('');
                  }
                }
                return const Text('');
              },
            ),
          ),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: true),
        barGroups: sampledData.asMap().entries.map((e) {
          return BarChartGroupData(
            x: e.key,
            barRods: [
              BarChartRodData(
                toY: e.value.value,
                color: Colors.blue,
                width: 16,
              ),
            ],
          );
        }).toList(),
      ),
    );
  }

  List<Map<String, dynamic>> _processData(Map<String, dynamic> data) {
    final dataArray = data['data'] ?? [];
    if (dataArray is! List) return [];

    final dateMap = <String, Map<String, dynamic>>{};

    for (final row in dataArray) {
      if (row is! Map) continue;

      final date = row['date'] ?? row['Date'] ?? row['period'] ?? row['index'];
      if (date == null) continue;

      String dateStr;
      if (date is String) {
        dateStr = date.split('T')[0];
      } else {
        try {
          dateStr = DateTime.parse(date.toString()).toIso8601String().split('T')[0];
        } catch (_) {
          continue;
        }
      }

      dateMap.putIfAbsent(dateStr, () => {'date': dateStr});

      for (final key in _selectedIndicators) {
        final indicator = _indicators[key];
        if (indicator != null) {
          final value = row[indicator.id] ?? row[indicator.label] ?? row[key];
          if (value != null) {
            try {
              dateMap[dateStr]![key] = double.parse(value.toString());
            } catch (_) {
              // Skip invalid values
            }
          }
        }
      }
    }

    final result = dateMap.values.toList()
      ..sort((a, b) => (a['date'] as String).compareTo(b['date'] as String));
    return result;
  }
}

// Provider for FRED data
final _fredDataProvider = FutureProvider.family<
    Map<String, dynamic>,
    ({String seriesIds, String startDate, String endDate})>(
  (ref, params) async {
    final apiClient = ref.watch(apiClientProvider);
    final response = await apiClient.get(
      '/financial/fred',
      queryParameters: {
        'series_ids': params.seriesIds,
        'start_date': params.startDate,
        'end_date': params.endDate,
      },
    );
    return response.data as Map<String, dynamic>;
  },
);

// Data models
class _Indicator {
  const _Indicator({
    required this.id,
    required this.freq,
    required this.label,
  });

  final String id;
  final String freq;
  final String label;
}

class _DataPoint {
  const _DataPoint({
    required this.date,
    required this.value,
  });

  final String date;
  final double value;
}

enum _ChartType { line, bar }
