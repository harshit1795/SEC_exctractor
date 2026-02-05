import 'package:flutter/material.dart';
import '../../../data/financial_hierarchies.dart';
import '../utils/metric_calculations.dart';
import 'financial_tree_node.dart';

/// Panel component to render a complete financial statement tree
class FinancialTreePanel extends StatelessWidget {
  const FinancialTreePanel({
    super.key,
    required this.title,
    required this.roots,
    required this.metricsData,
    required this.headerColor,
  });

  final String title;
  final List<FinancialNode> roots;
  final Map<String, MetricData> metricsData;
  final Color headerColor;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: headerColor.withOpacity(0.1),
              border: Border(
                bottom: BorderSide(
                  color: headerColor,
                  width: 2,
                ),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  _getHeaderIcon(),
                  color: headerColor,
                  size: 24,
                ),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: headerColor,
                  ),
                ),
              ],
            ),
          ),

          // Tree content
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: roots.map((root) {
                  return FinancialTreeNode(
                    node: root,
                    metricsData: metricsData,
                    depth: 0,
                    initiallyExpanded: true,
                  );
                }).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  IconData _getHeaderIcon() {
    if (title.contains('Balance Sheet')) {
      return Icons.account_balance;
    } else if (title.contains('Income Statement')) {
      return Icons.trending_up;
    }
    return Icons.bar_chart;
  }
}
