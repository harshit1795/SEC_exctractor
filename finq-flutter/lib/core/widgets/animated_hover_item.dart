import 'package:flutter/material.dart';

class AnimatedHoverItem extends StatefulWidget {
  const AnimatedHoverItem({
    super.key,
    required this.child,
    this.hoverColor,
    this.borderRadius,
    this.padding,
    this.onTap,
  });

  final Widget child;
  final Color? hoverColor;
  final BorderRadiusGeometry? borderRadius;
  final EdgeInsetsGeometry? padding;
  final VoidCallback? onTap;

  @override
  State<AnimatedHoverItem> createState() => _AnimatedHoverItemState();
}

class _AnimatedHoverItemState extends State<AnimatedHoverItem> {
  bool _isHovering = false;

  @override
  Widget build(BuildContext context) {
    final defaultHoverColor = Theme.of(context).primaryColor.withOpacity(0.05);

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovering = true),
      onExit: (_) => setState(() => _isHovering = false),
      cursor: widget.onTap != null ? SystemMouseCursors.click : SystemMouseCursors.basic,
      child: GestureDetector(
        onTap: widget.onTap,
        behavior: HitTestBehavior.opaque,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeInOut,
          padding: widget.padding ?? EdgeInsets.zero,
          decoration: BoxDecoration(
            color: _isHovering ? (widget.hoverColor ?? defaultHoverColor) : Colors.transparent,
            borderRadius: widget.borderRadius ?? BorderRadius.circular(4),
          ),
          child: widget.child,
        ),
      ),
    );
  }
}
