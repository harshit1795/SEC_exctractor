
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../dashboard_providers.dart';
import 'ticker_search_autocomplete.dart';

class DashboardFilters extends ConsumerWidget {
  const DashboardFilters({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final category = ref.watch(categoryProvider);
    final selectedTickers = ref.watch(selectedTickersProvider);

    final definitions = [
      ('IncomeStatement', 'Income Statement'),
      ('BalanceSheet', 'Balance Sheet'),
      ('CashFlow', 'Cash Flow'),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Ticker Search - First thing at the top
        const TickerSearchAutocomplete(),
        
        const SizedBox(height: 12),
        
        // Selected Tickers Chips
        if (selectedTickers.isNotEmpty)
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: selectedTickers.map((ticker) {
              return Chip(
                label: Text(ticker, style: const TextStyle(fontWeight: FontWeight.bold)),
                backgroundColor: Colors.green.shade50,
                deleteIcon: const Icon(Icons.close, size: 18),
                onDeleted: () {
                  ref.read(selectedTickersProvider.notifier).removeTicker(ticker);
                },
                side: BorderSide(color: Colors.green.shade200),
              );
            }).toList(),
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

