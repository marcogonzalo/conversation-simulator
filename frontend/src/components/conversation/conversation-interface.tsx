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

interface ConversationInterfaceProps {
  conversationId?: string
  personaId?: string
  personaName?: string
  personaAccent?: string
  persona?: {
    id: string
    name: string
    description: string
    accent: string
    voice: string
  }
}

export function ConversationInterface({ 
  conversationId = 'test-conversation', 
  personaId, 
  personaName, 
  personaAccent,
  persona 
}: ConversationInterfaceProps) {
  
  // Use persona prop if provided, otherwise use individual props
  const actualPersonaName = persona?.name || personaName || 'Test Persona'
  const actualPersonaId = persona?.id || personaId || 'test-persona'
  const actualPersonaAccent = persona?.accent || personaAccent || 'neutral'
  // UI State
  const [callStatus, setCallStatus] = useState<'idle' | 'connecting' | 'connected' | 'disconnected'>('idle')
  const [callDuration, setCallDuration] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null)
  const [isEnding, setIsEnding] = useState(false)
  const [isReadyToSpeak, setIsReadyToSpeak] = useState(false)
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
  
  const handleAudioReady = async (audioBlob: Blob) => {
    if (isEnding) {
      console.log('🚫 Conversation ending, not sending audio')
      return
    }
    
    console.log('🎤 Audio ready, blob size:', audioBlob.size, 'isWaitingForResponse:', isWaitingForResponse)
    
    try {
      // Check if audio blob is valid and has content
      if (!audioBlob || audioBlob.size === 0) {
        console.log('🚫 Empty audio blob, not sending')
        return
      }
      
      const base64 = await AudioService.convertAudioToBase64(audioBlob)
      
      // Check if base64 conversion was successful
      if (!base64 || base64.length === 0) {
        console.log('🚫 Empty base64 audio, not sending')
        return
      }
      
      // Crear un hash simple del audio para detectar duplicados
      const audioHash = base64.substring(0, 50) + base64.length
      
      // Verificar si ya se envió este audio
      if (lastAudioSentRef.current === audioHash) {
        console.log('🚫 Duplicate audio detected, not sending')
        return
      }
      
      lastAudioSentRef.current = audioHash
      
      const message = AudioService.createAudioMessage(base64)
      sendMessage(message)
      console.log('✅ Audio message sent')
      
      setIsWaitingForResponse(true)
      console.log('⏳ Set isWaitingForResponse to true, waiting for backend response...')
      
      // Crear mensaje temporal del usuario
      addMessage({ content: '[Audio message]', sender: 'user', isAudio: true })
      
    } catch (error) {
      console.error('❌ Error sending audio:', error)
    }
  }

  const handleWebSocketMessage = (data: any) => {
    console.log('📨 WebSocket message:', data.type)
    
    switch (data.type) {
      case 'transcribed_text':
        console.log('📨 Processing transcribed_text:', data.content)
        
        if (data.content && data.content.trim()) {
          // Check if this is a user transcription (starts with "User: ")
          if (data.content.startsWith('User: ')) {
            // This is user transcription - update the last user audio message
            const userTranscript = data.content.substring(6) // Remove "User: " prefix
            console.log('📨 Processing user transcription:', userTranscript)
            
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
                console.log('📨 Updating user message with transcription:', userTranscript)
                const updated = [...prev]
                updated[lastUserMessageIndex] = {
                  ...updated[lastUserMessageIndex],
                  content: userTranscript
                }
                return updated
              } else {
                // Create a new user message if none found
                console.log('📨 Creating new user message with transcription:', userTranscript)
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
            console.log('📨 Processing AI transcription:', aiTranscript)
            
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
              
              // Solo actualizar si el mensaje es muy reciente (últimos 10 segundos)
              // Esto evita concatenar fragmentos de respuestas anteriores
              const isRecentMessage = lastAiMessageIndex !== -1 && 
                prev[lastAiMessageIndex].timestamp.getTime() > Date.now() - 10000
              
              if (isRecentMessage) {
                // Actualizar el mensaje AI existente
                const updated = [...prev]
                const currentContent = updated[lastAiMessageIndex].content === '[Audio response]' ? '' : updated[lastAiMessageIndex].content
                
                if (aiTranscript) {
                  // Add a space if the content is a number
                  const separator = !isNaN(Number(aiTranscript)) ? ' ' : '';
                  updated[lastAiMessageIndex] = {
                    ...updated[lastAiMessageIndex],
                    content: currentContent + separator + aiTranscript
                  }
                }
                return updated
              } else {
                // Crear un nuevo mensaje AI solo si el contenido no está vacío
                if (aiTranscript.trim()) {
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
              }
            })
          }
        }
        break
        
      case 'audio_chunk':
        if (data.audio_data && audioStreamingRef.current) {
          audioStreamingRef.current.addAudioChunk(data.audio_data)
        }
        break
        
      case 'text_response':
        console.log('📨 Processing text_response:', data.content)
        addMessage({ content: data.content, sender: 'ai', isAudio: false })
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
            
            audio.oncanplaythrough = () => {
              audio.play().catch(e => {
                console.error("❌ Audio play failed:", e)
                setIsPlaying(false)
                setCurrentAudio(null)
              })
            }
            
            audio.onerror = (e) => {
              console.error('❌ Audio error:', e)
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
    onDisconnect: handleDisconnect
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
    isPlaying
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
    console.log('📞 End call initiated')
    console.log('📞 Stack trace:', new Error().stack)
    setIsEnding(true)
    
    // Immediately stop recording and cleanup
    if (isRecording) {
      console.log('📞 Stopping recording...')
      stopRecording()
    }
    
    // Force cleanup of audio resources
    console.log('📞 Cleaning up audio resources...')
    cleanup()
    
    // Clear any pending audio hash to prevent sending stale audio
    lastAudioSentRef.current = null
    
    setTimeout(() => {
      console.log('📞 Sending end_voice_conversation message')
      sendMessage({ type: 'end_voice_conversation' })
      setTimeout(() => {
        console.log('📞 Disconnecting WebSocket')
        disconnect()
      }, 200)
    }, 1000) // Reduced timeout for faster cleanup
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
              <p className="text-sm font-medium text-white/80">{actualPersonaAccent}</p>
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