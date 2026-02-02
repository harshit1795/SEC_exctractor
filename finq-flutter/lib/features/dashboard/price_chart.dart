import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class PricePoint {
  PricePoint({required this.date, required this.close});

  final DateTime date;
  final double close;
}

class PriceChart extends StatelessWidget {
  const PriceChart({
    super.key,
    required this.points,
  });

  final List<PricePoint> points;

  @override
  Widget build(BuildContext context) {
    if (points.isEmpty) {
      return const SizedBox(
        height: 260,
        child: Center(child: Text('No price data available.')),
      );
    }

    final minY = points.map((e) => e.close).reduce((a, b) => a < b ? a : b);
    final maxY = points.map((e) => e.close).reduce((a, b) => a > b ? a : b);
    final range = (maxY - minY).abs();
    final padding = range == 0 ? maxY * 0.1 : range * 0.1;

    final spots = <FlSpot>[];
    for (var i = 0; i < points.length; i++) {
      spots.add(FlSpot(i.toDouble(), points[i].close));
    }

    return SizedBox(
      height: 260,
      child: LineChart(
        LineChartData(
          minY: minY - padding,
          maxY: maxY + padding,
          gridData: const FlGridData(show: true),
          borderData: FlBorderData(show: false),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 42,
                getTitlesWidget: (value, meta) => Text(
                  value.toStringAsFixed(2),
                  style: const TextStyle(fontSize: 10),
                ),
              ),
            ),
            rightTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            topTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: points.length > 10 ? (points.length / 4).floorToDouble() : 1,
                getTitlesWidget: (value, meta) {
                  final index = value.toInt();
                  if (index < 0 || index >= points.length) {
                    return const SizedBox.shrink();
                  }
                  final date = points[index].date;
                  return Text(
                    '${date.month}/${date.day}',
                    style: const TextStyle(fontSize: 10),
                  );
                },
              ),
            ),
          ),
          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              barWidth: 2,
              dotData: const FlDotData(show: false),
              color: Colors.indigo,
            ),
          ],
        ),
      ),
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
