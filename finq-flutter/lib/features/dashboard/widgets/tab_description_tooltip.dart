import 'package:flutter/material.dart';
import '../../../data/tab_descriptions.dart';

/// A reusable widget that displays a tab description tooltip
class TabDescriptionTooltip extends StatelessWidget {
  const TabDescriptionTooltip({
    super.key,
    required this.tabId,
    this.iconSize = 20,
  });

  final String tabId;
  final double iconSize;

  void _showDescriptionDialog(BuildContext context) {
    final description = TabDescriptions.getDescription(tabId);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        title: Row(
          children: [
            Icon(
              Icons.help_outline,
              color: Colors.blue.shade700,
              size: 24,
            ),
            const SizedBox(width: 12),
            const Expanded(
              child: Text(
                'About This Tab',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
        content: ConstrainedBox(
          constraints: const BoxConstraints(
            maxWidth: 500,
            maxHeight: 400,
          ),
          child: SingleChildScrollView(
            child: Text(
              description,
              style: const TextStyle(
                fontSize: 14,
                height: 1.5,
                color: Colors.black87,
              ),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Got it'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Icon(
        Icons.help_outline,
        size: iconSize,
        color: Colors.blue.shade600,
      ),
      tooltip: 'Learn more about this tab',
      onPressed: () => _showDescriptionDialog(context),
      padding: EdgeInsets.zero,
      constraints: BoxConstraints(
        minWidth: iconSize + 8,
        minHeight: iconSize + 8,
      ),
    );
  }
}
