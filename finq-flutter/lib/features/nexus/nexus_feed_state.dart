class NexusFeedState {
  const NexusFeedState({
    required this.isConnected,
    required this.messages,
    this.error,
  });

  final bool isConnected;
  final List<NexusMessage> messages;
  final String? error;

  NexusFeedState copyWith({
    bool? isConnected,
    List<NexusMessage>? messages,
    String? error,
  }) {
    return NexusFeedState(
      isConnected: isConnected ?? this.isConnected,
      messages: messages ?? this.messages,
      error: error,
    );
  }
}

class NexusMessage {
  NexusMessage({
    required this.type,
    required this.payload,
    required this.receivedAt,
  });

  final String type;
  final Map<String, dynamic> payload;
  final DateTime receivedAt;
}
