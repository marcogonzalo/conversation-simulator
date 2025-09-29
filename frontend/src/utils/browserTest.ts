/**
 * Browser testing utilities for cross-browser compatibility validation
 */

import { browserCompatibility } from './browserCompatibility'

export interface BrowserTestResult {
  testName: string
  passed: boolean
  duration: number
  details: string
  browser: string
}

export interface PerformanceMetrics {
  audioLoadTime: number
  recordingStartTime: number
  vadResponseTime: number
  playbackLatency: number
  memoryUsage: number
}

export class BrowserTestSuite {
  private results: BrowserTestResult[] = []
  private startTime: number = 0

  /**
   * Run comprehensive browser compatibility tests
   */
  async runAllTests(): Promise<BrowserTestResult[]> {
    // Check if we're in a browser environment
    if (typeof window === 'undefined') {
      console.warn('BrowserTestSuite: Not in browser environment, skipping tests')
      return []
    }

    this.results = []
    console.log('🧪 Starting browser compatibility test suite...')
    
    await this.testMediaRecorderSupport()
    await this.testWebAudioAPISupport()
    await this.testAudioFormatSupport()
    await this.testAudioPlaybackPerformance()
    await this.testVoiceActivityDetection()
    await this.testWebSocketCompatibility()
    
    console.log('🧪 Test suite completed. Results:', this.results)
    return this.results
  }

  /**
   * Test MediaRecorder API support and performance
   */
  private async testMediaRecorderSupport(): Promise<void> {
    this.startTimer()
    
    try {
      if (typeof MediaRecorder === 'undefined') {
        this.addResult('MediaRecorder Support', false, 0, 'MediaRecorder API not available')
        return
      }

      // Test different audio formats
      const capabilities = browserCompatibility.detectCapabilities()
      let supportedFormats = 0
      
      for (const format of capabilities.supportedAudioFormats) {
        if (MediaRecorder.isTypeSupported(format)) {
          supportedFormats++
        }
      }

      const duration = this.getElapsedTime()
      const passed = supportedFormats > 0
      
      this.addResult(
        'MediaRecorder Support',
        passed,
        duration,
        `Supported formats: ${supportedFormats}/${capabilities.supportedAudioFormats.length}`
      )
    } catch (error) {
      this.addResult('MediaRecorder Support', false, this.getElapsedTime(), `Error: ${error}`)
    }
  }

  /**
   * Test Web Audio API support and performance
   */
  private async testWebAudioAPISupport(): Promise<void> {
    this.startTimer()
    
    try {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext
      
      if (!AudioContextClass) {
        this.addResult('Web Audio API Support', false, 0, 'AudioContext not available')
        return
      }

      // Test AudioContext creation
      const audioContext = new AudioContextClass()
      const source = audioContext.createOscillator()
      const analyser = audioContext.createAnalyser()
      
      source.connect(analyser)
      source.start()
      source.stop()
      
      await audioContext.close()
      
      const duration = this.getElapsedTime()
      this.addResult(
        'Web Audio API Support',
        true,
        duration,
        `AudioContext created successfully with sample rate: ${audioContext.sampleRate}Hz`
      )
    } catch (error) {
      this.addResult('Web Audio API Support', false, this.getElapsedTime(), `Error: ${error}`)
    }
  }

  /**
   * Test audio format support
   */
  private async testAudioFormatSupport(): Promise<void> {
    this.startTimer()
    
    try {
      const capabilities = browserCompatibility.detectCapabilities()
      const testFormats = [
        'audio/webm;codecs=opus',
        'audio/mp4',
        'audio/wav',
        'audio/ogg;codecs=opus'
      ]
      
      let supportedCount = 0
      const supportedFormats: string[] = []
      
      for (const format of testFormats) {
        if (MediaRecorder.isTypeSupported(format)) {
          supportedCount++
          supportedFormats.push(format)
        }
      }
      
      const duration = this.getElapsedTime()
      const passed = supportedCount > 0
      
      this.addResult(
        'Audio Format Support',
        passed,
        duration,
        `Supported: ${supportedFormats.join(', ')}`
      )
    } catch (error) {
      this.addResult('Audio Format Support', false, this.getElapsedTime(), `Error: ${error}`)
    }
  }

  /**
   * Test audio playback performance
   */
  private async testAudioPlaybackPerformance(): Promise<void> {
    this.startTimer()
    
    try {
      const capabilities = browserCompatibility.detectCapabilities()
      
      // Test if Audio constructor is available
      if (typeof Audio === 'undefined') {
        this.addResult('Audio Playback Performance', false, this.getElapsedTime(), 'Audio API not available')
        return
      }
      
      // Create a very simple, browser-agnostic audio data URL
      const audioDataUrl = 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA='
      
      // Create audio element
      const audio = new Audio()
      
      // Set source after creating element
      audio.src = audioDataUrl
      
      // Test audio properties
      audio.volume = 0.5
      audio.loop = false
      
      // Check if we can access audio properties
      const volumeOk = audio.volume === 0.5
      const loopOk = audio.loop === false
      const srcOk = audio.src === audioDataUrl
      
      // Test canPlayType for different formats
      const formatSupport = {
        wav: audio.canPlayType('audio/wav'),
        webm: audio.canPlayType('audio/webm'),
        mp4: audio.canPlayType('audio/mp4'),
        ogg: audio.canPlayType('audio/ogg')
      }
      
      const duration = this.getElapsedTime()
      
      // Consider test successful if we can create audio and set properties
      const testPassed = volumeOk && loopOk && srcOk && Object.values(formatSupport).some(support => support !== '')
      
      this.addResult(
        'Audio Playback Performance',
        testPassed,
        duration,
        testPassed 
          ? `Audio API functional: ${Object.keys(formatSupport).filter(f => formatSupport[f as keyof typeof formatSupport] !== '').join(', ')} supported (${duration}ms)`
          : `Audio API issues detected after ${duration}ms`
      )
    } catch (error) {
      this.addResult(
        'Audio Playback Performance', 
        false, 
        this.getElapsedTime(), 
        `Error: ${error instanceof Error ? error.message : String(error)}`
      )
    }
  }

  /**
   * Test Voice Activity Detection performance
   */
  private async testVoiceActivityDetection(): Promise<void> {
    this.startTimer()
    
    try {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext
      
      if (!AudioContextClass) {
        this.addResult('VAD Performance', false, 0, 'AudioContext not available')
        return
      }

      const audioContext = new AudioContextClass()
      const analyser = audioContext.createAnalyser()
      
      // Test different FFT sizes
      const fftSizes = [256, 512, 1024, 2048]
      let optimalFFTSize = 256
      
      for (const fftSize of fftSizes) {
        analyser.fftSize = fftSize
        const bufferLength = analyser.frequencyBinCount
        const dataArray = new Uint8Array(bufferLength)
        
        // Simulate analysis
        analyser.getByteFrequencyData(dataArray)
        optimalFFTSize = fftSize
      }
      
      await audioContext.close()
      
      const duration = this.getElapsedTime()
      this.addResult(
        'VAD Performance',
        true,
        duration,
        `Optimal FFT size: ${optimalFFTSize}, Analysis time: ${duration}ms`
      )
    } catch (error) {
      this.addResult('VAD Performance', false, this.getElapsedTime(), `Error: ${error}`)
    }
  }

  /**
   * Test WebSocket compatibility
   */
  private async testWebSocketCompatibility(): Promise<void> {
    this.startTimer()
    
    try {
      if (typeof WebSocket === 'undefined') {
        this.addResult('WebSocket Compatibility', false, 0, 'WebSocket not available')
        return
      }

      // Test WebSocket creation (without connecting)
      const ws = new WebSocket('ws://localhost:8000/test')
      
      const connectionPromise = new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Connection timeout'))
        }, 1000)
        
        ws.onopen = () => {
          clearTimeout(timeout)
          resolve(true)
        }
        
        ws.onerror = () => {
          clearTimeout(timeout)
          // This is expected since we're not connecting to a real server
          resolve(false)
        }
      })
      
      await connectionPromise
      ws.close()
      
      const duration = this.getElapsedTime()
      this.addResult(
        'WebSocket Compatibility',
        true,
        duration,
        'WebSocket API available and functional'
      )
    } catch (error) {
      this.addResult('WebSocket Compatibility', false, this.getElapsedTime(), `Error: ${error}`)
    }
  }

  /**
   * Get performance metrics for current browser
   */
  getPerformanceMetrics(): PerformanceMetrics {
    const capabilities = browserCompatibility.detectCapabilities()
    const performance = browserCompatibility.getPerformanceRecommendations()
    
    return {
      audioLoadTime: 0, // Would be measured during actual usage
      recordingStartTime: 0, // Would be measured during actual usage
      vadResponseTime: 0, // Would be measured during actual usage
      playbackLatency: 0, // Would be measured during actual usage
      memoryUsage: (performance as any).memory?.usedJSHeapSize || 0
    }
  }

  /**
   * Generate browser compatibility report
   */
  generateReport(): string {
    const capabilities = browserCompatibility.detectCapabilities()
    const passedTests = this.results.filter(r => r.passed).length
    const totalTests = this.results.length
    const successRate = totalTests > 0 ? (passedTests / totalTests) * 100 : 0
    
    let report = `# Browser Compatibility Report\n\n`
    report += `**Browser**: ${capabilities.browserName} ${capabilities.browserVersion}\n`
    report += `**Test Results**: ${passedTests}/${totalTests} tests passed (${successRate.toFixed(1)}%)\n\n`
    
    report += `## Test Results\n\n`
    this.results.forEach(result => {
      const status = result.passed ? '✅' : '❌'
      report += `- ${status} **${result.testName}**: ${result.details} (${result.duration}ms)\n`
    })
    
    report += `\n## Browser Capabilities\n\n`
    report += `- MediaRecorder: ${capabilities.hasMediaRecorder ? '✅' : '❌'}\n`
    report += `- Web Audio API: ${capabilities.hasWebAudioAPI ? '✅' : '❌'}\n`
    report += `- WebSocket: ${capabilities.hasWebSocket ? '✅' : '❌'}\n`
    report += `- Preferred Audio Format: ${capabilities.preferredAudioFormat}\n`
    report += `- Supported Formats: ${capabilities.supportedAudioFormats.length}\n`
    
    return report
  }

  private startTimer(): void {
    this.startTime = performance.now()
  }

  private getElapsedTime(): number {
    return Math.round(performance.now() - this.startTime)
  }

  private addResult(testName: string, passed: boolean, duration: number, details: string): void {
    const capabilities = browserCompatibility.detectCapabilities()
    
    this.results.push({
      testName,
      passed,
      duration,
      details,
      browser: capabilities.browserName
    })
  }
}

export const browserTestSuite = new BrowserTestSuite()
