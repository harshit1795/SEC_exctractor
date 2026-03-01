import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../price_chart.dart';
import '../widgets/floating_filter_panel.dart';
import '../../../core/widgets/shimmer_loading.dart';

class PriceChartTab extends StatefulWidget {
  const PriceChartTab({
    super.key,
    required this.period,
    required this.periods,
    required this.onPeriodChanged,
    required this.onSubmit,
    required this.tickerData,
    required this.fundamentals,
  });

  final String period;
  final List<String> periods;
  final ValueChanged<String> onPeriodChanged;
  final VoidCallback onSubmit;
  final AsyncValue<Map<String, dynamic>> tickerData;
  final AsyncValue<Map<String, dynamic>> fundamentals;

  @override
  State<PriceChartTab> createState() => _PriceChartTabState();
}

class _PriceChartTabState extends State<PriceChartTab> {
  DateTime? _startDate;
  DateTime? _endDate;
  String _aggregation = 'Daily';
  bool _showBollinger = true;
  bool _showRSI = true;
  bool _showMACD = true;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: [
          _FilterPanel(
            tickerData: widget.tickerData,
            fundamentals: widget.fundamentals,
            startDate: _startDate,
            endDate: _endDate,
            aggregation: _aggregation,
            showBollinger: _showBollinger,
            showRSI: _showRSI,
            showMACD: _showMACD,
            selectedPeriod: widget.period,
            periods: widget.periods,
            onDateRangeChanged: (start, end) => setState(() {
              _startDate = start;
              _endDate = end;
            }),
            onAggregationChanged: (v) => setState(() => _aggregation = v),
            onBollingerChanged: (v) => setState(() => _showBollinger = v),
            onRsiChanged: (v) => setState(() => _showRSI = v),
            onMacdChanged: (v) => setState(() => _showMACD = v),
            onPeriodChanged: widget.onPeriodChanged,
          ),
          const SizedBox(height: 12),
          _InfoCard(
            title: 'Price Chart',
            child: _buildChartContent(),
          ),
        ],
      ),
    );
  }

  Widget _buildChartContent() {
    return widget.tickerData.when(
      data: (data) {
        final seriesList = <PriceSeries>[];
        
        // Helper to aggregate points based on selected interval
        List<PricePoint> aggregatePoints(List<PricePoint> rawPoints) {
            if (_aggregation == 'Daily' || rawPoints.isEmpty) return rawPoints;
            
            final Map<String, List<PricePoint>> groups = {};
            for (final p in rawPoints) {
                String key;
                if (_aggregation == 'Weekly') {
                     // Get the Monday of this week as the key
                     final monday = p.date.subtract(Duration(days: p.date.weekday - 1));
                     key = '${monday.year}-${monday.month.toString().padLeft(2, '0')}-${monday.day.toString().padLeft(2, '0')}';
                } else {
                     // Monthly
                     key = '${p.date.year}-${p.date.month.toString().padLeft(2, '0')}';
                }
                groups.putIfAbsent(key, () => []).add(p);
            }
            
            final aggregated = <PricePoint>[];
            final sortedKeys = groups.keys.toList()..sort();
            
            for (final key in sortedKeys) {
                 final groupPoints = groups[key]!;
                 groupPoints.sort((a, b) => a.date.compareTo(b.date));
                 
                 final last = groupPoints.last;
                 
                 aggregated.add(PricePoint(
                      date: last.date, // Use end of period date for plotting
                      close: last.close,
                 ));
            }
            return aggregated;
        }

        // Multi-ticker check
        if (data.containsKey('tickers') && data['tickers'] is List) {
            final tickers = (data['tickers'] as List).cast<String>();
            final tickersData = data['data'] as Map<String, dynamic>;
            
            final colors = [
                Colors.black,
                Colors.blue.shade700,
                Colors.orange.shade700,
                Colors.purple.shade700,
                Colors.green.shade700,
            ];
            
            int colorIdx = 0;
            for (final ticker in tickers) {
                final tickerPayload = tickersData[ticker];
                var points = parsePriceSeries(tickerPayload);
                
                // 1. Filter by date range
                if (_startDate != null && _endDate != null) {
                  points = points.where((p) => 
                     p.date.isAfter(_startDate!.subtract(const Duration(days: 1))) && 
                     p.date.isBefore(_endDate!.add(const Duration(days: 1)))
                  ).toList();
                }
                
                // 2. Aggregate data (Daily, Weekly, Monthly)
                points = aggregatePoints(points);

                if (points.isNotEmpty) {
                    seriesList.add(PriceSeries(
                        name: ticker,
                        points: points,
                        color: colors[colorIdx % colors.length],
                    ));
                }
                colorIdx++;
            }
        } else {
            // Single ticker
            var points = parsePriceSeries(data);
            
             // 1. Filter by date range
            if (_startDate != null && _endDate != null) {
              points = points.where((p) => 
                p.date.isAfter(_startDate!.subtract(const Duration(days: 1))) && 
                p.date.isBefore(_endDate!.add(const Duration(days: 1)))
              ).toList();
            }
            
            // 2. Aggregate data (Daily, Weekly, Monthly)
            points = aggregatePoints(points);

            if (points.isNotEmpty) {
                final ticker = data['ticker'] as String? ?? 'Stock';
                seriesList.add(PriceSeries(
                    name: ticker,
                    points: points,
                    color: Colors.black,
                ));
            }
        }
        
        return PriceChart(
          seriesList: seriesList,
          showBollinger: _showBollinger,
          showMACD: _showMACD,
          showRSI: _showRSI,
        );
      },
      loading: () => const ShimmerChart(height: 300),
      error: (e, s) => SizedBox(height: 300, child: Center(child: Text('Error: $e'))),
    );
  }
}

class _FilterPanel extends StatelessWidget {
  const _FilterPanel({
    required this.tickerData,
    required this.fundamentals,
    required this.startDate,
    required this.endDate,
    required this.aggregation,
    required this.showBollinger,
    required this.showRSI,
    required this.showMACD,
    required this.selectedPeriod,
    required this.periods,
    required this.onDateRangeChanged,
    required this.onAggregationChanged,
    required this.onBollingerChanged,
    required this.onRsiChanged,
    required this.onMacdChanged,
    required this.onPeriodChanged,
  });

  final AsyncValue<Map<String, dynamic>> tickerData;
  final AsyncValue<Map<String, dynamic>> fundamentals;
  final DateTime? startDate;
  final DateTime? endDate;
  final String aggregation;
  final bool showBollinger;
  final bool showRSI;
  final bool showMACD;
  final String selectedPeriod;
  final List<String> periods;
  
  final Function(DateTime?, DateTime?) onDateRangeChanged;
  final ValueChanged<String> onAggregationChanged;
  final ValueChanged<bool> onBollingerChanged;
  final ValueChanged<bool> onRsiChanged;
  final ValueChanged<bool> onMacdChanged;
  final ValueChanged<String> onPeriodChanged;

  @override
  Widget build(BuildContext context) {
    return FloatingFilterPanel(
      title: 'Price Chart Filters',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
           // Period Selector
          const Text(
            'Time Period',
            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: periods.map((p) {
                final isSelected = p == selectedPeriod;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(p),
                    selected: isSelected,
                    onSelected: (selected) {
                      if (selected) onPeriodChanged(p);
                    },
                    selectedColor: Theme.of(context).primaryColor.withOpacity(0.2),
                    labelStyle: TextStyle(
                      color: isSelected ? Theme.of(context).primaryColor : Colors.black87,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 16),

          // Date Range Filter
          const Text(
            'Date Range Filter',
            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: InkWell(
                  onTap: () async {
                    final picked = await showDateRangePicker(
                      context: context,
                      firstDate: DateTime(2000),
                      lastDate: DateTime.now(),
                      initialDateRange: startDate != null && endDate != null
                          ? DateTimeRange(start: startDate!, end: endDate!)
                          : DateTimeRange(
                              start: DateTime.now().subtract(const Duration(days: 365)),
                              end: DateTime.now(),
                            ),
                      builder: (context, child) {
                        return Theme(
                          data: Theme.of(context).copyWith(
                            colorScheme: Theme.of(context).colorScheme.copyWith(
                              primary: Theme.of(context).colorScheme.primary,
                            ),
                          ),
                          child: child!,
                        );
                      },
                    );
                    if (picked != null) {
                      onDateRangeChanged(picked.start, picked.end);
                    }
                  },
                  borderRadius: BorderRadius.circular(8),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: startDate != null ? Theme.of(context).colorScheme.primary : Colors.grey.shade400,
                      ),
                      borderRadius: BorderRadius.circular(8),
                      color: startDate != null
                          ? Theme.of(context).colorScheme.primary.withOpacity(0.05)
                          : null,
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.date_range,
                          size: 20,
                          color: startDate != null
                              ? Theme.of(context).colorScheme.primary
                              : Colors.grey,
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            startDate != null && endDate != null
                                ? '${startDate!.month}/${startDate!.day}/${startDate!.year}  →  ${endDate!.month}/${endDate!.day}/${endDate!.year}'
                                : 'Select date range...',
                            style: TextStyle(
                              fontSize: 14,
                              color: startDate != null ? Colors.black87 : Colors.grey,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              if (startDate != null) ...[
                const SizedBox(width: 12),
                IconButton(
                  onPressed: () => onDateRangeChanged(null, null),
                  icon: const Icon(Icons.clear, size: 20),
                  tooltip: 'Clear date range',
                  style: IconButton.styleFrom(
                    foregroundColor: Colors.red.shade600,
                  ),
                ),
              ],
            ],
          ),
          const SizedBox(height: 16),
          // Controls - responsive layout
          LayoutBuilder(
            builder: (context, constraints) {
              final isNarrow = constraints.maxWidth < 600;

              final aggregationWidget = Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Aggregation', style: TextStyle(fontSize: 12)),
                  const SizedBox(height: 8),
                  DropdownButton<String>(
                    value: aggregation,
                    isExpanded: true,
                    items: ['Daily', 'Weekly', 'Monthly']
                        .map((value) => DropdownMenuItem(
                              value: value,
                              child: Text(value),
                            ))
                        .toList(),
                    onChanged: (value) {
                      if (value != null) onAggregationChanged(value);
                    },
                  ),
                ],
              );

              final indicatorsWidget = Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Indicators', style: TextStyle(fontSize: 12)),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 16,
                    runSpacing: 4,
                    children: [
                      _CompactCheckbox(
                        label: 'Bollinger Bands',
                        value: showBollinger,
                        onChanged: (v) => onBollingerChanged(v ?? true),
                      ),
                      _CompactCheckbox(
                        label: 'RSI',
                        value: showRSI,
                        onChanged: (v) => onRsiChanged(v ?? true),
                      ),
                      _CompactCheckbox(
                        label: 'MACD',
                        value: showMACD,
                        onChanged: (v) => onMacdChanged(v ?? true),
                      ),
                    ],
                  ),
                ],
              );

              if (isNarrow) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    aggregationWidget,
                    const SizedBox(height: 16),
                    indicatorsWidget,
                  ],
                );
              }

              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: aggregationWidget),
                  const SizedBox(width: 24),
                  Expanded(flex: 2, child: indicatorsWidget),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}

class _CompactCheckbox extends StatelessWidget {
  const _CompactCheckbox({
    required this.label,
    required this.value,
    required this.onChanged,
  });

  final String label;
  final bool value;
  final ValueChanged<bool?> onChanged;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () => onChanged(!value),
      borderRadius: BorderRadius.circular(4),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: 24,
            height: 24,
            child: Checkbox(
              value: value,
              onChanged: onChanged,
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              visualDensity: VisualDensity.compact,
            ),
          ),
          const SizedBox(width: 4),
          Text(label, style: const TextStyle(fontSize: 14)),
        ],
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            child,
          ],
        ),
      ),
    );
  }
}
