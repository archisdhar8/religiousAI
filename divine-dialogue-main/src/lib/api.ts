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

