import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api/api_client.dart';
import '../../../core/di/providers.dart';

class DataPipelineButton extends ConsumerStatefulWidget {
  const DataPipelineButton({
    super.key,
    required this.ticker,
  });

  final String ticker;

  @override
  ConsumerState<DataPipelineButton> createState() => _DataPipelineButtonState();
}

class _DataPipelineButtonState extends ConsumerState<DataPipelineButton> {
  bool _isUpdating = false;

  Future<void> _updateData({bool updateAll = false}) async {
    setState(() => _isUpdating = true);

    try {
      final apiClient = ref.read(apiClientProvider);
      final endpoint = updateAll
          ? '/financial/pipeline/update-all'
          : '/financial/pipeline/update/${widget.ticker}';

      await apiClient.post(endpoint);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              updateAll
                  ? 'Data update started for all tickers'
                  : 'Data update started for ${widget.ticker}',
            ),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error updating data: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isUpdating = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<String>(
      tooltip: 'Data Pipeline Management',
      icon: _isUpdating
          ? const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.amber.shade100,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.amber.shade300),
              ),
              child: Icon(Icons.bolt, color: Colors.amber.shade800, size: 24),
            ),
      onSelected: (value) {
        if (value == 'current') {
          _updateData(updateAll: false);
        } else if (value == 'all') {
          _updateData(updateAll: true);
        }
      },
      itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
        PopupMenuItem<String>(
          value: 'current',
          enabled: widget.ticker.isNotEmpty,
          child: ListTile(
            leading: const Icon(Icons.refresh),
            title: Text('Update ${widget.ticker.isEmpty ? 'Current' : widget.ticker}'),
            contentPadding: EdgeInsets.zero,
            dense: true,
          ),
        ),
        const PopupMenuItem<String>(
          value: 'all',
          child: ListTile(
            leading: Icon(Icons.update),
            title: Text('Update All Tickers'),
            contentPadding: EdgeInsets.zero,
            dense: true,
          ),
        ),
        const PopupMenuDivider(),
        PopupMenuItem<String>(
          enabled: false,
          child: Text(
            'Premium Feature',
            style: TextStyle(
              fontSize: 10,
              color: Colors.amber.shade800,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }
}
