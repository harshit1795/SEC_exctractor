import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../price_chart.dart';

class PriceChartTab extends StatelessWidget {
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
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: [
          _FilterPanel(
            tickerData: tickerData,
            fundamentals: fundamentals,
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
    return tickerData.when(
      data: (data) {
        final seriesList = <PriceSeries>[];
        
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
                final points = parsePriceSeries(tickerPayload);
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
            final points = parsePriceSeries(data);
            if (points.isNotEmpty) {
                final ticker = data['ticker'] as String? ?? 'Stock';
                seriesList.add(PriceSeries(
                    name: ticker,
                    points: points,
                    color: Colors.black,
                ));
            }
        }
        
        return PriceChart(seriesList: seriesList);
      },
      loading: () => const SizedBox(height: 300, child: Center(child: CircularProgressIndicator())),
      error: (e, s) => SizedBox(height: 300, child: Center(child: Text('Error: $e'))),
    );
  }
}

class _FilterPanel extends StatefulWidget {
  const _FilterPanel({
    required this.tickerData,
    required this.fundamentals,
  });

  final AsyncValue<Map<String, dynamic>> tickerData;
  final AsyncValue<Map<String, dynamic>> fundamentals;

  @override
  State<_FilterPanel> createState() => _FilterPanelState();
}

class _FilterPanelState extends State<_FilterPanel> {
  DateTime? _startDate;
  DateTime? _endDate;
  String _chartType = 'Line';
  String _aggregation = 'Daily';
  bool _showBollinger = true;
  bool _showRSI = true;
  bool _showMACD = true;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Date Range Filter
            const Text(
              'Date Range Filter',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Start Date', style: TextStyle(fontSize: 12)),
                      const SizedBox(height: 4),
                      InkWell(
                        onTap: () async {
                          final date = await showDatePicker(
                            context: context,
                            initialDate: _startDate ?? DateTime.now().subtract(const Duration(days: 365)),
                            firstDate: DateTime(2000),
                            lastDate: DateTime.now(),
                          );
                          if (date != null) {
                            setState(() => _startDate = date);
                          }
                        },
                        child: InputDecorator(
                          decoration: const InputDecoration(
                            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                          child: Text(
                            _startDate != null
                                ? '${_startDate!.month}/${_startDate!.day}/${_startDate!.year}'
                                : 'mm/dd/yyyy',
                            style: TextStyle(
                              color: _startDate != null ? Colors.black : Colors.grey,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('End Date', style: TextStyle(fontSize: 12)),
                      const SizedBox(height: 4),
                      InkWell(
                        onTap: () async {
                          final date = await showDatePicker(
                            context: context,
                            initialDate: _endDate ?? DateTime.now(),
                            firstDate: _startDate ?? DateTime(2000),
                            lastDate: DateTime.now(),
                          );
                          if (date != null) {
                            setState(() => _endDate = date);
                          }
                        },
                        child: InputDecorator(
                          decoration: const InputDecoration(
                            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                          child: Text(
                            _endDate != null
                                ? '${_endDate!.month}/${_endDate!.day}/${_endDate!.year}'
                                : 'mm/dd/yyyy',
                            style: TextStyle(
                              color: _endDate != null ? Colors.black : Colors.grey,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Padding(
                  padding: const EdgeInsets.only(top: 20),
                  child: OutlinedButton(
                    onPressed: () {
                      setState(() {
                        _startDate = null;
                        _endDate = null;
                      });
                    },
                    child: const Text('Clear Filter'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // Controls Row
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Chart Type
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Chart Type', style: TextStyle(fontSize: 12)),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Radio<String>(
                            value: 'Line',
                            groupValue: _chartType,
                            onChanged: (value) {
                              if (value != null) {
                                setState(() => _chartType = value);
                              }
                            },
                          ),
                          const Text('Line'),
                          const SizedBox(width: 16),
                          Radio<String>(
                            value: 'Candlestick',
                            groupValue: _chartType,
                            onChanged: (value) {
                              if (value != null) {
                                setState(() => _chartType = value);
                              }
                            },
                          ),
                          const Text('Candlestick'),
                        ],
                      ),
                    ],
                  ),
                ),
                // Aggregation
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Aggregation', style: TextStyle(fontSize: 12)),
                      const SizedBox(height: 8),
                      DropdownButton<String>(
                        value: _aggregation,
                        isExpanded: true,
                        items: ['Daily', 'Weekly', 'Monthly']
                            .map((value) => DropdownMenuItem(
                                  value: value,
                                  child: Text(value),
                                ))
                            .toList(),
                        onChanged: (value) {
                          if (value != null) {
                            setState(() => _aggregation = value);
                          }
                        },
                      ),
                    ],
                  ),
                ),
                // Indicators
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Indicators', style: TextStyle(fontSize: 12)),
                      const SizedBox(height: 4),
                      CheckboxListTile(
                        title: const Text('Bollinger Bands', style: TextStyle(fontSize: 14)),
                        value: _showBollinger,
                        onChanged: (value) {
                          setState(() => _showBollinger = value ?? true);
                        },
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        controlAffinity: ListTileControlAffinity.leading,
                      ),
                      CheckboxListTile(
                        title: const Text('RSI', style: TextStyle(fontSize: 14)),
                        value: _showRSI,
                        onChanged: (value) {
                          setState(() => _showRSI = value ?? true);
                        },
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        controlAffinity: ListTileControlAffinity.leading,
                      ),
                      CheckboxListTile(
                        title: const Text('MACD', style: TextStyle(fontSize: 14)),
                        value: _showMACD,
                        onChanged: (value) {
                          setState(() => _showMACD = value ?? true);
                        },
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        controlAffinity: ListTileControlAffinity.leading,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
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
