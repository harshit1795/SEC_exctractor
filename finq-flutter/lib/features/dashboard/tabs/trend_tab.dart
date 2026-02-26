import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';

import '../dashboard_providers.dart';
import '../widgets/multi_select_dropdown.dart';
import '../widgets/metric_tooltip.dart';
import '../widgets/tab_description_tooltip.dart';
import '../widgets/loading_skeleton.dart';
import '../widgets/error_view.dart';
import '../widgets/hierarchy_view.dart';
import '../providers/preferences_provider.dart';
import '../utils/metric_calculations.dart';
import '../widgets/floating_filter_panel.dart';
import '../../../data/financial_hierarchies.dart';
import '../../../services/csv_export_service.dart';

enum TrendViewMode { chart, hierarchy }

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
  var _viewMode = TrendViewMode.hierarchy;
  var _chartType = _ChartType.line;
  final _selectedMetrics = <String>{};
  var _preferencesLoaded = false;
  String _lastTickerCategory = '';

  final List<Color> _tickerColors = [
    Colors.black,
    Colors.blue.shade700,
    Colors.orange.shade700,
    Colors.purple.shade700,
    Colors.green.shade700,
  ];

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
      // Extract periods from data (using first ticker's periods for simplicity)
      final firstTickerData = parsed.tickerData.values.first;
      final periods = firstTickerData.map((pd) => pd.period).toList();
      
      // Prepare metrics data for export (currently only supports primary ticker exporting)
      // TODO: Enhance export for multi-ticker
      final metricsData = <String, List<double?>>{};
      for (final metric in _selectedMetrics) {
        final values = <double?>[];
        for (final periodData in firstTickerData) {
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

  /// Prepare metrics data for hierarchy view (Primary ticker only)
  Map<String, MetricData> _prepareMetricsData(List<_PeriodData> periodData) {
    final metricsData = <String, MetricData>{};
    
    // Convert period data to PeriodData format
    final periods = periodData.map((pd) {
      return PeriodData(
        period: pd.period,
        metrics: pd.metrics,
      );
    }).toList();

    // Helper function to process a node and its children recursively
    void processNode(FinancialNode node) {
      // Try to get metric data from backend
      MetricData? data;
      
      if (node.metricName != null) {
        data = MetricCalculations.calculateMetricData(
          periods,
          node.metricName!,
          node.alternativeNames,
        );
      }
      
      // If this is a calculated or parent node, compute it from children
      if (data == null && node.children.isNotEmpty) {
        // First process all children
        for (final child in node.children) {
          processNode(child);
        }
        
        // Then calculate parent value from children
        if (node.calculationType != CalculationType.none) {
          data = MetricCalculations.calculateDerivedMetric(
            node,
            metricsData,
            periods,
          );
          
          // If still null, try rollup
          if (data == null && node.children.isNotEmpty) {
            data = MetricCalculations.rollupChildMetrics(
              node.children,
              metricsData,
              periods.isNotEmpty ? periods.first.period : '',
            );
          }
        }
      }
      
      if (data != null) {
        metricsData[node.id] = data;
      }
      
      // Process children if not already done
      for (final child in node.children) {
        if (!metricsData.containsKey(child.id)) {
          processNode(child);
        }
      }
    }

    // 1. Collect all known metrics from standard hierarchies
    final knownMetrics = <String>{};
    void collectKnownMetrics(FinancialNode node) {
      if (node.metricName != null) knownMetrics.add(node.metricName!);
      knownMetrics.addAll(node.alternativeNames);
      for (final child in node.children) {
        collectKnownMetrics(child);
      }
    }

    // Process all Balance Sheet roots
    for (final root in BalanceSheetHierarchy.roots) {
      collectKnownMetrics(root);
      processNode(root);
    }
    
    // Process Income Statement root
    collectKnownMetrics(IncomeStatementHierarchy.root);
    processNode(IncomeStatementHierarchy.root);

    // 2. Identify metrics not in the standard hierarchies (case-insensitive check)
    // We need to re-scan periodData for this
    final availableMetrics = <String>{};
    final metricCategoriesMap = <String, String>{};
    
    for(final p in periodData) {
        availableMetrics.addAll(p.metrics.keys);
        metricCategoriesMap.addAll(p.metricCategories);
    }

    final normalizedWidgetCategory = widget.category.toLowerCase().replaceAll(' ', '');
    final showAllCategories = widget.category.toLowerCase() == 'all' || 
                              widget.category.toLowerCase() == 'all fundamentals';

    final unknownMetrics = availableMetrics.where((m) {
      final lowerM = m.toLowerCase();
      // Check if this metric or any case-variant is already known
      final isUnknown = !knownMetrics.any((k) => k.toLowerCase() == lowerM);
      if (!isUnknown) return false;
      
      // If we are showing all categories, include it
      if (showAllCategories) return true;
      
      // Otherwise, ONLY include unknown metrics if they actually belong to the current category
      final mCat = metricCategoriesMap[m] ?? '';
      final normalizedMCat = mCat.toLowerCase().replaceAll(' ', '');
      return normalizedMCat == normalizedWidgetCategory;
      
    }).toList()
      ..sort();

    // 3. Create "Other Metrics" node if needed
    if (unknownMetrics.isNotEmpty) {
      final otherMetricsNode = FinancialNode(
        id: 'other_metrics',
        displayName: 'Other Metrics',
        category: NodeCategory.profit, // Use generic category
        type: NodeType.root,
        children: unknownMetrics.map((metric) {
          return FinancialNode(
            id: 'other_${metric.toLowerCase().replaceAll(' ', '_')}',
            displayName: metric,
            metricName: metric,
            category: NodeCategory.profit,
            type: NodeType.leaf,
          );
        }).toList(),
      );

      processNode(otherMetricsNode);
    }

    return metricsData;
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
        final isMulti = parsed.tickers.length > 1;

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
        
        // Force chart view if multi-ticker
        if (isMulti && _viewMode == TrendViewMode.hierarchy) {
             _viewMode = TrendViewMode.chart;
        }

        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Tab description tooltip and view mode toggle
              Padding(
                padding: const EdgeInsets.only(left: 4, bottom: 8),
                child: LayoutBuilder(
                  builder: (context, constraints) {
                    final isNarrow = constraints.maxWidth < 500;
                    final titleRow = Row(
                      mainAxisSize: MainAxisSize.min,
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
                    );

                    if (!isMulti) {
                      final viewToggle = SegmentedButton<TrendViewMode>(
                        segments: const [
                          ButtonSegment(
                            value: TrendViewMode.chart,
                            icon: Icon(Icons.show_chart, size: 18),
                            label: Text('Chart View'),
                          ),
                          ButtonSegment(
                            value: TrendViewMode.hierarchy,
                            icon: Icon(Icons.account_tree, size: 18),
                            label: Text('Hierarchy View'),
                          ),
                        ],
                        selected: {_viewMode},
                        onSelectionChanged: (Set<TrendViewMode> selection) {
                          setState(() => _viewMode = selection.first);
                        },
                        style: ButtonStyle(
                          textStyle: WidgetStateProperty.all(
                            const TextStyle(fontSize: 13),
                          ),
                        ),
                      );

                      if (isNarrow) {
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            titleRow,
                            const SizedBox(height: 12),
                            viewToggle,
                          ],
                        );
                      }

                      return Row(
                        children: [
                          titleRow,
                          const Spacer(),
                          viewToggle,
                        ],
                      );
                    }

                    return titleRow;
                  },
                ),
              ),
              
              if (isMulti)
                Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
                    child: Wrap(
                        spacing: 8,
                        children: parsed.tickers.asMap().entries.map((entry) {
                            final idx = entry.key;
                            final t = entry.value;
                            return Chip(
                                label: Text(t, style: const TextStyle(color: Colors.white, fontSize: 12)),
                                backgroundColor: _tickerColors[idx % _tickerColors.length],
                                side: BorderSide.none,
                                visualDensity: VisualDensity.compact,
                            );
                        }).toList(),
                    ),
                ),

              // Conditional rendering based on view mode
              if (_viewMode == TrendViewMode.hierarchy && !isMulti)
                HierarchyView(
                  ticker: widget.ticker,
                  category: widget.category,
                  metricsData: _prepareMetricsData(parsed.tickerData.values.first),
                  latestPeriod: parsed.tickerData.values.first.isNotEmpty 
                      ? parsed.tickerData.values.first.first.period 
                      : null,
                )
              else ...[
                // Metric selection card - only in Chart View
                FloatingFilterPanel(
                  title: 'Trend Filters',
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
                          if (_selectedMetrics.isNotEmpty && !isMulti)
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
                const SizedBox(height: 16),
                // Charts - only in Chart View
                LayoutBuilder(
                  builder: (context, constraints) {
                    final isWide = constraints.maxWidth > 900;
                    return Wrap(
                      spacing: 16,
                      runSpacing: 16,
                      children: _selectedMetrics.map((metric) {
                        return SizedBox(
                          width: isWide
                              ? (constraints.maxWidth - 16) / 2
                              : constraints.maxWidth,
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
                                        ? _buildLineChart(parsed, metric)
                                        : _buildBarChart(parsed, metric),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    );
                  },
                ),
              ],
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

  Widget _buildLineChart(_FundamentalsData parsed, String metric) {
    List<LineChartBarData> lines = [];
    List<String> allPeriods = [];
    
    // Get unique sorted periods
    final periodSet = <String>{};
    for(final data in parsed.tickerData.values) {
        periodSet.addAll(data.map((d) => d.period));
    }
    
    // Sort periods
    allPeriods = periodSet.toList()..sort((a, b) {
        final aParts = _parsePeriod(a);
        final bParts = _parsePeriod(b);
        if (aParts.$1 != bParts.$1) return aParts.$1.compareTo(bParts.$1);
        return aParts.$2.compareTo(bParts.$2);
    });

    int tickerIdx = 0;
    for (final ticker in parsed.tickers) {
        final data = parsed.tickerData[ticker] ?? [];
        final color = _tickerColors[tickerIdx % _tickerColors.length];
        
        final spots = <FlSpot>[];
        for (int i = 0; i < allPeriods.length; i++) {
            final period = allPeriods[i];
            // Find data for this period
            final periodData = data.firstWhere((p) => p.period == period, orElse: () => const _PeriodData(period: '', metrics: {}, metricCategories: {}));
            if (periodData.metrics.containsKey(metric)) {
                spots.add(FlSpot(i.toDouble(), periodData.metrics[metric]!));
            }
        }
        
        lines.add(LineChartBarData(
            spots: spots,
            isCurved: false,
            color: color,
            barWidth: 2,
            dotData: FlDotData(
              show: true,
              getDotPainter: (spot, percent, barData, index) {
                return FlDotCirclePainter(
                  radius: 2,
                  color: color,
                  strokeWidth: 0,
                );
              },
            ),
        ));
        
        tickerIdx++;
    }

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
              interval: (allPeriods.length / 5).ceil().toDouble(),
              getTitlesWidget: (value, meta) {
                final index = value.toInt();
                if (index >= 0 && index < allPeriods.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      allPeriods[index],
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
        lineTouchData: LineTouchData(
          touchTooltipData: LineTouchTooltipData(
            getTooltipItems: (touchedSpots) {
              return touchedSpots.map((LineBarSpot touchedSpot) {
                final tickerIndex = touchedSpot.barIndex;
                final tickerName = tickerIndex < parsed.tickers.length ? parsed.tickers[tickerIndex] : '';
                return LineTooltipItem(
                  '$tickerName\n${_formatValue(touchedSpot.y)}',
                  TextStyle(
                    color: touchedSpot.bar.color ?? Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                );
              }).toList();
            },
          ),
        ),
        lineBarsData: lines,
      ),
    );
  }

  Widget _buildBarChart(_FundamentalsData parsed, String metric) {
     // Get unique sorted periods as before
    final periodSet = <String>{};
    for(final data in parsed.tickerData.values) {
        periodSet.addAll(data.map((d) => d.period));
    }
    
    final allPeriods = periodSet.toList()..sort((a, b) {
        final aParts = _parsePeriod(a);
        final bParts = _parsePeriod(b);
        if (aParts.$1 != bParts.$1) return aParts.$1.compareTo(bParts.$1);
        return aParts.$2.compareTo(bParts.$2);
    });

    final barGroups = <BarChartGroupData>[];
    
    for (int i = 0; i < allPeriods.length; i++) {
        final period = allPeriods[i];
        final rods = <BarChartRodData>[];
        
        int tickerIdx = 0;
        for (final ticker in parsed.tickers) {
             final data = parsed.tickerData[ticker] ?? [];
             final color = _tickerColors[tickerIdx % _tickerColors.length];
             
             final periodData = data.firstWhere((p) => p.period == period, orElse: () => const _PeriodData(period: '', metrics: {}, metricCategories: {}));
             final val = periodData.metrics[metric] ?? 0;
             
             if (val != 0) {
                 rods.add(BarChartRodData(
                     toY: val,
                     color: color,
                     width: 12, // slightly thinner to fit
                     borderRadius: BorderRadius.circular(4),
                 ));
             } else {
                 // Add placeholder transparent rod to maintain spacing/alignment
                 rods.add(BarChartRodData(toY: 0, color: Colors.transparent, width: 12));
             }
             tickerIdx++;
        }
        
        barGroups.add(BarChartGroupData(x: i, barRods: rods, barsSpace: 4));
    }

    return BarChart(
        BarChartData(
          barTouchData: BarTouchData(
            touchTooltipData: BarTouchTooltipData(
              getTooltipItem: (group, groupIndex, rod, rodIndex) {
                 final tickerIndex = rodIndex;
                 final tickerName = tickerIndex < parsed.tickers.length ? parsed.tickers[tickerIndex] : '';
                 if (rod.toY == 0) return null;
                 
                return BarTooltipItem(
                  '$tickerName\n${_formatValue(rod.toY)}',
                  TextStyle(
                    color: rod.color ?? Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                );
              },
            ),
          ),
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
                interval: (allPeriods.length / 5).ceil().toDouble(),
                getTitlesWidget: (value, meta) {
                  final index = value.toInt();
                  if (index >= 0 && index < allPeriods.length) {
                    return Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        allPeriods[index],
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
          barGroups: barGroups,
          maxY: _calculateMaxY(barGroups),
        ));
  }
  
  double _calculateMaxY(List<BarChartGroupData> groups) {
      double max = 0;
      for (final group in groups) {
          for (final rod in group.barRods) {
              if (rod.toY > max) max = rod.toY;
          }
      }
      return max * 1.2; // Add some buffer
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
    if (data.containsKey('tickers') && data['data'] is Map) {
        // Multi-ticker response
        final tickers = (data['tickers'] as List).cast<String>();
        final rawDataMap = data['data'] as Map<String, dynamic>;
        
        final tickerData = <String, List<_PeriodData>>{};
        final allMetrics = <String>{};
        
        for (final ticker in tickers) {
             final singleData = rawDataMap[ticker];
             if (singleData != null) {
                 final parsedSingle = _parseSingleTickerData(singleData, ticker);
                 tickerData[ticker] = parsedSingle.data;
                 allMetrics.addAll(parsedSingle.metrics);
             } else {
                 tickerData[ticker] = [];
             }
        }

        return _FundamentalsData(metrics: allMetrics, tickerData: tickerData, tickers: tickers);
    } else {
        // Single ticker response
        final parsed = _parseSingleTickerData(data, widget.ticker);
        return _FundamentalsData(
            metrics: parsed.metrics,
            tickerData: {widget.ticker: parsed.data},
            tickers: [widget.ticker],
        );
    }
  }
  
  // Helper to parse single ticker data returning temporary struct
  _FundamentalsDataHelper _parseSingleTickerData(Map<String, dynamic> data, String ticker) {
    final dataArray = data['data'] ?? data;
    if (dataArray is! List) {
      return _FundamentalsDataHelper(metrics: {}, data: []);
    }

    final metrics = <String>{};
    final periodMap = <String, Map<String, double>>{};
    final categoryMap = <String, Map<String, String>>{};
    final normalizedWidgetCategory = widget.category.toLowerCase().replaceAll(' ', '');
    final showAllCategories = widget.category.toLowerCase() == 'all' || 
                              widget.category.toLowerCase() == 'all fundamentals';

    for (final item in dataArray) {
      if (item is! Map) continue;

      final itemCategory = item['Category'] ?? item['category'] ?? '';
      final period = item['FiscalPeriod'] ??
          item['fiscalPeriod'] ??
          item['Date'] ??
          item['date'] ??
          '';
      final metric = item['Metric'] ?? item['metric'] ?? '';
      final value = (item['Value'] ?? item['value'] ?? 0).toDouble();

      if (period.isEmpty || metric.isEmpty) continue;

      // Always populate period map with ALL metrics for HierarchyView cross-calculations
      periodMap.putIfAbsent(period, () => {});
      categoryMap.putIfAbsent(period, () => {});
      
      periodMap[period]![metric] = value;
      categoryMap[period]![metric] = itemCategory.toString();

      // Filter the metrics list (used for Chart View dropdown) by selected category
      bool matchesCategory = showAllCategories;
      if (!matchesCategory) {
        final normalizedItemCategory = itemCategory.toString().toLowerCase().replaceAll(' ', '');
        matchesCategory = normalizedItemCategory == normalizedWidgetCategory;
      }

      if (matchesCategory) {
        metrics.add(metric);
      }
    }

    final validPeriods = periodMap.keys.where((p) {
        final m = periodMap[p]!;
        int nonZeroCount = m.values.where((v) => v != 0.0).length;
        // Projected/dummy periods from Yahoo Finance usually only have 3-5 EPS/Share estimates
        // A legitimate financial report will have dozens of fundamental metrics.
        return nonZeroCount > 10;
    }).toList();

    final periods = validPeriods
      ..sort((a, b) {
        // Sort by year and quarter (DESCENDING for MetricCalculations)
        final aParts = _parsePeriod(a);
        final bParts = _parsePeriod(b);
        if (aParts.$1 != bParts.$1) return bParts.$1.compareTo(aParts.$1);
        return bParts.$2.compareTo(aParts.$2);
    });

    final periodData = periods
        .map((period) => _PeriodData(
              period: period,
              metrics: periodMap[period]!,
              metricCategories: categoryMap[period]!,
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
  });

  final Set<String> metrics;
  final Map<String, List<_PeriodData>> tickerData;
  final List<String> tickers; 
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
    required this.metricCategories,
  });

  final String period;
  final Map<String, double> metrics;
  final Map<String, String> metricCategories;
}



enum _ChartType { line, bar }
