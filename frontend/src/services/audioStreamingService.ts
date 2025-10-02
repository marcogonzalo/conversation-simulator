/**
 * Audio Streaming Service
 * Handles streaming audio playback for real-time conversation experience with browser compatibility
 */

import { browserCompatibility } from '../utils/browserCompatibility'

export class AudioStreamingService {
  private audioQueue: HTMLAudioElement[] = []
  private isPlaying = false
  private currentAudio: HTMLAudioElement | null = null
  private onPlaybackStart?: () => void
  private onPlaybackEnd?: () => void

  constructor(
    onPlaybackStart?: () => void,
    onPlaybackEnd?: () => void
  ) {
    this.onPlaybackStart = onPlaybackStart
    this.onPlaybackEnd = onPlaybackEnd
  }

  /**
   * Add audio chunk to the streaming queue
   */
  addAudioChunk(audioData: string): void {
    try {
      const capabilities = browserCompatibility.detectCapabilities()
      const performanceConfig = browserCompatibility.getPerformanceRecommendations()
      
      // Decode base64 to get audio data
      const audioDataBytes = Uint8Array.from(atob(audioData), c => c.charCodeAt(0))
      
      // Use browser-specific MIME type
      const mimeType = capabilities.preferredAudioFormat || 'audio/webm'
      
      // Create audio blob with browser-appropriate MIME type
      const audioBlob = new Blob([audioDataBytes], { type: mimeType })
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      
      // Apply browser-specific preload strategy
      audio.preload = performanceConfig.preloadStrategy
      
      // Add to queue
      this.audioQueue.push(audio)
      
      // Start playing if not already playing
      if (!this.isPlaying) {
        this.playNext()
      }
      
    } catch (error) {
      console.error('❌ Error adding audio chunk:', error)
    }
  }

  /**
   * Play the next audio in queue
   */
  private playNext(): void {
    if (this.audioQueue.length === 0) {
      this.isPlaying = false
      this.currentAudio = null
      this.onPlaybackEnd?.()
      return
    }

    const audio = this.audioQueue.shift()!
    this.currentAudio = audio
    this.isPlaying = true

    // Notify playback start (only for first chunk)
    if (this.audioQueue.length === 0) {
      this.onPlaybackStart?.()
    }

    // Set up event handlers
    audio.oncanplaythrough = async () => {
      const playSuccess = await browserCompatibility.playAudioWithUserGesture(audio)
      if (!playSuccess) {
        console.error('AudioStreamingService: Audio play failed, trying next chunk')
        this.playNext() // Try next chunk
      }
    }

    audio.onended = () => {
      URL.revokeObjectURL(audio.src)
      
      // Immediate transition for smoother playback
      this.playNext() // Play next chunk immediately
    }

    audio.onerror = (e) => {
      console.error('❌ Audio chunk error:', e)
      URL.revokeObjectURL(audio.src)
      
      // Small delay before trying next chunk
      setTimeout(() => {
        this.playNext() // Try next chunk
      }, 100)
    }

    // Start loading
    audio.load()
  }

  /**
   * Stop all audio playback and clear queue
   */
  stop(): void {
    console.log('🎵 Stopping audio streaming')
    
    // Stop current audio
    if (this.currentAudio) {
      this.currentAudio.pause()
      this.currentAudio.currentTime = 0
      URL.revokeObjectURL(this.currentAudio.src)
      this.currentAudio = null
    }

    // Clear queue
    this.audioQueue.forEach(audio => {
      audio.pause()
      URL.revokeObjectURL(audio.src)
    })
    this.audioQueue = []
    
    this.isPlaying = false
  }

  /**
   * Check if currently playing
   */
  getIsPlaying(): boolean {
    return this.isPlaying
  }

  /**
   * Get queue length
   */
  getQueueLength(): number {
    return this.audioQueue.length
  }

  /**
   * Check if there are pending chunks in the queue
   */
  hasPendingChunks(): boolean {
    return this.audioQueue.length > 0
  }

  /**
   * Check if audio is actually playing (not paused or ended)
   */
  isActuallyPlaying(): boolean {
    if (!this.currentAudio) return false
    return !this.currentAudio.paused && 
           !this.currentAudio.ended && 
           this.currentAudio.currentTime > 0 &&
           this.isPlaying
  }
}
