import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../services/html_export_service.dart';

import 'dashboard_providers.dart';

class CompanyHeader extends ConsumerWidget {
  const CompanyHeader({
    super.key,
    required this.tickerData,
  });

  final AsyncValue<Map<String, dynamic>> tickerData;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthScoresAsync = ref.watch(dashboardHealthScoresProvider);

    return tickerData.when(
      data: (data) {
        if (data.containsKey('tickers') && data['tickers'] is List) {
           final tickers = (data['tickers'] as List).cast<String>();
           
           final List<dynamic> healthScores = healthScoresAsync.valueOrNull ?? [];
           
           return Container(
              margin: const EdgeInsets.only(bottom: 16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.1),
                    spreadRadius: 1,
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Row(
                children: [
                    Container(
                        width: 60,
                        height: 60,
                        decoration: BoxDecoration(
                            color: Colors.purple.shade50,
                            borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(Icons.compare_arrows, size: 32, color: Colors.purple.shade700),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  const Text(
                                      'Comparison Mode',
                                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                                  ),
                                  if (healthScores.isNotEmpty)
                                    ElevatedButton.icon(
                                      onPressed: () => _downloadReport(context, ref, healthScores),
                                      icon: const Icon(Icons.picture_as_pdf, size: 16),
                                      label: const Text('Comparison Report'),
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: Colors.purple.shade50,
                                        foregroundColor: Colors.purple.shade700,
                                        elevation: 0,
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Wrap(
                                spacing: 12,
                                runSpacing: 8,
                                children: tickers.map((t) {
                                  final tScoreData = healthScores.firstWhere(
                                    (s) => s['ticker'] == t, 
                                    orElse: () => null,
                                  );
                                  return Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Text(
                                          t,
                                          style: TextStyle(fontSize: 16, color: Colors.grey.shade800, fontWeight: FontWeight.bold),
                                      ),
                                      if (tScoreData != null) ...[
                                        const SizedBox(width: 6),
                                        _buildHealthBadge(tScoreData),
                                      ]
                                    ],
                                  );
                                }).toList(),
                              ),
                          ],
                      ),
                    ),
                ],
              ),
           );
        }

        // Single ticker logic
        // The API returns { "ticker": "...", "data": { "info": ... } }
        // We need to drill down into 'data' key if present, or fallback to root if 'info' is there.
        final innerData = (data['data'] as Map<String, dynamic>?) ?? data;
        final info = (innerData['info'] as Map<String, dynamic>?) ?? {};
        
        final ticker = data['ticker'] as String? ?? '';
        final companyName = info['longName'] ?? info['shortName'] ?? ticker;
        final sector = info['sector'] ?? info['Sector'] ?? 'N/A';
        final industry = info['industry'] ?? info['Industry'] ?? 'N/A';
        final logoAsync = ref.watch(logoUrlProvider(ticker));
        
        debugPrint('CompanyHeader build: ticker=$ticker, sector=$sector, industry=$industry, infoKeys=${info.keys.toList()}');

        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                spreadRadius: 1,
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Company Logo
                SizedBox(
                  width: 80,
                  height: 80,
                  child: logoAsync.when(
                    data: (url) {
                      if (url != null) {
                        return ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Image.network(
                            url,
                            fit: BoxFit.contain,
                            loadingBuilder: (context, child, loadingProgress) {
                              if (loadingProgress == null) {
                                return child;
                              }
                              return _buildFallbackLogo(ticker, isLoading: true);
                            },
                            errorBuilder: (context, error, stackTrace) {
                              // SVG failed to load, show fallback
                              return _buildFallbackLogo(ticker);
                            },
                          ),
                        );
                      }
                      return _buildFallbackLogo(ticker);
                    },
                    loading: () => _buildFallbackLogo(ticker, isLoading: true),
                    error: (_, __) => _buildFallbackLogo(ticker),
                  ),
                ),
                const SizedBox(width: 16),
                // Company Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: Text(
                              '$ticker – $companyName',
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: Colors.black87,
                              ),
                            ),
                          ),
                          if (healthScoresAsync.valueOrNull != null && healthScoresAsync.valueOrNull!.isNotEmpty)
                            Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                _buildHealthBadge(healthScoresAsync.valueOrNull!.first),
                                const SizedBox(width: 12),
                                ElevatedButton.icon(
                                  onPressed: () => _downloadReport(context, ref, healthScoresAsync.valueOrNull!),
                                  icon: const Icon(Icons.picture_as_pdf, size: 16),
                                  label: const Text('Export Report'),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.green.shade50,
                                    foregroundColor: Colors.green.shade700,
                                    elevation: 0,
                                  ),
                                ),
                              ],
                            ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 4,
                        children: [
                          if (sector != 'N/A')
                            _buildChip(sector, Colors.blue.shade50, Colors.blue.shade700),
                          if (industry != 'N/A')
                            _buildChip(industry, Colors.green.shade50, Colors.green.shade700),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
      loading: () => _buildLoadingCard(),
      error: (error, _) => _buildErrorCard(error.toString()),
    );
  }

  Widget _buildFallbackLogo(String ticker, {bool isLoading = false}) {
    return Container(
      width: 80,
      height: 80,
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Center(
        child: isLoading
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : Text(
                ticker.isNotEmpty ? ticker[0].toUpperCase() : '?',
                style: TextStyle(
                  fontSize: 36,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue.shade700,
                ),
              ),
      ),
    );
  }

  Widget _buildChip(String label, Color bg, Color text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: text,
        ),
      ),
    );
  }

  Widget _buildLoadingCard() {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: const Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            SizedBox(width: 12),
            Text(
              'Loading company info...',
              style: TextStyle(fontSize: 14, color: Colors.black54),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorCard(String message) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.error_outline, color: Colors.red.shade700),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'Failed to load company information',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.red.shade700,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthBadge(Map<dynamic, dynamic> scoreData) {
    final score = scoreData['healthScore'] as double?;
    if (score == null) return const SizedBox.shrink();
    final pct = (score * 100).toStringAsFixed(1) + '%';
    Color color = Colors.green.shade700;
    Color bg = Colors.green.shade50;
    if (score < 0.4) {
      color = Colors.red.shade700;
      bg = Colors.red.shade50;
    } else if (score < 0.7) {
      color = Colors.orange.shade800;
      bg = Colors.orange.shade50;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        'FinQ Health: $pct',
        style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 12),
      ),
    );
  }

  Future<void> _downloadReport(BuildContext context, WidgetRef ref, List<dynamic> tickersData) async {
    try {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Generating AI Health Report...')),
      );
      final repo = ref.read(dashboardRepositoryProvider);
      final payload = tickersData.map((e) => Map<String, dynamic>.from(e as Map)).toList();
      final html = await repo.generateHealthReportHtml(payload);
      
      await HtmlExportService.downloadHtmlReport(
        htmlString: html,
        filenamePrefix: tickersData.length > 1 ? 'comparison' : tickersData[0]['ticker'] as String,
      );
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error generating report: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }
}
