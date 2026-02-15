import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';

import '../dashboard_providers.dart';
import '../widgets/tab_description_tooltip.dart';
import '../widgets/floating_filter_panel.dart';

class FinQ360Tab extends ConsumerStatefulWidget {
  const FinQ360Tab({
    required this.ticker,
    required this.category,
    super.key,
  });

  final String ticker;
  final String category;

  @override
  ConsumerState<FinQ360Tab> createState() => _FinQ360TabState();
}

class _FinQ360TabState extends ConsumerState<FinQ360Tab> {
  List<String> _selectedFundamentals = [];
  List<String> _selectedEarnings = [];
  DateTime _startDate = DateTime(2000, 1, 1);
  DateTime _endDate = DateTime.now();
  String _aggregation = 'Quarterly';
  String _chartType = 'Line';

  @override
  Widget build(BuildContext context) {
    final fundamentals = ref.watch(fundamentalsProvider);
    final tickerData = ref.watch(tickerDataProvider);

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Tab description tooltip
          Padding(
            padding: const EdgeInsets.only(left: 4, bottom: 8),
            child: Row(
              children: [
                Icon(Icons.search, size: 24, color: Colors.grey.shade700),
                const SizedBox(width: 8),
                Text(
                  'FinQ 360',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
                const SizedBox(width: 8),
                const TabDescriptionTooltip(tabId: 'finq360'),
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
                    'Create custom charts by combining company fundamentals, earnings, and macroeconomic data for ${widget.ticker}.',
                    style: TextStyle(
                      color: Colors.grey.shade600,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          // Metric Selection
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Company Fundamentals
                  _buildMetricSelector(
                    'Company Fundamentals',
                    _selectedFundamentals,
                    fundamentals,
                    (selected) {
                      setState(() => _selectedFundamentals = selected);
                    },
                  ),
                  const SizedBox(height: 16),
                  // Earnings
                  _buildEarningsSelector(),
                  const SizedBox(height: 16),
                  // Macroeconomic Data
                  _buildMacroeconomicSelector(),
                  const Divider(height: 32),
                  // Filters
                  FloatingFilterPanel(
                    title: 'FinQ360 Filters',
                    child: LayoutBuilder(
                      builder: (context, constraints) {
                        final isNarrow = constraints.maxWidth < 600;

                        final dateRangeWidget = Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Date Range', style: TextStyle(fontSize: 12)),
                            const SizedBox(height: 4),
                            InkWell(
                              onTap: () async {
                                final picked = await showDateRangePicker(
                                  context: context,
                                  firstDate: DateTime(2000),
                                  lastDate: DateTime.now(),
                                  initialDateRange: DateTimeRange(
                                    start: _startDate,
                                    end: _endDate,
                                  ),
                                );
                                if (picked != null) {
                                  setState(() {
                                    _startDate = picked.start;
                                    _endDate = picked.end;
                                  });
                                }
                              },
                              borderRadius: BorderRadius.circular(8),
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                                decoration: BoxDecoration(
                                  border: Border.all(color: Colors.grey.shade400),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(Icons.date_range, size: 18, color: Colors.grey),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        '${_startDate.month}/${_startDate.day}/${_startDate.year}  →  ${_endDate.month}/${_endDate.day}/${_endDate.year}',
                                        style: const TextStyle(fontSize: 14),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        );

                        final aggregationWidget = Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Aggregation', style: TextStyle(fontSize: 12)),
                            const SizedBox(height: 4),
                            DropdownButtonFormField<String>(
                              value: _aggregation,
                              decoration: const InputDecoration(
                                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                border: OutlineInputBorder(),
                                isDense: true,
                              ),
                              items: ['Quarterly', 'Yearly']
                                  .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                                  .toList(),
                              onChanged: (value) {
                                if (value != null) setState(() => _aggregation = value);
                              },
                            ),
                          ],
                        );

                        if (isNarrow) {
                          return Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              dateRangeWidget,
                              const SizedBox(height: 16),
                              aggregationWidget,
                            ],
                          );
                        }

                        return Row(
                          children: [
                            Expanded(flex: 2, child: dateRangeWidget),
                            const SizedBox(width: 16),
                            Expanded(child: aggregationWidget),
                          ],
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          // Combined Chart
          _buildCombinedChart(fundamentals, tickerData),
        ],
      ),
    );
  }

  Widget _buildMetricSelector(
    String title,
    List<String> selected,
    AsyncValue<Map<String, dynamic>> data,
    ValueChanged<List<String>> onChanged,
  ) {
    return data.when(
      data: (dataMap) {
        final dataArray = dataMap['data'];
        final availableMetrics = <String>{};
        
        if (dataArray is List) {
          for (final item in dataArray) {
            if (item is Map) {
              final metric = item['Metric'] ?? item['metric'];
              if (metric != null) availableMetrics.add(metric.toString());
            }
          }
        }

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            InkWell(
              onTap: () async {
                await _showMetricSelectionDialog(
                  title,
                  availableMetrics.toList(),
                  selected,
                  onChanged,
                );
              },
              child: InputDecorator(
                decoration: const InputDecoration(
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        selected.isEmpty
                            ? 'Select metrics...'
                            : '${selected.length} metric${selected.length != 1 ? 's' : ''} selected',
                        style: TextStyle(
                          color: selected.isEmpty ? Colors.grey : Colors.black,
                        ),
                      ),
                    ),
                    const Icon(Icons.arrow_drop_down),
                  ],
                ),
              ),
            ),
            if (selected.isNotEmpty) ...[
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: selected
                    .map((metric) => Chip(
                          label: Text(metric, style: const TextStyle(fontSize: 12)),
                          deleteIcon: const Icon(Icons.close, size: 16),
                          onDeleted: () {
                            final newList = List<String>.from(selected)
                              ..remove(metric);
                            onChanged(newList);
                          },
                        ))
                    .toList(),
              ),
            ],
          ],
        );
      },
      loading: () => const CircularProgressIndicator(),
      error: (_, __) => Text('Error loading $title'),
    );
  }

  Widget _buildEarningsSelector() {
    final earningsMetrics = ['Reported EPS', 'Estimated EPS'];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Earnings', style: TextStyle(fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        InkWell(
          onTap: () async {
            await _showMetricSelectionDialog(
              'Earnings',
              earningsMetrics,
              _selectedEarnings,
              (selected) {
                setState(() => _selectedEarnings = selected);
              },
            );
          },
          child: InputDecorator(
            decoration: const InputDecoration(
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              border: OutlineInputBorder(),
              isDense: true,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    _selectedEarnings.isEmpty
                        ? 'Select metrics...'
                        : '${_selectedEarnings.length} metric${_selectedEarnings.length != 1 ? 's' : ''} selected',
                    style: TextStyle(
                      color:
                          _selectedEarnings.isEmpty ? Colors.grey : Colors.black,
                    ),
                  ),
                ),
                const Icon(Icons.arrow_drop_down),
              ],
            ),
          ),
        ),
        if (_selectedEarnings.isNotEmpty) ...[
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _selectedEarnings
                .map((metric) => Chip(
                      label: Text(metric, style: const TextStyle(fontSize: 12)),
                      deleteIcon: const Icon(Icons.close, size: 16),
                      onDeleted: () {
                        setState(() {
                          _selectedEarnings = List<String>.from(_selectedEarnings)
                            ..remove(metric);
                        });
                      },
                    ))
                .toList(),
          ),
        ],
      ],
    );
  }

  Widget _buildMacroeconomicSelector() {
    // Placeholder for now
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Macroeconomic Data',
            style: TextStyle(fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        InputDecorator(
          decoration: const InputDecoration(
            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            border: OutlineInputBorder(),
            isDense: true,
          ),
          child: Text(
            'Select macroeconomic indicators...',
            style: TextStyle(color: Colors.grey),
          ),
        ),
      ],
    );
  }

  Future<void> _showMetricSelectionDialog(
    String title,
    List<String> available,
    List<String> selected,
    ValueChanged<List<String>> onChanged,
  ) async {
    final result = await showDialog<List<String>>(
      context: context,
      builder: (context) => _MetricSelectionDialog(
        title: title,
        available: available,
        initialSelected: selected,
      ),
    );
    if (result != null) {
      onChanged(result);
    }
  }

  Widget _buildDatePicker(
      String label, DateTime value, ValueChanged<DateTime> onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 12)),
        const SizedBox(height: 4),
        InkWell(
          onTap: () async {
            final date = await showDatePicker(
              context: context,
              initialDate: value,
              firstDate: DateTime(2000),
              lastDate: DateTime.now(),
            );
            if (date != null) {
              onChanged(date);
            }
          },
          child: InputDecorator(
            decoration: const InputDecoration(
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              border: OutlineInputBorder(),
              isDense: true,
            ),
            child: Text(
              '${value.month}/${value.day}/${value.year}',
              style: const TextStyle(fontSize: 14),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCombinedChart(
    AsyncValue<Map<String, dynamic>> fundamentals,
    AsyncValue<Map<String, dynamic>> tickerData,
  ) {
    final totalSelected =
        _selectedFundamentals.length + _selectedEarnings.length;
    
    if (totalSelected == 0) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(48),
          child: Center(
            child: Column(
              children: [
                Icon(Icons.auto_graph, size: 64, color: Colors.grey.shade300),
                const SizedBox(height: 16),
                Text(
                  'Select metrics above to create your custom chart',
                  style: TextStyle(color: Colors.grey.shade600),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Combined Metric Analysis',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 400,
              child: fundamentals.when(
                data: (fundData) => tickerData.when(
                  data: (tickerDataMap) {
                    final chartData = _prepareCombinedData(fundData, tickerDataMap);
                    if (chartData.isEmpty) {
                      return Center(
                        child: Text(
                          'No data available for selected metrics',
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                      );
                    }
                    return _renderCombinedChart(chartData);
                  },
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (e, _) => Center(child: Text('Error: $e')),
                ),
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Center(child: Text('Error: $e')),
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<_CombinedDataPoint> _prepareCombinedData(
    Map<String, dynamic> fundData,
    Map<String, dynamic> tickerData,
  ) {
    final Map<DateTime, Map<String, double>> timeSeriesMap = {};
    
    // Extract fundamental metrics
    if (_selectedFundamentals.isNotEmpty) {
      final dataArray = fundData['data'];
      if (dataArray is List) {
        for (final item in dataArray) {
          if (item is! Map) continue;
          
          final metric = item['Metric'] ?? item['metric'];
          if (!_selectedFundamentals.contains(metric)) continue;
          
          final date = _parseDate(item['Date'] ?? item['date']);
          if (date == null) continue;
          
          final value = _parseDouble(item['Value'] ?? item['value']);
          if (value == null) continue;
          
          timeSeriesMap.putIfAbsent(date, () => {});
          timeSeriesMap[date]![metric] = value;
        }
      }
    }
    
    // Extract earnings metrics
    if (_selectedEarnings.isNotEmpty) {
      final earningsDates = tickerData['earnings_dates'];
      if (earningsDates is List) {
        for (final item in earningsDates) {
          if (item is! Map) continue;
          
          final date = _parseDate(
            item['Earnings Date'] ?? item['earningsDate'] ?? item['date']
          );
          if (date == null) continue;
          
          if (_selectedEarnings.contains('Reported EPS')) {
            final value = _parseDouble(
              item['Reported EPS'] ?? item['reportedEPS']
            );
            if (value != null) {
              timeSeriesMap.putIfAbsent(date, () => {});
              timeSeriesMap[date]!['Reported EPS'] = value;
            }
          }
          
          if (_selectedEarnings.contains('Estimated EPS')) {
            final value = _parseDouble(
              item['EPS Estimate'] ?? item['estimatedEPS']
            );
            if (value != null) {
              timeSeriesMap.putIfAbsent(date, () => {});
              timeSeriesMap[date]!['Estimated EPS'] = value;
            }
          }
        }
      }
    }
    
    // Filter by date range
    final filteredMap = Map.fromEntries(
      timeSeriesMap.entries.where((entry) =>
        entry.key.isAfter(_startDate.subtract(const Duration(days: 1))) &&
        entry.key.isBefore(_endDate.add(const Duration(days: 1)))
      )
    );
    
    // Convert to list and sort
    final dataPoints = filteredMap.entries
        .map((e) => _CombinedDataPoint(date: e.key, values: e.value))
        .toList();
    dataPoints.sort((a, b) => a.date.compareTo(b.date));
    
    // Normalize values to 0-100 scale
    for (final metric in [..._selectedFundamentals, ..._selectedEarnings]) {
      final values = dataPoints
          .where((p) => p.values.containsKey(metric))
          .map((p) => p.values[metric]!)
          .toList();
      
      if (values.isEmpty) continue;
      
      final min = values.reduce((a, b) => a < b ? a : b);
      final max = values.reduce((a, b) => a > b ? a : b);
      final range = max - min;
      
      if (range == 0) continue;
      
      for (final point in dataPoints) {
        if (point.values.containsKey(metric)) {
          final original = point.values[metric]!;
          point.values['${metric}_normalized'] = ((original - min) / range) * 100;
          point.values['${metric}_original'] = original;
        }
      }
    }
    
    return dataPoints;
  }

  DateTime? _parseDate(dynamic value) {
    if (value == null) return null;
    if (value is DateTime) return value;
    if (value is String) return DateTime.tryParse(value);
    if (value is int) return DateTime.fromMillisecondsSinceEpoch(value);
    return null;
  }

  double? _parseDouble(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }

  Widget _renderCombinedChart(List<_CombinedDataPoint> data) {
    final allMetrics = [..._selectedFundamentals, ..._selectedEarnings];
    final colors = [
      Colors.blue,
      Colors.green,
      Colors.orange,
      Colors.purple,
      Colors.red,
      Colors.teal,
    ];
    
    final lineBarsData = <LineChartBarData>[];
    
    for (int i = 0; i < allMetrics.length; i++) {
      final metric = allMetrics[i];
      final color = colors[i % colors.length];
      
      final spots = <FlSpot>[];
      for (int j = 0; j < data.length; j++) {
        final normalized = data[j].values['${metric}_normalized'];
        if (normalized != null) {
          spots.add(FlSpot(j.toDouble(), normalized));
        }
      }
      
      if (spots.isNotEmpty) {
        lineBarsData.add(LineChartBarData(
          spots: spots,
          color: color,
          barWidth: 2,
          dotData: const FlDotData(show: false),
          isCurved: true,
        ));
      }
    }
    
    if (lineBarsData.isEmpty) {
      return const Center(child: Text('No data to display'));
    }
    
    return Column(
      children: [
        // Legend
        Wrap(
          spacing: 16,
          runSpacing: 8,
          children: allMetrics.asMap().entries.map((entry) {
            final index = entry.key;
            final metric = entry.value;
            final color = colors[index % colors.length];
            return Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 16,
                  height: 3,
                  color: color,
                ),
                const SizedBox(width: 4),
                Text(metric, style: const TextStyle(fontSize: 12)),
              ],
            );
          }).toList(),
        ),
        const SizedBox(height: 16),
        Expanded(
          child: LineChart(
            LineChartData(
              minY: 0,
              maxY: 100,
              gridData: const FlGridData(show: true),
              titlesData: FlTitlesData(
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 40,
                    getTitlesWidget: (value, meta) {
                      return Text('${value.toInt()}%', style: const TextStyle(fontSize: 10));
                    },
                  ),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 30,
                    getTitlesWidget: (value, meta) {
                      final index = value.toInt();
                      if (index < 0 || index >= data.length) {
                        return const SizedBox.shrink();
                      }
                      
                      final interval = (data.length / 5).ceil();
                      if (index % interval != 0 && index != data.length - 1) {
                        return const SizedBox.shrink();
                      }
                      
                      final date = data[index].date;
                      return Text(
                        DateFormat('MMM\nyy').format(date),
                        style: const TextStyle(fontSize: 9),
                        textAlign: TextAlign.center,
                      );
                    },
                  ),
                ),
                rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              ),
              borderData: FlBorderData(show: true),
              lineTouchData: LineTouchData(
                enabled: true,
                touchTooltipData: LineTouchTooltipData(
                  getTooltipItems: (touchedSpots) {
                    return touchedSpots.map((spot) {
                      final index = spot.x.toInt();
                      if (index < 0 || index >= data.length) return null;
                      
                      final point = data[index];
                      final metricIndex = lineBarsData.indexOf(
                        lineBarsData.firstWhere((bar) => bar.spots.contains(spot))
                      );
                      final metric = allMetrics[metricIndex];
                      final original = point.values['${metric}_original'];
                      
                      return LineTooltipItem(
                        '$metric\n${original?.toStringAsFixed(2) ?? 'N/A'}',
                        const TextStyle(color: Colors.white, fontSize: 11),
                      );
                    }).toList();
                  },
                ),
              ),
              lineBarsData: lineBarsData,
            ),
          ),
        ),
      ],
    );
  }
}

class _CombinedDataPoint {
  final DateTime date;
  final Map<String, double> values; // metric name -> normalized value

  _CombinedDataPoint({required this.date, required this.values});
}

class _MetricSelectionDialog extends StatefulWidget {
  const _MetricSelectionDialog({
    required this.title,
    required this.available,
    required this.initialSelected,
  });

  final String title;
  final List<String> available;
  final List<String> initialSelected;

  @override
  State<_MetricSelectionDialog> createState() => _MetricSelectionDialogState();
}

class _MetricSelectionDialogState extends State<_MetricSelectionDialog> {
  late List<String> _selected;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _selected = List.from(widget.initialSelected);
  }

  @override
  Widget build(BuildContext context) {
    final filtered = widget.available
        .where((m) => m.toLowerCase().contains(_searchQuery.toLowerCase()))
        .toList();

    return AlertDialog(
      title: Text('Select ${widget.title}'),
      content: SizedBox(
        width: 400,
        height: 500,
        child: Column(
          children: [
            TextField(
              decoration: const InputDecoration(
                labelText: 'Search metrics',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
              onChanged: (value) {
                setState(() => _searchQuery = value);
              },
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: filtered.length,
                itemBuilder: (context, index) {
                  final metric = filtered[index];
                  final isSelected = _selected.contains(metric);
                  return CheckboxListTile(
                    title: Text(metric),
                    value: isSelected,
                    onChanged: (checked) {
                      setState(() {
                        if (checked == true) {
                          _selected.add(metric);
                        } else {
                          _selected.remove(metric);
                        }
                      });
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () => Navigator.of(context).pop(_selected),
          child: const Text('Apply'),
        ),
      ],
    );
  }
}
