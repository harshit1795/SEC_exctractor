import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import '../../features/auth/auth_providers.dart';

class GlobalSidebar extends ConsumerWidget {
  const GlobalSidebar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAsync = ref.watch(authUserProvider);
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      width: 280,
      color: colorScheme.surface,
      child: Column(
        children: [
          _buildHeader(context),
          Divider(height: 1, color: colorScheme.outlineVariant),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
              children: [
                _buildSectionLabel(context),
                _NavItem(
                  icon: Icons.dashboard_outlined,
                  activeIcon: Icons.dashboard,
                  label: 'Dashboard',
                  route: '/',
                  isActive: GoRouterState.of(context).uri.toString() == '/',
                ),
                _NavItem(
                  icon: Icons.people_outline,
                  activeIcon: Icons.people,
                  label: 'Nexus',
                  route: '/nexus',
                  isActive: GoRouterState.of(context).uri.toString().startsWith('/nexus'),
                ),
                _NavItem(
                  icon: Icons.health_and_safety_outlined,
                  activeIcon: Icons.health_and_safety,
                  label: 'Health',
                  route: '/health',
                  isActive: GoRouterState.of(context).uri.toString().startsWith('/health'),
                ),
                _NavItem(
                  icon: Icons.settings_outlined,
                  activeIcon: Icons.settings,
                  label: 'Settings',
                  route: '/settings',
                  isActive: GoRouterState.of(context).uri.toString().startsWith('/settings'),
                ),
              ],
            ),
          ),
          Divider(height: 1, color: colorScheme.outlineVariant),
          _buildFooter(context, userAsync),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 24.0),
      child: SvgPicture.asset(
        'assets/FinQLogoNew.svg',
        height: 80,
        fit: BoxFit.contain,
      ),
    );
  }

  Widget _buildSectionLabel(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, left: 12),
      child: Text(
        'NAVIGATION',
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: Theme.of(context).colorScheme.onSurfaceVariant,
          letterSpacing: 1.0,
        ),
      ),
    );
  }

  Widget _buildFooter(BuildContext context, AsyncValue userAsync) {
    final colorScheme = Theme.of(context).colorScheme;
    return userAsync.when(
      data: (user) {
        final displayName = user?.displayName ?? 'User';
        final email = user?.email ?? '';
        final photoUrl = user?.photoURL;

        return Container(
          padding: const EdgeInsets.all(24),
          child: Row(
            children: [
              if (photoUrl != null && photoUrl.isNotEmpty)
                CircleAvatar(
                  backgroundImage: NetworkImage(photoUrl),
                  backgroundColor: colorScheme.surfaceContainerHighest,
                  radius: 20,
                )
              else
                CircleAvatar(
                  backgroundColor: colorScheme.surfaceContainerHighest,
                  radius: 20,
                  child: Icon(Icons.person, color: colorScheme.onSurfaceVariant),
                ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      displayName,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (email.isNotEmpty)
                      Text(
                        email,
                        style: TextStyle(
                          color: colorScheme.onSurfaceVariant,
                          fontSize: 12,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
      loading: () => Container(
        padding: const EdgeInsets.all(24),
        child: const CircularProgressIndicator(strokeWidth: 2),
      ),
      error: (_, __) => Container(
        padding: const EdgeInsets.all(24),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: colorScheme.surfaceContainerHighest,
              child: Icon(Icons.person, color: colorScheme.onSurfaceVariant),
            ),
            const SizedBox(width: 12),
            const Text('User', style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  const _NavItem({
    required this.icon,
    required this.activeIcon,
    required this.label,
    required this.route,
    required this.isActive,
  });

  final IconData icon;
  final IconData activeIcon;
  final String label;
  final String route;
  final bool isActive;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Material(
      color: Colors.transparent,
      child: ListTile(
        leading: Icon(
          isActive ? activeIcon : icon,
          color: isActive ? colorScheme.primary : colorScheme.onSurfaceVariant,
        ),
        title: Text(
          label,
          style: TextStyle(
            fontWeight: isActive ? FontWeight.bold : FontWeight.w500,
            fontSize: isActive ? 15 : 14,
            color: isActive 
                ? (Theme.of(context).brightness == Brightness.dark 
                    ? colorScheme.primaryContainer.withAlpha(255) // Brighter in dark mode
                    : colorScheme.primary) 
                : colorScheme.onSurface,
          ),
        ),
        selected: isActive,
        selectedTileColor: colorScheme.primaryContainer.withOpacity(0.4),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        onTap: () => context.go(route),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      ),
    );
  }
}
