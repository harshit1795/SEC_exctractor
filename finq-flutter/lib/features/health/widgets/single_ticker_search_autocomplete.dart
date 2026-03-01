import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/widgets/animated_hover_item.dart';
import '../../dashboard/dashboard_providers.dart';

class SingleTickerSearchAutocomplete extends ConsumerStatefulWidget {
  final String initialValue;
  final ValueChanged<String> onSelected;

  const SingleTickerSearchAutocomplete({
    super.key,
    required this.onSelected,
    this.initialValue = '',
  });

  @override
  ConsumerState<SingleTickerSearchAutocomplete> createState() => _SingleTickerSearchAutocompleteState();
}

class _SingleTickerSearchAutocompleteState extends ConsumerState<SingleTickerSearchAutocomplete> {
  late final TextEditingController _controller;
  final _focusNode = FocusNode();
  Timer? _debounce;
  List<Map<String, dynamic>> _options = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.initialValue);
  }

  @override
  void dispose() {
    _debounce?.cancel();
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
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _options = [];
          _isLoading = false;
        });
      }
    }
  }

  void _selectTicker(String ticker) {
    widget.onSelected(ticker);
    _controller.text = ticker;
    setState(() => _options = []);
    _focusNode.unfocus();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.shade300),
          ),
          child: Column(
            children: [
              Row(
                children: [
                  const SizedBox(width: 16),
                  const Icon(Icons.search, color: Colors.grey),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      focusNode: _focusNode,
                      decoration: const InputDecoration(
                        border: InputBorder.none,
                        hintText: 'Search Ticker or Company Name',
                        contentPadding: EdgeInsets.symmetric(vertical: 14),
                      ),
                      textCapitalization: TextCapitalization.characters,
                      onChanged: _onSearchChanged,
                      onSubmitted: (val) {
                        if (val.trim().isEmpty) return;
                        if (_options.isNotEmpty) {
                          final firstOption = _options.first;
                          _selectTicker(firstOption['ticker'] as String);
                        } else {
                          _selectTicker(val.trim().toUpperCase());
                        }
                      },
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
              if (_options.isNotEmpty)
                Container(
                  constraints: const BoxConstraints(maxHeight: 200),
                  decoration: BoxDecoration(
                    border: Border(top: BorderSide(color: Colors.grey.shade200)),
                  ),
                  child: ListView.separated(
                    shrinkWrap: true,
                    itemCount: _options.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (context, index) {
                      final option = _options[index];
                      final ticker = option['ticker'] as String;
                      final name = option['name'] as String;
                      return AnimatedHoverItem(
                        onTap: () => _selectTicker(ticker),
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
            ],
          ),
        ),
      ],
    );
  }
}
