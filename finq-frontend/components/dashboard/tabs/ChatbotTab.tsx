'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useChatHistory, useAnalyzeFinancialData, useChatSessions } from '@/lib/hooks/useChat';
import { useAuth } from '@/lib/hooks/useAuth';
import { useFundamentals } from '@/lib/hooks/useTickerData';
import { useSecFilings, useSec10K, useSec10Q } from '@/lib/hooks/useSecData';
import { useFredData } from '@/lib/hooks/useFredData';
import { useAvailableTickers } from '@/lib/hooks/useTickerData';
import { Card } from '@/components/shared/Card';
import { Loading } from '@/components/shared/Loading';
import { ErrorDisplay } from '@/components/shared/ErrorDisplay';
import { MultiSelect } from '@/components/shared/MultiSelect';
import { format, formatDistanceToNow } from 'date-fns';

interface ChatbotTabProps {
  ticker: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatSession {
  session_id: string;
  last_message_at: string;
  message_count: number;
  summary?: string;
}

const METRIC_CATEGORIES = [
  'Income Statement',
  'Balance Sheet',
  'Cash Flow',
  'Stock Price & Volume',
  'Earnings & Estimates',
  'Valuation Metrics',
  'Technical Indicators',
];

const FRED_SERIES = ['GDP', 'UNRATE', 'CPIAUCSL', 'DGS10', 'FEDFUNDS'];

const PRE_GENERATED_PROMPTS = [
  {
    label: '📊 Company Overview',
    prompt: 'Provide a comprehensive overview of this company, including its business model, key financial metrics, and recent performance trends.',
  },
  {
    label: '📈 Revenue Analysis',
    prompt: 'Analyze the revenue trends, growth rates, and revenue breakdown by segment if available.',
  },
  {
    label: '💰 Profitability Analysis',
    prompt: 'Evaluate the company\'s profitability, including margins, net income trends, and return metrics.',
  },
  {
    label: '💵 Cash Flow Analysis',
    prompt: 'Analyze the company\'s cash flow, including operating, investing, and financing activities.',
  },
  {
    label: '📊 Balance Sheet Health',
    prompt: 'Assess the company\'s balance sheet strength, including debt levels, liquidity, and asset composition.',
  },
  {
    label: '🔍 Risk Assessment',
    prompt: 'Identify and analyze the key risks facing this company based on SEC filings and financial data.',
  },
  {
    label: '🌐 Market Context',
    prompt: 'Compare this company\'s performance with macroeconomic indicators and market trends.',
  },
  {
    label: '📉 Valuation Analysis',
    prompt: 'Evaluate the company\'s valuation metrics and compare them with industry benchmarks.',
  },
];

export function ChatbotTab({ ticker }: ChatbotTabProps) {
  const { user } = useAuth();
  const userId = user?.uid || 'anonymous';
  
  // Session management
  const [currentSessionId, setCurrentSessionId] = useState<string>(() => {
    // Load from localStorage or create new
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(`chat_session_${userId}`);
      return saved || `session_${Date.now()}`;
    }
    return `session_${Date.now()}`;
  });
  const [showSessions, setShowSessions] = useState(false);
  
  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  
  // Data source selections
  const [selectedTickers, setSelectedTickers] = useState<string[]>([ticker]);
  const [selectedMetricCategories, setSelectedMetricCategories] = useState<string[]>(['Income Statement', 'Balance Sheet']);
  const [selected10KSections, setSelected10KSections] = useState<string[]>(['business', 'risk', 'mda']);
  const [selected10QSections, setSelected10QSections] = useState<string[]>(['risk', 'mda']);
  const [selectedFredSeries, setSelectedFredSeries] = useState<string[]>(['GDP', 'UNRATE']);
  const [showDataSourceSelector, setShowDataSourceSelector] = useState(false);
  
  // Data loading states
  const [fundamentalsLoaded, setFundamentalsLoaded] = useState(false);
  const [sec10KLoaded, setSec10KLoaded] = useState(false);
  const [sec10QLoaded, setSec10QLoaded] = useState(false);
  const [fredDataLoaded, setFredDataLoaded] = useState(false);

  // Fetch sessions and history
  const { data: sessionsData, refetch: refetchSessions } = useChatSessions();
  const { data: chatHistory, refetch: refetchHistory } = useChatHistory(100, currentSessionId);
  const analyzeMutation = useAnalyzeFinancialData();
  const { data: availableTickers } = useAvailableTickers();
  const { data: fundamentalsData } = useFundamentals(ticker);
  const { data: secFilings } = useSecFilings(ticker);
  const { data: sec10K } = useSec10K(ticker, selected10KSections);
  const { data: sec10Q } = useSec10Q(ticker, selected10QSections);
  
  const endDate = format(new Date(), 'yyyy-MM-dd');
  const startDate = format(new Date(Date.now() - 365 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd');
  const { data: fredData } = useFredData(selectedFredSeries, startDate, endDate);

  // Save session to localStorage
  useEffect(() => {
    if (currentSessionId && typeof window !== 'undefined') {
      localStorage.setItem(`chat_session_${userId}`, currentSessionId);
    }
  }, [currentSessionId, userId]);

  // Load messages for current session
  useEffect(() => {
    if (chatHistory?.insights && Array.isArray(chatHistory.insights)) {
      const sessionMessages: Message[] = [];
      
      // Sort by created_at to maintain chronological order
      const sortedInsights = [...chatHistory.insights].sort((a, b) => {
        const dateA = new Date(a.created_at || 0).getTime();
        const dateB = new Date(b.created_at || 0).getTime();
        return dateA - dateB;
      });
      
      sortedInsights.forEach((item: any) => {
        const prompt = item.prompt || item.content?.prompt || '';
        const response = item.response || item.content?.response || item.answer || '';
        
        if (prompt) {
          sessionMessages.push({ role: 'user', content: prompt });
        }
        if (response) {
          sessionMessages.push({ role: 'assistant', content: response });
        }
      });
      
      setMessages(sessionMessages);
      setHistoryLoaded(true);
    } else if (!chatHistory) {
      // No history for this session
      setMessages([]);
      setHistoryLoaded(true);
    }
  }, [chatHistory, currentSessionId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Create new session
  const handleNewSession = useCallback(() => {
    const newSessionId = `session_${Date.now()}`;
    setCurrentSessionId(newSessionId);
    setMessages([]);
    setHistoryLoaded(false);
    refetchSessions();
  }, [refetchSessions]);

  // Switch to a different session
  const handleSwitchSession = useCallback((sessionId: string) => {
    setCurrentSessionId(sessionId);
    setMessages([]);
    setHistoryLoaded(false);
    setShowSessions(false);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Prevent duplicate submissions
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    const question = input;
    setInput('');
    setIsLoading(true); // Set loading immediately to prevent duplicate clicks

    try {
      // Build context data
      const contextData: any = {
        selected_tickers: selectedTickers,
        metric_categories: selectedMetricCategories,
      };

      // Add fundamentals data if loaded
      if (fundamentalsLoaded && fundamentalsData?.data) {
        contextData.fundamentals_data = fundamentalsData.data;
      }

      // Add SEC 10-K data if loaded
      if (sec10KLoaded && sec10K?.sections) {
        contextData['10k_data'] = { [ticker]: sec10K.sections };
      }
      
      // Add SEC 10-Q data if loaded
      if (sec10QLoaded && sec10Q?.sections) {
        contextData['10q_data'] = { [ticker]: sec10Q.sections };
      }

      // Add FRED data if loaded
      if (fredDataLoaded && fredData?.data) {
        contextData.economic_data = fredData.data;
      }

      const result = await analyzeMutation.mutateAsync({
        prompt: question,
        context_data: contextData,
        session_id: currentSessionId,
      });

      const responseText = result?.response || result?.answer || result?.data?.response;
      
      if (!responseText) {
        throw new Error('No response received from AI service');
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: responseText,
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
      
      // Refresh sessions and history
      refetchSessions();
      refetchHistory();
    } catch (error: any) {
      let errorContent = 'Failed to get response from the AI service.';
      
      if (error.response) {
        const status = error.response.status;
        const detail = error.response.data?.detail || error.response.data?.message;
        
        if (status === 429) {
          // Rate limit error - provide helpful message
          errorContent = `⏱️ Rate Limit Exceeded: ${detail || 'Too many requests. Please wait a minute before trying again. The system will automatically retry with backoff.'}`;
        } else if (status === 401 || status === 500) {
          errorContent = `⚠️ Configuration Error: ${detail || 'AI service is not properly configured.'}`;
        } else if (status === 422) {
          errorContent = `Validation Error: ${detail || 'Invalid request format.'}`;
        } else {
          errorContent = `Error (${status}): ${detail || error.message || 'Unknown error occurred'}`;
        }
      } else if (error.message) {
        errorContent = `Error: ${error.message}`;
      }
      
      const errorMessage: Message = {
        role: 'assistant',
        content: errorContent,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickPrompt = (prompt: string) => {
    setInput(prompt);
  };

  const handleLoadFundamentals = () => {
    setFundamentalsLoaded(true);
  };

  const handleLoadSec10K = () => {
    setSec10KLoaded(true);
  };

  const handleLoadSec10Q = () => {
    setSec10QLoaded(true);
  };

  const handleLoadFredData = () => {
    setFredDataLoaded(true);
  };

  const sessions: ChatSession[] = sessionsData?.sessions || [];

  return (
    <div className="flex gap-4">
      {/* Sessions Sidebar */}
      <div className={`w-64 flex-shrink-0 transition-all ${showSessions ? '' : 'hidden md:block'}`}>
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold">💬 Chat Sessions</h3>
            <button
              onClick={handleNewSession}
              className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              + New
            </button>
          </div>
          
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {sessions.length === 0 ? (
              <p className="text-xs text-gray-500 text-center py-4">No previous sessions</p>
            ) : (
              sessions.map((session) => (
                <button
                  key={session.session_id}
                  onClick={() => handleSwitchSession(session.session_id)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    currentSessionId === session.session_id
                      ? 'bg-blue-50 border-blue-500'
                      : 'bg-white border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="text-xs font-medium text-gray-900 mb-1 line-clamp-2">
                    {session.summary || 'New Chat'}
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <div className="text-xs text-gray-500">
                      {formatDistanceToNow(new Date(session.last_message_at), { addSuffix: true })}
                    </div>
                    <div className="text-xs text-gray-400">
                      {session.message_count} msg{session.message_count !== 1 ? 's' : ''}
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 space-y-4">
        <Card>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowSessions(!showSessions)}
                className="md:hidden px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                {showSessions ? '←' : '☰'} Sessions
              </button>
              <div>
                <h3 className="text-lg font-semibold mb-2">🤖 FinQ Financial Assistant</h3>
                <p className="text-sm text-gray-600">
                  Ask me anything about {ticker} or financial analysis!
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowDataSourceSelector(!showDataSourceSelector)}
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            >
              {showDataSourceSelector ? 'Hide' : 'Show'} Data Sources
            </button>
          </div>

          {/* Data Source Selector */}
          {showDataSourceSelector && (
            <div className="mb-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
              <h4 className="font-semibold mb-4">🔍 Data Sources & Context</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select Companies
                    </label>
                    <MultiSelect
                      options={availableTickers || []}
                      selected={selectedTickers}
                      onChange={setSelectedTickers}
                      placeholder="Select companies..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      📊 Financial Metrics Categories
                    </label>
                    <MultiSelect
                      options={METRIC_CATEGORIES}
                      selected={selectedMetricCategories}
                      onChange={setSelectedMetricCategories}
                      placeholder="Select metric categories..."
                    />
                    <button
                      onClick={handleLoadFundamentals}
                      className="mt-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Load Company Data
                    </button>
                    {fundamentalsLoaded && (
                      <span className="ml-2 text-sm text-green-600">✓ Loaded</span>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      📝 SEC Filings - 10-K Sections
                    </label>
                    <MultiSelect
                      options={['business', 'risk', 'mda']}
                      selected={selected10KSections}
                      onChange={setSelected10KSections}
                      placeholder="Select 10-K sections..."
                    />
                    <button
                      onClick={handleLoadSec10K}
                      className="mt-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Load 10-K Data
                    </button>
                    {sec10KLoaded && (
                      <span className="ml-2 text-sm text-green-600">✓ Loaded</span>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      📄 SEC Filings - 10-Q Sections
                    </label>
                    <MultiSelect
                      options={['risk', 'mda']}
                      selected={selected10QSections}
                      onChange={setSelected10QSections}
                      placeholder="Select 10-Q sections..."
                    />
                    <button
                      onClick={handleLoadSec10Q}
                      className="mt-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Load 10-Q Data
                    </button>
                    {sec10QLoaded && (
                      <span className="ml-2 text-sm text-green-600">✓ Loaded</span>
                    )}
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      🌐 Macroeconomic Indicators
                    </label>
                    <MultiSelect
                      options={FRED_SERIES}
                      selected={selectedFredSeries}
                      onChange={setSelectedFredSeries}
                      placeholder="Select FRED series..."
                    />
                    <button
                      onClick={handleLoadFredData}
                      className="mt-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Load Economic Data
                    </button>
                    {fredDataLoaded && (
                      <span className="ml-2 text-sm text-green-600">✓ Loaded</span>
                    )}
                  </div>

                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-xs text-gray-700">
                      <strong>💡 Valuation Metrics:</strong> When "Valuation Metrics" is selected in Financial Metrics Categories, 
                      the AI will analyze valuation ratios like P/E Ratio, Market Cap, EV/EBITDA, Price-to-Book, and other 
                      valuation metrics if available in the fundamentals data for the selected companies.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="mb-4">
            <h4 className="text-sm font-semibold mb-2">🚀 Quick Actions</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {PRE_GENERATED_PROMPTS.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickPrompt(action.prompt)}
                  className="px-3 py-2 text-xs bg-gray-100 hover:bg-gray-200 rounded-md transition-colors text-left"
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>

          {/* Chat Messages */}
          <div className="border rounded-lg p-4 bg-gray-50 h-96 overflow-y-auto mb-4">
            {messages.length === 0 && !isLoading ? (
              <div className="text-center text-gray-500 py-8">
                <p>Start a conversation by asking a question below.</p>
                <p className="text-sm mt-2">Try: "What is the revenue trend for {ticker}?"</p>
                <p className="text-xs mt-2 text-gray-400">Or click a quick action above to get started.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}-${message.content.substring(0, 20)}`}
                    className={`flex ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-900 border'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white rounded-lg p-3 border">
                      <Loading message="Analyzing..." size="sm" />
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about financial data, company analysis, or market insights..."
              className="flex-1 rounded-md border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="rounded-md bg-blue-600 px-6 py-2 text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </form>
        </Card>
      </div>
    </div>
  );
}
