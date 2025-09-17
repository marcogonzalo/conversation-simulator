import { useState, useRef, useCallback, useEffect } from 'react'

interface UseAudioRecordingProps {
  onAudioReady: (audioBlob: Blob) => void
  isWaitingForResponse: boolean
  isEnding: boolean
}

export function useAudioRecording({ onAudioReady, isWaitingForResponse, isEnding }: UseAudioRecordingProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const dataArrayRef = useRef<Uint8Array | null>(null)
  const vadIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const stopRecording = useCallback(() => {
    console.log('🛑 stopRecording called')
    
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
    
    // Cleanup VAD
    if (vadIntervalRef.current) {
      console.log('🛑 Cleaning up VAD interval')
      clearInterval(vadIntervalRef.current)
      vadIntervalRef.current = null
    }
    
    if (audioContextRef.current) {
      console.log('🛑 Closing audio context')
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    
    setIsSpeaking(false)
  }, [isRecording])


  const setupVoiceActivityDetection = useCallback((stream: MediaStream) => {
    try {
      audioContextRef.current = new AudioContext()
      const source = audioContextRef.current.createMediaStreamSource(stream)
      analyserRef.current = audioContextRef.current.createAnalyser()
      
      analyserRef.current.fftSize = 256
      analyserRef.current.smoothingTimeConstant = 0.8
      source.connect(analyserRef.current)
      
      const bufferLength = analyserRef.current.frequencyBinCount
      dataArrayRef.current = new Uint8Array(bufferLength)
      
      const VAD_THRESHOLD = 15 // Lowered threshold for better sensitivity
      const SILENCE_DURATION_THRESHOLD = 2000 // 2 seconds of silence before stopping
      let vadLogCounter = 0
      let silenceStartTime: number | null = null
      let lastVoiceTime = 0
      
      const checkVoiceActivity = () => {
        if (!analyserRef.current || !dataArrayRef.current) return
        
        const now = Date.now()
        
        // Create a new Uint8Array with proper typing
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
        analyserRef.current.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length
        
        // Log every second for debugging
        vadLogCounter++
        if (vadLogCounter % 10 === 0) {
          console.log(`🎤 VAD - Volume: ${average.toFixed(2)}, Speaking: ${isSpeaking}, Recording: ${isRecording}`)
        }
        
        if (average > VAD_THRESHOLD) {
          // Voice detected
          if (!isSpeaking) {
            console.log(`🎤 Voice detected (volume: ${average.toFixed(2)})`)
            setIsSpeaking(true)
          }
          lastVoiceTime = now
          silenceStartTime = null // Reset silence timer
        } else {
          // Silence detected
          if (isSpeaking) {
            console.log(`🎤 Silence detected (volume: ${average.toFixed(2)})`)
            setIsSpeaking(false)
            
            // Start silence timer if not already started
            if (silenceStartTime === null) {
              silenceStartTime = now
            }
          }
          
          // Check if we've had enough silence to stop recording
          if (isRecording && !isWaitingForResponse && silenceStartTime !== null) {
            const silenceDuration = now - silenceStartTime
            const timeSinceLastVoice = now - lastVoiceTime
            
            // Only stop if we've had silence for the threshold duration
            // and there has been at least some voice activity before
            if (silenceDuration >= SILENCE_DURATION_THRESHOLD && lastVoiceTime > 0) {
              console.log(`🎤 Stopping recording due to ${silenceDuration}ms of silence`)
              stopRecording()
            }
          }
        }
      }
      
      vadIntervalRef.current = setInterval(checkVoiceActivity, 100)
    } catch (error) {
      console.error('❌ Error setting up VAD:', error)
    }
  }, [isSpeaking, isRecording, isWaitingForResponse, stopRecording])

  // Setup VAD when recording starts
  useEffect(() => {
    if (isRecording && streamRef.current) {
      console.log('🎤 Setting up VAD for recording...')
      setupVoiceActivityDetection(streamRef.current)
    }
  }, [isRecording, setupVoiceActivityDetection])

  const startRecording = useCallback(async () => {
    try {
      console.log('🎤 Starting recording...')
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        
        if (audioBlob.size > 1000) {
          console.log('🎤 Audio ready, size:', audioBlob.size, 'bytes')
          onAudioReady(audioBlob)
        } else {
          console.log('🎤 Audio too small, skipping')
        }
        
        // Cleanup stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
          streamRef.current = null
        }
      }
      
      mediaRecorder.start()
      setIsRecording(true)
      
    } catch (error) {
      console.error('❌ Error starting recording:', error)
    }
  }, [setupVoiceActivityDetection, onAudioReady])

  const cleanup = useCallback(() => {
    stopRecording()
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
  }, [stopRecording])

  // Cleanup when ending
  useEffect(() => {
    if (isEnding) {
      console.log('🛑 isEnding is true, cleaning up VAD and recording')
      cleanup()
    }
  }, [isEnding, cleanup])

  return {
    isRecording,
    isSpeaking,
    startRecording,
    stopRecording,
    cleanup
  }
}
