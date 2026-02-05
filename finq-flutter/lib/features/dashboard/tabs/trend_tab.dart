import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';

import '../dashboard_providers.dart';
import '../widgets/multi_select_dropdown.dart';
import '../widgets/metric_tooltip.dart';
import '../widgets/tab_description_tooltip.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_view.dart';
import '../providers/preferences_provider.dart';
import '../../../services/csv_export_service.dart';

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
  var _preferencesLoaded = false;
  String _lastTickerCategory = '';

  void _loadPreferences(List<String> allMetrics) {
    // Only load once per ticker/category combination
    final key = '${widget.ticker}_${widget.category}';
    if (_preferencesLoaded && _lastTickerCategory == key) {
      return;
    }
    
    _lastTickerCategory = key;
    _preferencesLoaded = true;
    
    final service = ref.read(preferencesServiceProvider);
    final saved = service.getMetrics(widget.ticker, widget.category);
    
    if (saved.isNotEmpty && mounted) {
      // Filter to only include available metrics
      final validSaved = saved.where((m) => allMetrics.contains(m)).toSet();
      if (validSaved.isNotEmpty) {
        setState(() {
          _selectedMetrics.clear();
          _selectedMetrics.addAll(validSaved);
        });
        return;
      }
    }
    
    // Auto-select first 3 metrics if no saved preferences
    if (_selectedMetrics.isEmpty && allMetrics.isNotEmpty) {
      setState(() {
        _selectedMetrics.addAll(allMetrics.take(3));
      });
      // Save as default
      service.saveMetrics(widget.ticker, widget.category, _selectedMetrics.toList());
    }
  }

  void _onMetricsChanged(Set<String> metrics) {
    setState(() {
      _selectedMetrics.clear();
      _selectedMetrics.addAll(metrics);
    });
    // Auto-save preferences
    ref.read(preferencesServiceProvider).saveMetrics(
      widget.ticker,
      widget.category,
      metrics.toList(),
    );
  }

  Future<void> _clearPreferences() async {
    await ref.read(preferencesServiceProvider).clearCategory(
      widget.ticker,
      widget.category,
    );
    setState(() {
      _selectedMetrics.clear();
      _preferencesLoaded = false;
    });
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Preferences cleared')),
      );
    }
  }

  Future<void> _exportToCsv(_FundamentalsData parsed) async {
    if (_selectedMetrics.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one metric to export')),
      );
      return;
    }

    try {
      // Extract periods from data
      final periods = parsed.data.map((pd) => pd.period).toList();
      
      // Prepare metrics data for export
      final metricsData = <String, List<double?>>{};
      for (final metric in _selectedMetrics) {
        final values = <double?>[];
        for (final periodData in parsed.data) {
          values.add(periodData.metrics[metric]);
        }
        metricsData[metric] = values;
      }

      await CsvExportService.exportTrendData(
        ticker: widget.ticker,
        category: widget.category,
        periods: periods,
        metricsData: metricsData,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('CSV exported successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Export failed: $e')),
        );
      }
    }
  }

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

        // Load saved preferences or auto-select defaults
        if (!_preferencesLoaded && allMetrics.isNotEmpty) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            _loadPreferences(allMetrics);
          });
        }

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
                      'Trend Analysis',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                    const SizedBox(width: 8),
                    const TabDescriptionTooltip(tabId: 'trend'),
                  ],
                ),
              ),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Expanded(
                            child: Text(
                              'Metrics to Plot',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                          DropdownButton<_ChartType>(
                            value: _chartType,
                            items: const [
                              DropdownMenuItem(
                                value: _ChartType.line,
                                child: Text('Line Chart'),
                              ),
                              DropdownMenuItem(
                                value: _ChartType.bar,
                                child: Text('Bar Chart'),
                              ),
                            ],
                            onChanged: (value) {
                              if (value != null) {
                                setState(() => _chartType = value);
                              }
                            },
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      MultiSelectDropdown<String>(
                        label: 'Select metrics to plot',
                        searchHint: 'Search metrics...',
                        items: allMetrics,
                        selectedItems: _selectedMetrics,
                        onSelectionChanged: _onMetricsChanged,
                        itemLabel: (metric) => metric,
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          const Spacer(),
                          if (_selectedMetrics.isNotEmpty)
                            TextButton.icon(
                              onPressed: () => _exportToCsv(parsed),
                              icon: const Icon(Icons.download, size: 18),
                              label: const Text('Export CSV'),
                              style: TextButton.styleFrom(
                                foregroundColor: Colors.blue.shade700,
                              ),
                            ),
                          if (_selectedMetrics.isNotEmpty &&
                              ref.read(preferencesServiceProvider).hasPreferences(
                                    widget.ticker,
                                    widget.category,
                                  ))
                            const SizedBox(width: 8),
                          if (ref.read(preferencesServiceProvider).hasPreferences(
                                widget.ticker,
                                widget.category,
                              ))
                            TextButton.icon(
                              onPressed: _clearPreferences,
                              icon: const Icon(Icons.clear, size: 18),
                              label: const Text('Clear Preferences'),
                              style: TextButton.styleFrom(
                                foregroundColor: Colors.orange.shade700,
                              ),
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
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  metric,
                                  style: const TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                              MetricTooltip(metricName: metric),
                            ],
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
      loading: () => SingleChildScrollView(
        child: Column(
          children: [
            const ChartSkeleton(height: 300),
            const SizedBox(height: 16),
            const ChartSkeleton(height: 300),
          ],
        ),
      ),
      error: (error, _) => ErrorView(
        error: error,
        title: 'Failed to load trend data',
        onRetry: () {
          // Force a refresh by invalidating the provider
          ref.invalidate(fundamentalsProvider);
        },
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
