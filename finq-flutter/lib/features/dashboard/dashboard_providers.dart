import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/di/providers.dart';
import 'dashboard_repository.dart';

final dashboardRepositoryProvider = Provider<DashboardRepository>((ref) {
  return DashboardRepository(ref.read(apiClientProvider));
});

final healthStatusProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.read(dashboardRepositoryProvider);
  return repository.fetchHealthStatus();
});
