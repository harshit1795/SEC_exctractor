import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/widgets/animated_hover_item.dart';
import '../dashboard_providers.dart';

class TickerSearchAutocomplete extends ConsumerStatefulWidget {
  const TickerSearchAutocomplete({super.key});

  @override
  ConsumerState<TickerSearchAutocomplete> createState() => _TickerSearchAutocompleteState();
}

class _TickerSearchAutocompleteState extends ConsumerState<TickerSearchAutocomplete> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();
  final LayerLink _layerLink = LayerLink();
  OverlayEntry? _overlayEntry;
  
  Timer? _debounce;
  List<Map<String, dynamic>> _options = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _focusNode.addListener(() {
      if (!_focusNode.hasFocus) {
        Future.delayed(const Duration(milliseconds: 200), () {
          if (mounted) _hideOverlay();
        });
      } else if (_options.isNotEmpty) {
        _showOverlay();
      }
    });
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _hideOverlay();
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      if (query.isNotEmpty) {
        _search(query);
      } else {
        setState(() => _options = []);
        _hideOverlay();
      }
    });
  }

  Future<void> _search(String query) async {
    setState(() => _isLoading = true);
    try {
      final repository = ref.read(dashboardRepositoryProvider);
      final results = await repository.searchTickers(query);
      if (mounted) {
        setState(() {
          _options = results;
          _isLoading = false;
        });
        if (_options.isNotEmpty && _focusNode.hasFocus) {
          _showOverlay();
        } else {
          _hideOverlay();
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _options = [];
          _isLoading = false;
        });
        _hideOverlay();
      }
    }
  }

  void _onSubmitted(String query) {
    if (query.isEmpty) return;
    if (_options.isNotEmpty) {
      final firstOption = _options.first;
      _selectTicker(firstOption['ticker'] as String);
    } else {
      _selectTicker(query.toUpperCase());
    }
  }

  void _selectTicker(String ticker) {
    ref.read(selectedTickersProvider.notifier).addTicker(ticker);
    _controller.clear();
    setState(() => _options = []);
    _hideOverlay();
    _focusNode.unfocus();
  }

  void _showOverlay() {
    if (_overlayEntry != null) {
      _overlayEntry!.markNeedsBuild();
      return;
    }

    final RenderBox renderBox = context.findRenderObject() as RenderBox;
    final size = renderBox.size;

    _overlayEntry = OverlayEntry(
      builder: (context) {
        return Positioned(
          width: size.width,
          child: CompositedTransformFollower(
            link: _layerLink,
            showWhenUnlinked: false,
            offset: Offset(0.0, size.height + 4.0),
            child: Material(
              elevation: 4.0,
              borderRadius: BorderRadius.circular(8),
              color: Theme.of(context).colorScheme.surfaceContainerHigh,
              child: Container(
                constraints: const BoxConstraints(maxHeight: 300),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Theme.of(context).colorScheme.outline.withOpacity(0.4)),
                ),
                child: ListView.separated(
                  padding: EdgeInsets.zero,
                  shrinkWrap: true,
                  itemCount: _options.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final option = _options[index];
                    final ticker = option['ticker'] as String;
                    final name = option['name'] as String;
                    return AnimatedHoverItem(
                      onTap: () {
                        _selectTicker(ticker);
                      },
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(ticker, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                          const SizedBox(height: 4),
                          Text(
                            name,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ),
          ),
        );
      },
    );
    Overlay.of(context).insert(_overlayEntry!);
  }

  void _hideOverlay() {
    _overlayEntry?.remove();
    _overlayEntry = null;
  }

  @override
  Widget build(BuildContext context) {
    return CompositedTransformTarget(
      link: _layerLink,
      child: Container(
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerLow,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Theme.of(context).colorScheme.outline.withOpacity(0.4)),
        ),
        child: Row(
          children: [
            const SizedBox(width: 16),
            const Icon(Icons.search, color: Colors.grey),
            const SizedBox(width: 12),
            Expanded(
              child: TextField(
                controller: _controller,
                focusNode: _focusNode,
                textCapitalization: TextCapitalization.characters,
                decoration: const InputDecoration(
                  border: InputBorder.none,
                  hintText: 'Search Ticker or Company Name',
                  contentPadding: EdgeInsets.symmetric(vertical: 14),
                ),
                onChanged: _onSearchChanged,
                onSubmitted: _onSubmitted,
              ),
            ),
            if (_isLoading)
              const Padding(
                padding: EdgeInsets.only(right: 16),
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
