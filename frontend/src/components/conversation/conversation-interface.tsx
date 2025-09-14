"use client"

import { useState, useEffect, useRef } from 'react'
import { Badge } from '@/components/ui/badge'
import { Avatar } from './avatar'
import { CallControls } from './call-controls'
import { CallStatus } from './call-status'
import { useAudioRecording } from '@/hooks/useAudioRecording'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useConversation, Message } from '@/hooks/useConversation'
import { AudioService } from '@/services/audioService'

interface ConversationInterfaceProps {
  conversationId: string
  personaId: string
  personaName: string
  personaAccent: string
}

export function ConversationInterface({ 
  conversationId, 
  personaId, 
  personaName, 
  personaAccent 
}: ConversationInterfaceProps) {
  // UI State
  const [callStatus, setCallStatus] = useState<'idle' | 'connecting' | 'connected' | 'disconnected'>('idle')
  const [callDuration, setCallDuration] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null)
  const [isEnding, setIsEnding] = useState(false)
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const callDurationRef = useRef<NodeJS.Timeout | null>(null)

  // Event Handlers (defined before hooks that use them)
  const handleConnect = () => {
    setCallStatus('connected')
  }

  const handleDisconnect = () => {
    setCallStatus('disconnected')
    setCallDuration(0)
    setIsPlaying(false)
    setCurrentAudio(null)
    cleanup()
  }

  const handleAudioReady = async (audioBlob: Blob) => {
    if (isEnding) return
    
    try {
      console.log('🎤 handleAudioReady called with blob size:', audioBlob.size)
      const base64 = await AudioService.convertAudioToBase64(audioBlob)
      console.log('📤 Converting audio to base64...')
      console.log('📤 Base64 length:', base64.length, 'characters')
      
      const message = AudioService.createAudioMessage(base64)
      console.log('📤 Created WebSocket message:', message.type)
      
      console.log('📤 Sending WebSocket message...')
      console.log('📤 WebSocket connection state:', isConnected ? 'CONNECTED' : 'DISCONNECTED')
      console.log('📤 Conversation ID:', realConversationId)
      sendMessage(message)
      console.log('✅ Audio message sent successfully!')
      
      setIsWaitingForResponse(true)
      addMessage({ content: '[Audio message]', sender: 'user', isAudio: true })
      
    } catch (error) {
      console.error('❌ Error sending audio:', error)
    }
  }

  const handleWebSocketMessage = (data: any) => {
    console.log('📨 WebSocket message:', data.type)
    console.log('📨 WebSocket message data:', data)
    console.log('📨 Current isWaitingForResponse:', isWaitingForResponse)
    
    switch (data.type) {
      case 'transcribed_text':
        console.log('📨 Processing transcribed_text:', data.content)
        updateLastMessage(data.content)
        break
        
      case 'text_response':
        console.log('📨 Processing text_response:', data.content)
        addMessage({ content: data.content, sender: 'ai', isAudio: false })
        break
        
      case 'audio_response':
        console.log('📨 Processing audio_response:', data.audio_data ? `audio_data length: ${data.audio_data.length}` : 'no audio_data')
        console.log('📨 Full audio_response data:', data)
        
        // Clear waiting state
        console.log('📨 Setting isWaitingForResponse to false')
        setIsWaitingForResponse(false)
        
        // Add message for AI audio response
        addMessage({ content: '[Audio response]', sender: 'ai', isAudio: true })
        
        if (data.audio_data) {
          console.log('📨 Creating audio element from base64 data...')
          try {
            const audio = AudioService.createAudioElement(data.audio_data)
            setCurrentAudio(audio)
            
            audio.oncanplaythrough = () => {
              console.log('📨 Audio ready to play, starting playback...')
              audio.play().catch(e => console.error("Audio play failed:", e))
            }

            audio.onended = () => {
              console.log('📨 Audio playback ended, restarting recording...')
              setIsPlaying(false)
              setCurrentAudio(null)
              URL.revokeObjectURL(audio.src)
              startRecording()
            }
            
            setIsPlaying(true)
            console.log('📨 Audio element created and playing set to true')
          } catch (error) {
            console.error('❌ Error creating audio element:', error)
            setTimeout(() => startRecording(), 1000)
          }
        } else {
          console.log('📨 No audio data, restarting recording in 1 second')
          setTimeout(() => startRecording(), 1000)
        }
        break
        
      case 'persona_info':
        console.log('Persona info:', data.name, data.accent)
        setTimeout(() => startRecording(), 500)
        break
        
      case 'ping':
        sendMessage({ type: 'pong' })
        break
        
      default:
        console.log('Unknown message type:', data.type)
    }
  }

  // Custom Hooks
  const { messages, isWaitingForResponse, setIsWaitingForResponse, addMessage, updateLastMessage } = useConversation()
  
  const { isConnected, isLoading, realConversationId, connect, sendMessage, disconnect } = useWebSocket({
    onMessage: handleWebSocketMessage,
    onConnect: handleConnect,
    onDisconnect: handleDisconnect
  })

  const { isRecording, isSpeaking, startRecording, stopRecording, cleanup } = useAudioRecording({
    onAudioReady: handleAudioReady,
    isWaitingForResponse,
    isEnding
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
    setCallStatus('connecting')
    setIsEnding(false)
    await connect(personaId)
  }

  const endCall = () => {
    setIsEnding(true)
    if (isRecording) {
      stopRecording()
    }
    
    setTimeout(() => {
      sendMessage({ type: 'end_voice_conversation' })
      setTimeout(() => disconnect(), 100)
    }, 2000)
  }

  const stopAudio = () => {
    if (currentAudio) {
      currentAudio.pause()
      currentAudio.currentTime = 0
      setIsPlaying(false)
      setCurrentAudio(null)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-sm border-b border-white/20 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
              {personaName.charAt(0)}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{personaName}</h2>
              <p className="text-sm font-medium text-white/80">{personaAccent}</p>
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