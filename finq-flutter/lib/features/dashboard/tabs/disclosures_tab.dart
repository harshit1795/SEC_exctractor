import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:universal_html/html.dart' as html;

import '../../../core/di/providers.dart';
import '../dashboard_providers.dart';
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
  final Map<String, bool> _isExpandedMap = {};
  final Map<String, String> _onDemandSummaries = {};
  final Map<String, bool> _isLoadingSummaries = {};
  final Map<String, String> _comparisonSummaries = {};
  final Map<String, bool> _isLoadingComparison = {};

  @override
  void didUpdateWidget(DisclosuresTab oldWidget) {
    super.didUpdateWidget(oldWidget);
  }

  Future<void> _fetchSummary(String ticker, _ReportType type, String sectionName, String sectionText) async {
    final key = '${ticker}_${type}_$_selectedSection';
    if (_onDemandSummaries.containsKey(key)) return;

    setState(() {
      _isLoadingSummaries[key] = true;
    });

    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.post('/financial/sec/summarize-section', body: {
        'section_name': sectionName,
        'section_text': sectionText,
      });

      if (response.data != null && response.data is Map && (response.data as Map)['summary'] != null) {
        setState(() {
          _onDemandSummaries[key] = (response.data as Map)['summary'];
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to fetch summary: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoadingSummaries[key] = false;
        });
      }
    }
  }

  Future<void> _fetchComparisonSummary(List<String> tickers, _ReportType type, String sectionKey) async {
    final key = '${tickers.join('_')}_${type}_$sectionKey';
    if (_comparisonSummaries.containsKey(key)) return;

    setState(() {
      _isLoadingComparison[key] = true;
    });

    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.post('/financial/sec/summarize-comparison', body: {
        'tickers': tickers,
        'report_type': type == _ReportType.tenK ? '10-k' : '10-q',
        'section_key': sectionKey,
      });

      if (response.data != null && response.data is Map && (response.data as Map)['summary'] != null) {
        setState(() {
          _comparisonSummaries[key] = (response.data as Map)['summary'];
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to fetch comparison summary: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoadingComparison[key] = false;
        });
      }
    }
  }

  void _launchURL(String url) {
    html.window.open(url, '_blank');
  }

  @override
  Widget build(BuildContext context) {
    final selectedTickers = ref.watch(selectedTickersProvider);
    final isMulti = selectedTickers.length > 1;

    final currentTicker = widget.ticker;

    final sectionOptions = _reportType == _ReportType.tenK
        ? _sectionOptions10K
        : _sectionOptions10Q;

    // Reset section if it's not valid for current report type
    if (!sectionOptions.any((opt) => opt.key == _selectedSection)) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) setState(() => _selectedSection = sectionOptions.first.key);
      });
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.only(bottom: 24),
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

          // Filters Card
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Report Type', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                              const SizedBox(height: 8),
                              SegmentedButton<_ReportType>(
                                segments: const [
                                  ButtonSegment(value: _ReportType.tenK, label: Text('10-K')),
                                  ButtonSegment(value: _ReportType.tenQ, label: Text('10-Q')),
                                ],
                                selected: {_reportType},
                                onSelectionChanged: (values) {
                                  setState(() => _reportType = values.first);
                                },
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Section', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                              const SizedBox(height: 8),
                              DropdownButtonFormField<String>(
                                value: _selectedSection,
                                isExpanded: true,
                                decoration: const InputDecoration(
                                    border: OutlineInputBorder(),
                                    contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8)),
                                items: (_reportType == _ReportType.tenK ? _sectionOptions10K : _sectionOptions10Q)
                                    .map((opt) => DropdownMenuItem(value: opt.key, child: Text(opt.label)))
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
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Section Content
          if (isMulti)
            _buildComparisonSummaryCard(selectedTickers, _reportType, _selectedSection),

          SizedBox(
            height: isMulti ? 600 : 800,
            child: isMulti
                ? ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: selectedTickers.length,
                    separatorBuilder: (context, index) => const SizedBox(width: 16),
                    itemBuilder: (context, index) {
                      return SizedBox(
                        width: 400,
                        child: _SECSectionContent(
                          ticker: selectedTickers[index],
                          reportType: _reportType,
                          sectionKey: _selectedSection,
                          isExpandedMap: _isExpandedMap,
                          onDemandSummaries: _onDemandSummaries,
                          isLoadingSummaries: _isLoadingSummaries,
                          onFetchSummary: _fetchSummary,
                          onLaunchLink: _launchURL,
                        ),
                      );
                    },
                  )
                : _SECSectionContent(
                    ticker: currentTicker,
                    reportType: _reportType,
                    sectionKey: _selectedSection,
                    isExpandedMap: _isExpandedMap,
                    onDemandSummaries: _onDemandSummaries,
                    isLoadingSummaries: _isLoadingSummaries,
                    onFetchSummary: _fetchSummary,
                    onLaunchLink: _launchURL,
                  ),
          ),
        ],
      ),
    );
  }

  // Helper to allow certain text styles if needed (dummy for now)
  TextStyle? getAllowedTextStyle(TextStyle style) => style;

  Widget _buildComparisonSummaryCard(List<String> tickers, _ReportType type, String sectionKey) {
    final key = '${tickers.join('_')}_${type}_$sectionKey';
    final summary = _comparisonSummaries[key];
    final isLoading = _isLoadingComparison[key] ?? false;

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Card(
        color: Colors.blue.shade50,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: Colors.blue.shade200, width: 1),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.auto_awesome, color: Colors.blue, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'Comparison AI Analysis',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue.shade900,
                    ),
                  ),
                  const Spacer(),
                  if (summary == null && !isLoading)
                    ElevatedButton(
                      onPressed: () => _fetchComparisonSummary(tickers, type, sectionKey),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                        visualDensity: VisualDensity.compact,
                      ),
                      child: const Text('Generate Comparative Analysis'),
                    )
                  else if (isLoading)
                    const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  else
                    TextButton.icon(
                      onPressed: () {
                        Clipboard.setData(ClipboardData(text: summary ?? ''));
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Comparison copied'), duration: Duration(seconds: 1)),
                        );
                      },
                      icon: const Icon(Icons.copy, size: 16),
                      label: const Text('Copy Analysis'),
                      style: TextButton.styleFrom(foregroundColor: Colors.blue.shade700),
                    ),
                ],
              ),
              if (summary != null) ...[
                const Divider(height: 24),
                MarkdownBody(
                  data: summary,
                  selectable: true,
                  styleSheet: MarkdownStyleSheet(
                    p: TextStyle(fontSize: 14, color: Colors.blue.shade900, height: 1.5),
                    listBullet: TextStyle(fontSize: 14, color: Colors.blue.shade900),
                  ),
                ),
              ] else if (!isLoading) ...[
                const SizedBox(height: 8),
                Text(
                  'Synthesize insights across all selected companies (${tickers.join(', ')}) for the "$sectionKey" section.',
                  style: TextStyle(fontSize: 13, color: Colors.blue.shade700),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _SECSectionContent extends ConsumerWidget {
  const _SECSectionContent({
    required this.ticker,
    required this.reportType,
    required this.sectionKey,
    required this.isExpandedMap,
    required this.onDemandSummaries,
    required this.isLoadingSummaries,
    required this.onFetchSummary,
    required this.onLaunchLink,
  });

  final String ticker;
  final _ReportType reportType;
  final String sectionKey;
  final Map<String, bool> isExpandedMap;
  final Map<String, String> onDemandSummaries;
  final Map<String, bool> isLoadingSummaries;
  final Future<void> Function(String, _ReportType, String, String) onFetchSummary;
  final void Function(String) onLaunchLink;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final filingsFuture = ref.watch(_secFilingsProvider(ticker));
    final sectionsFuture = ref.watch(
      reportType == _ReportType.tenK
          ? _sec10KProvider(ticker)
          : _sec10QProvider(ticker),
    );

    return filingsFuture.when(
      data: (filingsData) {
        final filingInfo = reportType == _ReportType.tenK
            ? (filingsData['filings']?['10-k'] ?? filingsData['filings']?['10-K'])
            : (filingsData['filings']?['10-q'] ?? filingsData['filings']?['10-Q']);

        final sectionOptions = reportType == _ReportType.tenK
            ? _sectionOptions10K
            : _sectionOptions10Q;

        final sectionLabel = sectionOptions
            .firstWhere((opt) => opt.key == sectionKey, orElse: () => sectionOptions.first)
            .label;

        return sectionsFuture.when(
          data: (sectionsData) {
            final fullContent = sectionsData['sections']?[sectionLabel] ??
                sectionsData['sections']?[sectionKey];
            
            final key = '${ticker}_${reportType}_$sectionKey';
            final isExpanded = isExpandedMap[key] ?? true;
            final summaryContent = onDemandSummaries[key];
            final isLoadingSummary = isLoadingSummaries[key] ?? false;
            
            final displayContent = (isExpanded || summaryContent == null) ? fullContent : summaryContent;
            final isShowingSummary = !isExpanded && summaryContent != null;

            return Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          ticker,
                          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blue),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            sectionLabel,
                            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    if (filingInfo != null) ...[
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Text(
                            'Filed on ${filingInfo['filingDate'] ?? filingInfo['filing_date'] ?? 'N/A'}',
                            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                          ),
                          const Spacer(),
                          if (filingInfo['doc_url'] != null)
                            TextButton.icon(
                              onPressed: () => onLaunchLink(filingInfo['doc_url']),
                              icon: const Icon(Icons.open_in_new, size: 12),
                              label: const Text('Official Filing', style: TextStyle(fontSize: 12)),
                              style: TextButton.styleFrom(visualDensity: VisualDensity.compact),
                            ),
                        ],
                      ),
                    ],
                    const Divider(height: 16),
                    if (summaryContent != null || isLoadingSummary)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Row(
                          children: [
                            Icon(
                              isShowingSummary ? Icons.auto_awesome : Icons.description,
                              size: 16,
                              color: Colors.purple.shade700,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                isLoadingSummary 
                                  ? 'Generating AI Summary...' 
                                  : (isShowingSummary ? 'AI-Powered Summary' : 'Full Section Text'),
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.purple.shade700,
                                ),
                              ),
                            ),
                            TextButton.icon(
                              onPressed: isLoadingSummary ? null : () async {
                                if (isExpanded && summaryContent == null) {
                                   await onFetchSummary(ticker, reportType, sectionLabel, fullContent ?? '');
                                }
                                (context as Element).markNeedsBuild(); // Trigger rebuild for local state ref
                                // Since we use setState in parent for maps, it will rebuild anyway
                              },
                              icon: isLoadingSummary 
                                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                                : Icon(isShowingSummary ? Icons.expand : Icons.summarize, size: 16),
                              label: Text(isShowingSummary ? 'Full Text' : 'AI Summary'),
                              style: TextButton.styleFrom(
                                visualDensity: VisualDensity.compact,
                                foregroundColor: Colors.purple,
                              ),
                            ),
                          ],
                        ),
                      )
                    else
                      Align(
                        alignment: Alignment.centerRight,
                        child: TextButton.icon(
                          onPressed: () async {
                            await onFetchSummary(ticker, reportType, sectionLabel, fullContent ?? '');
                          },
                          icon: const Icon(Icons.summarize, size: 16),
                          label: const Text('Fetch AI Summary'),
                          style: TextButton.styleFrom(
                            visualDensity: VisualDensity.compact,
                            foregroundColor: Colors.purple,
                          ),
                        ),
                      ),
                    if (displayContent != null)
                      Expanded(
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.grey.shade50,
                            border: Border.all(color: Colors.grey.shade200),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: SingleChildScrollView(
                            child: MarkdownBody(
                              data: displayContent,
                              selectable: true,
                              styleSheet: MarkdownStyleSheet(
                                p: const TextStyle(fontSize: 13, color: Colors.black87, height: 1.4),
                              ),
                            ),
                          ),
                        ),
                      )
                    else
                      const Expanded(child: Center(child: Text('No content available'))),
                    const SizedBox(height: 8),
                    ElevatedButton.icon(
                      onPressed: displayContent == null ? null : () {
                        Clipboard.setData(ClipboardData(text: displayContent));
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Copied to clipboard'), duration: Duration(seconds: 1)),
                        );
                      },
                      icon: const Icon(Icons.copy, size: 14),
                      label: const Text('Copy', style: TextStyle(fontSize: 12)),
                      style: ElevatedButton.styleFrom(visualDensity: VisualDensity.compact),
                    ),
                  ],
                ),
              ),
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => Center(child: Text('Error: $e')),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Error: $e')),
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
    final response = await apiClient.get('/financial/sec/$ticker/10k', queryParameters: {'summarize': 'false'});
    return response.data as Map<String, dynamic>;
  },
);

final _sec10QProvider = FutureProvider.family<Map<String, dynamic>, String>(
  (ref, ticker) async {
    final apiClient = ref.watch(apiClientProvider);
    final response = await apiClient.get('/financial/sec/$ticker/10q', queryParameters: {'summarize': 'false'});
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
