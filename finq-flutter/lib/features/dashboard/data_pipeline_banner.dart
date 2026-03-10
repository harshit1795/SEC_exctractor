import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api/api_client.dart';
import '../../core/di/providers.dart';
import '../../services/report_cache_service.dart';
import '../dashboard_providers.dart';

class DataPipelineBanner extends ConsumerStatefulWidget {
  const DataPipelineBanner({
    super.key,
    required this.ticker,
  });

  final String ticker;

  @override
  ConsumerState<DataPipelineBanner> createState() => _DataPipelineBannerState();
}

class _DataPipelineBannerState extends ConsumerState<DataPipelineBanner> {
  bool _isUpdating = false;

  Future<void> _updateData({bool updateAll = false}) async {
    setState(() => _isUpdating = true);

    try {
      final apiClient = ref.read(apiClientProvider);
      final endpoint = updateAll
          ? '/data-pipeline/update-batch'
          : '/data-pipeline/update/${widget.ticker}';

      await apiClient.post(endpoint);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              updateAll
                  ? 'Data update started for all tickers'
                  : 'Data update started for ${widget.ticker}',
            ),
            backgroundColor: Colors.green,
          ),
        );
        
        // Invalidate providers to force refresh
        ref.invalidate(fundamentalsProvider);
        ref.invalidate(tickerDataProvider);
        ref.invalidate(dataStatusProvider(widget.ticker));

        // Clear health report cache for this ticker
        await ReportCacheService.deleteReport([widget.ticker]);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error updating data: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isUpdating = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final dataStatus = ref.watch(dataStatusProvider(widget.ticker));

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        border: Border.all(color: Colors.blue.shade200),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Text(
                            '📊',
                            style: TextStyle(fontSize: 16),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Data Pipeline Management',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: Colors.blue.shade900,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Update quarterly financial data from Yahoo Finance. Real-time data (prices, FRED, SEC filings) is always current.',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.blue.shade700,
                        ),
                      ),
                      const SizedBox(height: 8),
                      dataStatus.when(
                        data: (status) {
                          final latestPeriod = status['latest_period'] ?? 'N/A';
                          final totalRecords = status['total_records'] ?? 0;
                          
                          return Text(
                            'Current data: $latestPeriod • ${totalRecords.toString().replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]},')} records',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.blue.shade600,
                              fontWeight: FontWeight.w500,
                            ),
                          );
                        },
                        loading: () => Text(
                          'Loading data status...',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.blue.shade600,
                          ),
                        ),
                        error: (_, __) => Text(
                          'Data status unavailable',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.blue.shade600,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                ElevatedButton.icon(
                  onPressed: _isUpdating ? null : () => _updateData(updateAll: false),
                  icon: _isUpdating
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Icon(Icons.refresh, size: 18),
                  label: Text(_isUpdating ? 'Updating...' : 'Update ${widget.ticker}'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  ),
                ),
                const SizedBox(width: 12),
                OutlinedButton.icon(
                  onPressed: _isUpdating ? null : () => _updateData(updateAll: true),
                  icon: const Icon(Icons.update, size: 18),
                  label: const Text('Update All'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.blue.shade700,
                    side: BorderSide(color: Colors.blue.shade300),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
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

// Local provider removed, now uses global dataStatusProvider from dashboard_providers.dart
