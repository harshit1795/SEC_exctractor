import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'tabs/health_score_tab.dart';
import 'tabs/custom_metrics_tab.dart';

class HealthPage extends ConsumerWidget {
  const HealthPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return SafeArea(
      child: DefaultTabController(
        length: 2,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  Icon(Icons.health_and_safety, size: 28, color: Colors.green.shade700),
                  const SizedBox(width: 12),
                  const Text(
                    'Financial Health Monitoring',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            TabBar(
              labelColor: Theme.of(context).colorScheme.primary,
              unselectedLabelColor: Theme.of(context).colorScheme.onSurfaceVariant,
              indicatorColor: Theme.of(context).colorScheme.primary,
              tabs: const [
                Tab(text: 'Custom Health Score', icon: Icon(Icons.settings_suggest)),
                Tab(text: 'FinQ Suggestions', icon: Icon(Icons.recommend)),
              ],
            ),
            const Expanded(
              child: TabBarView(
                children: [
                  CustomMetricsTab(),
                  HealthScoreTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
