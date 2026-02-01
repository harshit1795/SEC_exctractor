import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/app_config.dart';
import 'dashboard_providers.dart';

class DashboardPage extends ConsumerStatefulWidget {
  const DashboardPage({super.key});

  @override
  ConsumerState<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends ConsumerState<DashboardPage> {
  late TextEditingController _tickerController;
  late String _period;

  static const _periodOptions = ['1m', '3m', '6m', '1y', '5y'];

  @override
  void initState() {
    super.initState();
    _tickerController = TextEditingController(
      text: ref.read(tickerProvider),
    );
    _period = ref.read(periodProvider);
  }

  @override
  void dispose() {
    _tickerController.dispose();
    super.dispose();
  }

  void _loadData() {
    final ticker = _tickerController.text.trim().toUpperCase();
    if (ticker.isEmpty) {
      return;
    }
    _tickerController.text = ticker;
    ref.read(tickerProvider.notifier).state = ticker;
    ref.read(periodProvider.notifier).state = _period;
  }

  @override
  Widget build(BuildContext context) {
    final healthStatus = ref.watch(healthStatusProvider);
    final tickerData = ref.watch(tickerDataProvider);
    final fundamentals = ref.watch(fundamentalsProvider);

    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'FinQ Dashboard',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Text(
              'API Base URL: ${AppConfig.apiBaseUrl}',
              style: const TextStyle(fontSize: 12, color: Colors.black54),
            ),
            const SizedBox(height: 20),
            healthStatus.when(
              data: (data) => _HealthStatusCard(data: data),
              loading: () => const _LoadingCard(),
              error: (error, _) => _ErrorCard(message: error.toString()),
            ),
            const SizedBox(height: 20),
            _QueryCard(
              tickerController: _tickerController,
              period: _period,
              periods: _periodOptions,
              onPeriodChanged: (value) => setState(() => _period = value),
              onSubmit: _loadData,
            ),
            const SizedBox(height: 16),
            _DataCard(
              title: 'Ticker Data',
              value: tickerData,
            ),
            const SizedBox(height: 16),
            _DataCard(
              title: 'Fundamentals',
              value: fundamentals,
            ),
          ],
        ),
      ),
    );
  }
}

class _QueryCard extends StatelessWidget {
  const _QueryCard({
    required this.tickerController,
    required this.period,
    required this.periods,
    required this.onPeriodChanged,
    required this.onSubmit,
  });

  final TextEditingController tickerController;
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
                Expanded(
                  child: TextField(
                    controller: tickerController,
                    decoration: const InputDecoration(
                      labelText: 'Ticker',
                      hintText: 'AAPL',
                    ),
                  ),
                ),
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

class _HealthStatusCard extends StatelessWidget {
  const _HealthStatusCard({required this.data});

  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final status = data['status']?.toString() ?? 'unknown';
    final service = data['service']?.toString() ?? 'FinQ Backend API';
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Backend Health',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text('Status: $status'),
            Text('Service: $service'),
          ],
        ),
      ),
    );
  }
}

class _LoadingCard extends StatelessWidget {
  const _LoadingCard();

  @override
  Widget build(BuildContext context) {
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            SizedBox(
              width: 18,
              height: 18,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            SizedBox(width: 12),
            Text('Checking backend health...'),
          ],
        ),
      ),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  const _ErrorCard({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Text(
          'Health check failed: $message',
          style: TextStyle(color: Colors.red.shade700),
        ),
      ),
    );
  }
}
