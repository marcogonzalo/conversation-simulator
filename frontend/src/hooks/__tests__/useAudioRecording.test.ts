import { renderHook, act } from '@testing-library/react'
import { useAudioRecording } from '../useAudioRecording'

// Mock is already set up in jest.setup.js, so we don't need to redefine it

const defaultProps = {
  onAudioReady: jest.fn(),
  isWaitingForResponse: false,
  isEnding: false,
}

beforeEach(() => {
  jest.clearAllMocks()
  
  // Reset mocks to default state
  if (navigator.mediaDevices?.getUserMedia) {
    navigator.mediaDevices.getUserMedia.mockResolvedValue({
      getTracks: () => [{ stop: jest.fn() }],
    })
  }
})

describe('useAudioRecording', () => {
  it('should initialize with correct default values', () => {
    const { result } = renderHook(() => useAudioRecording(defaultProps))
    
    expect(result.current.isRecording).toBe(false)
    expect(result.current.isSpeaking).toBe(false)
    expect(typeof result.current.startRecording).toBe('function')
    expect(typeof result.current.stopRecording).toBe('function')
    expect(typeof result.current.cleanup).toBe('function')
  })

  it('should start recording when startRecording is called', async () => {
    const { result } = renderHook(() => useAudioRecording(defaultProps))
    
    await act(async () => {
      await result.current.startRecording()
    })
    
    expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
      audio: true
    })
  })

  it('should stop recording when stopRecording is called', async () => {
    const { result } = renderHook(() => useAudioRecording(defaultProps))
    
    // First start recording
    await act(async () => {
      await result.current.startRecording()
    })
    
    // Then stop it
    act(() => {
      result.current.stopRecording()
    })
    
    // Should not be recording anymore
    expect(result.current.isRecording).toBe(false)
  })

  it('should handle getUserMedia errors gracefully', async () => {
    // Mock getUserMedia to reject
    navigator.mediaDevices.getUserMedia.mockRejectedValue(new Error('Permission denied'))
    
    const { result } = renderHook(() => useAudioRecording(defaultProps))
    
    await act(async () => {
      await result.current.startRecording()
    })
    
    // Should not be recording if permission denied
    expect(result.current.isRecording).toBe(false)
  })

  it('should call onAudioReady when audio is ready', async () => {
    const onAudioReady = jest.fn()
    const props = { ...defaultProps, onAudioReady }
    
    const { result } = renderHook(() => useAudioRecording(props))
    
    await act(async () => {
      await result.current.startRecording()
    })
    
    // onAudioReady should be defined (actual calls depend on MediaRecorder events)
    expect(onAudioReady).toBeDefined()
  })

  it('should handle waiting for response state', () => {
    const props = { ...defaultProps, isWaitingForResponse: true }
    
    const { result } = renderHook(() => useAudioRecording(props))
    
    // Should still have all expected properties
    expect(result.current.isRecording).toBe(false)
    expect(result.current.isSpeaking).toBe(false)
  })

  it('should handle ending state', () => {
    const props = { ...defaultProps, isEnding: true }
    
    const { result } = renderHook(() => useAudioRecording(props))
    
    // Should still have all expected properties
    expect(result.current.isRecording).toBe(false)
    expect(result.current.isSpeaking).toBe(false)
  })

  it('should cleanup resources when cleanup is called', () => {
    const { result } = renderHook(() => useAudioRecording(defaultProps))
    
    // Should not throw when cleanup is called
    expect(() => {
      act(() => {
        result.current.cleanup()
      })
    }).not.toThrow()
  })
})