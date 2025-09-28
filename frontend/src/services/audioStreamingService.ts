/**
 * Audio Streaming Service
 * Handles streaming audio playback for real-time conversation experience
 */

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
      
      // Decode base64 to get WebM data
      const webmData = Uint8Array.from(atob(audioData), c => c.charCodeAt(0))
      
      // Create WebM audio blob
      const audioBlob = new Blob([webmData], { type: 'audio/webm' })
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      
      // Preload the audio for smoother playback
      audio.preload = 'auto'
      
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
    audio.oncanplaythrough = () => {
      audio.play().catch(e => {
        console.error('❌ Audio play failed:', e)
        this.playNext() // Try next chunk
      })
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
}
