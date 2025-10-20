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
  private minBufferSize = 1  // Minimum chunks to buffer before playback (1 for immediate playback)
  private maxQueueSize = 30  // Maximum chunks in queue to prevent memory issues
  private isBuffering = true // Buffer first chunk before playing

  constructor(
    onPlaybackStart?: () => void,
    onPlaybackEnd?: () => void
  ) {
    this.onPlaybackStart = onPlaybackStart
    this.onPlaybackEnd = onPlaybackEnd
    this.isBuffering = true // Ensure buffering is true on init
  }

  /**
   * Detect audio format from binary data
   */
  private detectAudioFormat(audioDataBytes: Uint8Array): string {
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

  /**
   * Add audio chunk to the streaming queue
   */
  addAudioChunk(audioData: string): void {
    try {
      const performanceConfig = browserCompatibility.getPerformanceRecommendations()
      
      // Decode base64 to get audio data
      const audioDataBytes = Uint8Array.from(atob(audioData), c => c.charCodeAt(0))
      
      // Detect audio format from binary data
      const mimeType = this.detectAudioFormat(audioDataBytes)
      console.log(`🎵 Detected audio format: ${mimeType}, size: ${audioDataBytes.length} bytes`)
      
      // Create audio blob with detected MIME type
      const audioBlob = new Blob([audioDataBytes], { type: mimeType })
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      
      // Apply browser-specific preload strategy
      audio.preload = performanceConfig.preloadStrategy
      
      // Add error handler for playback issues
      audio.onerror = (e) => {
        console.error('❌ Audio playback error:', e)
        console.error('Audio details:', {
          src: audio.src,
          error: audio.error,
          networkState: audio.networkState,
          readyState: audio.readyState
        })
      }
      
      // Add load handler to confirm audio is ready
      audio.onloadeddata = () => {
        console.log('✅ Audio loaded successfully, duration:', audio.duration, 'seconds')
      }
      
      // Check queue size limit to prevent memory issues
      if (this.audioQueue.length >= this.maxQueueSize) {
        console.warn(`⚠️ Audio queue full (${this.audioQueue.length}/${this.maxQueueSize}), dropping oldest chunk`)
        const dropped = this.audioQueue.shift()
        if (dropped) {
          URL.revokeObjectURL(dropped.src)
        }
      }
      
      // Add to queue
      this.audioQueue.push(audio)
      console.log(`🎵 Added audio chunk to queue (queue size: ${this.audioQueue.length})`)
      
      // Start playing when we have minimum buffer
      if (!this.isPlaying && this.audioQueue.length >= this.minBufferSize) {
        console.log(`🎵 Starting playback (buffered ${this.audioQueue.length} chunks)`)
        this.isBuffering = false
        this.playNext()
      } else if (this.isBuffering && this.audioQueue.length < this.minBufferSize) {
        console.log(`🎵 Buffering... (${this.audioQueue.length}/${this.minBufferSize} chunks)`)
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
    
    // Set isPlaying before anything else to prevent race conditions
    const wasPlaying = this.isPlaying
    this.isPlaying = true

    console.log(`🎵 Playing audio (${this.audioQueue.length} remaining in queue)`)

    // Notify playback start ONLY on the first chunk
    if (!wasPlaying) {
      this.onPlaybackStart?.()
    }

    // Set up event handlers
    audio.oncanplaythrough = async () => {
      console.log('🎵 Audio can play through, starting playback...')
      const playSuccess = await browserCompatibility.playAudioWithUserGesture(audio)
      if (!playSuccess) {
        console.error('❌ Audio play failed (user gesture required?), trying next chunk')
        this.playNext() // Try next chunk
      } else {
        console.log('✅ Audio playback started successfully')
      }
    }

    audio.onended = () => {
      console.log('🎵 Audio ended, cleaning up and playing next')
      URL.revokeObjectURL(audio.src)
      
      // Immediate transition for smoother playback
      this.playNext() // Play next chunk immediately
    }

    audio.onerror = (e) => {
      console.error('❌ Audio chunk error during playback:', e, audio.error)
      URL.revokeObjectURL(audio.src)
      
      // Keep isPlaying true if there are more chunks to prevent recording during errors
      console.log(`⚠️ Audio error, ${this.audioQueue.length} chunks remaining`)
      
      // Small delay before trying next chunk
      setTimeout(() => {
        this.playNext() // Try next chunk (will set isPlaying = false if queue empty)
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
    this.isBuffering = true  // Reset buffering state for next audio
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
