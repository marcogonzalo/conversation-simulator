"use client"

import { useState, useEffect, useRef, useCallback } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar } from './avatar'
import { CallControls } from './call-controls'
import { CallStatus } from './call-status'
import { MicrophonePermission } from './microphone-permission'
import { useAudioRecording } from '@/hooks/useAudioRecording'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useMicrophonePermission } from '@/hooks/useMicrophonePermission'
import { useConversation, Message } from '@/hooks/useConversation'
import { AudioService } from '@/services/audioService'
import { AudioStreamingService } from '@/services/audioStreamingService'
import { processTextChunk } from '@/utils/textChunkProcessor'
import { Persona } from '@/types/persona'
import { humanizeAccent } from '@/utils/accentUtils'

interface ConversationInterfaceProps {
  conversationId?: string | Promise<string>
  personaId?: string
  personaName?: string
  personaAccent?: string
  persona?: Persona
}

export function ConversationInterface({ 
  conversationId = 'test-conversation', 
  personaId, 
  personaName, 
  personaAccent,
  persona 
}: ConversationInterfaceProps) {
  
  // State for resolved conversation ID
  const [resolvedConversationId, setResolvedConversationId] = useState<string>('')
  
  // Use persona prop if provided, otherwise use individual props
  const actualPersonaName = persona?.name || personaName || 'Test Persona'
  const actualPersonaId = persona?.id || personaId || 'test-persona'
  const actualPersonaAccent = persona?.accent || personaAccent || 'neutral'
  
  // Resolve conversation ID if it's a Promise
  useEffect(() => {
    if (typeof conversationId === 'string') {
      setResolvedConversationId(conversationId)
    } else if (conversationId instanceof Promise) {
      conversationId.then(id => setResolvedConversationId(id))
    }
  }, [conversationId])
  // UI State
  const [callStatus, setCallStatus] = useState<'idle' | 'connecting' | 'connected' | 'disconnected'>('idle')
  const [callDuration, setCallDuration] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null)
  const [isEnding, setIsEnding] = useState(false)
  const [isReadyToSpeak, setIsReadyToSpeak] = useState(false)
  const [audioEnabled, setAudioEnabled] = useState(false)
  const [canEndCall, setCanEndCall] = useState(true)
  
  
  // Audio streaming service
  const audioStreamingRef = useRef<AudioStreamingService | null>(null)
    
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const callDurationRef = useRef<NodeJS.Timeout | null>(null)

  // Event Handlers (defined before hooks that use them)
  const handleConnect = () => {
    setCallStatus('connected')
    
    // Initialize audio streaming service
    audioStreamingRef.current = new AudioStreamingService(
      () => {
        console.log('🎵 Audio streaming started')
        setIsPlaying(true)
      },
      () => {
        console.log('🎵 Audio streaming ended')
        setIsPlaying(false)
        setCurrentAudio(null)
        
        // Reset cleanup state to allow recording to restart
        resetCleanupState()
        
        // Wait before starting recording to prevent audio feedback
        setTimeout(() => {
          if (!isEnding) {
            startRecording()
          }
        }, 300)
      }
    )
    
    // Set ready to speak after a short delay to allow connection to stabilize
    setTimeout(() => {
      setIsReadyToSpeak(true)
    }, 1000)
  }

  const handleDisconnect = () => {
    setCallStatus('disconnected')
    setCallDuration(0)
    setIsPlaying(false)
    setCurrentAudio(null)
    setIsReadyToSpeak(false)
    setIsWaitingForResponse(false) // Reset waiting state on disconnect
    
    // Stop audio streaming
    if (audioStreamingRef.current) {
      audioStreamingRef.current.stop()
      audioStreamingRef.current = null
    }
    
    cleanup()
  }

  // Ref para evitar envíos duplicados
  const lastAudioSentRef = useRef<string | null>(null)
  
  const enableAudio = async () => {
    try {
      // Get microphone permissions to enable audio context in Safari
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { 
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      })
      
      // Create AudioContext with the stream to enable audio playback
      if (typeof window !== 'undefined' && window.AudioContext) {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
        
        // Create media stream source to keep context active
        const source = audioContext.createMediaStreamSource(stream)
        const analyser = audioContext.createAnalyser()
        source.connect(analyser)
        
        if (audioContext.state === 'suspended') {
          await audioContext.resume()
        }
        
        // Stop the stream and close context after a brief moment
        setTimeout(() => {
          stream.getTracks().forEach(track => track.stop())
          audioContext.close()
        }, 1000)
      }
      
      setAudioEnabled(true)
    } catch (error) {
      console.error('Failed to enable audio:', error)
      // Even if there's an error, mark as enabled to try anyway
      setAudioEnabled(true)
    }
  }

  const isSafari = () => {
    if (typeof window === 'undefined') return false
    return /^((?!chrome|android).)*safari/i.test(navigator.userAgent)
  }

  const handleAudioReady = async (audioBlob: Blob) => {
    if (isEnding || callStatus === 'disconnected') {
      return
    }
    
    try {
      // Check if audio blob is valid and has content
      if (!audioBlob || audioBlob.size === 0) {
        return
      }
      
      const base64 = await AudioService.convertAudioToBase64(audioBlob)
      
      // Check if base64 conversion was successful
      if (!base64 || base64.length === 0) {
        return
      }
      
      // Create a simple hash to detect duplicates
      const audioHash = base64.substring(0, 50) + base64.length
      
      // Check if this audio was already sent
      if (lastAudioSentRef.current === audioHash) {
        return
      }
      
      lastAudioSentRef.current = audioHash
      
      const message = AudioService.createAudioMessage(base64)
      sendMessage(message)
      
      setIsWaitingForResponse(true)
      
      // Create temporary user message
      addMessage({ content: '[Audio message]', sender: 'user', isAudio: true })
      
    } catch (error) {
      console.error('Error sending audio:', error)
    }
  }

  const handleAnalysis = (analysisData: any) => {
    // Analysis received and stored on backend
    console.log('📊 Analysis generated and saved:', {
      analysis_id: analysisData?.analysis_id,
      conversation_id: analysisData?.conversation_id
    })
  }

  const handleWebSocketMessage = (data: any) => {
    // Ignore audio messages if conversation is ending or disconnected
    if ((isEnding || callStatus === 'disconnected') && data.type === 'audio') {
      return
    }
    
    switch (data.type) {
      case 'transcribed_text':
        
        if (data.content && data.content.trim()) {
          // Check if this is a user transcription (starts with "User: ")
          if (data.content.startsWith('User: ')) {
            // This is user transcription - update the last user audio message
            const userTranscript = data.content.substring(6) // Remove "User: " prefix
            
            setMessages(prev => {
              // Find the last user audio message
              let lastUserMessageIndex = -1
              for (let i = prev.length - 1; i >= 0; i--) {
                const msg = prev[i]
                if (msg.sender === 'user' && msg.isAudio === true) {
                  lastUserMessageIndex = i
                  break
                }
              }
              
              if (lastUserMessageIndex !== -1) {
                // Update the existing user message
                const updated = [...prev]
                updated[lastUserMessageIndex] = {
                  ...updated[lastUserMessageIndex],
                  content: userTranscript
                }
                return updated
              } else {
                // Create a new user message if none found
                const newMessage: Message = {
                  id: `user_${Date.now()}`,
                  content: userTranscript,
                  sender: 'user',
                  timestamp: new Date(),
                  isAudio: true
                }
                return [...prev, newMessage]
              }
            })
          } else if (data.content.startsWith('AI: ')) {
            // This is AI transcription - handle as before
            const aiTranscript = data.content.substring(4) // Remove "AI: " prefix
            
            setMessages(prev => {
              // Buscar el último mensaje de AI de audio (buscar desde atrás)
              let lastAiMessageIndex = -1
              for (let i = prev.length - 1; i >= 0; i--) {
                const msg = prev[i]
                if (msg.sender === 'ai' && msg.isAudio === true) {
                  lastAiMessageIndex = i
                  break
                }
              }
              
              // Solo actualizar si el mensaje es muy reciente (últimos 5 segundos)
              // Esto evita concatenar fragmentos de respuestas anteriores
              const isRecentMessage = lastAiMessageIndex !== -1 && 
                prev[lastAiMessageIndex].timestamp.getTime() > Date.now() - 5000
              
              if (isRecentMessage && aiTranscript.trim()) {
                // Actualizar el mensaje AI existente solo si el contenido es diferente
                const updated = [...prev]
                const currentContent = updated[lastAiMessageIndex].content === '[Audio response]' ? '' : updated[lastAiMessageIndex].content
                
                if (aiTranscript.trim()) {
                  // Use the smart text chunk processor for proper concatenation
                  const processedContent = processTextChunk(currentContent, aiTranscript)
                  updated[lastAiMessageIndex] = {
                    ...updated[lastAiMessageIndex],
                    content: processedContent
                  }
                }
                return updated
              } else if (aiTranscript.trim()) {
                // Crear un nuevo mensaje AI solo si el contenido no está vacío
                const newMessage: Message = {
                  id: `ai_${Date.now()}`,
                  content: aiTranscript,
                  sender: 'ai',
                  timestamp: new Date(),
                  isAudio: true
                }
                return [...prev, newMessage]
              }
              return prev
            })
          }
        }
        break
        
      case 'audio_chunk':
        if (data.audio_data && audioStreamingRef.current) {
          audioStreamingRef.current.addAudioChunk(data.audio_data)
          // Reset waiting state when AI starts responding with audio
          setIsWaitingForResponse(false)
        }
        break
        
      case 'text_response':
        addMessage({ content: data.content, sender: 'ai', isAudio: false })
        setIsWaitingForResponse(false) // Reset waiting state when AI responds
        break
        
      case 'audio_response':
        setIsWaitingForResponse(false)
        
        // Only use this as fallback if streaming is not active
        if (data.audio_data && !audioStreamingRef.current?.getIsPlaying()) {
          try {
            // Stop any currently playing audio to prevent overlap
            if (currentAudio) {
              currentAudio.pause()
              currentAudio.currentTime = 0
              URL.revokeObjectURL(currentAudio.src)
            }
            
            const audio = AudioService.createAudioElement(data.audio_data)
            setCurrentAudio(audio)
            setIsPlaying(true)
            
            audio.oncanplaythrough = async () => {
              const playSuccess = await AudioService.playAudio(audio)
              if (!playSuccess) {
                console.error("Audio play failed")
                setIsPlaying(false)
                setCurrentAudio(null)
              }
            }
            
            audio.onerror = (e) => {
              console.error('Audio error:', e)
              setIsPlaying(false)
              setCurrentAudio(null)
            }

            audio.onended = () => {
              setIsPlaying(false)
              setCurrentAudio(null)
              URL.revokeObjectURL(audio.src)
              
              // Reset cleanup state to allow recording to restart
              resetCleanupState()
              
              // Wait before starting recording to prevent audio feedback
              setTimeout(() => {
                if (!isEnding) {
                  startRecording()
                }
              }, 300)
            }
            
            setIsPlaying(true)
          } catch (error) {
            console.error('Error creating audio element:', error)
            // Reset cleanup state to allow recording to restart
            resetCleanupState()
            setTimeout(() => {
              if (!isEnding) {
                startRecording()
              }
            }, 1000)
          }
        }
        break
        
      case 'persona_info':
        console.log('Persona info:', data.name, data.accent)
        // Mark as ready to speak when persona info is received
        setIsReadyToSpeak(true)
        startRecording()
        break
        
      case 'ping':
        sendMessage({ type: 'pong' })
        break
        
      case 'error':
        console.error('WebSocket error:', data.error)
        addMessage({ content: `Error: ${data.error}`, sender: 'ai', isAudio: false })
        // Reset waiting state on error
        setIsWaitingForResponse(false)
        break
        
      default:
        console.log('Unknown message type:', data.type)
    }
  }

  // Custom Hooks
  const { 
    messages, 
    setMessages,
    isWaitingForResponse, 
    setIsWaitingForResponse, 
    addMessage, 
    updateLastMessage,
    clearMessages
  } = useConversation()
  
  const { isConnected, isLoading, realConversationId, connect, sendMessage, disconnect } = useWebSocket({
    onMessage: handleWebSocketMessage,
    onConnect: handleConnect,
    onDisconnect: handleDisconnect,
    onAnalysis: handleAnalysis
  })

  const { permissionStatus, isRequesting, error, requestPermission } = useMicrophonePermission({
    onPermissionGranted: () => {
      console.log('✅ Microphone permission granted')
    },
    onPermissionDenied: () => {
      console.log('❌ Microphone permission denied')
    }
  })

  // Only show permission component if not connected and permission not granted
  const shouldShowPermissionComponent = !isConnected && permissionStatus !== 'granted'

  const { isRecording, isSpeaking, startRecording, stopRecording, cleanup, resetCleanupState } = useAudioRecording({
    onAudioReady: handleAudioReady,
    isWaitingForResponse,
    isEnding,
    isPlaying,
    onStartRecording: () => {
      // Reset waiting state when user starts recording
      setIsWaitingForResponse(false)
    }
  })


  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Call duration timer
  useEffect(() => {
    if (callStatus === 'connected') {
      callDurationRef.current = setInterval(() => {
        setCallDuration(prev => prev + 1)
      }, 1000)
    } else {
      if (callDurationRef.current) {
        clearInterval(callDurationRef.current)
        callDurationRef.current = null
      }
    }

    return () => {
      if (callDurationRef.current) {
        clearInterval(callDurationRef.current)
      }
    }
  }, [callStatus])


  // Main Actions
  const startCall = async () => {
    // Check microphone permission first
    if (permissionStatus !== 'granted') {
      console.log('⚠️ Microphone permission not granted, requesting...')
      await requestPermission()
      return
    }
    
    setCallStatus('connecting')
    setIsEnding(false)
    setIsReadyToSpeak(false)
    setIsWaitingForResponse(false) // Reset waiting state on new call
    
    // Reset cleanup state to allow recording to start
    resetCleanupState()
    
    // Limpiar hash de audio anterior para nueva conversación
    lastAudioSentRef.current = null
    
    await connect(actualPersonaId)
  }

  const endCall = () => {
    setIsEnding(true)
    setCallStatus('disconnected') // Mark as disconnected immediately
    
    // Immediately stop recording and cleanup
    if (isRecording) {
      stopRecording()
    }
    
    // Force cleanup of audio resources
    cleanup()
    
    // Clear any pending audio hash to prevent sending stale audio
    lastAudioSentRef.current = null
    
    // Clear waiting state immediately
    setIsWaitingForResponse(false)
    
    setTimeout(() => {
      sendMessage({ type: 'end_voice_conversation' })
      setTimeout(() => {
        disconnect()
        // Clear any remaining audio state
        setCurrentAudio(null)
        setIsPlaying(false)
        setIsWaitingForResponse(false)
      }, 500) // Increased timeout to ensure proper cleanup
    }, 500) // Reduced initial timeout
  }

  const stopAudio = () => {
    if (currentAudio) {
      currentAudio.pause()
      currentAudio.currentTime = 0
    }
    setIsPlaying(false)
    setCurrentAudio(null)
  }

  return (
    <div 
      data-testid="conversation-interface"
      className="flex flex-col h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"
    >
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-sm border-b border-white/20 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
              {actualPersonaName.charAt(0)}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{actualPersonaName}</h2>
              <p className="text-sm font-medium text-white/80">{humanizeAccent(actualPersonaAccent)}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={isConnected ? "default" : "destructive"}>
              {isConnected ? 'Online' : 'Offline'}
            </Badge>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-8 p-8">
        {/* Left Column: Call Interface */}
        <div className="md:col-span-3 flex flex-col items-center justify-center p-8 bg-black/20 rounded-2xl">
          {/* Show microphone permission component only when not connected and permission not granted */}
          {shouldShowPermissionComponent ? (
            <MicrophonePermission
              permissionStatus={permissionStatus}
              isRequesting={isRequesting}
              error={error}
              onRequestPermission={requestPermission}
            />
          ) : (
            <>
              {/* Avatar */}
              <div className="mb-8">
                <Avatar 
                  size="xl" 
                  isActive={isConnected} 
                  isSpeaking={isSpeaking}
                  className="mb-4"
                />
              </div>

              {/* Call Status */}
              <div className="mb-8">
                <CallStatus 
                  status={callStatus}
                  duration={callDuration}
                  isConnected={isConnected}
                  isRecording={isRecording}
                  isReadyToSpeak={isReadyToSpeak}
                />
              </div>

              {/* Safari Audio Enable Button */}
              {isSafari() && !audioEnabled && (
                <div className="mb-4">
                  <button
                    onClick={enableAudio}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-colors duration-200 flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.79L4.617 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.617l3.766-3.79a1 1 0 011.617.79zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clipRule="evenodd" />
                    </svg>
                    Habilitar Audio y Micrófono (Safari)
                  </button>
                </div>
              )}

              {/* Call Controls */}
              <div className="mb-8">
                <CallControls
                  isPlaying={isPlaying}
                  isConnected={isConnected}
                  isRecording={isRecording}
                  isSpeaking={isSpeaking}
                  isWaitingForResponse={isWaitingForResponse}
                  onStartCall={startCall}
                  onEndCall={endCall}
                  onPlayAudio={() => {}}
                  onStopAudio={stopAudio}
                />
              </div>
            </>
          )}
        </div>

        {/* Right Column: Chat History */}
        <div className="md:col-span-1 bg-black/20 rounded-2xl flex flex-col h-full max-h-[calc(100vh-12rem)]">
          <h2 className="text-lg font-bold text-white/90 p-4 border-b border-white/10">
            Historial de la Conversación
          </h2>
          <div className="flex-1 p-4 overflow-y-auto">
            {messages.length > 0 ? (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex flex-col ${message.sender === 'user' ? 'items-end' : 'items-start'}`}
                  >
                    <div className={`
                      max-w-xs lg:max-w-sm xl:max-w-md
                      px-4 py-2 rounded-2xl
                      ${message.sender === 'user' ? 'bg-blue-600/50 rounded-br-none' : 'bg-gray-700/50 rounded-bl-none'}
                    `}>
                      <p className="text-sm text-white/90">{message.content}</p>
                    </div>
                    <span className="text-xs text-white/40 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            ) : (
              <div className="flex items-center justify-center h-full">
                <p className="text-sm text-white/50">La transcripción aparecerá aquí.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}