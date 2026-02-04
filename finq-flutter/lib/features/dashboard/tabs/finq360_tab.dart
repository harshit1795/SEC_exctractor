import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../dashboard_providers.dart';

class FinQ360Tab extends ConsumerWidget {
  const FinQ360Tab({
    required this.ticker,
    required this.category,
    super.key,
  });

  final String ticker;
  final String category;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthStatus = ref.watch(healthStatusProvider);
    final tickerData = ref.watch(tickerDataProvider);
    final fundamentals = ref.watch(fundamentalsProvider);

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.auto_awesome, size: 28, color: Colors.purple.shade700),
                      const SizedBox(width: 12),
                      const Text(
                        'FinQ 360',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Comprehensive 360° view of $ticker with multi-metric analysis.',
                    style: TextStyle(
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          // Health Status Section
          _buildHealthSection(healthStatus),
          const SizedBox(height: 16),
          // Ticker Info Section
          _buildTickerSection(tickerData),
          const SizedBox(height: 16),
          // Fundamentals Summary
          _buildFundamentalsSection(fundamentals, category),
        ],
      ),
    );
  }

  Widget _buildHealthSection(AsyncValue<Map<String, dynamic>> healthStatus) {
    return healthStatus.when(
      data: (data) {
        final status = data['status'] ?? 'unknown';
        final color = status == 'healthy'
            ? Colors.green
            : status == 'degraded'
                ? Colors.orange
                : Colors.red;

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.health_and_safety, color: color),
                    const SizedBox(width: 12),
                    const Text(
                      'System Health',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 16,
                  runSpacing: 8,
                  children: [
                    _buildStatChip('Status', status.toUpperCase(), color),
                    if (data['version'] != null)
                      _buildStatChip('Version', data['version'], Colors.blue),
                  ],
                ),
              ],
            ),
          ),
        );
      },
      loading: () => const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(child: CircularProgressIndicator()),
        ),
      ),
      error: (error, _) => const SizedBox.shrink(),
    );
  }

  Widget _buildTickerSection(AsyncValue<Map<String, dynamic>> tickerData) {
    return tickerData.when(
      data: (data) {
        final info = data['info'] as Map<String, dynamic>?;
        final currentPrice = data['current_price'];
        final priceData = data['price_data'] as List?;

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.trending_up, color: Colors.green.shade700),
                    const SizedBox(width: 12),
                    const Text(
                      'Ticker Information',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                if (currentPrice != null)
                  _buildStatItem(
                    'Current Price',
                    '\$${currentPrice.toStringAsFixed(2)}',
                  ),
                if (info != null) ...[
                  const SizedBox(height: 8),
                  if (info['longName'] != null)
                    _buildStatItem('Company', info['longName']),
                  if (info['sector'] != null) ...[
                    const SizedBox(height: 8),
                    _buildStatItem('Sector', info['sector']),
                  ],
                  if (info['industry'] != null) ...[
                    const SizedBox(height: 8),
                    _buildStatItem('Industry', info['industry']),
                  ],
                ],
                if (priceData != null && priceData.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(
                    '${priceData.length} price data points available',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
      loading: () => const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(child: CircularProgressIndicator()),
        ),
      ),
      error: (error, _) => const SizedBox.shrink(),
    );
  }

  Widget _buildFundamentalsSection(
    AsyncValue<Map<String, dynamic>> fundamentals,
    String category,
  ) {
    if (category.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            'Select a category to view fundamentals summary',
            style: TextStyle(color: Colors.grey.shade600),
          ),
        ),
      );
    }

    return fundamentals.when(
      data: (data) {
        final dataArray = data['data'] ?? [];
        if (dataArray is! List || dataArray.isEmpty) {
          return Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'No fundamentals data available',
                style: TextStyle(color: Colors.grey.shade600),
              ),
            ),
          );
        }

        final filtered = dataArray.where((item) {
          if (item is! Map) return false;
          final itemCategory = item['Category'] ?? item['category'] ?? '';
          return itemCategory == category;
        }).toList();

        final metrics = <String>{};
        for (final item in filtered) {
          final metric = item['Metric'] ?? item['metric'];
          if (metric != null) metrics.add(metric);
        }

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.analytics, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    Text(
                      'Fundamentals - $category',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  '${metrics.length} metrics available in $category category',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade700,
                  ),
                ),
                if (metrics.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: metrics.take(5).map((metric) {
                      return Chip(
                        label: Text(
                          metric,
                          style: const TextStyle(fontSize: 12),
                        ),
                        backgroundColor: Colors.blue.shade50,
                      );
                    }).toList(),
                  ),
                  if (metrics.length > 5)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        '...and ${metrics.length - 5} more',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                ],
              ],
            ),
          ),
        );
      },
      loading: () => const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(child: CircularProgressIndicator()),
        ),
      ),
      error: (error, _) => const SizedBox.shrink(),
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          '$label: ',
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey.shade600,
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildStatChip(String label, String value, Color color) {
    return Chip(
      avatar: CircleAvatar(
        backgroundColor: color,
        radius: 8,
      ),
      label: Text('$label: $value'),
      backgroundColor: color.withOpacity(0.1),
    );
  }
}
