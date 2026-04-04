class ChatMessage {
  final String id;
  final String sessionId;
  final String role; // 'user' or 'model'
  final String content;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;

  ChatMessage({
    required this.id,
    required this.sessionId,
    required this.role,
    required this.content,
    this.metadata,
    required this.createdAt,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] as String? ?? '',
      sessionId: json['session_id'] as String? ?? '',
      role: json['role'] as String? ?? 'user',
      content: json['content'] as String? ?? '',
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'session_id': sessionId,
      'role': role,
      'content': content,
      'metadata': metadata,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

class ChatSession {
  final String id;
  final String userId;
  final String title;
  final Map<String, dynamic>? contextData;
  final DateTime createdAt;
  final DateTime updatedAt;

  ChatSession({
    required this.id,
    required this.userId,
    required this.title,
    this.contextData,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ChatSession.fromJson(Map<String, dynamic> json) {
    return ChatSession(
      id: json['id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      title: json['title'] as String? ?? 'Chat',
      contextData: json['context_data'] as Map<String, dynamic>?,
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : DateTime.now(),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at']) 
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'title': title,
      'context_data': contextData,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}

class ChatSessionDetail extends ChatSession {
  final List<ChatMessage> messages;

  ChatSessionDetail({
    required String id,
    required String userId,
    required String title,
    Map<String, dynamic>? contextData,
    required DateTime createdAt,
    required DateTime updatedAt,
    required this.messages,
  }) : super(
          id: id,
          userId: userId,
          title: title,
          contextData: contextData,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  factory ChatSessionDetail.fromJson(Map<String, dynamic> json) {
    var messagesList = json['messages'] as List<dynamic>? ?? [];
    List<ChatMessage> parsedMessages = messagesList
        .map((m) => ChatMessage.fromJson(m as Map<String, dynamic>))
        .toList();

    return ChatSessionDetail(
      id: json['id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      title: json['title'] as String? ?? 'Chat',
      contextData: json['context_data'] as Map<String, dynamic>?,
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at']) 
          : DateTime.now(),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at']) 
          : DateTime.now(),
      messages: parsedMessages,
    );
  }
}
