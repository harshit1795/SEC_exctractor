import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
    'ROE',
    'ROA',
    'Current Ratio',
    'Quick Ratio',
  ];

  final _selectedMetrics = <String, double>{
    'Revenue Growth': 0.25,
    'Net Margin': 0.25,
    'FCF Margin': 0.25,
    'Debt to Equity': 0.25,
  };

  @override
  Widget build(BuildContext context) {
    final totalWeight = _selectedMetrics.values.fold(0.0, (sum, val) => sum + val);
    final isValidWeights = (totalWeight - 1.0).abs() < 0.01;

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
                  Row(
                    children: [
                      Icon(Icons.tune, size: 24, color: Colors.blue.shade700),
                      const SizedBox(width: 12),
                      const Text(
                        'Custom Health Score',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Create your own health score by selecting metrics and assigning weights.',
                    style: TextStyle(
                      color: Colors.grey.shade600,
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
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Metric Weights',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: isValidWeights ? Colors.green.shade50 : Colors.red.shade50,
                          border: Border.all(
                            color: isValidWeights ? Colors.green : Colors.red,
                          ),
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
                    Text(
                      'Weights must add up to 100%',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.red.shade700,
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  ..._selectedMetrics.entries.map((entry) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                entry.key,
                                style: const TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              Row(
                                children: [
                                  Text(
                                    '${(entry.value * 100).toStringAsFixed(0)}%',
                                    style: const TextStyle(
                                      fontSize: 14,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  IconButton(
                                    icon: const Icon(Icons.close, size: 20),
                                    onPressed: () {
                                      setState(() {
                                        _selectedMetrics.remove(entry.key);
                                      });
                                    },
                                  ),
                                ],
                              ),
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
                          ),
                        ],
                      ),
                    );
                  }),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    decoration: const InputDecoration(
                      labelText: 'Add Metric',
                      border: OutlineInputBorder(),
                    ),
                    items: _availableMetrics
                        .where((m) => !_selectedMetrics.containsKey(m))
                        .map((metric) => DropdownMenuItem(
                              value: metric,
                              child: Text(metric),
                            ))
                        .toList(),
                    onChanged: (value) {
                      if (value != null) {
                        setState(() {
                          _selectedMetrics[value] = 0.1;
                        });
                      }
                    },
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _tickerController,
                          decoration: const InputDecoration(
                            labelText: 'Ticker',
                            border: OutlineInputBorder(),
                          ),
                          textCapitalization: TextCapitalization.characters,
                        ),
                      ),
                      const SizedBox(width: 12),
                      ElevatedButton(
                        onPressed: isValidWeights
                            ? () {
                                setState(() {
                                  _ticker = _tickerController.text.trim().toUpperCase();
                                });
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text('Calculating health score for $_ticker...'),
                                  ),
                                );
                              }
                            : null,
                        child: const Text('Calculate'),
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
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  Text(
                    'Custom Health Score for $_ticker',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    'Coming Soon',
                    style: TextStyle(
                      fontSize: 48,
                      fontWeight: FontWeight.bold,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Custom health score calculation will be implemented with backend integration',
                    style: TextStyle(
                      color: Colors.grey.shade600,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
