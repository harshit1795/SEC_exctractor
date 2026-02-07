import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:finq_flutter/features/dashboard/company_header.dart';
import 'package:finq_flutter/features/dashboard/dashboard_providers.dart';

void main() {
  testWidgets('CompanyHeader displays ticker info and logo from provider', (WidgetTester tester) async {
    const ticker = 'AAPL';
    final tickerData = {
      'ticker': ticker,
      'info': {
        'longName': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
      },
    };

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          logoUrlProvider(ticker).overrideWith((ref) => Future.value('https://assets.parqet.com/logos/symbol/AAPL?format=svg')),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: CompanyHeader(
              tickerData: AsyncValue.data(tickerData),
            ),
          ),
        ),
      ),
    );

    // Initial build
    await tester.pump();
    
    // Verify Company Name
    expect(find.text('AAPL – Apple Inc.'), findsOneWidget);

    // Verify Sector/Industry Chips
    expect(find.text('Technology'), findsOneWidget);
    expect(find.text('Consumer Electronics'), findsOneWidget);

    // Verify Logo
    // Handling async image loading in tests can be tricky. 
    // network image won't load in test environment by default without http overrides, 
    // but the widget tree should contain an Image widget with the URL.
    // However, since we mock the provider to return a URL, the widget will try to render Image.network.
    // We can rely on finding the Image widget or just ensuring no errors occur.
    
    // Check if SvgPicture is present
    final imageFinder = find.byType(SvgPicture);
    expect(imageFinder, findsOneWidget);
  });

  testWidgets('CompanyHeader displays fallback when logo is null', (WidgetTester tester) async {
    const ticker = 'MSFT';
    final tickerData = {
      'ticker': ticker,
      'info': {'longName': 'Microsoft'},
    };

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          logoUrlProvider(ticker).overrideWith((ref) => Future.value(null)),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: CompanyHeader(
              tickerData: AsyncValue.data(tickerData),
            ),
          ),
        ),
      ),
    );

    await tester.pump();
    
    // Should show fallback (First letter of ticker)
    expect(find.text('M'), findsOneWidget);
    expect(find.byType(Image), findsNothing);
  });
}
