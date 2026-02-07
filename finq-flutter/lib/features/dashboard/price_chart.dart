import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'utils/technical_indicators.dart';

class PricePoint {
  PricePoint({required this.date, required this.close});

  final DateTime date;
  final double close;
}

class PriceChart extends StatefulWidget {
  const PriceChart({
    super.key,
    required this.points,
  });

  final List<PricePoint> points;

  @override
  State<PriceChart> createState() => _PriceChartState();
}

class _PriceChartState extends State<PriceChart> {
  bool _showBollinger = true;
  bool _showMACD = true;
  bool _showRSI = true;

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
    if (widget.points != oldWidget.points) {
      _calculateIndicators();
    }
  }

  void _calculateIndicators() {
    _bollinger = TechnicalIndicators.calculateBollingerBands(widget.points);
    _macd = TechnicalIndicators.calculateMACD(widget.points);
    _rsi = TechnicalIndicators.calculateRSI(widget.points);
  }

  @override
  Widget build(BuildContext context) {
    if (widget.points.isEmpty) {
      return const SizedBox(
        height: 400,
        child: Center(child: Text('No price data available.')),
      );
    }

    return Column(
      children: [
        _buildKPIs(),
        const SizedBox(height: 16),
        _buildControls(),
        const SizedBox(height: 16),
        SizedBox(
          height: 300,
          child: _buildMainChart(),
        ),
        if (_showMACD) ...[
            const SizedBox(height: 16),
            const Text('MACD', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
            SizedBox(
                height: 150,
                child: _buildMacdChart(),
            ),
        ],
        if (_showRSI) ...[
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
    final lastIdx = widget.points.length - 1;
    final close = widget.points.last.close;
    final rsi = _rsi.values[lastIdx];
    final macd = _macd.macd[lastIdx];
    final macdSignal = _macd.signal[lastIdx];

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        _KpiCard(label: 'Close', value: '\$${close.toStringAsFixed(2)}'),
        if (rsi != null)
          _KpiCard(label: 'RSI (14)', value: rsi.toStringAsFixed(2), color: _getRsiColor(rsi)),
        if (macd != null && macdSignal != null)
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
    final points = widget.points;
    final spots = points.asMap().entries.map((e) {
      return FlSpot(e.key.toDouble(), e.value.close);
    }).toList();

    var minY = points.map((e) => e.close).reduce((a, b) => a < b ? a : b);
    var maxY = points.map((e) => e.close).reduce((a, b) => a > b ? a : b);

    // Adjust min/max for Bollinger
    if (_showBollinger) {
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

    return LineChart(
      LineChartData(
        minY: minY - padding,
        maxY: maxY + padding,
        gridData: const FlGridData(show: true),
        titlesData: FlTitlesData(
            leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 40)),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), // Share x-axis logic
        ),
        borderData: FlBorderData(show: true),
        lineBarsData: [
          // Close Price
          LineChartBarData(
            spots: spots,
            isCurved: false,
            barWidth: 2,
            color: Colors.black,
            dotData: const FlDotData(show: false),
          ),
          // Bollinger Upper
          if (_showBollinger)
             LineChartBarData(
                spots: _toSpots(_bollinger.upper),
                isCurved: true,
                barWidth: 1,
                color: Colors.blue.withOpacity(0.5),
                dotData: const FlDotData(show: false),
             ),
          // Bollinger Middle
          if (_showBollinger)
             LineChartBarData(
                spots: _toSpots(_bollinger.middle),
                isCurved: true,
                barWidth: 1,
                color: Colors.blue.withOpacity(0.3),
                dotData: const FlDotData(show: false),
                dashArray: [5, 5],
             ),
          // Bollinger Lower
          if (_showBollinger)
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
      // MACD uses bar chart for histogram? Or Line? Usually Histogram.
      // FL Chart supports Combo? No. We can use BarChart for Histogram and LineChart for MACD lines.
      // But overlaying is hard in FL Chart without Stack.
      // Let's use LineChart for MACD/Signal and BarChart for Histogram in a Stack?
      // Or just LineChart for all, calculating Histogram as bars...
      // Simplest for now: Use LineCharts for MACD and Signal.
      
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
              gridData: const FlGridData(show: true), // Add horizontal lines at 30/70?
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

List<PricePoint> parsePriceSeries(Map<String, dynamic>? payload) {
  if (payload == null) {
    return [];
  }
  final data = payload['data'];
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
