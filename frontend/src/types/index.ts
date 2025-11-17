// User and Authentication Types
export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

// Banking Types
export type AccountType = 'checking' | 'savings' | 'credit' | 'investment';
export type TransactionType = 'deposit' | 'withdrawal' | 'transfer' | 'payment' | 'fee';
export type TransactionStatus = 'pending' | 'completed' | 'failed' | 'cancelled';

export interface BankAccount {
  id: string;
  user_id: string;
  account_number: string;
  account_type: AccountType;
  balance: number;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: string;
  account_id: string;
  transaction_type: TransactionType;
  amount: number;
  balance_after: number;
  description?: string;
  status: TransactionStatus;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface CreateAccountRequest {
  account_type: AccountType;
  currency?: string;
  initial_balance?: number;
}

export interface DepositRequest {
  amount: number;
  description?: string;
}

export interface WithdrawRequest {
  amount: number;
  description?: string;
}

export interface TransferRequest {
  from_account_id: string;
  to_account_id: string;
  amount: number;
  description?: string;
}

export interface AccountSummary {
  total_balance: number;
  accounts: BankAccount[];
  recent_transactions: Transaction[];
  statistics: {
    total_deposits: number;
    total_withdrawals: number;
    total_transfers: number;
    account_count: number;
  };
}

// Chat and RAG Types
export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  metadata?: Record<string, any>;
}

export interface ChatRequest {
  message: string;
  context?: Record<string, any>;
  stream?: boolean;
}

export interface ChatResponse {
  response: string;
  conversation_id?: string;
  sources?: RagSource[];
  metadata?: Record<string, any>;
}

export interface RagSource {
  content: string;
  metadata: {
    document_id?: string;
    filename?: string;
    page?: number;
    score?: number;
    [key: string]: any;
  };
}

export interface ChatHistory {
  conversations: Conversation[];
  total: number;
}

export interface Conversation {
  id: string;
  user_id: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

// Document Types
export type DocumentStatus = 'uploaded' | 'processing' | 'processed' | 'failed';

export interface Document {
  id: string;
  user_id: string;
  filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  status: DocumentStatus;
  ocr_text?: string;
  extracted_data?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface UploadDocumentRequest {
  file: File;
  process_ocr?: boolean;
}

export interface DocumentOcrResponse {
  document_id: string;
  text: string;
  confidence?: number;
  metadata?: Record<string, any>;
}

export interface DocumentIngestResponse {
  document_id: string;
  chunks_created: number;
  vector_ids: string[];
  success: boolean;
}

// Voice Types
export interface TranscriptionRequest {
  file: File;
  language?: string;
}

export interface TranscriptionResponse {
  text: string;
  language?: string;
  confidence?: number;
  duration?: number;
  metadata?: Record<string, any>;
}

export interface SynthesisRequest {
  text: string;
  language?: string;
  voice?: string;
}

export interface AudioInfo {
  duration: number;
  sample_rate: number;
  channels: number;
  format: string;
  size: number;
}

// Health Check Types
export interface HealthCheck {
  status: string;
  version: string;
  timestamp: string;
  services: {
    database: ServiceStatus;
    redis: ServiceStatus;
    qdrant: ServiceStatus;
    ollama: ServiceStatus;
  };
}

export interface ServiceStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  message?: string;
  response_time_ms?: number;
}

// Websocket Types
export interface WebSocketMessage {
  type: 'chat' | 'notification' | 'error' | 'ping' | 'pong';
  data: any;
  timestamp: string;
}

export interface WebSocketChatMessage {
  type: 'chat';
  data: {
    message: string;
    context?: Record<string, any>;
  };
}

export interface WebSocketChatResponse {
  type: 'chat';
  data: {
    chunk?: string;
    complete?: boolean;
    response?: string;
    sources?: RagSource[];
    error?: string;
  };
}

// API Error Types
export interface ApiError {
  message: string;
  status: number;
  detail?: string;
  errors?: Record<string, string[]>;
}

// Pagination Types
export interface PaginationParams {
  limit?: number;
  offset?: number;
  page?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// UI State Types
export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  description?: string;
  duration?: number;
}

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

// Form Types
export interface LoginFormData {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface SignupFormData {
  email: string;
  password: string;
  confirmPassword: string;
  full_name: string;
  acceptTerms: boolean;
}

export interface TransferFormData {
  fromAccountId: string;
  toAccountId: string;
  amount: number;
  description?: string;
}

export interface DepositFormData {
  accountId: string;
  amount: number;
  description?: string;
}

export interface WithdrawFormData {
  accountId: string;
  amount: number;
  description?: string;
}

// Chart and Analytics Types
export interface TransactionChartData {
  date: string;
  deposits: number;
  withdrawals: number;
  balance: number;
}

export interface AccountBalanceData {
  account_type: string;
  balance: number;
  percentage: number;
}

export interface SpendingCategory {
  category: string;
  amount: number;
  count: number;
  percentage: number;
}

// Notification Types
export interface Notification {
  id: string;
  user_id: string;
  type: 'info' | 'warning' | 'success' | 'error';
  title: string;
  message: string;
  read: boolean;
  metadata?: Record<string, any>;
  created_at: string;
}

// Settings Types
export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  currency: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  security: {
    two_factor_enabled: boolean;
    biometric_enabled: boolean;
  };
}

// File Upload Types
export interface FileUploadProgress {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

// Search Types
export interface SearchResult {
  type: 'transaction' | 'document' | 'conversation' | 'account';
  id: string;
  title: string;
  description: string;
  metadata?: Record<string, any>;
  score?: number;
}

export interface SearchParams {
  query: string;
  type?: 'transaction' | 'document' | 'conversation' | 'account' | 'all';
  limit?: number;
  filters?: Record<string, any>;
}

// Export utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Nullable<T> = T | null;

export type Optional<T> = T | undefined;

export type AsyncData<T> = {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
};
