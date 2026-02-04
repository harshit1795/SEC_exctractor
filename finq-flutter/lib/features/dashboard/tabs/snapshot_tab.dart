import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../dashboard_providers.dart';
import '../widgets/multi_select_dropdown.dart';

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

        // Auto-select first 10 metrics if none selected
        if (_selectedMetrics.isEmpty && allMetrics.isNotEmpty) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            setState(() {
              _selectedMetrics.addAll(allMetrics.take(10));
            });
          });
        }

        final latestPeriod = parsed.periods.isNotEmpty ? parsed.periods.first : '';
        final snapshotData = _calculateSnapshot(parsed, _selectedMetrics.toList());

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
                        onSelectionChanged: (selected) {
                          setState(() {
                            _selectedMetrics.clear();
                            _selectedMetrics.addAll(selected);
                          });
                        },
                        itemLabel: (metric) => metric,
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
                            DataCell(Text(row.metric)),
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
                  'Failed to load snapshot data',
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
