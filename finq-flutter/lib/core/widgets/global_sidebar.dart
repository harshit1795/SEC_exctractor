import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import '../../features/dashboard/dashboard_providers.dart';

class GlobalSidebar extends ConsumerWidget {
  const GlobalSidebar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {


    // Using a ScrollView to ensure it fits on smaller vertical screens
    return Container(
      width: 280,
      color: Colors.white,
      child: Column(
        children: [
          _buildHeader(context),
          const Divider(height: 1),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
              children: [
                _buildSectionLabel('NAVIGATION'),
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
          const Divider(height: 1),
          _buildFooter(),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 24.0),
      child: SvgPicture.asset(
        'assets/FinQLogoNew.svg',
        height: 50, // Adjusted height for the wide logo
        fit: BoxFit.contain,
      ),
    );
  }

  Widget _buildSectionLabel(String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, left: 12),
      child: Text(
        label,
        style: const TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: Colors.grey,
          letterSpacing: 1.0,
        ),
      ),
    );
  }



  Widget _buildFooter() {
    return Container(
      padding: const EdgeInsets.all(24),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: Colors.grey.shade200,
            child: const Icon(Icons.person, color: Colors.grey),
          ),
          const SizedBox(width: 12),
          const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('User', style: TextStyle(fontWeight: FontWeight.bold)),
              Text('Basic Plan', style: TextStyle(color: Colors.grey, fontSize: 12)),
            ],
          ),
        ],
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
    return Material(
      color: Colors.transparent,
      child: ListTile(
        leading: Icon(
          isActive ? activeIcon : icon,
          color: isActive ? const Color(0xFF2E7D32) : Colors.grey.shade700,
        ),
        title: Text(
          label,
          style: TextStyle(
            fontWeight: isActive ? FontWeight.bold : FontWeight.w500,
            color: isActive ? const Color(0xFF2E7D32) : Colors.black87,
          ),
        ),
        selected: isActive,
        selectedTileColor: const Color(0xFFE8F5E9),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        onTap: () => context.go(route),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      ),
    );
  }
}
