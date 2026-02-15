import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../../core/config/app_config.dart';
import 'nexus_feed_state.dart';

class NexusFeedController extends StateNotifier<NexusFeedState> {
  NexusFeedController({
    required String userId,
    required String baseUrl,
  })  : _userId = userId,
        _baseUrl = baseUrl,
        super(const NexusFeedState(isConnected: false, messages: []));

  final String _userId;
  final String _baseUrl;
  WebSocketChannel? _channel;

  Future<void> connect() async {
    if (_channel != null) {
      return;
    }

    final url = AppConfig.websocketUrl(
      baseUrl: _baseUrl,
      path: '/ws/feed',
      queryParameters: {'user_id': _userId},
    );

    try {
      _channel = WebSocketChannel.connect(Uri.parse(url));
      state = state.copyWith(isConnected: true, error: null);

      _channel!.stream.listen(
        (event) => _handleEvent(event),
        onError: (error) {
          state = state.copyWith(
            isConnected: false,
            error: error.toString(),
          );
          _channel = null;
        },
        onDone: () {
          state = state.copyWith(isConnected: false);
          _channel = null;
        },
      );
    } catch (error) {
      state = state.copyWith(
        isConnected: false,
        error: error.toString(),
      );
    }
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
    state = state.copyWith(isConnected: false);
  }

  void sendPing() {
    if (_channel == null) {
      return;
    }
    final payload = jsonEncode({
      'type': 'ping',
      'timestamp': DateTime.now().toIso8601String(),
    });
    _channel!.sink.add(payload);
  }

  void _handleEvent(dynamic event) {
    final payload = _parsePayload(event);
    final type = payload['type']?.toString() ?? 'message';
    final message = NexusMessage(
      type: type,
      payload: payload,
      receivedAt: DateTime.now(),
    );
    state = state.copyWith(
      messages: [message, ...state.messages].take(50).toList(),
      error: null,
    );
  }

  Map<String, dynamic> _parsePayload(dynamic event) {
    if (event is Map<String, dynamic>) {
      return event;
    }
    if (event is String) {
      try {
        final decoded = jsonDecode(event);
        if (decoded is Map<String, dynamic>) {
          return decoded;
        }
        if (decoded is Map) {
          return Map<String, dynamic>.from(decoded);
        }
      } catch (error) {
        debugPrint('WebSocket parse error: $error');
      }
      return {'type': 'raw', 'data': event};
    }
    return {'type': 'raw', 'data': event.toString()};
  }

  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }
}
