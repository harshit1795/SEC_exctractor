import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (for auth tokens if needed)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    // const token = getAuthToken();
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors globally
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized');
    } else if (!error.response) {
      // Network error - backend not reachable
      console.error('Network Error: Backend API is not reachable', {
        url: error.config?.url,
        baseURL: error.config?.baseURL,
        message: error.message,
      });
      // Provide more helpful error message
      error.message = `Network Error: Cannot connect to backend API at ${error.config?.baseURL || 'http://localhost:8000/api'}. Make sure the backend server is running.`;
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// API endpoints
export const api = {
  // Health
  health: () => apiClient.get('/health'),

  // Financial
  getTickerData: (ticker: string, period: string = '1y') =>
    apiClient.get(`/financial/ticker/${ticker}`, { params: { period } }),
  getTickers: (tickers: string[]) =>
    apiClient.post('/financial/tickers', { tickers }),
  getFredData: (seriesIds: string[], startDate: string, endDate: string) =>
    apiClient.get('/financial/fred', {
      params: { series_ids: seriesIds.join(','), start_date: startDate, end_date: endDate },
    }),
  getSecData: (ticker: string) =>
    apiClient.get(`/financial/sec/${ticker}`),
  getSec10K: (ticker: string, sections?: string) =>
    apiClient.get(`/financial/sec/${ticker}/10k`, { params: sections ? { sections } : {} }),
  getSec10Q: (ticker: string, sections?: string) =>
    apiClient.get(`/financial/sec/${ticker}/10q`, { params: sections ? { sections } : {} }),
  getFundamentals: (ticker: string) =>
    apiClient.get(`/financial/fundamentals/${ticker}`),
  getAvailableTickers: () =>
    apiClient.get('/financial/tickers/available'),
  
  // Health Scores
  getFinqHealthScores: (category?: string, limit?: number) =>
    apiClient.get('/health-scores/finq', { params: { category, limit } }),
  getCustomHealthScores: (metrics: string[], limit?: number) =>
    apiClient.get('/health-scores/custom', { params: { metrics: metrics.join(','), limit } }),

  // Chat
  analyzeFinancialData: (data: {
    prompt: string;
    context_data?: any;
    session_id?: string;
  }) => apiClient.post('/chat/analyze', data),
  getChatHistory: (user_id: string, limit: number = 50, session_id?: string) =>
    apiClient.get('/chat/history', { params: { user_id, limit, session_id } }),
  getChatSessions: (user_id: string, limit: number = 50) =>
    apiClient.get('/chat/sessions', { params: { user_id, limit } }),

  // Nexus
  createPost: (data: { user_id: string; content: string; media_url?: string }) =>
    apiClient.post('/nexus/posts', { content: data.content, media_url: data.media_url }, { params: { user_id: data.user_id } }),
  getFeed: (user_id: string, limit: number = 20) =>
    apiClient.get('/nexus/posts/feed', { params: { user_id, limit } }),
  getPost: (postId: string) =>
    apiClient.get(`/nexus/posts/${postId}`),
  likePost: (postId: string, user_id: string) =>
    apiClient.post(`/nexus/posts/${postId}/like`, null, { params: { user_id } }),
  unlikePost: (postId: string, user_id: string) =>
    apiClient.delete(`/nexus/posts/${postId}/like`, { params: { user_id } }),
  addComment: (postId: string, data: { user_id: string; content: string }) =>
    apiClient.post(`/nexus/posts/${postId}/comments`, data),
  sendFriendRequest: (data: { user_id: string; friend_id: string }) =>
    apiClient.post('/nexus/friends/request', data),
  acceptFriendRequest: (requestId: string, user_id: string) =>
    apiClient.post(`/nexus/friends/${requestId}/accept`, null, { params: { user_id } }),
  getFriends: (user_id: string) =>
    apiClient.get('/nexus/friends', { params: { user_id } }),
  getFriendRequests: (user_id: string) =>
    apiClient.get('/nexus/friends/requests', { params: { user_id } }),
  getUserDirectory: (user_id: string, limit: number = 100, offset: number = 0) =>
    apiClient.get('/nexus/users/directory', { params: { user_id, limit, offset } }),
  getUserProfile: (target_user_id: string, user_id: string) =>
    apiClient.get(`/nexus/users/${target_user_id}/profile`, { params: { user_id } }),
  getUserProfilePreferences: (user_id: string) =>
    apiClient.get(`/nexus/users/${user_id}/profile/preferences`, { params: { user_id } }),
  initializeUserProfile: (user_id: string, data?: { firebase_display_name?: string; firebase_photo_url?: string; firebase_email?: string }) =>
    apiClient.post(`/nexus/users/${user_id}/profile/initialize`, data || null, { params: { user_id } }),
  updateUserProfilePreferences: (user_id: string, data: { display_name?: string; profile_picture_url?: string; use_alias_as_display?: boolean }) =>
    apiClient.put(`/nexus/users/${user_id}/profile/preferences`, data, { params: { user_id } }),

  // Insights
  shareInsight: (data: { user_id: string; insight_id: string; content: string }) =>
    apiClient.post('/insights/share', data),
  getSharedInsights: (user_id: string, limit: number = 20) =>
    apiClient.get('/insights/shared', { params: { user_id, limit } }),
  getShareLink: (insightId: string) =>
    apiClient.get(`/insights/${insightId}/share-link`),

  // Media
  generatePriceChart: (ticker: string, period: string = '1y', user_id: string = 'anonymous') =>
    apiClient.get(`/media/chart/price/${ticker}`, { params: { period, user_id } }),
  generateSummary: (ticker: string, user_id: string = 'anonymous') =>
    apiClient.get(`/media/summary/${ticker}`, { params: { user_id } }),

  // Data Pipeline
  updateTickerData: (ticker: string, forceRefresh: boolean = false) =>
    apiClient.post(`/data-pipeline/update/${ticker}`, null, { params: { force_refresh: forceRefresh } }),
  updateLatestData: (tickers?: string[]) =>
    apiClient.post('/data-pipeline/update-latest', tickers ? { tickers } : {}),
  updateBatch: (tickers?: string[]) =>
    apiClient.post('/data-pipeline/update-batch', tickers ? { tickers } : {}),
  getDataStatus: (ticker?: string) =>
    apiClient.get('/data-pipeline/status', { params: ticker ? { ticker } : {} }),
};

