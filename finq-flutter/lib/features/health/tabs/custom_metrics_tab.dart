import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/health_providers.dart';
import '../widgets/single_ticker_search_autocomplete.dart';
import '../../../services/html_export_service.dart';
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
    'Revenue Growth': 'Calculation: (Current Revenue - Prev Revenue) / Prev Revenue.\nInterpretation: Ranked against universe. A score > 0.7 makes it a Leader indicating strong top-line momentum.',
    'Net Margin': 'Calculation: Net Income / Total Revenue.\nInterpretation: Ranked against universe. A score > 0.7 makes it a Leader, showing excellent profitability.',
    'FCF Margin': 'Calculation: Free Cash Flow / Total Revenue.\nInterpretation: Assesses discretionary cash generation. A score > 0.7 makes it a Leader.',
    'Debt to Equity': 'Calculation: Total Debt / Shareholder Equity.\nInterpretation: Assesses financial leverage. Ranked inversely. A score > 0.7 means conservative leverage (Leader).',
    'P/E Ratio': 'Calculation: Price / Earnings.\nInterpretation: Measures valuation. Ranked inversely. A score > 0.7 means attractive valuation (Leader).',
    'ROE': "Calculation: Net Income / Shareholder Equity.\nInterpretation: Effectiveness of equity use. A score > 0.7 is a Leader.",
    'ROA': "Calculation: Net Income / Total Assets.\nInterpretation: Return on assets. A score > 0.7 is a Leader.",
    'Current Ratio': "Calculation: Current Assets / Current Liabilities.\nInterpretation: Short-term liquidity. A score > 0.7 is a Leader.",
    'Quick Ratio': "Calculation: (Current Assets - Inventory) / Current Liabilities.\nInterpretation: Immediate liquidity. A score > 0.7 is a Leader.",
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
  bool _isGeneratingCustomReport = false;
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

    final defaultScoreAsync = _selectedTicker.isNotEmpty
        ? ref.watch(singleFinqHealthScoreProvider(_selectedTicker))
        : null;

    final customScoreAsync = _shouldCalculate && _selectedTicker.isNotEmpty
        ? ref.watch(customHealthScoreProvider(queryParams))
        : null;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Header Card
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
                          'Select a ticker, review its default health, assign custom metric weights, and calculate a tailored score.',
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

          // 2. Ticker Search Card
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Select Ticker', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 8),
                  SingleTickerSearchAutocomplete(
                    initialValue: _selectedTicker,
                    onSelected: (val) {
                      setState(() {
                        _selectedTicker = val;
                        _shouldCalculate = false;
                      });
                    },
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // 3. Default Score (Shown immediately on ticker selection)
          if (defaultScoreAsync != null) ...[
            defaultScoreAsync.when(
              data: (score) {
                if (score == null) return const SizedBox.shrink();
                return _buildScoreCard(score, isCustom: false);
              },
              loading: () => const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator())),
              error: (err, st) => Text('Error loading dashboard score: $err'),
            ),
            const SizedBox(height: 24),
          ],

          // 4. Weights Config Card
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Theme(
                    data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                    child: ExpansionTile(
                      initiallyExpanded: true,
                      tilePadding: EdgeInsets.zero,
                      title: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Adjust Metric Weights', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
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
                      children: [
                        if (!isValidWeights) ...[
                          const SizedBox(height: 8),
                          Align(
                            alignment: Alignment.centerLeft,
                            child: Text('Weights must add up to 100%', style: TextStyle(fontSize: 12, color: Colors.red.shade700))
                          ),
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
                                      });
                                    } else {
                                      setState(() {
                                        _shouldCalculate = false;
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
                              });
                            }
                          },
                        ),
                        const SizedBox(height: 16),
                      ],
                    ),
                  ),

                  // Calculate Button
                  const SizedBox(height: 8),
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
                        });
                      },
                      child: const Text('Calculate Custom Score', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // 5. Custom Score (if computed)
          if (customScoreAsync != null && _shouldCalculate) ...[
            customScoreAsync.when(
              data: (scores) {
                if (scores == null || scores.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.all(32),
                    child: Center(child: Text('No custom data available for this ticker/metrics.')),
                  );
                }
                return _buildScoreCard(scores.first, isCustom: true);
              },
              loading: () => const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator())),
              error: (err, st) => Padding(
                padding: const EdgeInsets.all(32),
                child: Center(child: Text('Error: $err', style: const TextStyle(color: Colors.red))),
              ),
            ),
          ],
          
          if (_selectedTicker.isNotEmpty) const SizedBox(height: 60),
        ],
      ),
    );
  }

  Widget _buildScoreCard(HealthScoreModel score, {required bool isCustom}) {
    final hScore = score.healthScore ?? 0.0;
    final hScorePct = (hScore * 100).toStringAsFixed(1);
    final hColor = _getScoreColor(hScore, isInverse: false);
    final hLabel = _getScoreLabel(hScore);

    final title = isCustom ? 'Custom Health Score – ${score.ticker}' : 'Default FinQ Health Score – ${score.ticker}';
    final cardColor = isCustom ? Theme.of(context).colorScheme.surface : Theme.of(context).colorScheme.surfaceContainerLow;

    final metricsToShow = isCustom
        ? _selectedMetrics.keys.toList()
        : ['Revenue Growth', 'Net Margin', 'FCF Margin', 'Debt to Equity', 'P/E Ratio'];

    final isGenerating = _isGeneratingReport && _isGeneratingCustomReport == isCustom;
    
    // Responsive grid counting
    final screenWidth = MediaQuery.of(context).size.width;
    int crossAxisCount = 2; // Mobile
    if (screenWidth > 1200) {
      crossAxisCount = 5; // Large Desktop
    } else if (screenWidth > 900) {
      crossAxisCount = 4; // Desktop
    } else if (screenWidth > 600) {
      crossAxisCount = 3; // Tablet
    }

    return Card(
      color: cardColor,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: isCustom ? BorderSide(color: Colors.blue.shade200, width: 2) : BorderSide.none,
      ),
      elevation: isCustom ? 4 : 1,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Text(
              title,
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
                    color: Theme.of(context).colorScheme.surface,
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
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(hLabel, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: hColor)),
                      if (score.insight != null && score.insight!.isNotEmpty)
                        Text(
                          score.insight!,
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade600, fontStyle: FontStyle.italic),
                          maxLines: 4,
                          overflow: TextOverflow.ellipsis,
                        ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            // Metric Highlights Grid (KPI Cards with Gauges)
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: crossAxisCount,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 2.8, // Ultra-wide to match reference image
              ),
              itemCount: metricsToShow.length,
              itemBuilder: (context, index) {
                final metric = metricsToShow[index];
                final val = _getRawMetricValue(score, metric);
                final metricScore = _getMetricRankValue(score, metric) ?? 0.0;
                
                final isInverse = metric == 'Debt to Equity' || metric == 'P/E Ratio';
                final interp = _getInterpretation(metricScore, isInverse: isInverse);
                final interpColor = _getScoreColor(metricScore, isInverse: false); // Percentile is ALREADY inverted in backend

                return Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceVariant.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Theme.of(context).colorScheme.outlineVariant.withOpacity(0.5)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      // Header Row
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Flexible(
                            child: FittedBox(
                              fit: BoxFit.scaleDown,
                              child: Text(
                                metric,
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                                  fontWeight: FontWeight.bold,
                                ),
                                maxLines: 1,
                              ),
                            ),
                          ),
                          Tooltip(
                            message: _metricExplanations[metric] ?? '',
                            padding: const EdgeInsets.all(12),
                            margin: const EdgeInsets.symmetric(horizontal: 24),
                            showDuration: const Duration(seconds: 4),
                            textStyle: const TextStyle(color: Colors.white, fontSize: 13),
                            decoration: BoxDecoration(color: Colors.black87, borderRadius: BorderRadius.circular(8)),
                            child: Icon(Icons.info_outline, size: 14, color: Theme.of(context).colorScheme.onSurfaceVariant),
                          ),
                        ],
                      ),
                      
                      // Progress Bar + Value + Interpretation Row
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                flex: 2,
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(4),
                                  child: LinearProgressIndicator(
                                    value: metricScore.clamp(0.0, 1.0),
                                    backgroundColor: Colors.grey.withOpacity(0.2),
                                    valueColor: AlwaysStoppedAnimation<Color>(interpColor),
                                    minHeight: 6,
                                  ),
                                ),
                              ),
                              const Spacer(flex: 1), // Only take up partial width for the bar
                            ],
                          ),
                          const SizedBox(height: 6),
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              Text(
                                val != null ? _formatRawMetric(metric, val) : 'N/A',
                                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, height: 1.0),
                              ),
                              const Spacer(),
                              Text(
                                interp,
                                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: interpColor, height: 1.0),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
            const SizedBox(height: 24),

            // Generate Report Button
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _isGeneratingReport ? null : () => _generateReport(score, isCustom: isCustom),
                    icon: isGenerating
                        ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                        : const Icon(Icons.description_outlined),
                    label: Text(isGenerating ? 'Generating...' : 'Generate ${isCustom ? "Custom " : "Default "}Report'),
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
                  onPressed: _isGeneratingReport ? null : () => _refreshAndGenerateReport(score, isCustom: isCustom),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  double? _getRawMetricValue(HealthScoreModel score, String metric) {
    if (score.rawMetrics.containsKey(metric)) return score.rawMetrics[metric];
    switch (metric) {
      case 'Revenue Growth': return score.rawMetrics['Growth'];
      case 'Net Margin': return score.rawMetrics['NetMargin'];
      case 'FCF Margin': return score.rawMetrics['FCFMargin'];
      case 'Debt to Equity': return score.rawMetrics['DebtEquity'];
      case 'P/E Ratio': return score.rawMetrics['PE'];
    }
    return null;
  }

  double? _getMetricRankValue(HealthScoreModel score, String metric) {
    if (score.metricScores.containsKey(metric)) return score.metricScores[metric];
    switch (metric) {
      case 'Revenue Growth': return score.metricScores['Growth'];
      case 'Net Margin': return score.metricScores['NetMargin'];
      case 'FCF Margin': return score.metricScores['FCFMargin'];
      case 'Debt to Equity': return score.metricScores['DebtEquity'];
      case 'P/E Ratio': return score.metricScores['PE'];
    }
    return null;
  }

  Future<void> _generateReport(HealthScoreModel score, {required bool isCustom}) async {
    setState(() {
      _isGeneratingReport = true;
      _isGeneratingCustomReport = isCustom;
    });

    try {
      final payload = <String, dynamic>{
        'ticker': score.ticker,
        'healthScore': score.healthScore,
        'growth': score.growth ?? _getRawMetricValue(score, 'Revenue Growth'),
        'netMargin': score.netMargin ?? _getRawMetricValue(score, 'Net Margin'),
        'fcfMargin': score.fcfMargin ?? _getRawMetricValue(score, 'FCF Margin'),
        'debtEquity': score.debtEquity ?? _getRawMetricValue(score, 'Debt to Equity'),
        'peRatio': score.peRatio ?? _getRawMetricValue(score, 'P/E Ratio'),
        'insight': score.insight,
        ...score.rawMetrics,
        'customWeights': isCustom 
           ? Map<String, double>.from(Map.fromIterables(_selectedMetrics.keys, _selectedMetrics.values)) 
           : null,
      };
      await HtmlExportService.generateAndOpenReport(
        htmlGenerator: () async {
          final result = await ref.read(healthReportProvider(payload).future);
          if (result == null) throw Exception('Failed to generate report');
          return result;
        },
        filenamePrefix: '${score.ticker}_${isCustom ? "custom_" : ""}health_report',
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error generating report: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() {
         _isGeneratingReport = false;
      });
    }
  }

  Future<void> _refreshAndGenerateReport(HealthScoreModel score, {required bool isCustom}) async {
    await ReportCacheService.deleteReport([score.ticker]);
    return _generateReport(score, isCustom: isCustom);
  }

  Color _getScoreColor(double score, {bool isInverse = false}) {
    // Note: The backend already inverts the percentile rank for DebtEquity and PE. 
    // So a higher `score` (percentile rank) is ALWAYS better, even for inverted metrics.
    // E.g., a low Debt/Equity becomes a 0.9 rank (Green). 
    // We do not need to flip colors.
    if (score >= 0.7) return Colors.green;
    if (score >= 0.4) return Colors.amber.shade600;
    return Colors.red;
  }

  String _getScoreLabel(double score) {
    if (score >= 0.7) return 'Strong';
    if (score >= 0.4) return 'Moderate';
    return 'Weak';
  }

  String _getInterpretation(double score, {bool isInverse = false}) {
    // The backend already converted low Debt/Equity into a HIGH percentile score (0.9 rank).
    // Therefore, a score >= 0.7 is always a "Leader", regardless of if it's inverse.
    if (score >= 0.7) {
      if (isInverse) return "Leader (Low is Good)";
      return 'Leader';
    }
    if (score >= 0.4) return 'Neutral';
    
    if (isInverse) return "Lagger (High is Bad)";
    return 'Lagger';
  }

  String _formatRawMetric(String metricName, double value) {
    final lowerName = metricName.toLowerCase();
    if (lowerName.contains('p/e') || lowerName.contains('pe ratio')) {
      return '${value.toStringAsFixed(1)}x';
    }
    if (lowerName.contains('margin') ||
        lowerName.contains('growth') ||
        lowerName.contains('roe') ||
        lowerName.contains('roa')) {
      return '${(value * 100).toStringAsFixed(2)}%';
    }
    return value.toStringAsFixed(2);
  }
}
// Custom Painters removed in favor of LinearProgressIndicator
