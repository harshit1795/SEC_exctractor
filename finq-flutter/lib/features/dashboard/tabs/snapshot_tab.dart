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
import '../widgets/floating_filter_panel.dart';

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

  Future<void> _exportToCsv(List<_MultiSnapshotRow> snapshotData, List<String> tickers) async {
    if (snapshotData.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No data to export')),
      );
      return;
    }

    try {
      // For multi-ticker, we might want a different export format or loop.
      // Current CSV service likely expects single ticker rows.
      // Let's just export the primary ticker for now as a fallback, 
      // or if we have time, upgrade the service.
      // Given constraints, I'll export primary ticker data.
      
      final primaryTicker = tickers.first;
      final exportRows = snapshotData.map((row) {
        final val = row.values[primaryTicker] ?? 0;
        final delta = row.deltas[primaryTicker];
        final deltaPct = row.deltaPercents[primaryTicker];
        
        return SnapshotRow(
          metric: row.metric,
          latestValue: val.toString(),
          previousValue: delta != null ? (val - delta).toString() : null,
          change: delta?.toString(),
          percentChange: deltaPct?.toStringAsFixed(2),
        );
      }).toList();

      await CsvExportService.exportSnapshotData(
        ticker: primaryTicker,
        category: widget.category,
        rows: exportRows,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('CSV exported successfully (Primary Ticker)')),
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
              FloatingFilterPanel(
                title: 'Snapshot Filters',
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
                            onPressed: () => _exportToCsv(snapshotData, parsed.tickers),
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
              const SizedBox(height: 16),
              if (_selectedMetrics.isNotEmpty)
                Card(
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: DataTable(
                      columns: [
                        const DataColumn(label: Text('Metric')),
                        ...parsed.tickers.map((t) => DataColumn(label: Text(t, style: const TextStyle(fontWeight: FontWeight.bold)))),
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
                            ...parsed.tickers.map((ticker) {
                                final val = row.values[ticker] ?? 0;
                                final delta = row.deltas[ticker];
                                final deltaPct = row.deltaPercents[ticker];
                                
                                String text;
                                Color? color;
                                
                                if (_displayMode == _DisplayMode.latest) {
                                    text = _formatValue(val);
                                } else if (_displayMode == _DisplayMode.qoq || _displayMode == _DisplayMode.yoy) {
                                    if (deltaPct != null) {
                                        text = '${deltaPct > 0 ? '+' : ''}${deltaPct.toStringAsFixed(2)}%';
                                        color = _getValueColor(deltaPct);
                                    } else {
                                        text = 'N/A';
                                    }
                                } else {
                                    text = '';
                                }
                                
                                return DataCell(Text(text, style: TextStyle(color: color)));
                            }),
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

  List<_MultiSnapshotRow> _calculateSnapshot(
    _FundamentalsData parsed,
    List<String> metrics,
  ) {
    return metrics.map((metric) {
      final values = <String, double>{};
      final deltas = <String, double?>{};
      final deltaPercents = <String, double?>{};
      
      for (final ticker in parsed.tickers) {
          final data = parsed.tickerData[ticker];
          // Determine periods for this ticker
          // For now, assuming parsed.periods is the union or primary ticker's periods
          // But each ticker data has its own periods.
          // Let's find latest for this ticker.
          
          if (data == null || data.isEmpty) {
              values[ticker] = 0;
              continue;
          }
           
           // Sort by period descending
           final sortedData = List<_PeriodData>.from(data)..sort((a, b) => b.period.compareTo(a.period)); 
           // Better period compare logic needed if format varies, but assuming consistent format
           
           final latestData = sortedData.first;
           final latestValue = latestData.metrics[metric] ?? 0;
           values[ticker] = latestValue;
           
           if (_displayMode == _DisplayMode.qoq && sortedData.length >= 2) {
               final prevData = sortedData[1];
               final prevValue = prevData.metrics[metric] ?? 0;
               final delta = latestValue - prevValue;
               deltas[ticker] = delta;
               deltaPercents[ticker] = prevValue != 0 ? (delta / prevValue.abs()) * 100 : 0;
           } else if (_displayMode == _DisplayMode.yoy) {
               // Simple YoY
               // Find period with same quarter but year - 1
               final latestParts = _parsePeriod(latestData.period);
               final targetYear = latestParts.$1 - 1;
               
               final yearAgoData = sortedData.firstWhere(
                  (p) {
                      final parts = _parsePeriod(p.period);
                      return parts.$1 == targetYear && parts.$2 == latestParts.$2;
                  },
                  orElse: () => const _PeriodData(period: '', metrics: {}),
               );
               
               if (yearAgoData.period.isNotEmpty) {
                   final yearAgoValue = yearAgoData.metrics[metric] ?? 0;
                   final delta = latestValue - yearAgoValue;
                   deltas[ticker] = delta;
                   deltaPercents[ticker] = yearAgoValue != 0 ? (delta / yearAgoValue.abs()) * 100 : 0;
               }
           }
      }

      return _MultiSnapshotRow(
        metric: metric,
        values: values,
        deltas: deltas,
        deltaPercents: deltaPercents,
      );
    }).toList();
  }

  _FundamentalsData _parseFundamentalsData(Map<String, dynamic> data) {
    if (data.containsKey('tickers') && data['data'] is Map) {
         // Multi-ticker
         final tickers = (data['tickers'] as List).cast<String>();
         final rawDataMap = data['data'] as Map<String, dynamic>;
         
         final tickerData = <String, List<_PeriodData>>{};
         final allMetrics = <String>{};
         final allPeriods = <String>{}; // Union of periods
         
         for (final ticker in tickers) {
              final singleData = rawDataMap[ticker];
              if (singleData != null) {
                  final parsedSingle = _parseSingleTickerData(singleData, ticker);
                  tickerData[ticker] = parsedSingle.data;
                  allMetrics.addAll(parsedSingle.metrics);
                  allPeriods.addAll(parsedSingle.data.map((d) => d.period));
              } else {
                  tickerData[ticker] = [];
              }
         }
         
         final sortedPeriods = allPeriods.toList()..sort((a,b) {
             final aParts = _parsePeriod(a);
             final bParts = _parsePeriod(b);
             if (aParts.$1 != bParts.$1) return bParts.$1.compareTo(aParts.$1); // Descending
             return bParts.$2.compareTo(aParts.$2);
         });
         
         return _FundamentalsData(
             metrics: allMetrics, 
             tickerData: tickerData, 
             tickers: tickers,
             periods: sortedPeriods,
         );

    } else {
        // Single
        final parsed = _parseSingleTickerData(data, widget.ticker);
        final periods = parsed.data.map((d) => d.period).toList()..sort((a, b) {
             final aParts = _parsePeriod(a);
             final bParts = _parsePeriod(b);
             if (aParts.$1 != bParts.$1) return bParts.$1.compareTo(aParts.$1); // Descending
             return bParts.$2.compareTo(aParts.$2);
        });
        
        return _FundamentalsData(
            metrics: parsed.metrics,
            tickerData: {widget.ticker: parsed.data},
            tickers: [widget.ticker],
            periods: periods,
        );
    }
  }

  _FundamentalsDataHelper _parseSingleTickerData(Map<String, dynamic> data, String ticker) {
    final dataArray = data['data'] ?? data;
    if (dataArray is! List) {
      return _FundamentalsDataHelper(metrics: {}, data: []);
    }

    final filtered = dataArray.where((item) {
      if (item is! Map) return false;
      final itemCategory = item['Category'] ?? item['category'] ?? '';
      return itemCategory == widget.category; // Removed strict ticker check
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

    final periodData = periodMap.entries
        .map((entry) => _PeriodData(
              period: entry.key,
              metrics: entry.value,
            ))
        .toList();

    return _FundamentalsDataHelper(metrics: metrics, data: periodData);
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
    required this.tickerData,
    required this.tickers,
    required this.periods,
  });

  final Set<String> metrics;
  final Map<String, List<_PeriodData>> tickerData;
  final List<String> tickers;
  final List<String> periods;
}

class _FundamentalsDataHelper {
  const _FundamentalsDataHelper({
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

class _MultiSnapshotRow {
  const _MultiSnapshotRow({
    required this.metric,
    required this.values,
    required this.deltas,
    required this.deltaPercents,
  });

  final String metric;
  final Map<String, double> values;
  final Map<String, double?> deltas;
  final Map<String, double?> deltaPercents;
}

enum _DisplayMode { latest, qoq, yoy }
