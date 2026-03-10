import 'package:flutter/material.dart';

/// A floating filter panel that collapses behind a funnel icon on narrow screens.
///
/// On wide screens (≥ [breakpoint] px), the filter content is shown directly
/// inside an elevated card. On narrow screens, a compact funnel-icon bar is
/// shown; tapping the icon expands / collapses the filter content with a smooth
/// animation.
class FloatingFilterPanel extends StatefulWidget {
  const FloatingFilterPanel({
    required this.child,
    this.title = 'Filters',
    this.breakpoint = 600,
    this.initiallyExpanded = false,
    super.key,
  });

  /// The filter content to show.
  final Widget child;

  /// Label shown next to the funnel icon on narrow screens.
  final String title;

  /// Width below which the panel collapses (default 600).
  final double breakpoint;

  /// Whether the panel starts expanded on narrow screens.
  final bool initiallyExpanded;

  @override
  State<FloatingFilterPanel> createState() => _FloatingFilterPanelState();
}

class _FloatingFilterPanelState extends State<FloatingFilterPanel>
    with SingleTickerProviderStateMixin {
  late bool _expanded;

  @override
  void initState() {
    super.initState();
    _expanded = widget.initiallyExpanded;
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isNarrow = constraints.maxWidth < widget.breakpoint;

        if (!isNarrow) {
          // Wide screen — show filter content in a floating card directly.
          return _buildFloatingCard(child: widget.child);
        }

        // Narrow screen — collapsible filter behind funnel icon.
        return _buildFloatingCard(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              InkWell(
                onTap: () => setState(() => _expanded = !_expanded),
                borderRadius: BorderRadius.circular(8),
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      Icon(
                        Icons.filter_alt_outlined,
                        size: 22,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        widget.title,
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                      ),
                      const Spacer(),
                      AnimatedRotation(
                        turns: _expanded ? 0.5 : 0,
                        duration: const Duration(milliseconds: 200),
                        child: Icon(
                          Icons.expand_more,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              AnimatedCrossFade(
                firstChild: const SizedBox.shrink(),
                secondChild: Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: widget.child,
                ),
                crossFadeState: _expanded
                    ? CrossFadeState.showSecond
                    : CrossFadeState.showFirst,
                duration: const Duration(milliseconds: 250),
                sizeCurve: Curves.easeInOut,
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildFloatingCard({required Widget child}) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: child,
      ),
    );
  }
}
