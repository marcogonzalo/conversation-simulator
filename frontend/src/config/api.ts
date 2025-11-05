/**
 * API Configuration
 * Centralized configuration for API endpoints and WebSocket URLs
 */

// Get API base URL from environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_BASE_URL || 'ws://localhost:8000'

export const apiConfig = {
  // HTTP API endpoints
  baseUrl: API_BASE_URL,
  conversations: `${API_BASE_URL}/api/v1/conversations/`,
  personas: `${API_BASE_URL}/api/v1/personas/`,
  analysis: `${API_BASE_URL}/api/v1/analysis/`,
  prompts: `${API_BASE_URL}/api/v1/prompts/`,
  
  // WebSocket endpoints
  wsBaseUrl: WS_BASE_URL,
  conversationWs: (conversationId: string) => `${WS_BASE_URL}/api/v1/ws/conversation/${conversationId}`,
  
  // Audio configuration
  audio: {
    // Minimum audio duration (configurable values)
    // These values prevent "buffer too small" errors from OpenAI API
    minDurationMs: 100,  // OpenAI minimum requirement (100ms)
    // Minimum bytes for WebM/Opus audio (~50ms at 32kbps)
    minBytesWebm: 200,   // Reduced for better fluency
  }
}

export default apiConfig
