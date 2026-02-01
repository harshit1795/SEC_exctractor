import 'package:flutter/material.dart';

class HealthPage extends StatelessWidget {
  const HealthPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const SafeArea(
      child: Center(
        child: Text(
          'Financial Health Module',
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}
