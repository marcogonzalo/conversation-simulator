import { renderHook, act } from '@testing-library/react'
import { useWebSocket } from '../useWebSocket'

// Mock the API config
jest.mock('../../config/api', () => ({
  API_CONFIG: {
    BASE_URL: 'http://localhost:8000',
    WS_URL: 'ws://localhost:8000',
  }
}))

describe('useWebSocket', () => {
  const testUrl = 'ws://localhost:8000/ws'

  beforeEach(() => {
    jest.clearAllMocks()
    
    // Reset fetch mock
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'test-conversation' }),
    })
  })

  it('should initialize with correct default values', () => {
    const { result } = renderHook(() => useWebSocket(testUrl))
    
    expect(result.current.isConnected).toBe(false)
    expect(result.current.isLoading).toBe(false)
    expect(result.current.realConversationId).toBe(null)
    expect(typeof result.current.sendMessage).toBe('function')
    expect(typeof result.current.connect).toBe('function')
    expect(typeof result.current.disconnect).toBe('function')
  })

  it('should handle sendMessage when not connected', () => {
    const { result } = renderHook(() => useWebSocket(testUrl))
    
    const testMessage = { type: 'test', data: 'hello' }
    
    // Should not throw when calling sendMessage while not connected
    expect(() => {
      act(() => {
        result.current.sendMessage(testMessage)
      })
    }).not.toThrow()
  })

  it('should have connect and disconnect functions', () => {
    const { result } = renderHook(() => useWebSocket(testUrl))
    
    expect(typeof result.current.connect).toBe('function')
    expect(typeof result.current.disconnect).toBe('function')
  })

  it('should handle connection state correctly', () => {
    const { result } = renderHook(() => useWebSocket(testUrl))
    
    // Initially not connected
    expect(result.current.isConnected).toBe(false)
    
    // connect function should exist and be callable
    expect(() => {
      act(() => {
        result.current.connect()
      })
    }).not.toThrow()
  })

  it('should handle disconnect correctly', () => {
    const { result } = renderHook(() => useWebSocket(testUrl))
    
    // disconnect function should exist and be callable
    expect(() => {
      act(() => {
        result.current.disconnect()
      })
    }).not.toThrow()
  })

  it('should return correct initial state properties', () => {
    const { result } = renderHook(() => useWebSocket(testUrl))
    
    // Check all expected properties exist (based on actual implementation)
    expect(result.current).toHaveProperty('isConnected')
    expect(result.current).toHaveProperty('isLoading')
    expect(result.current).toHaveProperty('realConversationId')
    expect(result.current).toHaveProperty('sendMessage')
    expect(result.current).toHaveProperty('connect')
    expect(result.current).toHaveProperty('disconnect')
  })

  it('should handle URL parameter correctly', () => {
    const customUrl = 'ws://example.com/test'
    const { result } = renderHook(() => useWebSocket(customUrl))
    
    // Should initialize without errors
    expect(result.current.isConnected).toBe(false)
    expect(result.current.isLoading).toBe(false)
  })

  it('should handle loading state', () => {
    const { result } = renderHook(() => useWebSocket(testUrl))
    
    // Initially should not be loading
    expect(result.current.isLoading).toBe(false)
  })

  it('should handle realConversationId state', () => {
    const { result } = renderHook(() => useWebSocket(testUrl))
    
    // Initially should be null
    expect(result.current.realConversationId).toBe(null)
  })
})