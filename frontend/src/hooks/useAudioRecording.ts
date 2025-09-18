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
  const isMountedRef = useRef(true)
  const isCleanedUpRef = useRef(false)

  const stopRecording = useCallback(() => {
    // Prevent multiple calls
    if (!isRecording) {
      return
    }
    
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
    
    // Cleanup VAD
    if (vadIntervalRef.current) {
      clearInterval(vadIntervalRef.current)
      vadIntervalRef.current = null
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    
    setIsSpeaking(false)
  }, [isRecording])


  const setupVoiceActivityDetection = useCallback((stream: MediaStream) => {
    try {
      // Check if component is cleaned up or unmounted
      if (isCleanedUpRef.current || !isMountedRef.current) {
        return
      }
      
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
      let hasDetectedVoice = false // Track if we've detected any voice at all
      let isProcessingStop = false // Prevent multiple stop calls
      
      const checkVoiceActivity = () => {
        // Early return if component is unmounted, cleaned up, not recording, already processing stop, or ending
        if (!isMountedRef.current || isCleanedUpRef.current || !isRecording || isProcessingStop || isEnding || !analyserRef.current || !dataArrayRef.current) {
          // Stop the interval immediately if conditions are not met
          if (vadIntervalRef.current) {
            clearInterval(vadIntervalRef.current)
            vadIntervalRef.current = null
          }
          return
        }
        
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
          hasDetectedVoice = true // Mark that we've detected voice
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
          // Only if we're not waiting for response and we've detected voice before
          if (!isWaitingForResponse && silenceStartTime !== null && hasDetectedVoice) {
            const silenceDuration = now - silenceStartTime
            
            // Only stop if we've had silence for the threshold duration
            if (silenceDuration >= SILENCE_DURATION_THRESHOLD) {
              isProcessingStop = true // Prevent multiple calls
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
  }, [isSpeaking, isRecording, isWaitingForResponse, isEnding, stopRecording])

  // Setup VAD when recording starts
  useEffect(() => {
    if (isRecording && streamRef.current) {
      setupVoiceActivityDetection(streamRef.current)
    }
  }, [isRecording, setupVoiceActivityDetection])

  const startRecording = useCallback(async () => {
    try {
      console.log('🎤 Starting recording...')
      
      // Check if component is cleaned up or unmounted
      if (isCleanedUpRef.current || !isMountedRef.current) {
        return
      }
      
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
          onAudioReady(audioBlob)
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
    // Mark as cleaned up immediately
    isCleanedUpRef.current = true
    
    // Force cleanup VAD immediately - try multiple times to ensure it's cleared
    if (vadIntervalRef.current) {
      clearInterval(vadIntervalRef.current)
      vadIntervalRef.current = null
    }
    
    // Additional cleanup attempt after a short delay
    setTimeout(() => {
      if (vadIntervalRef.current) {
        clearInterval(vadIntervalRef.current)
        vadIntervalRef.current = null
      }
    }, 100)
    
    // Stop recording
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current = null
    }
    
    // Force cleanup audio context
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    
    // Stop all media tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop()
      })
      streamRef.current = null
    }
    
    // Reset all states
    setIsRecording(false)
    setIsSpeaking(false)
  }, [isRecording])

  // Cleanup when ending
  useEffect(() => {
    if (isEnding) {
      console.log('🛑 Cleaning up VAD and recording')
      cleanup()
    }
  }, [isEnding, cleanup])

  // Immediate VAD cleanup when ending
  useEffect(() => {
    if (isEnding) {
      isCleanedUpRef.current = true
      
      if (vadIntervalRef.current) {
        clearInterval(vadIntervalRef.current)
        vadIntervalRef.current = null
      }
      
      // Additional cleanup attempts
      setTimeout(() => {
        if (vadIntervalRef.current) {
          clearInterval(vadIntervalRef.current)
          vadIntervalRef.current = null
        }
      }, 50)
      
      setTimeout(() => {
        if (vadIntervalRef.current) {
          clearInterval(vadIntervalRef.current)
          vadIntervalRef.current = null
        }
      }, 200)
    }
  }, [isEnding])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false
      isCleanedUpRef.current = true
      
      // Force cleanup everything multiple times
      if (vadIntervalRef.current) {
        clearInterval(vadIntervalRef.current)
        vadIntervalRef.current = null
      }
      
      // Additional cleanup attempts
      setTimeout(() => {
        if (vadIntervalRef.current) {
          clearInterval(vadIntervalRef.current)
          vadIntervalRef.current = null
        }
      }, 0)
      
      if (audioContextRef.current) {
        audioContextRef.current.close()
        audioContextRef.current = null
      }
      
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
        streamRef.current = null
      }
      
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current = null
      }
    }
  }, [])

  return {
    isRecording,
    isSpeaking,
    startRecording,
    stopRecording,
    cleanup
  }
}
