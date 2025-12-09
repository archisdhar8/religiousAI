/**
 * API Client for Divine Wisdom Guide Backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ChatRequest {
  message: string;
  religion?: string;
  session_id?: string;
  conversation_history?: Array<{ question: string; answer: string }>;
  mode?: string;
}

export interface ChatResponse {
  response: string;
  is_crisis: boolean;
  sources?: Array<{
    tradition: string;
    scripture: string;
    content: string;
  }>;
}

export interface DailyWisdomResponse {
  wisdom: string;
  tradition: string;
  scripture: string;
}

export interface Tradition {
  id: string;
  name: string;
  icon: string;
  description: string;
}

export interface TraditionsResponse {
  traditions: Tradition[];
}

export interface CompareRequest {
  topic: string;
  traditions: string[];
}

export interface CompareResponse {
  comparison: string;
  sources: Record<string, Array<{ scripture: string; content: string }>>;
}

export interface JournalRequest {
  entry: string;
  session_id?: string;
}

export interface JournalResponse {
  reflection: string;
}

export interface GreetingResponse {
  greeting: string;
}

// Auth interfaces
export interface SignUpRequest {
  email: string;
  password: string;
  name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  token?: string;
  user?: {
    email: string;
    name: string;
    created_at: string;
    preferences: {
      default_religion: string;
      theme: string;
    };
  };
}

export interface User {
  email: string;
  name: string;
  created_at: string;
  preferences: {
    default_religion: string;
    theme: string;
  };
}

/**
 * Get or create a session ID from localStorage
 */
export function getSessionId(): string {
  let sessionId = localStorage.getItem("divine_wisdom_session_id");
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem("divine_wisdom_session_id", sessionId);
  }
  return sessionId;
}

/**
 * Generic API request handler
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("An unexpected error occurred");
  }
}

/**
 * Send a chat message and get a response
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  return apiRequest<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({
      ...request,
      session_id: request.session_id || getSessionId(),
    }),
  });
}

/**
 * Get daily wisdom quote
 */
export async function getDailyWisdom(
  religion?: string
): Promise<DailyWisdomResponse> {
  const params = new URLSearchParams();
  if (religion) {
    params.append("religion", religion);
  }
  params.append("session_id", getSessionId());

  return apiRequest<DailyWisdomResponse>(
    `/api/daily-wisdom?${params.toString()}`
  );
}

/**
 * Get available traditions
 */
export async function getTraditions(): Promise<TraditionsResponse> {
  return apiRequest<TraditionsResponse>("/api/traditions");
}

/**
 * Compare traditions on a topic
 */
export async function compareTraditions(
  request: CompareRequest
): Promise<CompareResponse> {
  return apiRequest<CompareResponse>("/api/compare", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

/**
 * Submit a journal entry and get reflection
 */
export async function submitJournalEntry(
  request: JournalRequest
): Promise<JournalResponse> {
  return apiRequest<JournalResponse>("/api/journal", {
    method: "POST",
    body: JSON.stringify({
      ...request,
      session_id: request.session_id || getSessionId(),
    }),
  });
}

/**
 * Get personalized greeting
 */
export async function getGreeting(): Promise<GreetingResponse> {
  const params = new URLSearchParams();
  params.append("session_id", getSessionId());

  return apiRequest<GreetingResponse>(`/api/greeting?${params.toString()}`);
}


// =====================================================================
// AUTH FUNCTIONS
// =====================================================================

const AUTH_TOKEN_KEY = "divine_wisdom_auth_token";
const AUTH_USER_KEY = "divine_wisdom_user";

/**
 * Get stored auth token
 */
export function getAuthToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

/**
 * Get stored user data
 */
export function getStoredUser(): User | null {
  const userData = localStorage.getItem(AUTH_USER_KEY);
  if (userData) {
    try {
      return JSON.parse(userData);
    } catch {
      return null;
    }
  }
  return null;
}

/**
 * Store auth data after login/signup
 */
function storeAuthData(token: string, user: User): void {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
}

/**
 * Clear auth data on logout
 */
export function clearAuthData(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getAuthToken() && !!getStoredUser();
}

/**
 * Sign up a new user
 */
export async function signUp(request: SignUpRequest): Promise<AuthResponse> {
  const response = await apiRequest<AuthResponse>("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify(request),
  });
  
  if (response.success && response.token && response.user) {
    storeAuthData(response.token, response.user as User);
  }
  
  return response;
}

/**
 * Login with email and password
 */
export async function login(request: LoginRequest): Promise<AuthResponse> {
  const response = await apiRequest<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(request),
  });
  
  if (response.success && response.token && response.user) {
    storeAuthData(response.token, response.user as User);
  }
  
  return response;
}

/**
 * Logout current user
 */
export async function logout(): Promise<void> {
  const token = getAuthToken();
  
  try {
    await apiRequest("/api/auth/logout", {
      method: "POST",
      body: JSON.stringify({ token }),
    });
  } catch {
    // Ignore errors, still clear local data
  }
  
  clearAuthData();
}

/**
 * Get current user from server (validates token)
 */
export async function getCurrentUser(): Promise<User | null> {
  const token = getAuthToken();
  
  if (!token) {
    return null;
  }
  
  try {
    const user = await apiRequest<User>("/api/auth/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return user;
  } catch {
    // Token invalid, clear auth data
    clearAuthData();
    return null;
  }
}


// =====================================================================
// COMMUNITY FUNCTIONS
// =====================================================================

export interface CommunityProfile {
  display_name: string;
  bio?: string;
  traits?: Record<string, string[]>;
  preferred_traditions?: string[];
  opt_in?: boolean;
  connections_count?: number;
  pending_requests?: number;
}

export interface Match {
  email: string;
  display_name: string;
  bio: string;
  compatibility_score: number;
  matching_traits: string[];
  preferred_traditions: string[];
  last_active: string;
}

export interface Connection {
  email: string;
  display_name: string;
  bio: string;
  preferred_traditions: string[];
  last_active: string;
}

export interface ConnectionRequestData {
  from_email: string;
  from_name: string;
  message: string;
  sent_at: string;
}

/**
 * Get authenticated headers
 */
function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Create or update community profile
 */
export async function createCommunityProfile(profile: {
  display_name: string;
  bio?: string;
  preferred_traditions?: string[];
  opt_in?: boolean;
}): Promise<{ success: boolean; profile: CommunityProfile }> {
  return apiRequest("/api/community/profile", {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(profile),
  });
}

/**
 * Get current user's community profile
 */
export async function getCommunityProfile(): Promise<{ profile: CommunityProfile | null }> {
  return apiRequest("/api/community/profile", {
    headers: getAuthHeaders(),
  });
}

/**
 * Get compatible matches
 */
export async function getMatches(limit: number = 10): Promise<{ matches: Match[]; total: number }> {
  return apiRequest(`/api/community/matches?limit=${limit}`, {
    headers: getAuthHeaders(),
  });
}

/**
 * Send connection request
 */
export async function sendConnectionRequest(
  toEmail: string,
  message?: string
): Promise<{ success: boolean; message: string }> {
  return apiRequest("/api/community/connect", {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ to_email: toEmail, message: message || "" }),
  });
}

/**
 * Respond to connection request
 */
export async function respondToConnection(
  fromEmail: string,
  accept: boolean
): Promise<{ success: boolean; message: string }> {
  return apiRequest("/api/community/respond", {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ from_email: fromEmail, accept }),
  });
}

/**
 * Get connections list
 */
export async function getConnections(): Promise<{ connections: Connection[]; total: number }> {
  return apiRequest("/api/community/connections", {
    headers: getAuthHeaders(),
  });
}

/**
 * Get pending connection requests
 */
export async function getConnectionRequests(): Promise<{ requests: ConnectionRequestData[]; total: number }> {
  return apiRequest("/api/community/requests", {
    headers: getAuthHeaders(),
  });
}

