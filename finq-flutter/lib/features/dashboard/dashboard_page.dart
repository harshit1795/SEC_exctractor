import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/app_config.dart';
import 'dashboard_providers.dart';
import 'price_chart.dart';
import 'company_header.dart';
import 'data_pipeline_banner.dart';
import 'tabs/earnings_tab.dart';
import 'tabs/trend_tab.dart';
import 'tabs/snapshot_tab.dart';
import 'tabs/disclosures_tab.dart';
import 'tabs/macroeconomic_tab.dart';
import 'tabs/finq360_tab.dart';
import 'tabs/finq_chat_tab.dart';

class DashboardPage extends ConsumerStatefulWidget {
  const DashboardPage({super.key});

  @override
  ConsumerState<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends ConsumerState<DashboardPage> {
  late TextEditingController _tickerController;
  late String _period;
  late String _category;

  static const _periodOptions = ['1m', '3m', '6m', '1y', '5y'];
  static const _categories = [
    'IncomeStatement',
    'BalanceSheet',
    'CashFlow',
  ];

  @override
  void initState() {
    super.initState();
    _tickerController = TextEditingController(
      text: ref.read(tickerProvider),
    );
    _period = ref.read(periodProvider);
    _category = ref.read(categoryProvider);
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
    ref.read(categoryProvider.notifier).state = _category;
  }

  @override
  Widget build(BuildContext context) {
    final ticker = ref.watch(tickerProvider);
    final healthStatus = ref.watch(healthStatusProvider);
    final tickerData = ref.watch(tickerDataProvider);
    final fundamentals = ref.watch(fundamentalsProvider);

    return SafeArea(
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth >= 900;
          final filters = _FiltersCard(
            tickerController: _tickerController,
            category: _category,
            categories: _categories,
            onCategoryChanged: (value) => setState(() => _category = value),
            onApply: _loadData,
          );

          final mainContent = _DashboardContent(
            ticker: ticker,
            period: _period,
            periods: _periodOptions,
            onPeriodChanged: (value) => setState(() => _period = value),
            onSubmit: _loadData,
            healthStatus: healthStatus,
            tickerData: tickerData,
            fundamentals: fundamentals,
            category: _category,
          );

          if (isWide) {
            return Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SizedBox(width: 280, child: filters),
                  const SizedBox(width: 24),
                  Expanded(child: mainContent),
                ],
              ),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                filters,
                const SizedBox(height: 20),
                mainContent,
              ],
            ),
          );
        },
      ),
    );
  }
}

class _FiltersCard extends StatelessWidget {
  const _FiltersCard({
    required this.tickerController,
    required this.category,
    required this.categories,
    required this.onCategoryChanged,
    required this.onApply,
  });

  final TextEditingController tickerController;
  final String category;
  final List<String> categories;
  final ValueChanged<String> onCategoryChanged;
  final VoidCallback onApply;

  String _formatCategoryName(String category) {
    switch (category) {
      case 'IncomeStatement':
        return 'Income Statement';
      case 'BalanceSheet':
        return 'Balance Sheet';
      case 'CashFlow':
        return 'Cash Flow Statement';
      default:
        return category;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Filters',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: tickerController,
              decoration: const InputDecoration(
                labelText: 'Ticker',
                hintText: 'AAPL',
              ),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: category,
              decoration: const InputDecoration(labelText: 'Category'),
              items: categories
                  .map(
                    (value) => DropdownMenuItem(
                      value: value,
                      child: Text(_formatCategoryName(value)),
                    ),
                  )
                  .toList(),
              onChanged: (value) {
                if (value != null) {
                  onCategoryChanged(value);
                }
              },
            ),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: onApply,
              child: const Text('Apply'),
            ),
          ],
        ),
      ),
    );
  }
}

class _DashboardContent extends StatelessWidget {
  const _DashboardContent({
    required this.ticker,
    required this.period,
    required this.periods,
    required this.onPeriodChanged,
    required this.onSubmit,
    required this.healthStatus,
    required this.tickerData,
    required this.fundamentals,
    required this.category,
  });

  final String ticker;
  final String period;
  final List<String> periods;
  final ValueChanged<String> onPeriodChanged;
  final VoidCallback onSubmit;
  final AsyncValue<Map<String, dynamic>> healthStatus;
  final AsyncValue<Map<String, dynamic>> tickerData;
  final AsyncValue<Map<String, dynamic>> fundamentals;
  final String category;

  static const _tabs = [
    ('trend', '📈 Metrics Trend Analysis'),
    ('snapshot', '📷 Snapshot & Changes'),
    ('earnings', '💰 Earning Summary'),
    ('price', '📊 Price Chart'),
    ('disclosures', '📄 Disclosures'),
    ('macro', '🌐 Macroeconomic Data'),
    ('finq360', '🔍 FinQ 360'),
    ('bot', '🤖 FinQ Bot'),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Dashboard',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Text(
          'API Base URL: ${AppConfig.apiBaseUrl}',
          style: const TextStyle(fontSize: 12, color: Colors.black54),
        ),
        const SizedBox(height: 12),
        DataPipelineBanner(ticker: ticker),
        CompanyHeader(tickerData: tickerData),
        const SizedBox(height: 12),
        DefaultTabController(
          length: _tabs.length,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              TabBar(
                isScrollable: true,
                labelColor: Colors.green.shade700,
                unselectedLabelColor: Colors.grey.shade600,
                indicatorColor: Colors.green.shade500,
                labelStyle: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
                unselectedLabelStyle: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.normal,
                ),
                tabs: _tabs
                    .map(
                      (tab) => Tab(text: tab.$2),
                    )
                    .toList(),
              ),
              const SizedBox(height: 12),
              SizedBox(
                height: 540,
                child: TabBarView(
                  children: [
                    TrendTab(
                      ticker: ticker,
                      category: category,
                    ),
                    SnapshotTab(
                      ticker: ticker,
                      category: category,
                    ),
                    EarningsTab(ticker: ticker),
                    _PriceTab(
                      period: period,
                      periods: periods,
                      onPeriodChanged: onPeriodChanged,
                      onSubmit: onSubmit,
                      tickerData: tickerData,
                      fundamentals: fundamentals,
                    ),
                    DisclosuresTab(ticker: ticker),
                    const MacroeconomicTab(),
                    FinQ360Tab(
                      ticker: ticker,
                      category: category,
                    ),
                    FinQChatTab(ticker: ticker),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _StatusTab extends StatelessWidget {
  const _StatusTab({required this.healthStatus});

  final AsyncValue<Map<String, dynamic>> healthStatus;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        healthStatus.when(
          data: (data) => _HealthStatusCard(data: data),
          loading: () => const _LoadingCard(),
          error: (error, _) => _ErrorCard(message: error.toString()),
        ),
      ],
    );
  }
}

class _PriceTab extends StatelessWidget {
  const _PriceTab({
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

class _PlaceholderTab extends StatelessWidget {
  const _PlaceholderTab({required this.title, required this.message});

  final String title;
  final String message;

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
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            Text(message),
          ],
        ),
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
