import 'package:flutter/material.dart';
import '../utils/metric_calculations.dart';
import 'metric_tooltip.dart';

/// Summary bar displaying key financial metrics
class SummaryBar extends StatelessWidget {
  const SummaryBar({
    super.key,
    required this.metricsData,
    this.latestPeriod,
  });

  final Map<String, MetricData> metricsData;
  final String? latestPeriod;

  @override
  Widget build(BuildContext context) {
    // Calculate ratios if not already present
    final ratios = MetricCalculations.calculateRatios(
      metricsData,
      metricsData.values.firstOrNull?.period ?? '',
    );

    final allMetrics = {...metricsData, ...ratios};

    // Define key metrics to display
    final keyMetrics = [
      ('total_assets', 'Total Assets', Colors.green.shade700),
      ('total_liabilities', 'Total Liabilities', Colors.red.shade700),
      ('shareholders_equity', 'Shareholder Equity', Colors.blue.shade700),
      ('net_income', 'Net Income', Colors.amber.shade700),
      ('debt_to_equity', 'Debt-to-Equity', Colors.purple.shade700),
      ('current_ratio', 'Current Ratio', Colors.teal.shade700),
      ('roe', 'ROE', Colors.indigo.shade700),
      ('roa', 'ROA', Colors.cyan.shade700),
      ('working_capital', 'Working Capital', Colors.orange.shade700),
    ];

    return Card(
      elevation: 2,
      color: Colors.blue.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.dashboard, color: Colors.blue.shade700, size: 24),
                const SizedBox(width: 8),
                Text(
                  'Key Financial Metrics',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade700,
                  ),
                ),
                if (latestPeriod != null) ...[
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade100,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.blue.shade300),
                    ),
                    child: Text(
                      'Latest Period: $latestPeriod',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: Colors.blue.shade800,
                      ),
                    ),
                  ),
                ],
              ],
            ),
            const SizedBox(height: 16),
            LayoutBuilder(
              builder: (context, constraints) {
                // Determine number of columns based on width
                int crossAxisCount;
                if (constraints.maxWidth > 1200) {
                  crossAxisCount = 5;
                } else if (constraints.maxWidth > 900) {
                  crossAxisCount = 4;
                } else if (constraints.maxWidth > 600) {
                  crossAxisCount = 3;
                } else {
                  crossAxisCount = 2;
                }

                return GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: crossAxisCount,
                    childAspectRatio: 2.5,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                  ),
                  itemCount: keyMetrics.length,
                  itemBuilder: (context, index) {
                    final (id, name, color) = keyMetrics[index];
                    final data = allMetrics[id];
                    
                    return _SummaryMetricCard(
                      name: name,
                      data: data,
                      color: color,
                      isRatio: id.contains('ratio') || id == 'roe' || id == 'roa',
                    );
                  },
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _SummaryMetricCard extends StatelessWidget {
  const _SummaryMetricCard({
    required this.name,
    required this.data,
    required this.color,
    this.isRatio = false,
  });

  final String name;
  final MetricData? data;
  final Color color;
  final bool isRatio;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Metric name with tooltip
          Row(
            children: [
              Expanded(
                child: Text(
                  name,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: color,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              MetricTooltip(
                metricName: name,
                iconSize: 12,
              ),
            ],
          ),
          
          const SizedBox(height: 8),
          
          // Value
          if (data != null) ...[
            Row(
              children: [
                Expanded(
                  child: Text(
                    isRatio 
                        ? data!.currentValue.toStringAsFixed(2)
                        : data!.formatValue(compact: true),
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                // Trend icon
                Text(
                  data!.getTrendIcon(),
                  style: TextStyle(
                    fontSize: 14,
                    color: _getTrendColor(data!),
                  ),
                ),
              ],
            ),
            
            // Percentage change
            if (data!.percentChange != null)
              Text(
                data!.formatPercentChange(),
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: _getTrendColor(data!),
                ),
              ),
          ] else
            Text(
              'N/A',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade600,
                fontStyle: FontStyle.italic,
              ),
            ),
        ],
      ),
    );
  }

  Color _getTrendColor(MetricData data) {
    switch (data.trend) {
      case TrendDirection.up:
        return Colors.green.shade700;
      case TrendDirection.down:
        return Colors.red.shade700;
      case TrendDirection.flat:
      case TrendDirection.noData:
        return Colors.grey.shade600;
    }
  }
}
