
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'utils/technical_indicators.dart';

class PricePoint {
  PricePoint({required this.date, required this.close});

  final DateTime date;
  final double close;
}

class PriceSeries {
  PriceSeries({
    required this.name,
    required this.points,
    required this.color,
  });

  final String name;
  final List<PricePoint> points;
  final Color color;
}

class PriceChart extends StatefulWidget {
  const PriceChart({
    super.key,
    required this.seriesList,
  });

  final List<PriceSeries> seriesList;

  @override
  State<PriceChart> createState() => _PriceChartState();
}

class _PriceChartState extends State<PriceChart> {
  bool _showBollinger = true;
  bool _showMACD = true;
  bool _showRSI = true;

  // Indicators are only calculated for the FIRST series (primary ticker)
  late BollingerResult _bollinger;
  late MacdResult _macd;
  late RsiResult _rsi;

  @override
  void initState() {
    super.initState();
    _calculateIndicators();
  }

  @override
  void didUpdateWidget(PriceChart oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.seriesList != oldWidget.seriesList) {
      _calculateIndicators();
    }
  }

  void _calculateIndicators() {
    if (widget.seriesList.isEmpty) return;
    // Calculate indicators for the first series only
    final points = widget.seriesList.first.points;
    _bollinger = TechnicalIndicators.calculateBollingerBands(points);
    _macd = TechnicalIndicators.calculateMACD(points);
    _rsi = TechnicalIndicators.calculateRSI(points);
  }

  @override
  Widget build(BuildContext context) {
    if (widget.seriesList.isEmpty || widget.seriesList.every((s) => s.points.isEmpty)) {
      return const SizedBox(
        height: 400,
        child: Center(child: Text('No price data available.')),
      );
    }

    final isMulti = widget.seriesList.length > 1;

    return Column(
      children: [
        _buildKPIs(),
        const SizedBox(height: 16),
        if (!isMulti) ...[
            _buildControls(),
            const SizedBox(height: 16),
        ],
        if (isMulti)
             Wrap(
                 spacing: 12,
                 children: widget.seriesList.map((s) => Chip(
                     label: Text(s.name, style: const TextStyle(color: Colors.white, fontSize: 12)),
                     backgroundColor: s.color,
                     visualDensity: VisualDensity.compact,
                 )).toList(),
             ),
        const SizedBox(height: 12),
        SizedBox(
          height: 300,
          child: _buildMainChart(),
        ),
        if (!isMulti && _showMACD) ...[
            const SizedBox(height: 16),
            const Text('MACD', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
            SizedBox(
                height: 150,
                child: _buildMacdChart(),
            ),
        ],
        if (!isMulti && _showRSI) ...[
            const SizedBox(height: 16),
            const Text('RSI', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
            SizedBox(
                height: 150,
                child: _buildRsiChart(),
            ),
        ]
      ],
    );
  }

  Widget _buildKPIs() {
    if (widget.seriesList.isEmpty) return const SizedBox.shrink();

    // Show KPIs for the first series
    final primary = widget.seriesList.first;
    if (primary.points.isEmpty) return const SizedBox.shrink();

    final lastIdx = primary.points.length - 1;
    final close = primary.points.last.close;
    final rsi = _rsi.values.length > lastIdx ? _rsi.values[lastIdx] : null;
    final macd = _macd.macd.length > lastIdx ? _macd.macd[lastIdx] : null;
    final macdSignal = _macd.signal.length > lastIdx ? _macd.signal[lastIdx] : null;

    final isMulti = widget.seriesList.length > 1;

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        _KpiCard(label: '${primary.name} Close', value: '\$${close.toStringAsFixed(2)}'),
        // Only show indicators if single ticker
        if (!isMulti && rsi != null)
          _KpiCard(label: 'RSI (14)', value: rsi.toStringAsFixed(2), color: _getRsiColor(rsi)),
        if (!isMulti && macd != null && macdSignal != null)
           _KpiCard(
            label: 'MACD', 
            value: '${macd.toStringAsFixed(2)} / ${macdSignal.toStringAsFixed(2)}',
            subtitle: 'MACD / Signal',
           ),
      ],
    );
  }

  Color _getRsiColor(double rsi) {
      if (rsi > 70) return Colors.red;
      if (rsi < 30) return Colors.green;
      return Colors.black;
  }

  Widget _buildControls() {
    return Wrap(
      spacing: 8,
      children: [
        FilterChip(
          label: const Text('Bollinger Bands'),
          selected: _showBollinger,
          onSelected: (v) => setState(() => _showBollinger = v),
        ),
        FilterChip(
          label: const Text('MACD'),
          selected: _showMACD,
          onSelected: (v) => setState(() => _showMACD = v),
        ),
        FilterChip(
          label: const Text('RSI'),
          selected: _showRSI,
          onSelected: (v) => setState(() => _showRSI = v),
        ),
      ],
    );
  }

  Widget _buildMainChart() {
    final allPoints = widget.seriesList.expand((s) => s.points).toList();
    if (allPoints.isEmpty) return const SizedBox.shrink();

    var minY = allPoints.map((e) => e.close).reduce((a, b) => a < b ? a : b);
    var maxY = allPoints.map((e) => e.close).reduce((a, b) => a > b ? a : b);
    
    final isMulti = widget.seriesList.length > 1;

    // Adjust min/max for Bollinger (only if single)
    if (!isMulti && _showBollinger) {
        final lowers = _bollinger.lower.where((e) => e != null).cast<double>();
        final uppers = _bollinger.upper.where((e) => e != null).cast<double>();
        if (lowers.isNotEmpty) {
            final minLower = lowers.reduce((a, b) => a < b ? a : b);
            if (minLower < minY) minY = minLower;
        }
        if (uppers.isNotEmpty) {
            final maxUpper = uppers.reduce((a, b) => a > b ? a : b);
            if (maxUpper > maxY) maxY = maxUpper;
        }
    }

    final range = (maxY - minY).abs();
    final padding = range == 0 ? maxY * 0.1 : range * 0.1;

    // Use the primary series for x-axis labels
    final primaryPoints = widget.seriesList.first.points;

    return LineChart(
      LineChartData(
        minY: minY - padding,
        maxY: maxY + padding,
        gridData: const FlGridData(show: true),
        titlesData: FlTitlesData(
            leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 50)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 30,
                getTitlesWidget: (value, meta) {
                  final index = value.toInt();
                  if (index < 0 || index >= primaryPoints.length) {
                    return const SizedBox.shrink();
                  }
                  
                  // Show fewer labels based on data density
                  final totalPoints = primaryPoints.length;
                  int interval = 1;
                  if (totalPoints > 100) {
                    interval = (totalPoints / 5).ceil();
                  } else if (totalPoints > 50) {
                    interval = (totalPoints / 7).ceil();
                  } else if (totalPoints > 20) {
                    interval = (totalPoints / 10).ceil();
                  }
                  
                  if (index % interval != 0 && index != totalPoints - 1) {
                    return const SizedBox.shrink();
                  }
                  
                  final date = primaryPoints[index].date;
                  final label = totalPoints > 365
                      ? DateFormat('MMM\nyy').format(date)
                      : totalPoints > 90
                          ? DateFormat('MMM\nd').format(date)
                          : DateFormat('M/d').format(date);
                  
                  return Text(
                    label,
                    style: const TextStyle(fontSize: 10),
                    textAlign: TextAlign.center,
                  );
                },
              ),
            ),
        ),
        borderData: FlBorderData(show: true),
        lineTouchData: LineTouchData(
          enabled: true,
          touchTooltipData: LineTouchTooltipData(
            getTooltipItems: (touchedSpots) {
              return touchedSpots.map((spot) {
                 // Try to identify which series this spot belongs to
                 // This is tricky with FLChart's basic tooltip map
                 // But we know the order of bars matches seriesList order
                 final seriesIndex = spot.barIndex;
                 if (seriesIndex >= widget.seriesList.length) return null;
                 
                 final series = widget.seriesList[seriesIndex];
                 
                final index = spot.x.toInt();
                // Ensure index is valid for THIS series
                if (index < 0 || index >= series.points.length) return null;
                
                final point = series.points[index];
                final date = DateFormat('MMM d, yyyy').format(point.date);
                final price = point.close;
                
                return LineTooltipItem(
                  '${series.name}\n$date: \$${price.toStringAsFixed(2)}',
                  TextStyle(
                    color: series.color,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                );
              }).toList();
            },
          ),
        ),
        lineBarsData: [
            // Generate LineBarData for each series
            ...widget.seriesList.map((series) {
                return LineChartBarData(
                    spots: series.points.asMap().entries.map((e) {
                         return FlSpot(e.key.toDouble(), e.value.close);
                    }).toList(),
                    isCurved: false,
                    barWidth: 2,
                    color: series.color,
                    dotData: const FlDotData(show: false),
                );
            }),
            
          // Bollinger Bands (Only if single ticker)
          if (!isMulti && _showBollinger)
             LineChartBarData(
                spots: _toSpots(_bollinger.upper),
                isCurved: true,
                barWidth: 1,
                color: Colors.blue.withOpacity(0.5),
                dotData: const FlDotData(show: false),
             ),
          if (!isMulti && _showBollinger)
             LineChartBarData(
                spots: _toSpots(_bollinger.middle),
                isCurved: true,
                barWidth: 1,
                color: Colors.blue.withOpacity(0.3),
                dotData: const FlDotData(show: false),
                dashArray: [5, 5],
             ),
          if (!isMulti && _showBollinger)
             LineChartBarData(
                spots: _toSpots(_bollinger.lower),
                isCurved: true,
                barWidth: 1,
                color: Colors.blue.withOpacity(0.5),
                dotData: const FlDotData(show: false),
             ),
        ],
      ),
    );
  }

  Widget _buildMacdChart() {
      // Use LineCharts for MACD and Signal.
      final macdSpots = _toSpots(_macd.macd);
      final signalSpots = _toSpots(_macd.signal);
      
      return LineChart(
          LineChartData(
             gridData: const FlGridData(show: true),
             titlesData: const FlTitlesData(show: false),
             lineBarsData: [
                 LineChartBarData(spots: macdSpots, color: Colors.blue, barWidth: 1.5, dotData: const FlDotData(show: false)),
                 LineChartBarData(spots: signalSpots, color: Colors.orange, barWidth: 1.5, dotData: const FlDotData(show: false)),
             ],
             lineTouchData: const LineTouchData(enabled: true),
          ),
      );
  }

  Widget _buildRsiChart() {
      final rsiSpots = _toSpots(_rsi.values);
      return LineChart(
          LineChartData(
              minY: 0,
              maxY: 100,
              gridData: const FlGridData(show: true),
              titlesData: const FlTitlesData(show: false),
              extraLinesData: ExtraLinesData(
                  horizontalLines: [
                      HorizontalLine(y: 70, color: Colors.red.withOpacity(0.3), strokeWidth: 1, dashArray: [5,5]),
                      HorizontalLine(y: 30, color: Colors.green.withOpacity(0.3), strokeWidth: 1, dashArray: [5,5]),
                  ],
              ),
              lineBarsData: [
                  LineChartBarData(
                      spots: rsiSpots,
                      color: Colors.purple,
                      barWidth: 1.5,
                      dotData: const FlDotData(show: false),
                  ),
              ],
          ),
      );
  }

  List<FlSpot> _toSpots(List<double?> values) {
      final spots = <FlSpot>[];
      for (int i=0; i<values.length; i++) {
          if (values[i] != null) {
              spots.add(FlSpot(i.toDouble(), values[i]!));
          }
      }
      return spots;
  }
}

class _KpiCard extends StatelessWidget {
    const _KpiCard({required this.label, required this.value, this.subtitle, this.color});
    final String label;
    final String value;
    final String? subtitle;
    final Color? color;

    @override
    Widget build(BuildContext context) {
        return Column(
            children: [
                Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                Text(
                    value, 
                    style: TextStyle(
                        fontSize: 16, 
                        fontWeight: FontWeight.bold,
                        color: color ?? Colors.black
                    )
                ),
                if (subtitle != null)
                   Text(subtitle!, style: const TextStyle(fontSize: 10, color: Colors.grey)),
            ],
        );
    }
}

// Helper to parse a single series from payload
List<PricePoint> parsePriceSeries(Map<String, dynamic>? payload) {
  if (payload == null) {
    return [];
  }
  // If payload has 'data' key, it's a wrapper from backend
  var data = payload['data'] ?? payload;
  
  // If data is just a bare map with 'history_df' or 'history'
  if (data is Map<String, dynamic>) {
    final historyDf = data['history_df'];
    final points = <PricePoint>[];
    if (historyDf is List) {
      for (final item in historyDf) {
        if (item is Map) {
          final dateValue = item['Date'] ?? item['date'];
          final closeValue = item['Close'] ?? item['close'];
          final date = _parseDate(dateValue);
          final close = _parseDouble(closeValue);
          if (date != null && close != null) {
            points.add(PricePoint(date: date, close: close));
          }
        }
      }
    }
    if (points.isNotEmpty) {
      points.sort((a, b) => a.date.compareTo(b.date));
      return points;
    }

    final historyMap = data['history'];
    if (historyMap is Map) {
      final closeMap = historyMap['Close'] ?? historyMap['close'];
      if (closeMap is Map) {
        for (final entry in closeMap.entries) {
          final date = _parseDate(entry.key);
          final close = _parseDouble(entry.value);
          if (date != null && close != null) {
            points.add(PricePoint(date: date, close: close));
          }
        }
      }
    }
    points.sort((a, b) => a.date.compareTo(b.date));
    return points;
  }
  return [];
}

DateTime? _parseDate(Object? value) {
  if (value == null) {
    return null;
  }
  if (value is DateTime) {
    return value;
  }
  if (value is String) {
    return DateTime.tryParse(value);
  }
  if (value is int) {
    return DateTime.fromMillisecondsSinceEpoch(value);
  }
  return null;
}

double? _parseDouble(Object? value) {
  if (value == null) {
    return null;
  }
  if (value is num) {
    return value.toDouble();
  }
  if (value is String) {
    return double.tryParse(value);
  }
  return null;
}

