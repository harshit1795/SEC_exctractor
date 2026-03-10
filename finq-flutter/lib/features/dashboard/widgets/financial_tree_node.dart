import 'package:flutter/material.dart';
import '../../../data/financial_hierarchies.dart';
import '../utils/metric_calculations.dart';
import 'metric_tooltip.dart';

/// A tree node widget for displaying financial metrics hierarchically
class FinancialTreeNode extends StatefulWidget {
  const FinancialTreeNode({
    super.key,
    required this.node,
    required this.metricsData,
    this.depth = 0,
    this.initiallyExpanded = false,
  });

  final FinancialNode node;
  final Map<String, MetricData> metricsData;
  final int depth;
  final bool initiallyExpanded;

  @override
  State<FinancialTreeNode> createState() => _FinancialTreeNodeState();
}

class _FinancialTreeNodeState extends State<FinancialTreeNode>
    with SingleTickerProviderStateMixin {
  late bool _isExpanded;
  late AnimationController _animationController;
  late Animation<double> _expandAnimation;

  @override
  void initState() {
    super.initState();
    _isExpanded = widget.initiallyExpanded || widget.depth == 0;
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    
    _expandAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );

    if (_isExpanded) {
      _animationController.value = 1.0;
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _toggleExpanded() {
    setState(() {
      _isExpanded = !_isExpanded;
      if (_isExpanded) {
        _animationController.forward();
      } else {
        _animationController.reverse();
      }
    });
  }

  Color _getCategoryColor() {
    switch (widget.node.category) {
      case NodeCategory.asset:
      case NodeCategory.currentAsset:
        return Colors.green.shade600;
      case NodeCategory.nonCurrentAsset:
        return Colors.green.shade400;
      case NodeCategory.liability:
      case NodeCategory.currentLiability:
        return Colors.red.shade600;
      case NodeCategory.longTermLiability:
        return Colors.red.shade400;
      case NodeCategory.equity:
        return Colors.blue.shade600;
      case NodeCategory.revenue:
        return Colors.green.shade700;
      case NodeCategory.expense:
        return Colors.red.shade700;
      case NodeCategory.profit:
        return Colors.amber.shade700;
    }
  }

  Color _getBackgroundColor(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final opacity = isDark ? 0.15 : 0.05;
    
    switch (widget.node.category) {
      case NodeCategory.asset:
      case NodeCategory.currentAsset:
      case NodeCategory.nonCurrentAsset:
        return Colors.green.withOpacity(opacity);
      case NodeCategory.liability:
      case NodeCategory.currentLiability:
      case NodeCategory.longTermLiability:
        return Colors.red.withOpacity(opacity);
      case NodeCategory.equity:
        return Colors.blue.withOpacity(opacity);
      case NodeCategory.revenue:
        return Colors.green.withOpacity(opacity);
      case NodeCategory.expense:
        return Colors.red.withOpacity(opacity);
      case NodeCategory.profit:
        return Colors.amber.withOpacity(opacity);
    }
  }

  Color _getTrendColor(MetricData metricData, bool isExpense) {
    // For expenses and liabilities, inverse the color logic
    final shouldInvert = isExpense || 
        widget.node.category == NodeCategory.liability ||
        widget.node.category == NodeCategory.currentLiability ||
        widget.node.category == NodeCategory.longTermLiability ||
        widget.node.category == NodeCategory.expense;

    switch (metricData.trend) {
      case TrendDirection.up:
        return shouldInvert ? Colors.red.shade700 : Colors.green.shade700;
      case TrendDirection.down:
        return shouldInvert ? Colors.green.shade700 : Colors.red.shade700;
      case TrendDirection.flat:
      case TrendDirection.noData:
        return Colors.grey.shade600;
    }
  }

  @override
  Widget build(BuildContext context) {
    final metricData = widget.metricsData[widget.node.id];
    final hasChildren = widget.node.children.isNotEmpty;
    final indentation = widget.depth * 20.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Node row
        InkWell(
          onTap: hasChildren ? _toggleExpanded : null,
          child: Container(
            padding: EdgeInsets.only(
              left: indentation + 8,
              right: 8,
              top: 8,
              bottom: 8,
            ),
            decoration: BoxDecoration(
              color: _getBackgroundColor(context),
              border: Border(
                left: BorderSide(
                  color: _getCategoryColor(),
                  width: 3,
                ),
              ),
            ),
            child: Row(
              children: [
                // Expand/collapse icon
                if (hasChildren)
                  AnimatedRotation(
                    turns: _isExpanded ? 0.25 : 0.0,
                    duration: const Duration(milliseconds: 200),
                    child: Icon(
                      Icons.arrow_right,
                      size: 20,
                      color: _getCategoryColor(),
                    ),
                  )
                else
                  const SizedBox(width: 20),
                
                const SizedBox(width: 8),

                // Metric name with tooltip
                Expanded(
                  child: Row(
                    children: [
                      Text(
                        widget.node.displayName,
                        style: TextStyle(
                          fontSize: widget.depth == 0 ? 16 : 14,
                          fontWeight: widget.depth == 0
                              ? FontWeight.bold
                              : FontWeight.w500,
                          color: Theme.of(context).colorScheme.onSurface,
                        ),
                      ),
                      const SizedBox(width: 4),
                      if (widget.node.metricName != null)
                        MetricTooltip(
                          metricName: widget.node.metricName!,
                          iconSize: 14,
                        ),
                      if (metricData?.isPartial == true)
                        Padding(
                          padding: const EdgeInsets.only(left: 4),
                          child: Tooltip(
                            message: 'Some child metrics are missing',
                            child: Icon(
                              Icons.warning_amber,
                              size: 14,
                              color: Colors.orange.shade600,
                            ),
                          ),
                        ),
                    ],
                  ),
                ),

                // Value and trend
                if (metricData != null) ...[
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Trend icon
                      Text(
                        metricData.getTrendIcon(),
                        style: TextStyle(
                          color: _getTrendColor(
                            metricData,
                            widget.node.category == NodeCategory.expense,
                          ),
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(width: 8),
                      
                      // Value
                      Text(
                        metricData.formatValue(compact: true),
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Theme.of(context).colorScheme.onSurface,
                        ),
                      ),
                      
                      const SizedBox(width: 8),
                      
                      // Percentage change
                      if (metricData.percentChange != null)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 6,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: _getTrendColor(
                              metricData,
                              widget.node.category == NodeCategory.expense,
                            ).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            metricData.formatPercentChange(),
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: _getTrendColor(
                                metricData,
                                widget.node.category == NodeCategory.expense,
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ] else
                  Text(
                    'N/A',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade600,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
              ],
            ),
          ),
        ),

        // Children nodes
        if (hasChildren)
          SizeTransition(
            sizeFactor: _expandAnimation,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: widget.node.children.map((childNode) {
                return FinancialTreeNode(
                  node: childNode,
                  metricsData: widget.metricsData,
                  depth: widget.depth + 1,
                  initiallyExpanded: false,
                );
              }).toList(),
            ),
          ),
      ],
    );
  }
}
