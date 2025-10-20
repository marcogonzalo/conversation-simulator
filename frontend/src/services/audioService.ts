/**
 * Audio Service
 * Handles audio conversion and WebSocket communication with browser compatibility
 */

import { browserCompatibility } from '../utils/browserCompatibility'

export class AudioService {
  /**
   * Detect audio format from binary data
   */
  private static detectAudioFormat(audioDataBytes: Uint8Array): string {
    // Check for RIFF/WAV header (52 49 46 46 = "RIFF")
    if (audioDataBytes.length >= 4 &&
        audioDataBytes[0] === 0x52 && // R
        audioDataBytes[1] === 0x49 && // I
        audioDataBytes[2] === 0x46 && // F
        audioDataBytes[3] === 0x46) {  // F
      return 'audio/wav'
    }
    
    // Check for WebM header (1A 45 DF A3)
    if (audioDataBytes.length >= 4 &&
        audioDataBytes[0] === 0x1A &&
        audioDataBytes[1] === 0x45 &&
        audioDataBytes[2] === 0xDF &&
        audioDataBytes[3] === 0xA3) {
      return 'audio/webm'
    }
    
    // Default fallback
    return 'audio/webm'
  }

  private static uint8ArrayToBase64(uint8Array: Uint8Array): string {
    const CHUNK_SIZE = 0x8000 // 32k chunks
    let result = ''
    for (let i = 0; i < uint8Array.length; i += CHUNK_SIZE) {
      const chunk = uint8Array.subarray(i, i + CHUNK_SIZE)
      result += String.fromCharCode.apply(null, Array.from(chunk))
    }
    return btoa(result)
  }

  static async convertAudioToBase64(audioBlob: Blob): Promise<string> {
    console.log('📤 Converting audio to base64...')
    
    const arrayBuffer = await audioBlob.arrayBuffer()
    const uint8Array = new Uint8Array(arrayBuffer)
    const base64 = this.uint8ArrayToBase64(uint8Array)
    
    return base64
  }

  static createAudioMessage(audioData: string): any {
    return {
      type: 'audio_message',
      audio_data: audioData,
      audio_format: 'webm'
    }
  }

  static createAudioElement(audioData: string): HTMLAudioElement {
    try {
      const capabilities = browserCompatibility.detectCapabilities()
      console.log('🎵 Creating audio element from base64 data for', capabilities.browserName)
      
      // Decode base64 to get audio data
      const audioDataBytes = Uint8Array.from(atob(audioData), c => c.charCodeAt(0))
      console.log('🎵 Decoded audio data:', audioDataBytes.length, 'bytes')
      
      // Auto-detect format from binary data (WAV or WebM)
      const mimeType = this.detectAudioFormat(audioDataBytes)
      console.log('🎵 Detected audio format:', mimeType, 'from binary data')
      
      // Create audio blob with browser-appropriate MIME type
      const audioBlob = new Blob([audioDataBytes], { type: mimeType })
      console.log('🎵 Created audio blob:', audioBlob.size, 'bytes, type:', audioBlob.type)
      
      const audioUrl = URL.createObjectURL(audioBlob)
      console.log('🎵 Created audio URL:', audioUrl)
      
      const audio = new Audio(audioUrl)
      
      // Apply browser-specific optimizations
      const performanceConfig = browserCompatibility.getPerformanceRecommendations()
      audio.preload = performanceConfig.preloadStrategy
      
      // Add detailed event logging for debugging
      audio.addEventListener('loadstart', () => console.log('🎵 Audio load started'))
      audio.addEventListener('loadedmetadata', () => {
        console.log('🎵 Audio metadata loaded, duration:', audio.duration, 'seconds')
      })
      audio.addEventListener('canplay', () => console.log('🎵 Audio can play'))
      audio.addEventListener('loadeddata', () => console.log('🎵 Audio data loaded'))
      
      // Note: Don't add oncanplaythrough or onerror here
      // Let the caller set those handlers to avoid conflicts
      
      return audio
    } catch (error) {
      console.error('❌ Error creating audio element:', error)
      throw error
    }
  }

  static async playAudio(audioElement: HTMLAudioElement): Promise<boolean> {
    return await browserCompatibility.playAudioWithUserGesture(audioElement)
  }
}
