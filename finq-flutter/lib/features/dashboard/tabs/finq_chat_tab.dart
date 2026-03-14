import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;

import '../../../core/api/api_client.dart';
import '../../../core/di/providers.dart';
import '../../../models/chat.dart' as model;
import '../widgets/tab_description_tooltip.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class FinQChatTab extends ConsumerStatefulWidget {
  const FinQChatTab({
    required this.ticker,
    super.key,
  });

  final String ticker;

  @override
  ConsumerState<FinQChatTab> createState() => _FinQChatTabState();
}

class _FinQChatTabState extends ConsumerState<FinQChatTab> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();
  
  List<model.ChatMessage> _messages = [];
  String? _currentSessionId;
  List<model.ChatSession> _sessionHistory = [];
  
  Map<String, dynamic> _contextData = {};
  String? _pendingPromptAfterKey; // stores prompt to retry after BYOK save
  
  var _isLoading = false;
  var _isFetchingHistory = false;

  @override
  void initState() {
    super.initState();
    _contextData = {
      'selected_tickers': [widget.ticker],
    };
    _fetchSessions();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _fetchSessions() async {
    setState(() => _isFetchingHistory = true);
    try {
      final apiClient = ref.read(apiClientProvider);
      // Hardcoded user ID 'anonymous' as used in other parts of the app for now
      final response = await apiClient.get('/chat/sessions?user_id=anonymous');
      
      if (response.data is List) {
        final sessions = (response.data as List)
            .map((s) => model.ChatSession.fromJson(s as Map<String, dynamic>))
            .toList();
            
        // Filter sessions by the current ticker just to keep context relevant
        _sessionHistory = sessions.where((s) {
          final tickers = s.contextData?['selected_tickers'] as List<dynamic>?;
          return tickers != null && tickers.contains(widget.ticker);
        }).toList();
        
        // If we found a recent session, load it
        if (_sessionHistory.isNotEmpty) {
          _loadSession(_sessionHistory.first.id);
        } else {
          // Initialize empty
          _messages = [
            model.ChatMessage(
              id: 'welcome',
              sessionId: '',
              role: 'model',
              content: 'Hi! I\'m FinQ, your AI financial analyst. How can I help you analyze ${widget.ticker} today?',
              createdAt: DateTime.now(),
            )
          ];
        }
      }
    } catch (e) {
      debugPrint('Error fetching sessions: $e');
    } finally {
      if (mounted) setState(() => _isFetchingHistory = false);
    }
  }

  Future<void> _loadSession(String sessionId) async {
    setState(() => _isFetchingHistory = true);
    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.get('/chat/sessions/$sessionId');
      
      if (response.data is Map<String, dynamic>) {
        final detail = model.ChatSessionDetail.fromJson(response.data as Map<String, dynamic>);
        setState(() {
          _currentSessionId = detail.id;
          _messages = detail.messages;
          _contextData = detail.contextData ?? {'selected_tickers': [widget.ticker]};
        });
        _scrollToBottom();
      }
    } catch (e) {
      debugPrint('Error loading session: $e');
    } finally {
      if (mounted) setState(() => _isFetchingHistory = false);
    }
  }

  void _createNewSession() {
    setState(() {
      _currentSessionId = null;
      _messages = [
        model.ChatMessage(
          id: 'welcome',
          sessionId: '',
          role: 'model',
          content: 'Hi! I\'m FinQ. Let\'s start a new analysis for ${widget.ticker}.',
          createdAt: DateTime.now(),
        )
      ];
      _contextData = {'selected_tickers': [widget.ticker]};
    });
  }

  Future<void> _sendMessage() async {
    final messageText = _messageController.text.trim();
    if (messageText.isEmpty || _isLoading) return;

    setState(() {
      _messages.add(model.ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        sessionId: _currentSessionId ?? '',
        role: 'user',
        content: messageText,
        createdAt: DateTime.now(),
      ));
      _isLoading = true;
    });

    _messageController.clear();
    _scrollToBottom();

    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.post(
        '/chat/analyze',
        body: {
          'session_id': _currentSessionId,
          'prompt': messageText,
          'context_data': _contextData,
        },
      );

      if (response.data is Map<String, dynamic>) {
        final data = response.data as Map<String, dynamic>;
        final analysis = data['response'] ?? 'No response received';
        final returnedSessionId = data['session_id'];
        
        setState(() {
          _currentSessionId = returnedSessionId;
          _messages.add(model.ChatMessage(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            sessionId: returnedSessionId,
            role: 'model',
            content: analysis,
            createdAt: DateTime.now(),
          ));
          _isLoading = false;
        });
        
        // Refresh session history in background
        _fetchSessions();
      }
    } catch (e) {
      final eStr = e.toString();
      final isQuotaError = eStr.contains('503') || eStr.contains('quota') ||
          eStr.contains('429') || eStr.contains('Service Unavailable');

      if (isQuotaError && mounted) {
        // Remove the "thinking..." state first
        setState(() { _isLoading = false; });
        // Show BYOK dialog with retry
        await _showApiKeyQuotaDialog(pendingPrompt: messageText);
        return;
      }

      String errorMsg;
      if (eStr.contains('timeout') || eStr.contains('SocketException')) {
        errorMsg = '🌐 Connection timeout. The backend server may be starting up. Please try again in a moment.';
      } else if (eStr.contains('401') || eStr.contains('403')) {
        errorMsg = '🔑 Authentication failed. Please check your Gemini API key in Settings.';
      } else {
        errorMsg = '❌ Something went wrong. Please try again.';
      }
      setState(() {
        _messages.add(model.ChatMessage(
          id: 'error_${DateTime.now().millisecondsSinceEpoch}',
          sessionId: _currentSessionId ?? '',
          role: 'model',
          content: errorMsg,
          metadata: {'is_error': true},
          createdAt: DateTime.now(),
        ));
        _isLoading = false;
      });
    }

    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  /// Shows a dialog prompting the user to enter their Gemini API key (BYOK)
  /// when the backend quota is exhausted. Saves the key and optionally retries
  /// the [pendingPrompt] after saving.
  Future<void> _showApiKeyQuotaDialog({String? pendingPrompt}) async {
    final keyController = TextEditingController();
    bool _obscure = true;

    final saved = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => Dialog(
          backgroundColor: Colors.transparent,
          child: Container(
            width: 480,
            constraints: const BoxConstraints(maxWidth: 480),
            decoration: BoxDecoration(
              color: const Color(0xFF1A1A2E),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.blue.shade900, width: 1),
              boxShadow: [
                BoxShadow(
                  color: Colors.blue.withOpacity(0.15),
                  blurRadius: 40,
                  spreadRadius: 5,
                )
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.all(28),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.orange.shade900.withOpacity(0.3),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Icon(Icons.key_rounded, color: Colors.orange.shade300, size: 22),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'API Quota Exceeded',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 17,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'Provide your own Gemini key to continue',
                              style: TextStyle(color: Colors.white54, fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white38, size: 18),
                        onPressed: () => Navigator.of(ctx).pop(false),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),

                  // Explanation
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Colors.orange.withOpacity(0.07),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.orange.withOpacity(0.2)),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(Icons.info_outline, color: Colors.orange.shade300, size: 16),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            'The default Gemini API key has hit its free-tier daily request limit. Enter your own key from Google AI Studio to keep using FinQ AI without interruption — all at the same quality.',
                            style: TextStyle(color: Colors.white70, fontSize: 13, height: 1.5),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // API Key field
                  TextField(
                    controller: keyController,
                    obscureText: _obscure,
                    style: const TextStyle(color: Colors.white, fontSize: 14),
                    decoration: InputDecoration(
                      labelText: 'Gemini API Key',
                      labelStyle: TextStyle(color: Colors.blue.shade300),
                      hintText: 'AIzaSy...',
                      hintStyle: const TextStyle(color: Colors.white24),
                      filled: true,
                      fillColor: Colors.white.withOpacity(0.05),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: BorderSide(color: Colors.blue.shade800),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: BorderSide(color: Colors.blue.shade900),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: BorderSide(color: Colors.blue.shade400),
                      ),
                      suffixIcon: IconButton(
                        icon: Icon(
                          _obscure ? Icons.visibility_off : Icons.visibility,
                          color: Colors.white38,
                          size: 18,
                        ),
                        onPressed: () => setDialogState(() => _obscure = !_obscure),
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  GestureDetector(
                    onTap: () => html.window.open('https://aistudio.google.com/apikey', '_blank'),
                    child: Text(
                      '🔗 Get a free key at aistudio.google.com/apikey',
                      style: TextStyle(
                        color: Colors.blue.shade400,
                        fontSize: 12,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Action buttons
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton(
                        onPressed: () => Navigator.of(ctx).pop(false),
                        style: TextButton.styleFrom(foregroundColor: Colors.white38),
                        child: const Text('Cancel'),
                      ),
                      const SizedBox(width: 12),
                      ElevatedButton.icon(
                        onPressed: () async {
                          final key = keyController.text.trim();
                          if (key.isNotEmpty) {
                            // Save INSIDE the dialog before closing so
                            // Riverpod rebuilds apiClientProvider before retry
                            ref.read(geminiApiKeyProvider.notifier).state = key;
                            final prefs = ref.read(sharedPreferencesProvider);
                            await prefs.setString('gemini_api_key', key);
                            if (ctx.mounted) Navigator.of(ctx).pop(true);
                          }
                        },
                        icon: const Icon(Icons.check_circle_outline, size: 16),
                        label: const Text('Save & Retry'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue.shade700,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );

    if (saved == true && keyController.text.trim().isNotEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('✅ API key saved — retrying your request...'),
            backgroundColor: Colors.green.shade800,
            duration: const Duration(seconds: 2),
          ),
        );
        // Wait two frames for Riverpod to propagate the new key
        // through apiClientProvider before retrying
        await Future.delayed(const Duration(milliseconds: 800));
        if (mounted && pendingPrompt != null && pendingPrompt.isNotEmpty) {
          _messageController.text = pendingPrompt;
          _sendMessage();
        }
      }
    }
  }
  
  void _showContextAttachmentSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Attach Context Data',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              Text(
                'Include specific dashboard elements to help FinQ better understand your questions.',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey.shade600),
              ),
              const SizedBox(height: 24),
              // Checklist for context
              StatefulBuilder(builder: (context, setModalState) {
                return Column(
                  children: [
                    CheckboxListTile(
                      title: const Text('Fundamental Financials (Income, Balance, Cash Flow)'),
                      value: _contextData.containsKey('include_financials') ? _contextData['include_financials'] : false,
                      onChanged: (val) {
                        setModalState(() {
                          _contextData['include_financials'] = val;
                        });
                        setState(() {});
                      },
                    ),
                    CheckboxListTile(
                      title: const Text('Latest SEC Filings Overview'),
                      value: _contextData.containsKey('include_sec') ? _contextData['include_sec'] : false,
                      onChanged: (val) {
                        setModalState(() {
                          _contextData['include_sec'] = val;
                        });
                        setState(() {});
                      },
                    ),
                    CheckboxListTile(
                      title: const Text('Macroeconomic Indicators'),
                      value: _contextData.containsKey('include_macro') ? _contextData['include_macro'] : false,
                      onChanged: (val) {
                        setModalState(() {
                          _contextData['include_macro'] = val;
                        });
                        setState(() {});
                      },
                    ),
                  ],
                );
              }),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text('Apply Context'),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  void _showHistorySheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Recent Chat Sessions',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  TextButton.icon(
                    onPressed: () {
                      Navigator.pop(ctx);
                      _createNewSession();
                    },
                    icon: const Icon(Icons.add),
                    label: const Text('New Chat'),
                  )
                ],
              ),
              const Divider(),
              Expanded(
                child: _sessionHistory.isEmpty
                    ? const Center(child: Text('No previous sessions for this ticker.'))
                    : ListView.builder(
                        itemCount: _sessionHistory.length,
                        itemBuilder: (context, index) {
                          final session = _sessionHistory[index];
                          final isSelected = session.id == _currentSessionId;
                          return ListTile(
                            leading: Icon(
                              Icons.chat_bubble_outline,
                              color: isSelected ? Colors.blue.shade600 : Colors.grey.shade500,
                            ),
                            title: Text(
                              session.title,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                              ),
                            ),
                            subtitle: Text(_formatDate(session.updatedAt)),
                            selected: isSelected,
                            onTap: () {
                              Navigator.pop(ctx);
                              _loadSession(session.id);
                            },
                          );
                        },
                      ),
              )
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Tab Header
        Padding(
          padding: const EdgeInsets.only(left: 4, top: 8, bottom: 8, right: 8),
          child: Row(
            children: [
              Text(
                'FinQ AI Assistant',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
              const SizedBox(width: 8),
              const TabDescriptionTooltip(tabId: 'bot'),
              const Spacer(),
              if (_isFetchingHistory)
                const SizedBox(
                  width: 16, height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              else
                IconButton(
                  icon: const Icon(Icons.history, color: Colors.blueGrey),
                  tooltip: 'Chat History',
                  onPressed: _showHistorySheet,
                ),
            ],
          ),
        ),
        
        // Chat Area
        Expanded(
          child: _messages.length <= 1
              ? _buildWelcomeScreen()
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final message = _messages[index];
                    return _buildMessageBubble(message);
                  },
                ),
        ),
        
        // Quick Actions (only show at start or immediately after welcome msg)
        if (_messages.length <= 2 && !_isLoading)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildSuggestionChip('Scan latest SEC filings'),
                  const SizedBox(width: 8),
                  _buildSuggestionChip('Summarize profitability'),
                  const SizedBox(width: 8),
                  _buildSuggestionChip('Are there macro risks?'),
                  const SizedBox(width: 8),
                  _buildSuggestionChip('What can FinQ do?'),
                ],
              ),
            ),
          ),
          
        // Thinking Indicator
        if (_isLoading)
          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              children: [
                const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
                const SizedBox(width: 12),
                Text(
                  'FinQ is analyzing databases...',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
          
        // Input Area
        Builder(builder: (context) {
          final isDark = Theme.of(context).brightness == Brightness.dark;
          final colorScheme = Theme.of(context).colorScheme;
          return Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isDark ? const Color(0xFF1E1E2E) : Colors.white,
            border: Border(top: BorderSide(
              color: isDark ? Colors.white.withOpacity(0.08) : Colors.grey.shade200,
              width: 1,
            )),
            boxShadow: isDark ? [] : [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, -2),
              ),
            ],
          ),
          child: Row(
            children: [
              // Context Attachment Button
              Container(
                decoration: BoxDecoration(
                  color: isDark ? colorScheme.primary.withOpacity(0.15) : Colors.blue.shade50,
                  shape: BoxShape.circle,
                ),
                child: IconButton(
                  icon: Icon(Icons.add, color: Colors.blue.shade600),
                  tooltip: 'Attach Dashboard Context',
                  onPressed: _isLoading ? null : _showContextAttachmentSheet,
                ),
              ),
              const SizedBox(width: 12),
              // Text Field
              Expanded(
                child: TextField(
                  controller: _messageController,
                  style: TextStyle(color: isDark ? Colors.white : Colors.black87),
                  decoration: InputDecoration(
                    hintText: 'Ask a question about ${widget.ticker}...',
                    hintStyle: TextStyle(color: isDark ? Colors.white38 : Colors.grey.shade500),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(24),
                      borderSide: BorderSide.none,
                    ),
                    filled: true,
                    fillColor: isDark ? Colors.white.withOpacity(0.07) : Colors.grey.shade100,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 12,
                    ),
                  ),
                  enabled: !_isLoading,
                  onSubmitted: (_) => _sendMessage(),
                  textInputAction: TextInputAction.send,
                ),
              ),
              const SizedBox(width: 12),
              Container(
                decoration: BoxDecoration(
                  color: _isLoading || _messageController.text.trim().isEmpty 
                      ? (isDark ? Colors.white12 : Colors.grey.shade300)
                      : Colors.blue.shade600,
                  shape: BoxShape.circle,
                ),
                child: IconButton(
                  color: Colors.white,
                  icon: const Icon(Icons.arrow_upward),
                  onPressed: _isLoading ? null : _sendMessage,
                ),
              ),
            ],
          ),
        );
        }),
      ],
    );
  }

  Widget _buildWelcomeScreen() {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Center(
      child: Card(
        margin: const EdgeInsets.all(32),
        elevation: 0,
        color: isDark
            ? Colors.blue.shade900.withOpacity(0.25)
            : Colors.blue.shade50.withOpacity(0.5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: isDark ? Colors.white.withOpacity(0.08) : Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.blue.withOpacity(0.1),
                      blurRadius: 20,
                      spreadRadius: 5,
                    )
                  ]
                ),
                child: Icon(
                  Icons.auto_awesome,
                  size: 48,
                  color: Colors.blue.shade600,
                ),
              ),
              const SizedBox(height: 24),
              Text(
                'FinQ Agent',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: isDark ? Colors.blue.shade300 : Colors.blue.shade900,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'I can autonomously use the + attached context and external financial APIs to deeply analyze ${widget.ticker}.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: isDark ? Colors.blue.shade400 : Colors.blue.shade700,
                  height: 1.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSuggestionChip(String text) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return ActionChip(
      backgroundColor: isDark ? Colors.white.withOpacity(0.06) : Colors.white,
      side: BorderSide(color: isDark ? Colors.blue.shade700 : Colors.blue.shade200),
      label: Text(text, style: TextStyle(fontSize: 13, color: isDark ? Colors.blue.shade300 : Colors.blue.shade700)),
      onPressed: () {
        _messageController.text = text;
        _sendMessage();
      },
    );
  }

  Widget _buildMessageBubble(model.ChatMessage message) {
    bool isUser = message.role == 'user';
    bool isError = message.metadata?['is_error'] == true;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    final aiBubbleColor = isDark ? const Color(0xFF2A2A3E) : Colors.white;
    final aiBorderColor = isDark ? Colors.white.withOpacity(0.07) : Colors.grey.shade200;
    final aiTextColor = isDark ? Colors.white.withOpacity(0.87) : Colors.black87;
    
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.8,
        ),
        decoration: BoxDecoration(
          color: isError
              ? (isDark ? Colors.red.shade900.withOpacity(0.4) : Colors.red.shade50)
              : isUser
                  ? Colors.blue.shade600
                  : aiBubbleColor,
          borderRadius: BorderRadius.circular(20).copyWith(
            bottomLeft: isUser ? const Radius.circular(20) : Radius.zero,
            bottomRight: isUser ? Radius.zero : const Radius.circular(20),
          ),
          border: isUser ? null : Border.all(color: aiBorderColor),
          boxShadow: isUser ? [
            BoxShadow(
              color: Colors.blue.withOpacity(0.2),
              blurRadius: 8,
              offset: const Offset(0, 4),
            )
          ] : [
            BoxShadow(
              color: Colors.black.withOpacity(isDark ? 0.15 : 0.02),
              blurRadius: 5,
              offset: const Offset(0, 2),
            )
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (!isUser)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.auto_awesome,
                      size: 16,
                      color: isError ? Colors.red : Colors.blue.shade600,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'FinQ Agent',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: isError ? Colors.red : Colors.blue.shade800,
                      ),
                    ),
                  ],
                ),
              ),
              
            // Use Markdown for assistant messages, normal Text for user
            isUser ? Text(
              message.content,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 15,
                height: 1.4,
              ),
            ) : MarkdownBody(
              data: message.content,
              styleSheet: MarkdownStyleSheet(
                p: TextStyle(color: aiTextColor, fontSize: 15, height: 1.5),
                h1: TextStyle(color: aiTextColor, fontSize: 18, fontWeight: FontWeight.bold),
                h2: TextStyle(color: aiTextColor, fontSize: 17, fontWeight: FontWeight.bold),
                h3: TextStyle(color: aiTextColor, fontSize: 16, fontWeight: FontWeight.bold),
                listBullet: TextStyle(color: aiTextColor),
                code: TextStyle(
                  color: isDark ? Colors.green.shade300 : Colors.green.shade800,
                  backgroundColor: isDark ? Colors.black26 : Colors.grey.shade100,
                  fontSize: 13,
                ),
                blockquoteDecoration: BoxDecoration(
                  border: Border(left: BorderSide(color: Colors.blue.shade300, width: 3)),
                  color: isDark ? Colors.white.withOpacity(0.04) : Colors.blue.shade50,
                ),
              ),
            ),
            
            const SizedBox(height: 6),
            Align(
              alignment: Alignment.centerRight,
              child: Text(
                _formatTime(message.createdAt),
                style: TextStyle(
                  fontSize: 11,
                  color: isUser
                      ? Colors.white.withOpacity(0.7)
                      : Colors.grey.shade500,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);

    if (difference.inSeconds < 60) return 'Just now';
    if (difference.inMinutes < 60) return '${difference.inMinutes}m ago';
    if (difference.inHours < 24) return '${difference.inHours}h ago';
    return '${time.hour}:${time.minute.toString().padLeft(2, '0')}';
  }
  
  String _formatDate(DateTime date) {
    final now = DateTime.now();
    if (now.year == date.year && now.month == date.month && now.day == date.day) {
      return 'Today at ${_formatTime(date)}';
    }
    return '${date.month}/${date.day}/${date.year}';
  }
}
