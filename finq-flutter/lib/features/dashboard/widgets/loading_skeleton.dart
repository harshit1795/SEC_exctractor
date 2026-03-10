import 'package:flutter/material.dart';

/// A shimmer loading skeleton widget
class LoadingSkeleton extends StatefulWidget {
  const LoadingSkeleton({
    super.key,
    this.width = double.infinity,
    this.height = 16,
    this.borderRadius = 4,
  });

  final double width;
  final double height;
  final double borderRadius;

  @override
  State<LoadingSkeleton> createState() => _LoadingSkeletonState();
}

class _LoadingSkeletonState extends State<LoadingSkeleton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();

    _animation = Tween<double>(begin: -1.0, end: 2.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(widget.borderRadius),
            gradient: LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [
                Colors.grey.shade300,
                Colors.grey.shade200,
                Colors.grey.shade300,
              ],
              stops: [
                _animation.value - 0.3,
                _animation.value,
                _animation.value + 0.3,
              ],
            ),
          ),
        );
      },
    );
  }
}

/// Loading skeleton for dashboard cards
class DashboardCardSkeleton extends StatelessWidget {
  const DashboardCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const LoadingSkeleton(width: 150, height: 20),
            const SizedBox(height: 16),
            const LoadingSkeleton(height: 12),
            const SizedBox(height: 8),
            const LoadingSkeleton(height: 12, width: 200),
            const SizedBox(height: 8),
            const LoadingSkeleton(height: 12, width: 250),
            const SizedBox(height: 24),
            LoadingSkeleton(
              height: 200,
              borderRadius: 8,
              width: double.infinity,
            ),
          ],
        ),
      ),
    );
  }
}

/// Loading skeleton for data table
class DataTableSkeleton extends StatelessWidget {
  const DataTableSkeleton({
    super.key,
    this.rowCount = 5,
    this.columnCount = 4,
  });

  final int rowCount;
  final int columnCount;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header row
            Row(
              children: List.generate(
                columnCount,
                (index) => Expanded(
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: LoadingSkeleton(
                      height: 16,
                      width: double.infinity,
                    ),
                  ),
                ),
              ),
            ),
            const Divider(),
            // Data rows
            ...List.generate(
              rowCount,
              (rowIndex) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 8.0),
                child: Row(
                  children: List.generate(
                    columnCount,
                    (colIndex) => Expanded(
                      child: Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: LoadingSkeleton(
                          height: 14,
                          width: double.infinity,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Loading skeleton for chart
class ChartSkeleton extends StatelessWidget {
  const ChartSkeleton({super.key, this.height = 300});

  final double height;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const LoadingSkeleton(width: 150, height: 20),
            const SizedBox(height: 16),
            LoadingSkeleton(
              height: height,
              borderRadius: 8,
              width: double.infinity,
            ),
          ],
        ),
      ),
    );
  }
}
