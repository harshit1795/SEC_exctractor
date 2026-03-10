import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'core/widgets/global_sidebar.dart';

class AppShell extends StatelessWidget {
  const AppShell({
    super.key,
    required this.child,
    required this.location,
  });

  final Widget child;
  final String location;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isMobile = constraints.maxWidth < 900;

        if (isMobile) {
          return Scaffold(
            appBar: AppBar(
              title: const Text('FinQ', style: TextStyle(fontWeight: FontWeight.bold)),
              elevation: 0,
            ),
            drawer: const Drawer(
              child: GlobalSidebar(),
            ),
            body: child,
          );
        }

        return Scaffold(
          body: Row(
            children: [
              const GlobalSidebar(),
              const VerticalDivider(width: 1, thickness: 1),
              Expanded(child: child),
            ],
          ),
        );
      },
    );
  }
}
