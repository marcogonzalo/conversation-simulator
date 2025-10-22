/**
 * Browser compatibility utilities for audio and Web APIs
 */

export interface BrowserCapabilities {
  hasMediaRecorder: boolean;
  hasWebAudioAPI: boolean;
  hasWebSocket: boolean;
  supportedAudioFormats: string[];
  preferredAudioFormat: string;
  browserName: string;
  browserVersion: string;
}

export class BrowserCompatibility {
  private static instance: BrowserCompatibility;
  private capabilities: BrowserCapabilities | null = null;

  private constructor() {}

  static getInstance(): BrowserCompatibility {
    if (!BrowserCompatibility.instance) {
      BrowserCompatibility.instance = new BrowserCompatibility();
    }
    return BrowserCompatibility.instance;
  }

  /**
   * Detect browser capabilities and audio format support
   */
  detectCapabilities(): BrowserCapabilities {
    if (this.capabilities) {
      return this.capabilities;
    }

    // Check if we're in a browser environment
    if (typeof window === 'undefined' || typeof navigator === 'undefined') {
      // Return default capabilities for SSR
      this.capabilities = {
        hasMediaRecorder: false,
        hasWebAudioAPI: false,
        hasWebSocket: false,
        supportedAudioFormats: ['audio/webm;codecs=opus'],
        preferredAudioFormat: 'audio/webm;codecs=opus',
        browserName: 'Server',
        browserVersion: 'unknown'
      };
      return this.capabilities;
    }

    const userAgent = navigator.userAgent;
    const browserInfo = this.getBrowserInfo(userAgent);
    
    // Check MediaRecorder support
    const hasMediaRecorder = typeof MediaRecorder !== 'undefined';
    
    // Check Web Audio API support
    const hasWebAudioAPI = typeof AudioContext !== 'undefined' || 
                          typeof (window as any).webkitAudioContext !== 'undefined';
    
    // Check WebSocket support
    const hasWebSocket = typeof WebSocket !== 'undefined';
    
    // Determine supported audio formats based on browser
    const supportedAudioFormats = this.getSupportedAudioFormats(browserInfo.browserName);
    const preferredAudioFormat = this.getPreferredAudioFormat(browserInfo.browserName);

    this.capabilities = {
      hasMediaRecorder,
      hasWebAudioAPI,
      hasWebSocket,
      supportedAudioFormats,
      preferredAudioFormat,
      browserName: browserInfo.browserName,
      browserVersion: browserInfo.browserVersion
    };

    console.log('🔍 Browser capabilities detected:', this.capabilities);
    return this.capabilities;
  }

  /**
   * Get browser information from user agent
   */
  private getBrowserInfo(userAgent: string): { browserName: string; browserVersion: string } {
    if (userAgent.includes('Firefox/')) {
      const match = userAgent.match(/Firefox\/(\d+\.\d+)/);
      return {
        browserName: 'Firefox',
        browserVersion: match ? match[1] : 'unknown'
      };
    } else if (userAgent.includes('Chrome/') && !userAgent.includes('Edg/')) {
      const match = userAgent.match(/Chrome\/(\d+\.\d+)/);
      return {
        browserName: 'Chrome',
        browserVersion: match ? match[1] : 'unknown'
      };
    } else if (userAgent.includes('Safari/') && !userAgent.includes('Chrome/')) {
      const match = userAgent.match(/Version\/(\d+\.\d+)/);
      return {
        browserName: 'Safari',
        browserVersion: match ? match[1] : 'unknown'
      };
    } else if (userAgent.includes('Edg/')) {
      const match = userAgent.match(/Edg\/(\d+\.\d+)/);
      return {
        browserName: 'Edge',
        browserVersion: match ? match[1] : 'unknown'
      };
    } else {
      return {
        browserName: 'Unknown',
        browserVersion: 'unknown'
      };
    }
  }

  /**
   * Get supported audio formats for specific browser
   */
  private getSupportedAudioFormats(browserName: string): string[] {
    switch (browserName) {
      case 'Firefox':
        return ['audio/webm;codecs=opus', 'audio/ogg;codecs=opus', 'audio/wav'];
      case 'Safari':
        return ['audio/mp4', 'audio/mpeg', 'audio/wav'];
      case 'Chrome':
      case 'Edge':
        return ['audio/webm;codecs=opus', 'audio/mp4', 'audio/wav'];
      default:
        return ['audio/webm;codecs=opus', 'audio/wav'];
    }
  }

  /**
   * Get preferred audio format for specific browser
   */
  private getPreferredAudioFormat(browserName: string): string {
    switch (browserName) {
      case 'Firefox':
        return 'audio/webm;codecs=opus';
      case 'Safari':
        return 'audio/mp4';
      case 'Chrome':
      case 'Edge':
        return 'audio/webm;codecs=opus';
      default:
        return 'audio/webm;codecs=opus';
    }
  }

  /**
   * Check if a specific audio format is supported
   */
  isAudioFormatSupported(format: string): boolean {
    const capabilities = this.detectCapabilities();
    return capabilities.supportedAudioFormats.includes(format);
  }

  /**
   * Get optimal MediaRecorder options for current browser
   */
  getOptimalMediaRecorderOptions(): MediaRecorderOptions {
    const capabilities = this.detectCapabilities();
    
    // Try preferred format first
    if (capabilities.preferredAudioFormat && 
        MediaRecorder.isTypeSupported(capabilities.preferredAudioFormat)) {
      return { mimeType: capabilities.preferredAudioFormat };
    }
    
    // Fallback to first supported format
    for (const format of capabilities.supportedAudioFormats) {
      if (MediaRecorder.isTypeSupported(format)) {
        return { mimeType: format };
      }
    }
    
    // Ultimate fallback
    return {};
  }

  /**
   * Get optimal audio context settings for current browser
   */
  getOptimalAudioContextSettings(): AudioContextOptions {
    const capabilities = this.detectCapabilities();
    
    // Firefox-specific optimizations - use 48kHz to match most audio streams
    if (capabilities.browserName === 'Firefox') {
      return {
        sampleRate: 48000, // Changed from 44100 to match stream sample rates
        latencyHint: 'interactive'
      };
    }
    
    // Safari-specific optimizations
    if (capabilities.browserName === 'Safari') {
      return {
        sampleRate: 48000,
        latencyHint: 'balanced'
      };
    }
    
    // Chrome/Edge optimizations
    return {
      sampleRate: 48000,
      latencyHint: 'interactive'
    };
  }

  /**
   * Get browser-specific performance recommendations
   * 
   * AUDIO PERFORMANCE CONFIGURATION BY BROWSER
   * ===========================================
   * 
   * This configuration optimizes audio behavior for each browser
   * based on differences in their rendering engines and audio processing.
   * 
   * CONFIGURABLE ATTRIBUTES:
   * ------------------------
   * 
   * 1. vadThreshold (Voice Activity Detection Threshold)
   *    - Range: 1-10 (recommended: 3-7)
   *    - Low values (1-3): More sensitive, detects voice with low volume
   *    - High values (6-10): Less sensitive, requires more volume to activate
   *    - Current value: 5 (balance between sensitivity and noise filtering)
   *    - Impact: Affects when voice recording starts
   * 
   * 2. silenceDuration (Silence Duration to Stop Recording)
   *    - Range: 500-5000ms (recommended: 1000-2000ms)
   *    - Low values (500-1000ms): Stops recording quickly, may cut words
   *    - High values (3000-5000ms): Waits longer, may record unnecessary silence
   *    - Current value: 1500ms (1.5 seconds of silence to confirm end of speech)
   *    - Impact: Determines when user is considered to have finished speaking
   * 
   * 3. audioChunkSize (Audio Chunk Size)
   *    - Common values: 256, 512, 1024, 2048, 4096
   *    - Small chunks (256-512): Lower latency, more processing overhead
   *    - Large chunks (2048-4096): Less overhead, higher latency
   *    - Current value: 1024 (optimal balance between latency and performance)
   *    - Impact: Affects audio processing frequency and latency
   * 
   * 4. preloadStrategy (Audio Preload Strategy)
   *    - 'none': No preload, downloads only when playing
   *      * Advantages: Saves bandwidth and memory
   *      * Disadvantages: Notable delay when playing
   *    - 'metadata': Only downloads metadata (duration, size, format)
   *      * Advantages: Knows properties without downloading everything
   *      * Disadvantages: Small delay when playing
   *    - 'auto': Downloads entire audio immediately
   *      * Advantages: Instant playback
   *      * Disadvantages: Consumes more bandwidth and memory
   *    - Impact: Affects user experience and resource usage
   * 
   * BROWSER CONSIDERATIONS:
   * ----------------------
   * - Firefox: Uses Gecko Engine, more conservative with memory
   * - Safari: Uses WebKit, optimized for macOS/iOS
   * - Chrome/Edge: Uses Blink Engine, balance between performance and compatibility
   * 
   * IMPORTANT NOTES:
   * ---------------
   * - VAD Threshold: Very low values may activate with background noise
   * - Silence Duration: Should be consistent to avoid premature cuts
   * - Audio Chunk Size: Directly affects conversation latency
   * - Preload Strategy: Critical for real-time user experience
   */
  getPerformanceRecommendations(): {
    vadThreshold: number;
    silenceDuration: number;
    audioChunkSize: number;
    preloadStrategy: 'auto' | 'metadata' | 'none';
  } {
    const capabilities = this.detectCapabilities();
    
    switch (capabilities.browserName) {
      case 'Firefox':
        return {
          vadThreshold: 25, // Balanced threshold: detects sustained vowels, reduces feedback
          silenceDuration: 1200, // 1.2s for faster cutoff of noise-triggered recordings
          audioChunkSize: 1024,
          preloadStrategy: 'metadata'
        };
      case 'Safari':
        return {
          vadThreshold: 25, // Balanced threshold: detects sustained vowels, reduces feedback
          silenceDuration: 1200, // 1.2s for faster cutoff of noise-triggered recordings
          audioChunkSize: 2048,
          preloadStrategy: 'auto'
        };
      case 'Chrome':
      case 'Edge':
        return {
          vadThreshold: 25, // Balanced threshold: detects sustained vowels, reduces feedback
          silenceDuration: 1200, // 1.2s for faster cutoff of noise-triggered recordings
          audioChunkSize: 1024,
          preloadStrategy: 'auto'
        };
      default:
        return {
          vadThreshold: 25, // Balanced threshold: detects sustained vowels, reduces feedback
          silenceDuration: 1200, // 1.2s for faster cutoff of noise-triggered recordings
          audioChunkSize: 1024,
          preloadStrategy: 'metadata'
        };
    }
  }

  /**
   * Check if browser needs special handling for audio playback
   */
  needsSpecialAudioHandling(): boolean {
    const capabilities = this.detectCapabilities();
    return capabilities.browserName === 'Safari' || capabilities.browserName === 'Firefox';
  }

  /**
   * Safari-specific audio playback handler
   * Safari requires user interaction before allowing audio playback
   */
  async playAudioWithUserGesture(audioElement: HTMLAudioElement): Promise<boolean> {
    const capabilities = this.detectCapabilities()
    
    if (capabilities.browserName !== 'Safari') {
      // For non-Safari browsers, just play normally
      try {
        await audioElement.play()
        return true
      } catch (error) {
        console.error('❌ Audio play failed:', error)
        return false
      }
    }
    
    // Safari-specific handling
    try {
      // First, try to play with user gesture context
      await audioElement.play()
      return true
    } catch (error) {
      // If blocked, try to enable audio context first
      if (typeof window !== 'undefined' && window.AudioContext) {
        try {
          const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
          
          if (audioContext.state === 'suspended') {
            await audioContext.resume()
          }
          
          // Close the context
          await audioContext.close()
        } catch (contextError) {
          // Audio context could not be resumed
        }
      }
      
      // Try playing again
      try {
        await audioElement.play()
        return true
      } catch (retryError) {
        console.error('Safari: Audio play failed after retry:', retryError)
        return false
      }
    }
  }

  /**
   * Get optimal WebSocket configuration for current browser
   */
  getOptimalWebSocketConfig(): {
    protocols?: string[];
    binaryType: BinaryType;
    reconnectDelay: number;
  } {
    const capabilities = this.detectCapabilities();
    
    return {
      binaryType: 'arraybuffer',
      reconnectDelay: capabilities.browserName === 'Firefox' ? 2000 : 1000
    };
  }
}

export const browserCompatibility = BrowserCompatibility.getInstance();
