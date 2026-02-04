import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';

import '../../../core/di/providers.dart';

class HealthScoreTab extends ConsumerStatefulWidget {
  const HealthScoreTab({super.key});

  @override
  ConsumerState<HealthScoreTab> createState() => _HealthScoreTabState();
}

class _HealthScoreTabState extends ConsumerState<HealthScoreTab> {
  final _tickerController = TextEditingController(text: 'AAPL');
  String _ticker = 'AAPL';

  @override
  void dispose() {
    _tickerController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'FinQ Health Score',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Health Score Formula: (Growth + NetMargin + FCFMargin + (1 - DebtEquity)) / 4',
                    style: TextStyle(
                      fontSize: 14,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                  const SizedBox(height: 16),
                  ExpansionTile(
                    title: const Text('How are individual metrics scored?'),
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Text(
                          'Each metric (Growth, Net Margin, FCF Margin, Debt to Equity) is converted '
                          'into a score between 0 and 1 using percentile ranking. A higher percentile '
                          'rank indicates a better score.\n\n'
                          '• Growth_score, NetMargin_score, FCFMargin_score: Percentile ranks\n'
                          '• DebtEquity_score: 1 - percentile_rank (lower debt is better)\n\n'
                          'The final Health Score is the average of these individual metric scores.',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade700,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Select Ticker',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _tickerController,
                          decoration: const InputDecoration(
                            hintText: 'Enter ticker symbol',
                            border: OutlineInputBorder(),
                          ),
                          textCapitalization: TextCapitalization.characters,
                        ),
                      ),
                      const SizedBox(width: 12),
                      ElevatedButton(
                        onPressed: () {
                          setState(() {
                            _ticker = _tickerController.text.trim().toUpperCase();
                          });
                        },
                        child: const Text('Analyze'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          // Health Score Display
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  const Text(
                    'Overall Health Score',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    height: 200,
                    width: 200,
                    child: _buildHealthGauge(0.75), // Placeholder score
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Ticker: $_ticker',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Score: 75/100',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.green.shade700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'HEALTHY',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: Colors.green.shade700,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Health Metrics Breakdown',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  _buildMetricBar('Growth Score', 0.80, Colors.blue),
                  const SizedBox(height: 12),
                  _buildMetricBar('Net Margin Score', 0.85, Colors.green),
                  const SizedBox(height: 12),
                  _buildMetricBar('FCF Margin Score', 0.70, Colors.orange),
                  const SizedBox(height: 12),
                  _buildMetricBar('Debt/Equity Score', 0.65, Colors.purple),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthGauge(double score) {
    return PieChart(
      PieChartData(
        startDegreeOffset: 180,
        sectionsSpace: 0,
        centerSpaceRadius: 60,
        sections: [
          PieChartSectionData(
            value: score * 100,
            color: _getScoreColor(score),
            radius: 30,
            showTitle: false,
          ),
          PieChartSectionData(
            value: (1 - score) * 100,
            color: Colors.grey.shade200,
            radius: 30,
            showTitle: false,
          ),
        ],
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 0.7) return Colors.green;
    if (score >= 0.4) return Colors.orange;
    return Colors.red;
  }

  Widget _buildMetricBar(String label, double value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(
              '${(value * 100).toStringAsFixed(0)}%',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        LinearProgressIndicator(
          value: value,
          backgroundColor: Colors.grey.shade200,
          valueColor: AlwaysStoppedAnimation<Color>(color),
          minHeight: 8,
        ),
      ],
    );
  }
}
