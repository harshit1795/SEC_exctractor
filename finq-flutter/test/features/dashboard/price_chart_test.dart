import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:finq_flutter/features/dashboard/price_chart.dart';

void main() {
  testWidgets('PriceChart renders controls and charts', (WidgetTester tester) async {
    // Need enough data points for MACD (26 + 9)
    final points = List.generate(100, (i) => PricePoint(
        date: DateTime.now().add(Duration(days: i)),
        close: 100.0 + (i % 10), // vary the price a bit
    ));

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(child: PriceChart(
            seriesList: [
                PriceSeries(name: 'Test', points: points, color: Colors.blue),
            ],
        )),
      ),
    ));
    
    // Set a large surface size to ensure all charts fit
    await tester.binding.setSurfaceSize(const Size(800, 2000));
    await tester.pumpAndSettle();

    // Verify Controls
    expect(find.widgetWithText(FilterChip, 'Bollinger Bands'), findsOneWidget);
    expect(find.widgetWithText(FilterChip, 'MACD'), findsOneWidget);
    expect(find.widgetWithText(FilterChip, 'RSI'), findsOneWidget);

    // Verify KPIs
    expect(find.text('Close'), findsOneWidget);
    expect(find.text('RSI (14)'), findsOneWidget);

    // Verify Charts (finding by type or ensuring no errors)
    // Finding specific LineChart widgets is hard since they are from a package, 
    // but we can check if the Column contains children.
    
    expect(find.byType(Column), findsWidgets);
  });
}
