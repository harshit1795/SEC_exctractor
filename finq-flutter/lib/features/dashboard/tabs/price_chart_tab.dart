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
    final points = parsePriceSeries(tickerData.valueOrNull);
    return SingleChildScrollView(
      child: Column(
        children: [
          _QueryCard(
            period: period,
            periods: periods,
            onPeriodChanged: onPeriodChanged,
            onSubmit: onSubmit,
          ),
          const SizedBox(height: 12),
          _InfoCard(
            title: 'Price Chart',
            child: PriceChart(points: points),
          ),
          const SizedBox(height: 12),
          _DataCard(title: 'Ticker Data', value: tickerData),
          const SizedBox(height: 12),
          _DataCard(title: 'Fundamentals', value: fundamentals),
        ],
      ),
    );
  }
}

class _QueryCard extends StatelessWidget {
  const _QueryCard({
    required this.period,
    required this.periods,
    required this.onPeriodChanged,
    required this.onSubmit,
  });

  final String period;
  final List<String> periods;
  final ValueChanged<String> onPeriodChanged;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Data Query',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                const Text('Period'),
                const SizedBox(width: 12),
                DropdownButton<String>(
                  value: period,
                  items: periods
                      .map((value) => DropdownMenuItem(
                            value: value,
                            child: Text(value),
                          ))
                      .toList(),
                  onChanged: (value) {
                    if (value != null) {
                      onPeriodChanged(value);
                    }
                  },
                ),
              ],
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: onSubmit,
              child: const Text('Load Data'),
            ),
          ],
        ),
      ),
    );
  }
}

class _DataCard extends StatelessWidget {
  const _DataCard({required this.title, required this.value});

  final String title;
  final AsyncValue<Map<String, dynamic>> value;

  @override
  Widget build(BuildContext context) {
    return value.when(
      loading: () => _InfoCard(
        title: title,
        child: const LinearProgressIndicator(),
      ),
      error: (error, _) => _InfoCard(
        title: title,
        child: Text(
          error.toString(),
          style: TextStyle(color: Colors.red.shade700),
        ),
      ),
      data: (data) {
        final formatted = const JsonEncoder.withIndent('  ').convert(data);
        final preview = formatted.length > 800
            ? '${formatted.substring(0, 800)}\n...'
            : formatted;
        return _InfoCard(
          title: title,
          child: Text(
            preview,
            style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
          ),
        );
      },
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
