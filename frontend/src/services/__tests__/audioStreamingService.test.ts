/**
 * Unit tests for AudioStreamingService
 * Tests audio format detection, buffering, and playback logic
 */

import { AudioStreamingService } from '../audioStreamingService'

// Mock Audio API
class MockAudio {
  src = ''
  preload = 'auto'
  onended: (() => void) | null = null
  onerror: (() => void) | null = null

  play = jest.fn().mockResolvedValue(undefined)
  pause = jest.fn()
  load = jest.fn()
}

// Store instances for test access
const mockAudioInstances: MockAudio[] = []

const AudioConstructorMock = jest.fn().mockImplementation(() => {
  const instance = new MockAudio()
  mockAudioInstances.push(instance)
  return instance
})

global.Audio = AudioConstructorMock as any
global.URL.createObjectURL = jest.fn(() => 'blob:mock-url')
global.URL.revokeObjectURL = jest.fn()

describe('AudioStreamingService', () => {
  let service: AudioStreamingService
  let onPlaybackStart: jest.Mock
  let onPlaybackEnd: jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
    mockAudioInstances.length = 0 // Clear instances array
    onPlaybackStart = jest.fn()
    onPlaybackEnd = jest.fn()
    service = new AudioStreamingService(onPlaybackStart, onPlaybackEnd)
  })

  describe('detectAudioFormat', () => {
    it('should detect WAV format from RIFF header', () => {
      // Arrange - WAV file starts with "RIFF" (52 49 46 46)
      const wavData = new Uint8Array([0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00])
      const base64WavData = btoa(String.fromCharCode(...wavData))

      // Act
      service.addAudioChunk(base64WavData)

      // Assert
      expect(URL.createObjectURL).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'audio/wav'
        })
      )
    })

    it('should detect WebM format from header', () => {
      // Arrange - WebM file starts with (1A 45 DF A3)
      const webmData = new Uint8Array([0x1A, 0x45, 0xDF, 0xA3, 0x00, 0x00, 0x00, 0x00])
      const base64WebmData = btoa(String.fromCharCode(...webmData))

      // Act
      service.addAudioChunk(base64WebmData)

      // Assert
      expect(URL.createObjectURL).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'audio/webm'
        })
      )
    })

    it('should fallback to webm for unknown formats', () => {
      // Arrange - Unknown format
      const unknownData = new Uint8Array([0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00])
      const base64UnknownData = btoa(String.fromCharCode(...unknownData))

      // Act
      service.addAudioChunk(base64UnknownData)

      // Assert
      expect(URL.createObjectURL).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'audio/webm'
        })
      )
    })
  })

  describe('buffer management', () => {
    it('should create audio instance immediately with minBufferSize = 1', () => {
      // Arrange
      const wavData = new Uint8Array([0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00])
      const base64WavData = btoa(String.fromCharCode(...wavData))

      // Act
      service.addAudioChunk(base64WavData)

      // Assert - Audio instance should be created and service should report playing
      expect(mockAudioInstances.length).toBe(1)
      expect(AudioConstructorMock).toHaveBeenCalledTimes(1)
      expect(service.getIsPlaying()).toBe(true)
    })

    it('should queue multiple chunks and create audio instances', () => {
      // Arrange
      const wavData = new Uint8Array([0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00])
      const base64WavData = btoa(String.fromCharCode(...wavData))

      // Act - Add 3 chunks
      service.addAudioChunk(base64WavData)
      service.addAudioChunk(base64WavData)
      service.addAudioChunk(base64WavData)

      // Assert - 3 audio instances should be created
      expect(mockAudioInstances.length).toBe(3)
      expect(AudioConstructorMock).toHaveBeenCalledTimes(3)
      expect(service.getIsPlaying()).toBe(true)
    })

    it('should reset buffering state when stopped', () => {
      // Arrange
      const wavData = new Uint8Array([0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00])
      const base64WavData = btoa(String.fromCharCode(...wavData))
      service.addAudioChunk(base64WavData)

      // Act
      service.stop()

      // Assert
      expect(URL.revokeObjectURL).toHaveBeenCalled()
      expect(service.getIsPlaying()).toBe(false)
    })
  })

  describe('playback lifecycle', () => {
    it('should trigger onPlaybackEnd when queue is empty', () => {
      // Arrange
      const wavData = new Uint8Array([0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00])
      const base64WavData = btoa(String.fromCharCode(...wavData))
      service.addAudioChunk(base64WavData)

      // Act - Simulate audio ending
      const audioInstance = mockAudioInstances[0]
      audioInstance.onended?.()

      // Assert
      expect(onPlaybackEnd).toHaveBeenCalled()
    })

    it('should clean up resources when stopping', () => {
      // Arrange
      const wavData = new Uint8Array([0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00])
      const base64WavData = btoa(String.fromCharCode(...wavData))
      service.addAudioChunk(base64WavData)

      const audioInstance = mockAudioInstances[0]

      // Act
      service.stop()

      // Assert
      expect(audioInstance.pause).toHaveBeenCalled()
      expect(URL.revokeObjectURL).toHaveBeenCalled()
      expect(service.getIsPlaying()).toBe(false)
    })
  })

  describe('error handling', () => {
    it('should handle invalid base64 data gracefully', () => {
      // Arrange
      const invalidBase64 = 'not-valid-base64!!!'

      // Act & Assert - Should not throw
      expect(() => service.addAudioChunk(invalidBase64)).not.toThrow()
    })

    it('should handle audio playback errors', async () => {
      // Arrange
      const wavData = new Uint8Array([0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00])
      const base64WavData = btoa(String.fromCharCode(...wavData))
      service.addAudioChunk(base64WavData)
      
      await Promise.resolve()

      // Act - Simulate audio error by calling onerror
      const audioInstance = mockAudioInstances[0]
      
      // Simulate the error event
      if (audioInstance.onerror) {
        audioInstance.onerror()
      }

      // Assert - Audio instance should exist and error handler should be set
      expect(audioInstance.onerror).toBeDefined()
      // Service should still be in playing state as error handling continues to next chunk
      expect(mockAudioInstances.length).toBe(1)
    })
  })

  describe('state management', () => {
    it('should report correct playing state', () => {
      // Arrange
      expect(service.getIsPlaying()).toBe(false)

      const wavData = new Uint8Array([0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00])
      const base64WavData = btoa(String.fromCharCode(...wavData))

      // Act
      service.addAudioChunk(base64WavData)

      // Assert
      expect(service.getIsPlaying()).toBe(true)
    })

    it('should handle stop when not playing', () => {
      // Act & Assert - Should not throw
      expect(() => service.stop()).not.toThrow()
      expect(service.getIsPlaying()).toBe(false)
    })
  })

  describe('WAV header validation', () => {
    it('should correctly identify complete WAV files', () => {
      // Arrange - Minimal valid WAV file with header
      const wavHeader = new Uint8Array([
        // RIFF header
        0x52, 0x49, 0x46, 0x46, // "RIFF"
        0x24, 0x00, 0x00, 0x00, // File size - 8
        0x57, 0x41, 0x56, 0x45, // "WAVE"
        // fmt chunk
        0x66, 0x6D, 0x74, 0x20, // "fmt "
        0x10, 0x00, 0x00, 0x00, // Chunk size (16)
        0x01, 0x00,             // Audio format (1 = PCM)
        0x01, 0x00,             // Channels (1 = mono)
        0xC0, 0x5D, 0x00, 0x00, // Sample rate (24000)
        0x80, 0xBB, 0x00, 0x00, // Byte rate
        0x02, 0x00,             // Block align
        0x10, 0x00,             // Bits per sample (16)
        // data chunk
        0x64, 0x61, 0x74, 0x61, // "data"
        0x00, 0x00, 0x00, 0x00, // Data size (0)
      ])

      const base64WavData = btoa(String.fromCharCode(...wavHeader))

      // Act
      service.addAudioChunk(base64WavData)

      // Assert
      expect(URL.createObjectURL).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'audio/wav'
        })
      )
    })
  })
})

