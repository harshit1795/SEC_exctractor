import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';

import '../dashboard_providers.dart';
import '../widgets/tab_description_tooltip.dart';
import '../widgets/floating_filter_panel.dart';

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
  var _chartType = _ChartType.bar;
  var _aggregation = _Aggregation.quarterly;
  
  final List<Color> _tickerColors = [
    Colors.black,
    Colors.blue.shade700,
    Colors.orange.shade700,
    Colors.purple.shade700,
    Colors.green.shade700,
  ];

  @override
  Widget build(BuildContext context) {
    final tickerData = ref.watch(tickerDataProvider);

    return tickerData.when(
      data: (data) {
        final parsed = _parseTickerData(data);
        
        if (parsed.tickerData.isEmpty) {
          return Center(
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Text(
                  'No earnings data available.',
                  style: TextStyle(color: Colors.grey.shade600),
                ),
              ),
            ),
          );
        }
        
        final isMulti = parsed.tickers.length > 1;

        // Aggregate data for charting
        final chartDataMap = <String, List<_ChartDataPoint>>{};
        for (final ticker in parsed.tickers) {
            final earnings = parsed.tickerData[ticker] ?? [];
            if (earnings.isNotEmpty) {
                chartDataMap[ticker] = _aggregateData(earnings);
            }
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
                      'Earnings Analysis',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                    const SizedBox(width: 8),
                    const TabDescriptionTooltip(tabId: 'earnings'),
                  ],
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

              // Historical EPS Trend Chart
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Historical EPS Trend (Reported)',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                  FloatingFilterPanel(
                        title: 'Earnings Filters',
                        child: Wrap(
                          spacing: 24,
                          runSpacing: 16,
                          children: [
                            Column(
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
                            Column(
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
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),
                      if (chartDataMap.isNotEmpty)
                        SizedBox(
                          height: 300,
                          child: _chartType == _ChartType.line
                              ? _buildLineChart(parsed, chartDataMap)
                              : _buildBarChart(parsed, chartDataMap),
                        ),
                      if (chartDataMap.isNotEmpty && !isMulti) ...[
                        const SizedBox(height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            _buildLegendItem(
                              'Reported EPS',
                              Colors.blue,
                              isLine: true,
                            ),
                            const SizedBox(width: 24),
                            _buildLegendItem(
                              'Estimated EPS',
                              Colors.green,
                              isLine: true,
                              isDashed: true,
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              
              // Last Quarter's Earnings
              Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                      const Padding(
                          padding: EdgeInsets.only(left: 4, bottom: 8),
                          child: Text(
                              'Last Quarter\'s Earnings',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                      ),
                      LayoutBuilder(builder: (context, constraints) {
                          return Wrap(
                              spacing: 16,
                              runSpacing: 16,
                              children: parsed.tickers.map((ticker) {
                                  final earnings = parsed.tickerData[ticker] ?? [];
                                  final lastEarnings = _getLastEarnings(earnings);
                                  if (lastEarnings == null) return const SizedBox.shrink();
                                  
                                  return SizedBox(
                                      width: isMulti && constraints.maxWidth > 600 ? (constraints.maxWidth - 16) / 2 : constraints.maxWidth,
                                      child: Card(
                                          child: Padding(
                                              padding: const EdgeInsets.all(16),
                                              child: Column(
                                                  crossAxisAlignment: CrossAxisAlignment.start,
                                                  children: [
                                                      Text(ticker, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                                                      const Divider(),
                                                      const SizedBox(height: 8),
                                                      _buildStatItem(
                                                          'Date',
                                                          DateFormat.yMMMMd().format(lastEarnings.date),
                                                      ),
                                                      const SizedBox(height: 12),
                                                      Row(
                                                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                          children: [
                                                              _buildStatItem(
                                                                  'Reported',
                                                                  '\$${lastEarnings.reportedEPS.toStringAsFixed(2)}',
                                                              ),
                                                              _buildStatItem(
                                                                  'Estimated',
                                                                  '\$${lastEarnings.estimatedEPS.toStringAsFixed(2)}',
                                                              ),
                                                          ],
                                                      ),
                                                      if (lastEarnings.surprise != null) ...[
                                                          const SizedBox(height: 12),
                                                          _buildStatItem(
                                                              'Surprise',
                                                              '${lastEarnings.surprise! > 0 ? '+' : ''}${lastEarnings.surprise!.toStringAsFixed(2)}%',
                                                              color: lastEarnings.surprise! > 0
                                                                  ? Colors.green
                                                                  : Colors.red,
                                                          ),
                                                      ]
                                                  ],
                                              ),
                                          ),
                                      ),
                                  );
                              }).toList(),
                          );
                      }),
                  ],
              ),
              
              const SizedBox(height: 16),

              // Next Earnings
              Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                      const Padding(
                          padding: EdgeInsets.only(left: 4, bottom: 8),
                          child: Text(
                              'Next Earnings',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                      ),
                      LayoutBuilder(builder: (context, constraints) {
                          return Wrap(
                              spacing: 16,
                              runSpacing: 16,
                              children: parsed.tickers.map((ticker) {
                                  final earnings = parsed.tickerData[ticker] ?? [];
                                  final nextEarnings = _getNextEarnings(earnings);
                                  if (nextEarnings == null) return const SizedBox.shrink();
                                  
                                  return SizedBox(
                                      width: isMulti && constraints.maxWidth > 600 ? (constraints.maxWidth - 16) / 2 : constraints.maxWidth,
                                      child: Card(
                                          child: Padding(
                                              padding: const EdgeInsets.all(16),
                                              child: Column(
                                                  crossAxisAlignment: CrossAxisAlignment.start,
                                                  children: [
                                                      Text(ticker, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                                                      const Divider(),
                                                      const SizedBox(height: 8),
                                                      _buildStatItem(
                                                          'Date',
                                                          DateFormat.yMMMMd().format(nextEarnings.date),
                                                      ),
                                                      const SizedBox(height: 12),
                                                      _buildStatItem(
                                                          'Estimate',
                                                          '\$${nextEarnings.estimatedEPS.toStringAsFixed(2)}',
                                                      ),
                                                  ],
                                              ),
                                          ),
                                      ),
                                  );
                              }).toList(),
                          );
                      }),
                  ],
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
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildLegendItem(String label, Color color,
      {bool isLine = false, bool isDashed = false}) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 24,
          height: 3,
          decoration: BoxDecoration(
            color: isDashed ? Colors.transparent : color,
            border: isDashed
                ? Border(
                    bottom: BorderSide(
                      color: color,
                      width: 2,
                      style: BorderStyle.solid,
                    ),
                  )
                : null,
          ),
          child: isDashed
              ? CustomPaint(
                  painter: _DashedLinePainter(color: color),
                )
              : null,
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: const TextStyle(fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildLineChart(_EarningsData parsed, Map<String, List<_ChartDataPoint>> chartDataMap) {
      if (parsed.tickers.isEmpty) return const SizedBox.shrink();
      
      // Collect all periods
      final periodSet = <String>{};
      for(final data in chartDataMap.values) {
          periodSet.addAll(data.map((d) => d.period));
      }
      
      // Sort periods (Assuming format MMM yyyy or yyyy)
      final allPeriods = periodSet.toList()..sort((a, b) {
          // Simple parsing for sort
          try {
              if (a.length == 4 && b.length == 4) return a.compareTo(b); // Years
              final da = DateFormat('MMM yyyy').parse(a);
              final db = DateFormat('MMM yyyy').parse(b);
              return da.compareTo(db);
          } catch (e) {
              return a.compareTo(b);
          }
      });

      List<LineChartBarData> lines = [];
      int tickerIdx = 0;
      
      for (final ticker in parsed.tickers) {
          final data = chartDataMap[ticker] ?? [];
          final color = _tickerColors[tickerIdx % _tickerColors.length];
          
          final spots = <FlSpot>[];
          for (int i = 0; i < allPeriods.length; i++) {
              final period = allPeriods[i];
              // Find data
              final point = data.where((d) => d.period == period).firstOrNull;
              if (point != null) {
                  spots.add(FlSpot(i.toDouble(), point.reportedEPS));
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
              belowBarData: BarAreaData(show: false),
          ));
          
          // If single ticker, maybe add estimated? (Leaving out for now for simplicity/consistency)
          if (parsed.tickers.length == 1) {
             // Add estimated line
             final estimatedSpots = <FlSpot>[];
             for (int i = 0; i < allPeriods.length; i++) {
                final period = allPeriods[i];
                final point = data.where((d) => d.period == period).firstOrNull;
                if (point != null) {
                    estimatedSpots.add(FlSpot(i.toDouble(), point.estimatedEPS));
                }
             }
             
             lines.add(LineChartBarData(
                spots: estimatedSpots,
                isCurved: false,
                color: Colors.green,
                barWidth: 2,
                dotData: FlDotData(
                  show: true,
                  getDotPainter: (spot, percent, barData, index) {
                    return FlDotCirclePainter(
                      radius: 2,
                      color: Colors.green,
                      strokeWidth: 0,
                    );
                  },
                ),
                dashArray: [5, 5],
                belowBarData: BarAreaData(show: false),
             ));
          }
          
          tickerIdx++;
      }

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
                if (index >= 0 && index < allPeriods.length) {
                  // Show every other label if too many
                  if (allPeriods.length > 10 && index % 2 != 0) return const Text('');
                  
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
                 if (lines.length > 1 && parsed.tickers.length > 1) {
                     // Multi-ticker tooltip
                     final tickerIndex = touchedSpot.barIndex;
                     final tickerName = tickerIndex < parsed.tickers.length ? parsed.tickers[tickerIndex] : '';
                     return LineTooltipItem(
                      '$tickerName\n${touchedSpot.y.toStringAsFixed(2)}',
                      TextStyle(
                        color: touchedSpot.bar.color ?? Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    );
                 } else {
                     // Single ticker tooltip
                     final isReported = touchedSpot.barIndex == 0;
                     return LineTooltipItem(
                      '${isReported ? 'Reported' : 'Estimated'}: ${touchedSpot.y.toStringAsFixed(2)}',
                      TextStyle(
                        color: touchedSpot.bar.color ?? Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    );
                 }
              }).toList();
            },
          ),
        ),
        lineBarsData: lines,
      ),
    );
  }

  Widget _buildBarChart(_EarningsData parsed, Map<String, List<_ChartDataPoint>> chartDataMap) {
      if (parsed.tickers.isEmpty) return const SizedBox.shrink();
      
      // Collect all periods
      final periodSet = <String>{};
      for(final data in chartDataMap.values) {
          periodSet.addAll(data.map((d) => d.period));
      }
      
      // Sort
      final allPeriods = periodSet.toList()..sort((a, b) {
          try {
              if (a.length == 4 && b.length == 4) return a.compareTo(b);
              final da = DateFormat('MMM yyyy').parse(a);
              final db = DateFormat('MMM yyyy').parse(b);
              return da.compareTo(db);
          } catch (e) {
              return a.compareTo(b);
          }
      });
    
      final barGroups = <BarChartGroupData>[];
      
      for (int i = 0; i < allPeriods.length; i++) {
        final period = allPeriods[i];
        final rods = <BarChartRodData>[];
        
        int tickerIdx = 0;
        for (final ticker in parsed.tickers) {
             final data = chartDataMap[ticker] ?? [];
             final color = _tickerColors[tickerIdx % _tickerColors.length];
             
             final point = data.where((d) => d.period == period).firstOrNull;
             
             if (point != null) {
                  rods.add(BarChartRodData(
                     toY: point.reportedEPS,
                     color: color,
                     width: 12,
                     borderRadius: BorderRadius.circular(4),
                 ));
             } else {
                  rods.add(BarChartRodData(toY: 0, color: Colors.transparent, width: 12));
             }
             tickerIdx++;
        }
        
        barGroups.add(BarChartGroupData(x: i, barRods: rods, barsSpace: 4));
    }


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
      ),
    );
  }

  _EarningsData _parseTickerData(Map<String, dynamic> data) {
    if (data.containsKey('tickers') && data['data'] is Map) {
         // Multi-ticker
         final tickers = (data['tickers'] as List).cast<String>();
         final rawDataMap = data['data'] as Map<String, dynamic>;
         
         final tickerData = <String, List<_EarningsDataPoint>>{};
         
         for (final ticker in tickers) {
              final singleData = rawDataMap[ticker];
              if (singleData != null) {
                  tickerData[ticker] = _parseSingleEarningsData(singleData);
              } else {
                  tickerData[ticker] = [];
              }
         }
         
         return _EarningsData(tickers: tickers, tickerData: tickerData);
    } else {
        // Single
        final ticker = data['ticker'] as String? ?? 'Stock';
        final earnings = _parseSingleEarningsData(data);
        return _EarningsData(
            tickers: [ticker], 
            tickerData: {ticker: earnings}
        );
    }
  }

  List<_EarningsDataPoint> _parseSingleEarningsData(Map<String, dynamic> data) {
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

class _EarningsData {
    const _EarningsData({
        required this.tickers,
        required this.tickerData,
    });
    final List<String> tickers;
    final Map<String, List<_EarningsDataPoint>> tickerData;
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

class _DashedLinePainter extends CustomPainter {
  _DashedLinePainter({required this.color});

  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    const dashWidth = 3.0;
    const dashSpace = 3.0;
    double startX = 0;

    while (startX < size.width) {
      canvas.drawLine(
        Offset(startX, size.height / 2),
        Offset(startX + dashWidth, size.height / 2),
        paint,
      );
      startX += dashWidth + dashSpace;
    }
  }

  @override
  bool shouldRepaint(_DashedLinePainter oldDelegate) => false;
}
