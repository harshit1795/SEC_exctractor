import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:printing/printing.dart';
import 'package:pdf/pdf.dart';
import '../providers/health_providers.dart';

class HealthScoreTab extends ConsumerStatefulWidget {
  const HealthScoreTab({super.key});

  @override
  ConsumerState<HealthScoreTab> createState() => _HealthScoreTabState();
}

class _HealthScoreTabState extends ConsumerState<HealthScoreTab> {
  String _selectedCategory = 'Technology';
  bool _isGeneratingReport = false;
  String? _reportText;
  String? _reportTicker;
  
  final List<String> _categories = [
    'Technology',
    'Manufacturing',
    'Finance',
    'Energy',
    'Healthcare',
    'Consumer Goods',
    'Other'
  ];

  static const _metricExplanations = {
    'Growth': 'Measures year-over-year top-line revenue expansion. A higher growth rate indicates successful market penetration and pricing power, essential for long-term value creation.',
    'Net Margin': 'Represents the percentage of revenue remaining after all operating expenses, taxes, and interest are paid. A robust net margin signals efficient cost management and strong profitability.',
    'FCF Margin': 'Free Cash Flow Margin indicates the proportion of revenue converted into discretionary cash. High FCF margins demonstrate strong earnings quality and the ability to fund dividends or debt reduction.',
    'Debt/Equity': 'Evaluates financial leverage by comparing total liabilities to shareholder equity. A lower ratio (higher percentile rank) indicates a conservative capital structure and lower insolvency risk.',
  };

  @override
  Widget build(BuildContext context) {
    final healthScoresAsync = ref.watch(finqHealthScoreProvider(_selectedCategory));

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header & Info Card
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'FinQ Suggestions',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Health Score Formula: (Growth_score + NetMargin_score + FCFMargin_score + (1 - DebtEquity_score)) / 4',
                    style: TextStyle(
                      fontSize: 14,
                      fontStyle: FontStyle.italic,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 12),
                  ExpansionTile(
                    title: const Text(
                      'How are individual metrics scored?',
                      style: TextStyle(color: Colors.blue),
                    ),
                    tilePadding: EdgeInsets.zero,
                    childrenPadding: const EdgeInsets.only(bottom: 12),
                    children: [
                      Text(
                        'Each metric (Growth, Net Margin, FCF Margin, Debt to Equity) is converted '
                        'into a score between 0 and 1 using percentile ranking. A higher percentile '
                        'rank indicates a better score relative to the market.\n\n'
                        'The final Health Score is the average of these individual metric percentile scores.',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey.shade700,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Select Category',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  SizedBox(
                    width: 300,
                    child: DropdownButtonFormField<String>(
                      value: _selectedCategory,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      ),
                      items: _categories.map((cat) {
                        return DropdownMenuItem(value: cat, child: Text(cat));
                      }).toList(),
                      onChanged: (val) {
                        if (val != null) {
                          setState(() {
                            _selectedCategory = val;
                          });
                        }
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          
          Text(
            'Top Stocks in $_selectedCategory',
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),

          // Data Table Card
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: healthScoresAsync.when(
              data: (scores) {
                if (scores == null || scores.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.all(32),
                    child: Center(child: Text('No top stocks found for this category.')),
                  );
                }

                return SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: DataTable(
                    columnSpacing: 24,
                    horizontalMargin: 24,
                    headingRowHeight: 56,
                    dataRowMaxHeight: 80,
                    dataRowMinHeight: 60,
                    columns: [
                      const DataColumn(label: Text('TICKER', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.grey))),
                      const DataColumn(label: Text('HEALTH\nSCORE', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.grey))),
                      DataColumn(label: _buildTooltipHeader('GROWTH')),
                      DataColumn(label: _buildTooltipHeader('NET\nMARGIN')),
                      DataColumn(label: _buildTooltipHeader('FCF\nMARGIN')),
                      DataColumn(label: _buildTooltipHeader('DEBT/EQUITY')),
                      const DataColumn(label: Text('INSIGHT', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.grey))),
                      const DataColumn(label: Text('REPORT', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.grey))),
                    ],
                    rows: scores.map((score) {
                      final hScore = score.healthScore ?? 0.0;
                      final hScorePct = (hScore * 100).toStringAsFixed(1);
                      final hScoreColor = _getScoreColor(hScore);

                      // Format metrics for display (assuming they are ratios/raw values, we format to %)
                      final growthStr = score.growth != null ? '${(score.growth! * 100).toStringAsFixed(2)}%' : 'N/A';
                      final nmStr = score.netMargin != null ? '${(score.netMargin! * 100).toStringAsFixed(2)}%' : 'N/A';
                      final fcfStr = score.fcfMargin != null ? '${(score.fcfMargin! * 100).toStringAsFixed(2)}%' : 'N/A';
                      final deStr = score.debtEquity != null ? score.debtEquity!.toStringAsFixed(2) : 'N/A';

                      return DataRow(
                        cells: [
                          DataCell(
                            Row(
                              children: [
                                CircleAvatar(
                                  radius: 12,
                                  backgroundColor: Colors.blue.shade100,
                                  child: Text(
                                    score.ticker[0],
                                    style: TextStyle(fontSize: 12, color: Colors.blue.shade900, fontWeight: FontWeight.bold),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(score.ticker, style: const TextStyle(fontWeight: FontWeight.bold)),
                              ],
                            ),
                          ),
                          DataCell(
                            Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  height: 6,
                                  width: 60,
                                  decoration: BoxDecoration(
                                    color: Colors.grey.shade200,
                                    borderRadius: BorderRadius.circular(3),
                                  ),
                                  child: FractionallySizedBox(
                                    alignment: Alignment.centerLeft,
                                    widthFactor: hScore.clamp(0.0, 1.0),
                                    child: Container(
                                      decoration: BoxDecoration(
                                        color: hScoreColor,
                                        borderRadius: BorderRadius.circular(3),
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text('$hScorePct%', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                              ],
                            ),
                          ),
                          DataCell(Text(growthStr, style: const TextStyle(fontSize: 13, color: Colors.grey))),
                          DataCell(Text(nmStr, style: const TextStyle(fontSize: 13, color: Colors.grey))),
                          DataCell(Text(fcfStr, style: const TextStyle(fontSize: 13, color: Colors.grey))),
                          DataCell(Text(deStr, style: const TextStyle(fontSize: 13, color: Colors.grey))),
                          DataCell(
                            SizedBox(
                              width: 300,
                              child: Text(
                                score.insight ?? '-',
                                style: const TextStyle(fontSize: 12, color: Colors.grey),
                                maxLines: 3,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ),
                          DataCell(
                            _isGeneratingReport && _reportTicker == score.ticker
                              ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                              : IconButton(
                                  tooltip: 'Generate Health Report',
                                  icon: const Icon(Icons.description_outlined, size: 20),
                                  color: Colors.blue.shade700,
                                  onPressed: () => _generateReport(score),
                                ),
                          ),
                        ],
                      );
                    }).toList(),
                  ),
                );
              },
              loading: () => const Padding(
                padding: EdgeInsets.all(48),
                child: Center(child: CircularProgressIndicator()),
              ),
              error: (err, st) => Padding(
                padding: const EdgeInsets.all(32),
                child: Center(
                  child: Text('Error: $err', style: const TextStyle(color: Colors.red)),
                ),
              ),
            ),
          ),
          // Report Card
          if (_reportText != null) ...[  
            const SizedBox(height: 16),
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('AI Health Report – $_reportTicker', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              tooltip: 'Download Report',
                              icon: const Icon(Icons.download_outlined),
                              onPressed: () async {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(content: Text('Preparing AI Health Report PDF...')),
                                );
                                try {
                                  await Printing.layoutPdf(
                                    name: '${_reportTicker ?? 'health'}_report.pdf',
                                    onLayout: (PdfPageFormat format) async {
                                      return await Printing.convertHtml(
                                        format: format,
                                        html: _reportText!,
                                      );
                                    },
                                  );
                                } catch (e) {
                                  if (context.mounted) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(content: Text('Error creating PDF: $e'), backgroundColor: Colors.red),
                                    );
                                  }
                                }
                              },
                            ),
                            IconButton(
                              tooltip: 'Copy Report Text',
                              icon: const Icon(Icons.copy_outlined),
                              onPressed: () {
                                Clipboard.setData(ClipboardData(text: _reportText!));
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(content: Text('Report copied to clipboard!')),
                                );
                              },
                            ),
                          ],
                        ),
                      ],
                    ),
                    const Divider(),
                    const SizedBox(height: 8),
                    MarkdownBody(
                      data: _reportText!,
                      styleSheet: MarkdownStyleSheet(
                        h1: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        h2: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        p: const TextStyle(fontSize: 14, height: 1.5),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Future<void> _generateReport(HealthScoreModel score) async {
    setState(() {
      _isGeneratingReport = true;
      _reportText = null;
      _reportTicker = score.ticker;
    });
    try {
      final payload = <String, dynamic>{
        'ticker': score.ticker,
        'healthScore': score.healthScore,
        'growth': score.growth,
        'netMargin': score.netMargin,
        'fcfMargin': score.fcfMargin,
        'debtEquity': score.debtEquity,
        'growthScore': score.growthScore,
        'netMarginScore': score.netMarginScore,
        'fcfMarginScore': score.fcfMarginScore,
        'debtEquityScore': score.debtEquityScore,
        'insight': score.insight,
        'category': _selectedCategory,
      };
      final result = await ref.read(healthReportProvider(payload).future);
      setState(() { _reportText = result; });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      setState(() { _isGeneratingReport = false; });
    }
  }

  Widget _buildTooltipHeader(String title) {
    final key = title.replaceAll('\n', ' ');
    final tooltip = _metricExplanations[key] ?? '';
    
    return Tooltip(
      message: tooltip,
      padding: const EdgeInsets.all(12),
      margin: const EdgeInsets.symmetric(horizontal: 24),
      showDuration: const Duration(seconds: 3),
      textStyle: const TextStyle(color: Colors.white, fontSize: 13),
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontWeight: FontWeight.bold, 
              fontSize: 12, 
              color: Colors.grey,
              decoration: TextDecoration.underline,
              decorationStyle: TextDecorationStyle.dotted,
            ),
          ),
          const SizedBox(width: 4),
          const Icon(Icons.info_outline, size: 12, color: Colors.grey),
        ],
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 0.8) return Colors.green;
    if (score >= 0.6) return Colors.lightGreen;
    if (score >= 0.4) return Colors.orange;
    return Colors.red;
  }
}
