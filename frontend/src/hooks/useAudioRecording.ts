import { useState, useRef, useCallback, useEffect } from 'react'
import { apiConfig } from '@/config/api'
import { browserCompatibility } from '../utils/browserCompatibility'

interface UseAudioRecordingProps {
  onAudioReady: (audioBlob: Blob) => void
  isWaitingForResponse: boolean
  isEnding: boolean
  isPlaying?: boolean
  onStartRecording?: () => void // Callback when recording starts
  onFallbackStop?: () => void // Callback when fallback stops recording
}

export function useAudioRecording({ onAudioReady, isWaitingForResponse, isEnding, isPlaying = false, onStartRecording, onFallbackStop }: UseAudioRecordingProps) {
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
  
  // VAD state variables that persist across setupVoiceActivityDetection calls
  const hasDetectedVoiceRef = useRef(false)
  const silenceStartTimeRef = useRef<number | null>(null)
  const lastVoiceTimeRef = useRef(0)
  const isProcessingStopRef = useRef(false)
  const lastSilenceResetRef = useRef(0) // Track last silence timer reset to prevent rapid resets
  const recordingStartTimeRef = useRef(0) // Track when recording started for fallback
  const isSendingAudioRef = useRef(false) // Prevent multiple simultaneous audio sends
  const isFallbackStopRef = useRef(false) // Track if recording was stopped by fallback

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
  }, [isRecording])


  const setupVoiceActivityDetection = useCallback(async (stream: MediaStream) => {
    try {
      // Check if component is cleaned up or unmounted
      if (isCleanedUpRef.current || !isMountedRef.current) {
        return
      }
      
      // CRITICAL: Clear any existing VAD interval before creating a new one
      if (vadIntervalRef.current) {
        clearInterval(vadIntervalRef.current)
        vadIntervalRef.current = null
      }
      
      const capabilities = browserCompatibility.detectCapabilities()
      const performanceConfig = browserCompatibility.getPerformanceRecommendations()
      const audioContextOptions = browserCompatibility.getOptimalAudioContextSettings()
      
      // Create AudioContext with browser-specific settings
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)(audioContextOptions)
      
      // Firefox fix: Ensure we use the same sample rate as the stream
      const streamSampleRate = stream.getAudioTracks()[0]?.getSettings()?.sampleRate || 48000
      if (audioContextRef.current.sampleRate !== streamSampleRate) {
        console.log('🔧 Firefox: Recreating AudioContext to match stream sample rate:', streamSampleRate)
        await audioContextRef.current.close()
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
          ...audioContextOptions,
          sampleRate: streamSampleRate
        })
      }
      
      const source = audioContextRef.current.createMediaStreamSource(stream)
      analyserRef.current = audioContextRef.current.createAnalyser()
      
      // Browser-specific FFT size optimization
      analyserRef.current.fftSize = performanceConfig.audioChunkSize
      // Browser-specific smoothing for better performance
      analyserRef.current.smoothingTimeConstant = capabilities.browserName === 'Firefox' ? 0.9 : 0.8
      source.connect(analyserRef.current)
      
      const bufferLength = analyserRef.current.frequencyBinCount
      dataArrayRef.current = new Uint8Array(bufferLength)
      
      // Dual threshold strategy to handle sustained vowels:
      // - HIGH threshold (20) to START detection (prevents feedback from playback)
      // - LOW threshold (5) to MAINTAIN detection (allows sustained low-volume vowels)
      const VAD_THRESHOLD_HIGH = 20  // Fixed threshold for starting detection
      const VAD_THRESHOLD_LOW = 5    // Fixed threshold for maintaining detection
      const SILENCE_DURATION_THRESHOLD = performanceConfig.silenceDuration
      let vadLogCounter = 0
      
      const checkVoiceActivity = () => {
        // Early return if component is unmounted, cleaned up, not recording, already processing stop, ending, or audio is playing
        if (!isMountedRef.current || isCleanedUpRef.current || !isRecording || isProcessingStopRef.current || isEnding || isPlaying || !analyserRef.current || !dataArrayRef.current) {
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
        
        // Log VAD status less frequently for debugging
        // vadLogCounter++
        // if (vadLogCounter % 50 === 0) { // Every 5 seconds instead of every second
        //   console.log(`🎤 VAD - Volume: ${average.toFixed(2)}, Speaking: ${isSpeaking}, Recording: ${isRecording}`)
        // }
        
        // Dual threshold: HIGH to start, LOW to maintain (prevents cutting sustained vowels)
        const thresholdToUse = isSpeaking ? VAD_THRESHOLD_LOW : VAD_THRESHOLD_HIGH
        
        if (average > thresholdToUse) {
          // Voice detected - reset silence timer
          if (!isSpeaking) {
            console.log(`🎤 Voice detected! Volume: ${average.toFixed(2)} (threshold: ${thresholdToUse})`)
            setIsSpeaking(true)
          }
          lastVoiceTimeRef.current = now
          silenceStartTimeRef.current = null // ← KEY: Reset timer on ANY voice activity
          hasDetectedVoiceRef.current = true
        } else {
          // Below threshold - likely silence
          if (isSpeaking) {
            console.log(`🎤 Voice ended, starting silence timer (volume: ${average.toFixed(2)}, threshold: ${thresholdToUse})`)
            setIsSpeaking(false)
          }
          
          // Start silence timer only if not already started AND enough time has passed since last reset
          const timeSinceLastReset = now - lastSilenceResetRef.current
          if (silenceStartTimeRef.current === null && timeSinceLastReset > 500) { // 500ms debounce
            silenceStartTimeRef.current = now
            lastSilenceResetRef.current = now
            console.log(`🎤 Silence timer started (debounced)`)
          }
          
          // If waiting for response, stop VAD processing to prevent audio overlap
          if (isWaitingForResponse) {
            console.log('🎤 Waiting for AI response, pausing VAD processing')
            return
          }
          
          // Check if we've had enough silence to stop recording
          // Only if we've detected voice before
          if (silenceStartTimeRef.current !== null && hasDetectedVoiceRef.current) {
            console.debug(`🎤 Checking silence timer - isWaitingForResponse: ${isWaitingForResponse}, silenceStartTime: ${silenceStartTimeRef.current}, hasDetectedVoice: ${hasDetectedVoiceRef.current}`)
            const silenceDuration = now - silenceStartTimeRef.current
            
            // Log silence duration every second for debugging
            if (Math.floor(silenceDuration / 1000) !== Math.floor((silenceDuration - 100) / 1000)) {
              console.log(`🎤 Silence duration: ${silenceDuration}ms (threshold: ${SILENCE_DURATION_THRESHOLD}ms)`)
            }
            
            // Only stop if we've had silence for the threshold duration
            if (silenceDuration >= SILENCE_DURATION_THRESHOLD) {
              isProcessingStopRef.current = true // Prevent multiple calls
              console.log(`🎤 Stopping recording due to ${silenceDuration}ms of silence`)
              stopRecording()
            }
          }
        }
        
        // Fallback: Force stop recording after 15 seconds WITHOUT voice detection
        // Calculate time since recording started
        const timeSinceRecordingStart = now - recordingStartTimeRef.current
        
        // Trigger fallback ONLY if:
        // 1. 15 seconds have passed since recording started
        // 2. NO voice was EVER detected in this recording (hasDetectedVoiceRef is false)
        // 3. Not waiting for AI response
        if (timeSinceRecordingStart > 15000 && !hasDetectedVoiceRef.current && !isWaitingForResponse) {
          isProcessingStopRef.current = true
          isFallbackStopRef.current = true // Mark as fallback stop
          console.log(`🎤 Fallback: Stopping recording after 15s without voice detection - ending call`)
          stopRecording()
          // Call fallback callback to end the call
          if (onFallbackStop) {
            onFallbackStop()
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
      setupVoiceActivityDetection(streamRef.current).catch(error => {
        console.error('❌ Error in setupVoiceActivityDetection:', error)
      })
    }
  }, [isRecording, setupVoiceActivityDetection])
  
  // Reset VAD state when AI starts responding
  useEffect(() => {
    if (isWaitingForResponse) {
      console.log('🎤 AI responding, resetting VAD state')
      hasDetectedVoiceRef.current = false
      silenceStartTimeRef.current = null
      lastVoiceTimeRef.current = 0
      isProcessingStopRef.current = false
    }
  }, [isWaitingForResponse])


  const startRecording = useCallback(async () => {
    try {
      // CRITICAL: Reset all VAD state refs FIRST to prevent race conditions
      hasDetectedVoiceRef.current = false
      silenceStartTimeRef.current = null
      lastVoiceTimeRef.current = 0
      isProcessingStopRef.current = false
      isFallbackStopRef.current = false // Reset fallback flag
      lastSilenceResetRef.current = Date.now()
      
      // Check if component is cleaned up or unmounted
      if (isCleanedUpRef.current || !isMountedRef.current) {
        return
      }
      
      // Don't start recording if audio is currently playing to prevent feedback
      if (isPlaying) {
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
        // Don't process audio if component is cleaned up, unmounted, or ending
        if (isCleanedUpRef.current || !isMountedRef.current || isEnding) {
          console.log('🎤 Skipping audio processing - component cleaned up, unmounted, or ending')
          // Cleanup stream
          if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop())
            streamRef.current = null
          }
          return
        }
        
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        
        // Use configured minimum audio duration
        const minSize = apiConfig.audio.minBytesWebm
        const minDurationMs = apiConfig.audio.minDurationMs
        
        // Check if this was a fallback stop - don't send audio if no voice was detected
        if (isFallbackStopRef.current) {
          console.log('🎤 Fallback stop detected - skipping audio send to prevent unwanted responses')
          isFallbackStopRef.current = false // Reset flag
          return
        }
        
        // Check if we have any audio data at all
        if (audioChunksRef.current.length === 0) {
          console.log('🎤 No audio chunks recorded - skipping send')
        } else if (audioBlob.size > minSize) {
          // Prevent multiple simultaneous audio sends
          if (isSendingAudioRef.current) {
            console.warn('⚠️ Audio send already in progress - skipping duplicate send')
            return
          }
          
          isSendingAudioRef.current = true
          console.log(`🎤 Audio ready: ${audioBlob.size} bytes (minimum: ${minSize} bytes)`)
          onAudioReady(audioBlob)
        } else {
          console.log(`🎤 Audio too short: ${audioBlob.size} bytes (minimum: ${minSize} bytes) - skipping send`)
        }
        
        // Cleanup stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
          streamRef.current = null
        }
      }
      
      mediaRecorder.start()
      
      // Set recording start time BEFORE triggering useEffect (setIsRecording)
      // to prevent race condition with VAD fallback check
      recordingStartTimeRef.current = Date.now()
      
      setIsRecording(true)
      
      // Call the callback when recording starts
      if (onStartRecording) {
        onStartRecording()
      }
      
    } catch (error) {
      console.error('❌ Error starting recording:', error)
    }
  }, [setupVoiceActivityDetection, onAudioReady, isPlaying, isEnding, isWaitingForResponse])

  const resetAudioSendFlag = useCallback(() => {
    isSendingAudioRef.current = false
  }, [])

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
    isSendingAudioRef.current = false
    isFallbackStopRef.current = false
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

  const resetCleanupState = useCallback(() => {
    console.log('🔄 Resetting cleanup state for new conversation')
    isCleanedUpRef.current = false
    isMountedRef.current = true
  }, [])

  return {
    isRecording,
    isSpeaking,
    startRecording,
    stopRecording,
    cleanup,
    resetCleanupState,
    resetAudioSendFlag
  }
}
