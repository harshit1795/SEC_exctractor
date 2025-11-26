/**
 * TypeScript type definitions for FinQ Frontend
 */

// Financial Data Types
export interface TickerData {
  info: {
    symbol: string;
    shortName: string;
    longName: string;
    sector: string;
    industry: string;
    marketCap: number;
    currentPrice: number;
    [key: string]: any;
  };
  history: {
    Date: string[];
    Open: number[];
    High: number[];
    Low: number[];
    Close: number[];
    Volume: number[];
  };
}

export interface FundamentalsData {
  ticker: string;
  metric: string;
  value: number;
  date: string;
  [key: string]: any;
}

export interface SecFiling {
  cik: string;
  companyName: string;
  formType: string;
  dateFiled: string;
  url: string;
  [key: string]: any;
}

export interface FredSeries {
  series_id: string;
  title: string;
  units: string;
  data: Array<{
    date: string;
    value: number;
  }>;
}

// Chat Types
export interface ChatMessage {
  id: string;
  user_id: string;
  ticker?: string;
  question: string;
  answer: string;
  context?: any;
  created_at: string;
}

export interface ChatRequest {
  ticker?: string;
  question: string;
  context?: any;
  user_id?: string;
}

// Nexus Types
export interface Post {
  id: string;
  user_id: string;
  content: string;
  media_url?: string;
  created_at: string;
  updated_at: string;
  likes_count: number;
  comments_count: number;
  user_liked?: boolean;
  comments?: Comment[];
}

export interface Comment {
  id: string;
  post_id: string;
  user_id: string;
  content: string;
  created_at: string;
}

export interface Friend {
  id: string;
  user_id: string;
  friend_id: string;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
}

export interface FriendRequest {
  id: string;
  user_id: string;
  friend_id: string;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
}

// Insight Types
export interface Insight {
  id: string;
  user_id: string;
  ticker?: string;
  content: string;
  context?: any;
  created_at: string;
  shared_at?: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

// UI Types
export interface SelectOption {
  label: string;
  value: string;
}

export interface ChartDataPoint {
  date: string;
  value: number;
  [key: string]: any;
}

// User Types
export interface UserProfile {
  uid: string;
  email: string;
  displayName?: string;
  photoURL?: string;
}
