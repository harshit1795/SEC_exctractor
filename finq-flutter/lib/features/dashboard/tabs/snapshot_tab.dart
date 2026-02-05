import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../dashboard_providers.dart';
import '../widgets/multi_select_dropdown.dart';
import '../widgets/metric_tooltip.dart';
import '../widgets/tab_description_tooltip.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_view.dart';
import '../providers/preferences_provider.dart';
import '../../../services/csv_export_service.dart';

class SnapshotTab extends ConsumerStatefulWidget {
  const SnapshotTab({
    required this.ticker,
    required this.category,
    super.key,
  });

  final String ticker;
  final String category;

  @override
  ConsumerState<SnapshotTab> createState() => _SnapshotTabState();
}

class _SnapshotTabState extends ConsumerState<SnapshotTab> {
  var _displayMode = _DisplayMode.latest;
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
    
    // Auto-select first 10 metrics if no saved preferences
    if (_selectedMetrics.isEmpty && allMetrics.isNotEmpty) {
      setState(() {
        _selectedMetrics.addAll(allMetrics.take(10));
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

  Future<void> _exportToCsv(List<_SnapshotRow> snapshotData) async {
    if (snapshotData.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No data to export')),
      );
      return;
    }

    try {
      // Convert snapshot rows to export format
      final exportRows = snapshotData.map((row) {
        return SnapshotRow(
          metric: row.metric,
          latestValue: row.value.toString(),
          previousValue: row.delta != null ? (row.value - row.delta!).toString() : null,
          change: row.delta?.toString(),
          percentChange: row.deltaPercent?.toStringAsFixed(2),
        );
      }).toList();

      await CsvExportService.exportSnapshotData(
        ticker: widget.ticker,
        category: widget.category,
        rows: exportRows,
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
            child: Text('Select a category to view snapshot.'),
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

        final latestPeriod = parsed.periods.isNotEmpty ? parsed.periods.first : '';
        final snapshotData = _calculateSnapshot(parsed, _selectedMetrics.toList());

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
                      'Snapshot Analysis',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                    const SizedBox(width: 8),
                    const TabDescriptionTooltip(tabId: 'snapshot'),
                  ],
                ),
              ),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Display Mode (Period: $latestPeriod)',
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 8),
                      SegmentedButton<_DisplayMode>(
                        segments: const [
                          ButtonSegment(
                            value: _DisplayMode.latest,
                            label: Text('Latest'),
                          ),
                          ButtonSegment(
                            value: _DisplayMode.qoq,
                            label: Text('QoQ Δ'),
                          ),
                          ButtonSegment(
                            value: _DisplayMode.yoy,
                            label: Text('YoY Δ'),
                          ),
                        ],
                        selected: {_displayMode},
                        onSelectionChanged: (values) {
                          setState(() => _displayMode = values.first);
                        },
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'Metrics to Show',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 8),
                      MultiSelectDropdown<String>(
                        label: 'Select metrics to show',
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
                              onPressed: () => _exportToCsv(snapshotData),
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
              if (_selectedMetrics.isNotEmpty)
                Card(
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: DataTable(
                      columns: [
                        const DataColumn(label: Text('Metric')),
                        DataColumn(
                          label: Text(
                            _displayMode == _DisplayMode.latest
                                ? 'Value'
                                : 'Latest Value ($latestPeriod)',
                          ),
                        ),
                        if (_displayMode != _DisplayMode.latest) ...[
                          const DataColumn(label: Text('Change')),
                          const DataColumn(label: Text('Change %')),
                        ],
                      ],
                      rows: snapshotData.map((row) {
                        return DataRow(
                          cells: [
                            DataCell(
                              Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Text(row.metric),
                                  const SizedBox(width: 4),
                                  MetricTooltip(metricName: row.metric, iconSize: 16),
                                ],
                              ),
                            ),
                            DataCell(Text(_formatValue(row.value))),
                            if (_displayMode != _DisplayMode.latest) ...[
                              DataCell(
                                Text(
                                  row.delta != null ? _formatValue(row.delta!) : 'N/A',
                                  style: TextStyle(
                                    color: _getValueColor(row.delta),
                                  ),
                                ),
                              ),
                              DataCell(
                                Text(
                                  row.deltaPercent != null
                                      ? '${row.deltaPercent! > 0 ? '+' : ''}${row.deltaPercent!.toStringAsFixed(2)}%'
                                      : 'N/A',
                                  style: TextStyle(
                                    color: _getValueColor(row.deltaPercent),
                                  ),
                                ),
                              ),
                            ],
                          ],
                        );
                      }).toList(),
                    ),
                  ),
                ),
            ],
          ),
        );
      },
      loading: () => const DataTableSkeleton(rowCount: 10, columnCount: 5),
      error: (error, _) => ErrorView(
        error: error,
        title: 'Failed to load snapshot data',
        onRetry: () {
          // Force a refresh by invalidating the provider
          ref.invalidate(fundamentalsProvider);
        },
      ),
    );
  }

  String _formatValue(double value) {
    if (value.abs() >= 1e9) {
      return '\$${(value / 1e9).toStringAsFixed(2)}B';
    } else if (value.abs() >= 1e6) {
      return '\$${(value / 1e6).toStringAsFixed(2)}M';
    } else if (value.abs() >= 1e3) {
      return '\$${(value / 1e3).toStringAsFixed(2)}K';
    }
    return value.toStringAsFixed(2);
  }

  Color? _getValueColor(double? value) {
    if (value == null) return null;
    if (value > 0) return Colors.green;
    if (value < 0) return Colors.red;
    return null;
  }

  List<_SnapshotRow> _calculateSnapshot(
    _FundamentalsData parsed,
    List<String> metrics,
  ) {
    if (parsed.periods.isEmpty) return [];

    final latestPeriod = parsed.periods.first;
    final latestData = parsed.periodData[latestPeriod] ?? {};

    return metrics.map((metric) {
      final latestValue = latestData[metric] ?? 0;
      double? delta;
      double? deltaPercent;

      if (_displayMode == _DisplayMode.qoq && parsed.periods.length >= 2) {
        final prevPeriod = parsed.periods[1];
        final prevData = parsed.periodData[prevPeriod] ?? {};
        final prevValue = prevData[metric] ?? 0;
        delta = latestValue - prevValue;
        deltaPercent = prevValue != 0 ? (delta / prevValue.abs()) * 100 : 0;
      } else if (_displayMode == _DisplayMode.yoy) {
        final latestParts = _parsePeriod(latestPeriod);
        final targetYear = latestParts.$1 - 1;
        
        final yearAgoPeriod = parsed.periods.firstWhere(
          (p) {
            final parts = _parsePeriod(p);
            return parts.$1 == targetYear && parts.$2 == latestParts.$2;
          },
          orElse: () => '',
        );

        if (yearAgoPeriod.isNotEmpty) {
          final yearAgoData = parsed.periodData[yearAgoPeriod] ?? {};
          final yearAgoValue = yearAgoData[metric] ?? 0;
          delta = latestValue - yearAgoValue;
          deltaPercent = yearAgoValue != 0 ? (delta / yearAgoValue.abs()) * 100 : 0;
        }
      }

      return _SnapshotRow(
        metric: metric,
        value: latestValue,
        delta: delta,
        deltaPercent: deltaPercent,
      );
    }).toList();
  }

  _FundamentalsData _parseFundamentalsData(Map<String, dynamic> data) {
    final dataArray = data['data'] ?? data;
    if (dataArray is! List) {
      return _FundamentalsData(
        metrics: {},
        periods: [],
        periodData: {},
      );
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
        // Sort descending (latest first)
        final aParts = _parsePeriod(a);
        final bParts = _parsePeriod(b);
        if (aParts.$1 != bParts.$1) return bParts.$1.compareTo(aParts.$1);
        return bParts.$2.compareTo(aParts.$2);
      });

    return _FundamentalsData(
      metrics: metrics,
      periods: periods,
      periodData: periodMap,
    );
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
    required this.periods,
    required this.periodData,
  });

  final Set<String> metrics;
  final List<String> periods;
  final Map<String, Map<String, double>> periodData;
}

class _SnapshotRow {
  const _SnapshotRow({
    required this.metric,
    required this.value,
    this.delta,
    this.deltaPercent,
  });

  final String metric;
  final double value;
  final double? delta;
  final double? deltaPercent;
}

enum _DisplayMode { latest, qoq, yoy }
