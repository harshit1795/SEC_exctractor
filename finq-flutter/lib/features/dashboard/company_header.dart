import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class CompanyHeader extends ConsumerWidget {
  const CompanyHeader({
    super.key,
    required this.tickerData,
  });

  final AsyncValue<Map<String, dynamic>> tickerData;

  String _getLogoUrl(String ticker) {
    return 'https://logo.clearbit.com/${_getCompanyDomain(ticker)}';
  }

  String _getCompanyDomain(String ticker) {
    // Common ticker to domain mappings
    const Map<String, String> domainMap = {
      'AAPL': 'apple.com',
      'MSFT': 'microsoft.com',
      'GOOGL': 'google.com',
      'GOOG': 'google.com',
      'AMZN': 'amazon.com',
      'META': 'meta.com',
      'TSLA': 'tesla.com',
      'NVDA': 'nvidia.com',
      'JPM': 'jpmorganchase.com',
      'V': 'visa.com',
      'WMT': 'walmart.com',
      'DIS': 'disney.com',
      'NFLX': 'netflix.com',
      'INTC': 'intel.com',
      'AMD': 'amd.com',
      'CSCO': 'cisco.com',
      'ORCL': 'oracle.com',
      'IBM': 'ibm.com',
      'CRM': 'salesforce.com',
      'ADBE': 'adobe.com',
    };
    
    return domainMap[ticker.toUpperCase()] ?? '${ticker.toLowerCase()}.com';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return tickerData.when(
      data: (data) {
        final info = data['info'] as Map<String, dynamic>? ?? {};
        final ticker = data['ticker'] as String? ?? '';
        final companyName = info['longName'] ?? info['shortName'] ?? ticker;
        final sector = info['sector'] ?? 'N/A';
        final industry = info['industry'] ?? 'N/A';
        final logoUrl = _getLogoUrl(ticker);

        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                spreadRadius: 1,
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                // Company Logo
                ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Image.network(
                    logoUrl,
                    width: 80,
                    height: 80,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          color: Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Center(
                          child: Text(
                            ticker.isNotEmpty ? ticker[0].toUpperCase() : '?',
                            style: TextStyle(
                              fontSize: 36,
                              fontWeight: FontWeight.bold,
                              color: Colors.blue.shade700,
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(width: 16),
                // Company Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '$ticker – $companyName',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Sector: $sector • Industry: $industry',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
      loading: () => Container(
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.1),
              spreadRadius: 1,
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: const Padding(
          padding: EdgeInsets.all(16),
          child: Row(
            children: [
              SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
              SizedBox(width: 12),
              Text(
                'Loading company info...',
                style: TextStyle(fontSize: 14, color: Colors.black54),
              ),
            ],
          ),
        ),
      ),
      error: (error, _) => Container(
        margin: const EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          color: Colors.red.shade50,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.red.shade200),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(Icons.error_outline, color: Colors.red.shade700),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Failed to load company information',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.red.shade700,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
