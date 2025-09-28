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
      console.log('🎵 Creating audio element from base64 data...')
      
      // Decode base64 to get WebM data
      const webmData = Uint8Array.from(atob(audioData), c => c.charCodeAt(0))
      console.log('🎵 Decoded WebM data:', webmData.length, 'bytes')
      
      // Create WebM audio blob with proper MIME type
      const audioBlob = new Blob([webmData], { type: 'audio/webm' })
      console.log('🎵 Created audio blob:', audioBlob.size, 'bytes, type:', audioBlob.type)
      
      const audioUrl = URL.createObjectURL(audioBlob)
      console.log('🎵 Created audio URL:', audioUrl)
      
      const audio = new Audio(audioUrl)
      
      // Add detailed error logging
      audio.addEventListener('error', (e) => {
        console.error('❌ Audio element error:', e)
        console.error('❌ Audio error details:', {
          error: audio.error,
          networkState: audio.networkState,
          readyState: audio.readyState,
          src: audio.src,
          blobSize: audioBlob.size,
          blobType: audioBlob.type
        })
      })
      
      audio.addEventListener('loadstart', () => console.log('🎵 Audio load started'))
      audio.addEventListener('loadedmetadata', () => console.log('🎵 Audio metadata loaded'))
      audio.addEventListener('canplay', () => console.log('🎵 Audio can play'))
      audio.addEventListener('canplaythrough', () => console.log('🎵 Audio can play through'))
      
      return audio
    } catch (error) {
      console.error('❌ Error creating audio element:', error)
      throw error
    }
  }
}
