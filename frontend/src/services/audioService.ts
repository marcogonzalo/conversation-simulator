/**
 * Audio Service
 * Handles audio conversion and WebSocket communication
 */

export class AudioService {
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
      // Decode base64 to get WebM data
      const webmData = Uint8Array.from(atob(audioData), c => c.charCodeAt(0))
      
      // Create WebM audio blob
      const audioBlob = new Blob([webmData], { type: 'audio/webm; codecs=opus' })
      const audioUrl = URL.createObjectURL(audioBlob)
      
      const audio = new Audio(audioUrl)
      return audio
    } catch (error) {
      console.error('Error creating audio element:', error)
      throw error
    }
  }
}
