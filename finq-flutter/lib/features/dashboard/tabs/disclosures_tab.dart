import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/api/api_client.dart';
import '../../../core/di/providers.dart';
import '../widgets/tab_description_tooltip.dart';

class DisclosuresTab extends ConsumerStatefulWidget {
  const DisclosuresTab({
    required this.ticker,
    super.key,
  });

  final String ticker;

  @override
  ConsumerState<DisclosuresTab> createState() => _DisclosuresTabState();
}

class _DisclosuresTabState extends ConsumerState<DisclosuresTab> {
  var _reportType = _ReportType.tenK;
  String _selectedSection = 'business';

  @override
  Widget build(BuildContext context) {
    final filingsFuture = ref.watch(_secFilingsProvider(widget.ticker));
    final sectionsFuture = ref.watch(
      _reportType == _ReportType.tenK
          ? _sec10KProvider(widget.ticker)
          : _sec10QProvider(widget.ticker),
    );

    return filingsFuture.when(
      data: (filingsData) {
        final filingInfo = _reportType == _ReportType.tenK
            ? (filingsData['filings']?['10-k'] ?? filingsData['filings']?['10-K'])
            : (filingsData['filings']?['10-q'] ?? filingsData['filings']?['10-Q']);

        final sectionOptions = _reportType == _ReportType.tenK
            ? _sectionOptions10K
            : _sectionOptions10Q;

        // Reset section if it's not valid for current report type
        if (!sectionOptions.any((opt) => opt.key == _selectedSection)) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            setState(() => _selectedSection = sectionOptions.first.key);
          });
        }

        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Tab description tooltip
              Padding(
                padding: const EdgeInsets.only(left: 4, bottom: 8),
                child: Row(
                  children: [
                    Text(
                      'SEC Disclosures',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                    const SizedBox(width: 8),
                    const TabDescriptionTooltip(tabId: 'disclosures'),
                  ],
                ),
              ),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.account_balance, size: 28),
                          SizedBox(width: 12),
                          Text(
                            'Company Disclosures',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'View key sections from the latest 10-K and 10-Q filings for ${widget.ticker}.',
                        style: TextStyle(
                          color: Colors.grey.shade600,
                        ),
                      ),
                      const SizedBox(height: 24),
                      // Report Type Selection
                      const Text(
                        'Select Report Type',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 8),
                      SegmentedButton<_ReportType>(
                        segments: const [
                          ButtonSegment(
                            value: _ReportType.tenK,
                            label: Text('10-K'),
                          ),
                          ButtonSegment(
                            value: _ReportType.tenQ,
                            label: Text('10-Q'),
                          ),
                        ],
                        selected: {_reportType},
                        onSelectionChanged: (values) {
                          setState(() {
                            _reportType = values.first;
                            _selectedSection = sectionOptions.first.key;
                          });
                        },
                      ),
                      const SizedBox(height: 24),
                      // Filing Information
                      if (filingInfo != null)
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.blue.shade50,
                            border: Border.all(color: Colors.blue.shade200),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Latest ${_reportType == _ReportType.tenK ? '10-K' : '10-Q'} filed on: ${filingInfo['filingDate'] ?? filingInfo['filing_date'] ?? 'N/A'}',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w500,
                                  color: Colors.blue.shade900,
                                ),
                              ),
                              if (filingInfo['doc_url'] != null) ...[
                                const SizedBox(height: 8),
                                InkWell(
                                  onTap: () {
                                    // In a real app, you'd open this URL
                                    // For now, just copy to clipboard
                                    Clipboard.setData(
                                      ClipboardData(
                                        text: filingInfo['doc_url'],
                                      ),
                                    );
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(
                                        content: Text('URL copied to clipboard'),
                                        duration: Duration(seconds: 2),
                                      ),
                                    );
                                  },
                                  child: Text(
                                    'View on SEC.gov →',
                                    style: TextStyle(
                                      fontSize: 14,
                                      color: Colors.blue.shade700,
                                      decoration: TextDecoration.underline,
                                    ),
                                  ),
                                ),
                              ],
                              if (filingInfo['accessionNumber'] != null) ...[
                                const SizedBox(height: 4),
                                Text(
                                  'Accession Number: ${filingInfo['accessionNumber']}',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                              ],
                            ],
                          ),
                        )
                      else
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.yellow.shade50,
                            border: Border.all(color: Colors.yellow.shade200),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            'No ${_reportType == _ReportType.tenK ? '10-K' : '10-Q'} filings found for ${widget.ticker}.',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.yellow.shade900,
                            ),
                          ),
                        ),
                      const SizedBox(height: 24),
                      // Section Selection
                      const Text(
                        'Select Section to Display',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<String>(
                        value: _selectedSection,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          contentPadding: EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 8,
                          ),
                        ),
                        items: sectionOptions
                            .map((opt) => DropdownMenuItem(
                                  value: opt.key,
                                  child: Text(opt.label),
                                ))
                            .toList(),
                        onChanged: (value) {
                          if (value != null) {
                            setState(() => _selectedSection = value);
                          }
                        },
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              // Section Content
              sectionsFuture.when(
                data: (sectionsData) {
                  final sectionLabel = sectionOptions
                      .firstWhere((opt) => opt.key == _selectedSection)
                      .label;
                  final sectionContent = sectionsData['sections']?[sectionLabel] ??
                      sectionsData['sections']?[_selectedSection];

                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            sectionLabel,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          if (filingInfo != null) ...[
                            const SizedBox(height: 4),
                            Text(
                              'From ${_reportType == _ReportType.tenK ? '10-K' : '10-Q'} filed on ${filingInfo['filingDate'] ?? filingInfo['filing_date'] ?? 'N/A'}',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey.shade600,
                              ),
                            ),
                          ],
                          const SizedBox(height: 16),
                          if (sectionContent != null)
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.grey.shade50,
                                border: Border.all(color: Colors.grey.shade200),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              constraints: const BoxConstraints(maxHeight: 500),
                              child: SingleChildScrollView(
                                child: Text(
                                  sectionContent,
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey.shade700,
                                    height: 1.5,
                                  ),
                                ),
                              ),
                            )
                          else
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.yellow.shade50,
                                border: Border.all(color: Colors.yellow.shade200),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                'Section content not found or empty. This may occur if the filing structure is different than expected.',
                                style: TextStyle(
                                  color: Colors.yellow.shade800,
                                ),
                              ),
                            ),
                          if (sectionContent != null) ...[
                            const SizedBox(height: 16),
                            ElevatedButton.icon(
                              onPressed: () {
                                Clipboard.setData(
                                  ClipboardData(text: sectionContent),
                                );
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Section copied to clipboard'),
                                    duration: Duration(seconds: 2),
                                  ),
                                );
                              },
                              icon: const Icon(Icons.content_copy, size: 18),
                              label: const Text('Copy Section to Clipboard'),
                            ),
                          ],
                        ],
                      ),
                    ),
                  );
                },
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32),
                    child: CircularProgressIndicator(),
                  ),
                ),
                error: (error, _) => Card(
                  child: Padding(
                    padding: const EdgeInsets.all(32),
                    child: Column(
                      children: [
                        const Icon(
                          Icons.error_outline,
                          size: 48,
                          color: Colors.orange,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Failed to load section content',
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.grey.shade700,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'This may occur if the filing hasn\'t been processed yet.',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey.shade600,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline, size: 48, color: Colors.red),
                const SizedBox(height: 16),
                Text(
                  'Unable to Load SEC Filings',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey.shade900,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  error.toString(),
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade600,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// Providers for SEC data
final _secFilingsProvider = FutureProvider.family<Map<String, dynamic>, String>(
  (ref, ticker) async {
    final apiClient = ref.watch(apiClientProvider);
    final response = await apiClient.get('/financial/sec/$ticker');
    return response.data as Map<String, dynamic>;
  },
);

final _sec10KProvider = FutureProvider.family<Map<String, dynamic>, String>(
  (ref, ticker) async {
    final apiClient = ref.watch(apiClientProvider);
    final response = await apiClient.get('/financial/sec/$ticker/10k');
    return response.data as Map<String, dynamic>;
  },
);

final _sec10QProvider = FutureProvider.family<Map<String, dynamic>, String>(
  (ref, ticker) async {
    final apiClient = ref.watch(apiClientProvider);
    final response = await apiClient.get('/financial/sec/$ticker/10q');
    return response.data as Map<String, dynamic>;
  },
);

// Data models
class _SectionOption {
  const _SectionOption({required this.label, required this.key});

  final String label;
  final String key;
}

enum _ReportType { tenK, tenQ }

const _sectionOptions10K = [
  _SectionOption(label: 'Business Overview (Item 1)', key: 'business'),
  _SectionOption(label: 'Risk Factors (Item 1A)', key: 'risk'),
  _SectionOption(label: 'Management\'s Discussion & Analysis (Item 7)', key: 'mda'),
];

const _sectionOptions10Q = [
  _SectionOption(label: 'Risk Factors (Part II, Item 1A)', key: 'risk'),
  _SectionOption(label: 'Management\'s Discussion & Analysis (Part I, Item 2)', key: 'mda'),
];
