import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../dashboard_providers.dart';

class DashboardFilters extends ConsumerStatefulWidget {
  const DashboardFilters({super.key});

  @override
  ConsumerState<DashboardFilters> createState() => _DashboardFiltersState();
}

class _DashboardFiltersState extends ConsumerState<DashboardFilters> {
  late TextEditingController _tickerController;

  @override
  void initState() {
    super.initState();
    _tickerController = TextEditingController(
      text: ref.read(tickerProvider),
    );
  }

  @override
  void dispose() {
    _tickerController.dispose();
    super.dispose();
  }

  void _submitTicker() {
      final value = _tickerController.text.trim().toUpperCase();
      if (value.isNotEmpty) {
          ref.read(tickerProvider.notifier).setTicker(value);
      }
  }

  @override
  Widget build(BuildContext context) {
    // Listen to provider changes to update controller if needed (e.g. from persistence)
    ref.listen(tickerProvider, (previous, next) {
      if (_tickerController.text != next) {
        _tickerController.text = next;
      }
    });

    final category = ref.watch(categoryProvider);

    final definitions = [
      ('IncomeStatement', 'Income Statement'),
      ('BalanceSheet', 'Balance Sheet'),
      ('CashFlow', 'Cash Flow'),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Ticker Search - First thing at the top
        Container(
          height: 50,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.shade300),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            children: [
              const SizedBox(width: 16),
              const Icon(Icons.search, color: Colors.grey),
              const SizedBox(width: 12),
              Expanded(
                child: TextField(
                  controller: _tickerController,
                  decoration: const InputDecoration(
                    border: InputBorder.none,
                    hintText: 'Search Ticker (e.g. AAPL, GOOGL)',
                    contentPadding: EdgeInsets.symmetric(vertical: 12),
                  ),
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  onSubmitted: (_) => _submitTicker(),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.arrow_forward),
                onPressed: _submitTicker,
                color: const Color(0xFF2E7D32),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        // Filter Options - Below Ticker Search
        SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
                children: [
                    // Category Selector
                    Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                        decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.grey.shade300),
                        ),
                        child: DropdownButtonHideUnderline(
                            child: DropdownButton<String>(
                                value: category,
                                icon: const Icon(Icons.keyboard_arrow_down, color: Colors.grey),
                                style: const TextStyle(color: Colors.black87, fontWeight: FontWeight.w500),
                                items: definitions.map((def) {
                                    return DropdownMenuItem(
                                        value: def.$1,
                                        child: Text(def.$2),
                                    );
                                }).toList(),
                                onChanged: (value) {
                                    if (value != null) {
                                        ref.read(categoryProvider.notifier).setCategory(value);
                                    }
                                },
                            ),
                        ),
                    ),
                    const SizedBox(width: 12),
                    // Add other filters here if needed
                ],
            ),
        ),
      ],
    );
  }
}
