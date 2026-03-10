import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

import '../providers/health_providers.dart';
import '../widgets/single_ticker_search_autocomplete.dart';
import '../../../services/report_cache_service.dart';

class CustomMetricsTab extends ConsumerStatefulWidget {
  const CustomMetricsTab({super.key});

  @override
  ConsumerState<CustomMetricsTab> createState() => _CustomMetricsTabState();
}

class _CustomMetricsTabState extends ConsumerState<CustomMetricsTab> {
  final _availableMetrics = [
    'Revenue Growth',
    'Net Margin',
    'FCF Margin',
    'Debt to Equity',
    'P/E Ratio',
    'ROE',
    'ROA',
    'Current Ratio',
    'Quick Ratio',
  ];

  static const _metricExplanations = {
    'Revenue Growth': 'Measures year-over-year top-line revenue expansion.',
    'Net Margin': 'Represents the percentage of revenue remaining after all operating expenses.',
    'FCF Margin': 'Free Cash Flow Margin indicates the proportion of revenue converted into discretionary cash.',
    'Debt to Equity': 'Evaluates financial leverage by comparing total liabilities to shareholder equity.',
    'P/E Ratio': 'Price-to-Earnings ratio, a measure of company valuation.',
    'ROE': "Return on Equity shows how effectively management uses equity to grow the business.",
    'ROA': "Return on Assets indicates how profitable a company is relative to its total assets.",
    'Current Ratio': "Measures a company's ability to pay short-term obligations.",
    'Quick Ratio': "An indicator of a company's short-term liquidity position.",
  };

  final _selectedMetrics = <String, double>{
    'Revenue Growth': 0.25,
    'Net Margin': 0.25,
    'FCF Margin': 0.25,
    'Debt to Equity': 0.25,
  };

  String _selectedTicker = '';
  bool _shouldCalculate = false;
  bool _isGeneratingReport = false;
  String? _reportText;
  Key _dropdownKey = UniqueKey();

  @override
  Widget build(BuildContext context) {
    final totalWeight = _selectedMetrics.values.fold(0.0, (sum, val) => sum + val);
    final isValidWeights = (totalWeight - 1.0).abs() < 0.01;

    final queryParams = CustomHealthScoreParams(
      ticker: _selectedTicker.isNotEmpty ? _selectedTicker : null,
      metrics: _selectedMetrics.keys.toList(),
      weights: _selectedMetrics.values.toList(),
    );

    final healthScoreAsync = _shouldCalculate && _selectedTicker.isNotEmpty
        ? ref.watch(customHealthScoreProvider(queryParams))
        : null;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Card
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(Icons.tune, size: 24, color: Colors.blue.shade700),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Custom Health Score',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Select a ticker, choose metrics, assign weights and calculate a custom score.',
                          style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Ticker + Weights Config Card
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Ticker Search
                  const Text('Select Ticker', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 8),
                  SingleTickerSearchAutocomplete(
                    initialValue: _selectedTicker,
                    onSelected: (val) {
                      setState(() {
                        _selectedTicker = val;
                        _shouldCalculate = false;
                        _reportText = null;
                      });
                    },
                  ),
                  const SizedBox(height: 24),

                  // Weights Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Metric Weights', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: isValidWeights ? Colors.green.shade50 : Colors.red.shade50,
                          border: Border.all(color: isValidWeights ? Colors.green : Colors.red),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Text(
                          'Total: ${(totalWeight * 100).toStringAsFixed(0)}%',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: isValidWeights ? Colors.green.shade700 : Colors.red.shade700,
                          ),
                        ),
                      ),
                    ],
                  ),
                  if (!isValidWeights) ...[
                    const SizedBox(height: 8),
                    Text('Weights must add up to 100%', style: TextStyle(fontSize: 12, color: Colors.red.shade700)),
                  ],
                  const SizedBox(height: 16),

                  // Sliders
                  ..._selectedMetrics.entries.map((entry) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Tooltip(
                                message: _metricExplanations[entry.key] ?? '',
                                padding: const EdgeInsets.all(12),
                                margin: const EdgeInsets.symmetric(horizontal: 24),
                                showDuration: const Duration(seconds: 3),
                                textStyle: const TextStyle(color: Colors.white, fontSize: 13),
                                decoration: BoxDecoration(color: Colors.black87, borderRadius: BorderRadius.circular(8)),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.center,
                                  children: [
                                    Text(
                                      entry.key,
                                      style: const TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w500,
                                        decoration: TextDecoration.underline,
                                        decorationStyle: TextDecorationStyle.dotted,
                                      ),
                                    ),
                                    const SizedBox(width: 4),
                                    Icon(Icons.info_outline, size: 14, color: Colors.grey.shade600),
                                  ],
                                ),
                              ),
                              Row(children: [
                                Text('${(entry.value * 100).toStringAsFixed(0)}%',
                                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
                                IconButton(
                                  icon: const Icon(Icons.close, size: 20),
                                  onPressed: () {
                                    setState(() {
                                      _selectedMetrics.remove(entry.key);
                                      _shouldCalculate = false;
                                      _reportText = null;
                                    });
                                  },
                                ),
                              ]),
                            ],
                          ),
                          Slider(
                            value: entry.value,
                            min: 0,
                            max: 1,
                            divisions: 20,
                            label: '${(entry.value * 100).toStringAsFixed(0)}%',
                            onChanged: (value) {
                              setState(() {
                                _selectedMetrics[entry.key] = value;
                              });
                            },
                            onChangeEnd: (value) {
                              final totalW = _selectedMetrics.values.fold(0.0, (s, v) => s + v);
                              final isValid = (totalW - 1.0).abs() < 0.01;
                              if (isValid && _selectedTicker.isNotEmpty) {
                                setState(() {
                                  ref.invalidate(customHealthScoreProvider(queryParams));
                                  _shouldCalculate = true;
                                  _reportText = null;
                                });
                              } else {
                                setState(() {
                                  _shouldCalculate = false;
                                  _reportText = null;
                                });
                              }
                            },
                          ),
                        ],
                      ),
                    );
                  }),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    key: _dropdownKey,
                    decoration: const InputDecoration(
                      labelText: 'Add Metric',
                      border: OutlineInputBorder(),
                    ),
                    items: _availableMetrics
                        .where((m) => !_selectedMetrics.containsKey(m))
                        .map((metric) => DropdownMenuItem(value: metric, child: Text(metric)))
                        .toList(),
                    onChanged: (value) {
                      if (value != null) {
                        setState(() {
                          _dropdownKey = UniqueKey();
                          _selectedMetrics[value] = 0.1;
                          _shouldCalculate = false;
                          _reportText = null;
                        });
                      }
                    },
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue.shade700,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      onPressed: () {
                        if (_selectedTicker.isEmpty) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Please select a ticker first')),
                          );
                          return;
                        }
                        if (!isValidWeights) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Metric weights must add up to exactly 100%')),
                          );
                          return;
                        }
                        setState(() {
                          ref.invalidate(customHealthScoreProvider(queryParams));
                          _shouldCalculate = true;
                          _reportText = null;
                        });
                      },
                      child: const Text('Calculate Custom Score', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Results
          if (_shouldCalculate && _selectedTicker.isNotEmpty && healthScoreAsync != null)
            healthScoreAsync.when(
              data: (scores) {
                if (scores == null || scores.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.all(32),
                    child: Center(child: Text('No data available for this ticker / metric combination.')),
                  );
                }
                final score = scores.first;
                final hScore = score.healthScore ?? 0.0;
                final hScorePct = (hScore * 100).toStringAsFixed(1);
                final hColor = _getScoreColor(hScore);
                final hLabel = _getScoreLabel(hScore);

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Score Card
                    Card(
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Padding(
                        padding: const EdgeInsets.all(24),
                        child: Column(
                          children: [
                            Text(
                              'Custom Health Score – ${score.ticker}',
                              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 16),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Container(
                                  width: 80,
                                  height: 80,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    border: Border.all(color: hColor, width: 5),
                                  ),
                                  child: Center(
                                    child: Text(
                                      '$hScorePct%',
                                      style: TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                        color: hColor,
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(hLabel, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: hColor)),
                                    if (score.insight != null && score.insight!.isNotEmpty)
                                      SizedBox(
                                        width: 300,
                                        child: Text(
                                          score.insight!,
                                          style: TextStyle(fontSize: 12, color: Colors.grey.shade600, fontStyle: FontStyle.italic),
                                          maxLines: 3,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                  ],
                                ),
                              ],
                            ),
                            const SizedBox(height: 20),
                            // Metric Bars
                            ..._selectedMetrics.keys.map((metric) {
                              final metricScore = score.metricScores[metric] ?? 0.0;
                              return Padding(
                                padding: const EdgeInsets.only(bottom: 12),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(metric, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
                                        Row(
                                          children: [
                                            if (score.rawMetrics.containsKey(metric) && score.rawMetrics[metric] != null)
                                              Text(
                                                _formatRawMetric(metric, score.rawMetrics[metric]!),
                                                style: TextStyle(fontSize: 13, color: Theme.of(context).colorScheme.onSurfaceVariant),
                                              ),
                                            const SizedBox(width: 8),
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                              decoration: BoxDecoration(
                                                color: _getScoreColor(metricScore).withOpacity(0.1),
                                                borderRadius: BorderRadius.circular(4),
                                              ),
                                              child: Text('Rank: ${(metricScore * 100).toStringAsFixed(0)}%',
                                                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: _getScoreColor(metricScore))),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 6),
                                    LinearProgressIndicator(
                                      value: metricScore.clamp(0.0, 1.0),
                                      backgroundColor: Colors.grey.shade200,
                                      valueColor: AlwaysStoppedAnimation<Color>(_getScoreColor(metricScore)),
                                      minHeight: 8,
                                    ),
                                  ],
                                ),
                              );
                            }),
                            const SizedBox(height: 20),
                            // Generate Report Button
                            Row(
                              children: [
                                Expanded(
                                  child: OutlinedButton.icon(
                                    onPressed: _isGeneratingReport ? null : () => _generateReport(score),
                                    icon: _isGeneratingReport
                                        ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                                        : const Icon(Icons.description_outlined),
                                    label: Text(_isGeneratingReport ? 'Generating...' : 'Generate Health Report'),
                                    style: OutlinedButton.styleFrom(
                                      foregroundColor: Colors.blue.shade700,
                                      side: BorderSide(color: Colors.blue.shade700),
                                      padding: const EdgeInsets.symmetric(vertical: 14),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                IconButton(
                                  icon: const Icon(Icons.refresh, color: Colors.amber),
                                  tooltip: 'Refresh & Regen',
                                  onPressed: _isGeneratingReport ? null : () => _refreshAndGenerateReport(score),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                    // Report display
                    if (_reportText != null) ...[
                      const SizedBox(height: 16),
                      _buildReportCard(_reportText!),
                    ],
                  ],
                );
              },
              loading: () => const Padding(
                padding: EdgeInsets.all(48),
                child: Center(child: CircularProgressIndicator()),
              ),
              error: (err, st) => Padding(
                padding: const EdgeInsets.all(32),
                child: Center(child: Text('Error: $err', style: const TextStyle(color: Colors.red))),
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _generateReport(dynamic score) async {
    setState(() {
      _isGeneratingReport = true;
      _reportText = null;
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
        'customWeights': Map<String, double>.from(
          Map.fromIterables(
            _selectedMetrics.keys,
            _selectedMetrics.values,
          ),
        ),
      };
      final result = await ref.read(healthReportProvider(payload).future);
      setState(() {
        _reportText = result;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error generating report: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      setState(() {
        _isGeneratingReport = false;
      });
    }
  }

  Future<void> _refreshAndGenerateReport(dynamic score) async {
    await ReportCacheService.deleteReport([score.ticker]);
    return _generateReport(score);
  }

  Widget _buildReportCard(String reportText) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'AI Health Report',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Row(children: [
                  IconButton(
                    tooltip: 'Copy Report',
                    icon: const Icon(Icons.copy_outlined),
                    onPressed: () {
                      Clipboard.setData(ClipboardData(text: reportText));
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Report copied to clipboard!')),
                      );
                    },
                  ),
                ]),
              ],
            ),
            const Divider(),
            const SizedBox(height: 8),
            MarkdownBody(
              data: reportText,
              styleSheet: MarkdownStyleSheet(
                h1: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                h2: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                p: const TextStyle(fontSize: 14, height: 1.5),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 0.7) return Colors.green;
    if (score >= 0.4) return Colors.amber.shade600;
    return Colors.red;
  }

  String _getScoreLabel(double score) {
    if (score >= 0.7) return 'Strong';
    if (score >= 0.4) return 'Moderate';
    return 'Weak';
  }

  String _formatRawMetric(String metricName, double value) {
    // Determine if the metric is naturally a percentage or a raw ratio based on its name.
    final lowerName = metricName.toLowerCase();
    if (lowerName.contains('margin') ||
        lowerName.contains('growth') ||
        lowerName.contains('roe') ||
        lowerName.contains('roa')) {
      return '${(value * 100).toStringAsFixed(2)}%';
    }
    // E.g., Debt/Equity, Current Ratio
    return value.toStringAsFixed(2);
  }
}
