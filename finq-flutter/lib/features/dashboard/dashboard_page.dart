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
import 'tabs/price_chart_tab.dart';

import 'widgets/dashboard_filters.dart';

class DashboardPage extends ConsumerStatefulWidget {
  const DashboardPage({super.key});

  @override
  ConsumerState<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends ConsumerState<DashboardPage> {
  late String _period;

  static const _periodOptions = ['1m', '3m', '6m', '1y', '5y'];

  @override
  void initState() {
    super.initState();
    _period = ref.read(periodProvider);
  }

  void _loadData() {
    // Just refresh the providers by setting state, triggering watchers. 
    // Persisted state is already updated if changed via UI.
    // For period passed to PriceChart, we update the global provider to persist it.
    if (ref.read(periodProvider) != _period) {
        ref.read(periodProvider.notifier).setPeriod(_period);
    }
  }

  @override
  Widget build(BuildContext context) {

    // Watch global providers
    final selectedTickers = ref.watch(selectedTickersProvider);
    // Backward compatibility for single ticker components
    final primaryTicker = selectedTickers.isNotEmpty ? selectedTickers.first : '';
    
    final category = ref.watch(categoryProvider);
    
    // Watch data providers (which depend on ticker/period)
    final healthStatus = ref.watch(healthStatusProvider);
    final tickerData = ref.watch(tickerDataProvider);
    final fundamentals = ref.watch(fundamentalsProvider);

    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Filter Widget at the top
            const DashboardFilters(),
            const SizedBox(height: 20),
            
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
            DataPipelineBanner(ticker: primaryTicker),
            CompanyHeader(tickerData: tickerData),
            const SizedBox(height: 12),
            _DashboardContent(
              tickers: selectedTickers,
              period: _period,
              periods: _periodOptions,
              category: category,
              onPeriodChanged: (value) {
                setState(() => _period = value);
                _loadData();
              },
              onSubmit: _loadData,
              healthStatus: healthStatus,
              tickerData: tickerData,
              fundamentals: fundamentals,
            ),
          ],
        ),
      ),
    );
  }
}

class _DashboardContent extends StatelessWidget {
  const _DashboardContent({
    required this.tickers,
    required this.period,
    required this.periods,
    required this.category,
    required this.onPeriodChanged,
    required this.onSubmit,
    required this.healthStatus,
    required this.tickerData,
    required this.fundamentals,
  });

  final List<String> tickers;
  final String period;
  final List<String> periods;
  final String category;
  final ValueChanged<String> onPeriodChanged;
  final VoidCallback onSubmit;
  final AsyncValue<Map<String, dynamic>> healthStatus;
  final AsyncValue<Map<String, dynamic>> tickerData;
  final AsyncValue<Map<String, dynamic>> fundamentals;

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
    final primaryTicker = tickers.isNotEmpty ? tickers.first : '';
    final isMulti = tickers.length > 1;

    return DefaultTabController(
      length: _tabs.length,
      initialIndex: 3, // Default to Price Chart
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
            tabs: _tabs.map((tab) => Tab(text: tab.$2)).toList(),
          ),
          const SizedBox(height: 12),
          // Show warning for single-ticker only tabs
          if (isMulti)
             Container(
                 width: double.infinity,
                 padding: const EdgeInsets.all(8),
                 margin: const EdgeInsets.only(bottom: 8),
                 color: Colors.orange.shade50,
                 child: Row(
                     children: [
                         Icon(Icons.info_outline, size: 16, color: Colors.orange.shade800),
                         const SizedBox(width: 8),
                         Expanded(
                             child: Text(
                                 'Comparison mode active. Some tabs only show data for $primaryTicker.',
                                 style: TextStyle(fontSize: 12, color: Colors.orange.shade900),
                             ),
                         ),
                     ],
                 ),
             ),
          LayoutBuilder(
            builder: (context, constraints) {
              final availableHeight = MediaQuery.of(context).size.height - 300;
              final tabHeight = availableHeight.clamp(400.0, 1200.0); // Increased max height
              
              return SizedBox(
                height: tabHeight,
                child: TabBarView(
                  children: [
                    TrendTab(
                      ticker: primaryTicker,
                      category: category,
                    ),
                    SnapshotTab(
                      ticker: primaryTicker,
                      category: category,
                    ),
                    EarningsTab(ticker: primaryTicker),
                    PriceChartTab(
                      period: period,
                      periods: periods,
                      onPeriodChanged: onPeriodChanged,
                      onSubmit: onSubmit,
                      tickerData: tickerData,
                      fundamentals: fundamentals,
                    ),
                    DisclosuresTab(ticker: primaryTicker),
                    const MacroeconomicTab(),
                    FinQ360Tab(
                      ticker: primaryTicker,
                      category: category,
                    ),
                    FinQChatTab(ticker: primaryTicker),
                  ],
                ),
              );
            },
          ),
        ],
      ),
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
