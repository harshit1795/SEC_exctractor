
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../dashboard_providers.dart';
import 'ticker_search_autocomplete.dart';
import 'data_pipeline_button.dart';

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
        // Ticker Search and Data Pipeline Management
        Row(
          children: [
            const Expanded(child: TickerSearchAutocomplete()),
            const SizedBox(width: 12),
            DataPipelineButton(
              ticker: selectedTickers.isNotEmpty ? selectedTickers.first : '',
            ),
          ],
        ),
        
        const SizedBox(height: 12),
        
        // Selected Tickers Chips
        if (selectedTickers.isNotEmpty)
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: selectedTickers.map((ticker) {
              return Chip(
                label: Text(ticker, style: const TextStyle(fontWeight: FontWeight.bold)),
                backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                labelStyle: TextStyle(color: Theme.of(context).colorScheme.onPrimaryContainer),
                deleteIcon: Icon(Icons.close, size: 18, color: Theme.of(context).colorScheme.onPrimaryContainer),
                onDeleted: () {
                  ref.read(selectedTickersProvider.notifier).removeTicker(ticker);
                },
                side: BorderSide(color: Theme.of(context).colorScheme.primary.withOpacity(0.3)),
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
                            color: Theme.of(context).colorScheme.surfaceContainerLow,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Theme.of(context).colorScheme.outline.withOpacity(0.4)),
                        ),
                        child: DropdownButtonHideUnderline(
                            child: DropdownButton<String>(
                                value: category,
                                icon: Icon(Icons.keyboard_arrow_down, color: Theme.of(context).colorScheme.onSurfaceVariant),
                                dropdownColor: Theme.of(context).colorScheme.surfaceContainerHigh,
                                style: TextStyle(color: Theme.of(context).colorScheme.onSurface, fontWeight: FontWeight.w500),
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

