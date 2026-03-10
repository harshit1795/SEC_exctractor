import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:finq_flutter/app_shell.dart';
import 'package:finq_flutter/core/widgets/global_sidebar.dart';
import 'package:finq_flutter/core/di/providers.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  late SharedPreferences prefs;

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    prefs = await SharedPreferences.getInstance();
  });

  testWidgets('AppShell shows Sidebar on Desktop', (WidgetTester tester) async {
    // Set desktop size
    await tester.binding.setSurfaceSize(const Size(1200, 800));

    final router = GoRouter(
      initialLocation: '/',
      routes: [
        ShellRoute(
          builder: (context, state, child) => AppShell(location: state.uri.toString(), child: child),
          routes: [
            GoRoute(path: '/', builder: (context, state) => const Text('Content')),
          ],
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
        child: MaterialApp.router(
          routerConfig: router,
        ),
      ),
    );

    // Verify sidebar structure (logo is now an SVG, exact text 'FinQ' might be removed if it was part of header row text widget)
    // The previous implementation had Text('FinQ'). New implementation has SvgPicture.
    // The test didn't explicitly check for 'FinQ' text in the previous step, it just checked for GlobalSidebar widget.
    // So the existing test 'AppShell shows Sidebar on Desktop' specific checking for GlobalSidebar existence is likely fine.
    
    expect(find.byType(GlobalSidebar), findsOneWidget);
    expect(find.byType(Drawer), findsNothing);
    expect(find.byType(AppBar), findsNothing);
  });

  testWidgets('AppShell shows AppBar and Drawer on Mobile', (WidgetTester tester) async {
    // Set mobile size
    await tester.binding.setSurfaceSize(const Size(400, 800));

    final router = GoRouter(
      initialLocation: '/',
      routes: [
        ShellRoute(
          builder: (context, state, child) => AppShell(location: state.uri.toString(), child: child),
          routes: [
            GoRoute(path: '/', builder: (context, state) => const Text('Content')),
          ],
        ),
      ],
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(prefs),
        ],
        child: MaterialApp.router(
          routerConfig: router,
        ),
      ),
    );

    // Sidebar should NOT be visible initially (it's in drawer)
    expect(find.byType(GlobalSidebar), findsNothing);
    
    // AppBar should be visible
    expect(find.byType(AppBar), findsOneWidget);
    
    // Open drawer
    await tester.tap(find.byType(IconButton)); // Hamburger menu
    await tester.pumpAndSettle();

    // Now Sidebar should be visible
    expect(find.byType(GlobalSidebar), findsOneWidget);
  });
}
