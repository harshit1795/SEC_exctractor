import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/di/providers.dart';
import 'package:equatable/equatable.dart';
import '../../../services/report_cache_service.dart';

class HealthScoreModel {
  final String ticker;
  final double? healthScore;
  
  // Base metrics
  final double? growth;
  final double? netMargin;
  final double? fcfMargin;
  final double? debtEquity;
  
  // Base metric scores (percentiles)
  final double? growthScore;
  final double? netMarginScore;
  final double? fcfMarginScore;
  final double? debtEquityScore;
  
  final String? insight;

  // Custom metrics dynamic data
  final Map<String, double> rawMetrics;
  final Map<String, double> metricScores;

  HealthScoreModel({
    required this.ticker,
    this.healthScore,
    this.growth,
    this.netMargin,
    this.fcfMargin,
    this.debtEquity,
    this.growthScore,
    this.netMarginScore,
    this.fcfMarginScore,
    this.debtEquityScore,
    this.insight,
    this.rawMetrics = const {},
    this.metricScores = const {},
  });

  factory HealthScoreModel.fromJson(Map<String, dynamic> json) {
    final rawMetrics = <String, double>{};
    final metricScores = <String, double>{};

    json.forEach((key, value) {
      if (value is num) {
        if (key.endsWith('_score')) {
          metricScores[key.replaceAll('_score', '')] = value.toDouble();
        } else if (key != 'healthScore') {
          rawMetrics[key] = value.toDouble();
        }
      }
    });

    // For backward compatibility, populate the old fields from the dynamic maps
    return HealthScoreModel(
      ticker: json['ticker'] as String,
      healthScore: (json['healthScore'] as num?)?.toDouble(),
      insight: json['insight'] as String?,
      
      // Populate standard metric fields from the maps for compatibility
      growth: rawMetrics['Growth'] ?? rawMetrics['Revenue Growth'],
      netMargin: rawMetrics['NetMargin'] ?? rawMetrics['Net Margin'],
      fcfMargin: rawMetrics['FCFMargin'] ?? rawMetrics['FCF Margin'],
      debtEquity: rawMetrics['DebtEquity'] ?? rawMetrics['Debt to Equity'],
      
      growthScore: metricScores['Growth'] ?? metricScores['Revenue Growth'],
      netMarginScore: metricScores['NetMargin'] ?? metricScores['Net Margin'],
      fcfMarginScore: metricScores['FCFMargin'] ?? metricScores['FCF Margin'],
      debtEquityScore: metricScores['DebtEquity'] ?? metricScores['Debt to Equity'],

      // Assign the full maps
      rawMetrics: rawMetrics,
      metricScores: metricScores,
    );
  }
}

class CustomHealthScoreParams extends Equatable {
  const CustomHealthScoreParams({
    this.ticker,
    this.category,
    required this.metrics,
    required this.weights,
  });

  final String? ticker;
  final String? category;
  final List<String> metrics;
  final List<double> weights;

  @override
  List<Object?> get props => [ticker, category, metrics, weights];
}

final finqHealthScoreProvider = FutureProvider.family<List<HealthScoreModel>?, String?>((ref, category) async {
  
  final apiClient = ref.watch(apiClientProvider);
  try {
    final queryParams = <String, dynamic>{'limit': 10};
    if (category != null && category.isNotEmpty) {
      queryParams['category'] = category;
    }

    final response = await apiClient.get<Map<String, dynamic>>(
      '/health-scores/finq',
      queryParameters: queryParams,
      forceRefresh: true,
    );
    
    if (response.statusCode == 200 && response.data['scores'] != null) {
      final scores = response.data['scores'] as List;
      return scores.map((json) => HealthScoreModel.fromJson(json as Map<String, dynamic>)).toList();
    }
  } catch (e, st) {
    print('Error fetching finq health scores for category $category: $e\n$st');
  }
  return null;
});

final customHealthScoreProvider = FutureProvider.family<List<HealthScoreModel>?, CustomHealthScoreParams>((ref, params) async {
  if (params.metrics.isEmpty) return null;
  if (params.ticker == null && params.category == null) return null;

  final apiClient = ref.watch(apiClientProvider);
  try {
    final queryParams = <String, dynamic>{
      'metrics': params.metrics.join(','),
      'weights': params.weights.join(','),
      'limit': 1,
    };
    if (params.ticker != null && params.ticker!.isNotEmpty) {
      queryParams['ticker'] = params.ticker;
    } else if (params.category != null && params.category!.isNotEmpty) {
      queryParams['category'] = params.category;
      queryParams['limit'] = 10;
    }

    final response = await apiClient.get<Map<String, dynamic>>(
      '/health-scores/custom',
      queryParameters: queryParams,
      forceRefresh: true,
    );
    
    if (response.statusCode == 200 && response.data['scores'] != null) {
      final scores = response.data['scores'] as List;
      return scores.map((json) => HealthScoreModel.fromJson(json as Map<String, dynamic>)).toList();
    }
  } catch (e, st) {
    print('Error fetching custom health scores: $e\n$st');
  }
  return null;
});

// Health Report Provider
final healthReportProvider = FutureProvider.family<String?, Map<String, dynamic>>((ref, payload) async {
  final apiClient = ref.watch(apiClientProvider);
  try {
    final ticker = payload['ticker'] as String?;
    final tickersList = ticker != null ? [ticker] : <String>[];
    
    if (tickersList.isNotEmpty) {
      final cachedHtml = await ReportCacheService.getCachedReport(tickersList);
      if (cachedHtml != null) {
        return cachedHtml;
      }
    }

    final response = await apiClient.post<Map<String, dynamic>>(
      '/health-scores/report',
      body: payload,
    );
    if (response.statusCode == 200 && response.data['report'] != null) {
      final html = response.data['report'] as String;
      if (tickersList.isNotEmpty) {
        await ReportCacheService.saveReport(tickersList, html);
      }
      return html;
    }
  } catch (e, st) {
    print('Error generating health report: $e\n$st');
  }
  return null;
});
