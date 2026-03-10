import 'package:flutter/material.dart';
import '../../../data/financial_hierarchies.dart';
import '../utils/metric_calculations.dart';
import 'financial_tree_panel.dart';
import 'summary_bar.dart';

/// Main container for hierarchical financial statement visualization
class HierarchyView extends StatelessWidget {
  const HierarchyView({
    super.key,
    required this.ticker,
    required this.category,
    required this.metricsData,
    this.latestPeriod,
  });

  final String ticker;
  final String category;
  final Map<String, MetricData> metricsData;
  final String? latestPeriod;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth > 900;

        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Summary Bar at top
              SummaryBar(metricsData: metricsData, latestPeriod: latestPeriod),
              
              const SizedBox(height: 16),
              
              // Split view or stacked view based on screen width
              if (isWide)
                // Desktop: Side-by-side panels
                SizedBox(
                  height: 800,
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Balance Sheet Panel (left)
                      Expanded(
                        child: FinancialTreePanel(
                          title: 'Balance Sheet',
                          roots: BalanceSheetHierarchy.roots,
                          metricsData: metricsData,
                          headerColor: Colors.green.shade700,
                        ),
                      ),
                      
                      const SizedBox(width: 16),
                      
                      // Income Statement Panel (right)
                      Expanded(
                        child: FinancialTreePanel(
                          title: 'Income Statement',
                          roots: [IncomeStatementHierarchy.root],
                          metricsData: metricsData,
                          headerColor: Colors.blue.shade700,
                        ),
                      ),
                    ],
                  ),
                )
              else
                // Mobile/Tablet: Vertical stack
                Column(
                  children: [
                    // Balance Sheet Panel
                    SizedBox(
                      height: 500,
                      child: FinancialTreePanel(
                        title: 'Balance Sheet',
                        roots: BalanceSheetHierarchy.roots,
                        metricsData: metricsData,
                        headerColor: Colors.green.shade700,
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // Income Statement Panel
                    SizedBox(
                      height: 500,
                      child: FinancialTreePanel(
                        title: 'Income Statement',
                        roots: [IncomeStatementHierarchy.root],
                        metricsData: metricsData,
                        headerColor: Colors.blue.shade700,
                      ),
                    ),
                  ],
                ),
            ],
          ),
        );
      },
    );
  }
}
