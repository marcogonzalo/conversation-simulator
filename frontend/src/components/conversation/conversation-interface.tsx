"use client"

import { useState, useEffect, useRef, useCallback } from 'react'
import { Mic, MicOff, Volume2, VolumeX, Send, Loader2, User, Bot, Phone, PhoneOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar } from './avatar'
import { CallControls } from './call-controls'
import { CallStatus } from './call-status'

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
  audioUrl?: string
  isAudio?: boolean
}

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
  const [messages, setMessages] = useState<Message[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [callStatus, setCallStatus] = useState<'idle' | 'connecting' | 'connected' | 'disconnected'>('idle')
  const [callDuration, setCallDuration] = useState(0)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [realConversationId, setRealConversationId] = useState<string | null>(null)
  const [recordingDuration, setRecordingDuration] = useState(0)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const websocketRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const callDurationRef = useRef<NodeJS.Timeout | null>(null)
  const recordingDurationRef = useRef<NodeJS.Timeout | null>(null)

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

  // Start call function
  const startCall = async () => {
    setCallStatus('connecting')
    setIsLoading(true)
    
    try {
      // First, create the conversation in the backend
      console.log('Creating conversation...')
      const createResponse = await fetch('http://localhost:8000/api/v1/conversations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          persona_id: personaId,
          metadata: {
            accent: personaAccent,
            created_at: new Date().toISOString()
          }
        }),
      })
      
      if (!createResponse.ok) {
        throw new Error('Failed to create conversation')
      }
      
      const conversationData = await createResponse.json()
      console.log('Conversation created:', conversationData)
      
      // Use the real conversation ID from the backend
      const realConversationId = conversationData.conversation_id
      setRealConversationId(realConversationId)
      
      // Connect to WebSocket
      const wsUrl = `ws://localhost:8000/api/v1/ws/conversation/${realConversationId}`
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setCallStatus('connected')
        setIsLoading(false)
        
        // Automatically start recording when connected (with delay to ensure WebSocket is stable)
        setTimeout(() => {
          startRecording()
        }, 500)
        
        // Send initial greeting from AI
        setTimeout(() => {
          const greetingMessage: Message = {
            id: `greeting_${Date.now()}`,
            content: `¡Hola! Soy ${personaName}. Estoy aquí para ayudarte a practicar tus habilidades de ventas. ¿En qué puedo ayudarte hoy?`,
            sender: 'ai',
            timestamp: new Date(),
            isAudio: false
          }
          setMessages([greetingMessage])
          setIsSpeaking(true)
          
          // Simulate AI speaking
          setTimeout(() => {
            setIsSpeaking(false)
          }, 3000)
        }, 1000)
      }
      
      ws.onmessage = (event) => {
        console.log('📨 WebSocket message received:', event.data)
        const data = JSON.parse(event.data)
        console.log('📨 Parsed message:', data)
        handleWebSocketMessage(data)
      }
      
      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected. Call has ended.')
        setIsConnected(false)
        setCallStatus('disconnected') // Show 'Disconnected' instead of resetting to 'idle'
        setCallDuration(0)
        // Note: We are NOT clearing messages, so the user can review the conversation.
        // setMessages([]) 
        setIsLoading(false)
        setIsSpeaking(false)
        setIsRecording(false)

        if (currentAudio) {
          currentAudio.pause()
          setCurrentAudio(null)
          setIsPlaying(false)
        }

        // Stop any lingering media tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
          streamRef.current = null
          console.log('🎤 Cleaned up stray media stream tracks in onclose.')
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
        setCallStatus('disconnected')
        setIsLoading(false)
      }
      
      websocketRef.current = ws
    } catch (error) {
      console.error('Error starting call:', error)
      setCallStatus('disconnected')
      setIsLoading(false)
    }
  }

  // End call function
  const endCall = () => {
    console.log('📞 User clicked end call.')
    if (isRecording) {
      console.log('📞 Recording is active, stopping it to send final audio.')
      stopRecording()
    } else if (websocketRef.current && (websocketRef.current.readyState === WebSocket.OPEN || websocketRef.current.readyState === WebSocket.CONNECTING)) {
      // If not recording, but still connected, close the socket directly.
      console.log('📞 Not recording, closing WebSocket directly.')
      websocketRef.current.close()
    }
    // The rest of the cleanup will be handled by the onclose event
  }

  // WebSocket connection is now handled in startCall function

  const handleWebSocketMessage = (data: any) => {
    console.log('🔍 Handling WebSocket message:', data)
    
    switch (data.type) {
      case 'processing_status':
        // Show processing status to user
        console.log('⚙️ Processing status:', data.status)
        break
        
      case 'transcribed_text':
        // Update the last user message with transcribed text
        console.log('📝 Transcribed text received:', data.content)
        setMessages(prev => {
          const updated = [...prev]
          const lastMessage = updated[updated.length - 1]
          if (lastMessage && lastMessage.sender === 'user' && lastMessage.content === '[Audio message]') {
            lastMessage.content = data.content
            console.log('📝 Updated user message with transcription')
          }
          return updated
        })
        break
        
      case 'text_response':
        // Add AI text response
        const textMessage: Message = {
          id: Date.now().toString(),
          content: data.content,
          sender: 'ai',
          timestamp: new Date(),
          isAudio: false
        }
        setMessages(prev => [...prev, textMessage])
        break
        
      case 'audio_response':
        // Handle audio response
        setIsLoading(true)
        setIsSpeaking(true)
        const audio = new Audio(data.audio_url)
        setCurrentAudio(audio)
        
        audio.oncanplaythrough = () => {
          setIsLoading(false)
          audio.play().catch(e => console.error("Audio play failed:", e))
        }

        audio.onended = () => {
          setIsPlaying(false)
          setIsSpeaking(false)
          setCurrentAudio(null)
          
          // Restart recording after AI finishes speaking
          console.log('🎤 AI finished speaking, restarting recording...')
          startRecording()
        }
        
        setIsPlaying(true)
        break
        
      case 'persona_info':
        // Update persona info if needed
        console.log('Persona info:', data.name, data.accent)
        break
        
      case 'error':
        console.error('WebSocket error:', data.error)
        setIsLoading(false)
        break
        
      case 'ping':
        // Handle ping from server
        console.log('🏓 Ping received from server, sending pong...')
        if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
          websocketRef.current.send(JSON.stringify({ type: 'pong' }))
        }
        break
        
      default:
        console.log('Unknown message type:', data.type)
    }
  }

  const startRecording = async () => {
    try {
      console.log('🎤 Starting recording...')
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream // Store the stream for later cleanup
      console.log('🎤 Audio stream obtained:', stream)
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      console.log('🎤 MediaRecorder created:', mediaRecorder)
      
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []
      
      mediaRecorder.ondataavailable = (event) => {
        console.log('🎤 Audio data available:', event.data.size, 'bytes')
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
          console.log('🎤 Audio chunks count:', audioChunksRef.current.length)
        }
      }
      
      mediaRecorder.onstop = async () => {
        console.log('🎤 Recording stopped, processing final audio...')
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        
        // Only send audio if it's substantial (e.g., > 1KB)
        if (audioBlob.size > 1000) {
          console.log('🎤 Final audio blob created:', audioBlob.size, 'bytes')
          if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
            try {
              console.log('📤 Sending final audio message...')
              await sendAudioMessage(audioBlob)
              console.log('✅ Final audio message sent successfully.')
            } catch (error) {
              console.error('❌ Error sending final audio message:', error)
            }
          } else {
            console.error('❌ WebSocket was not open for final audio. State:', websocketRef.current?.readyState)
          }
        } else {
          console.log('🎤 Audio data too small to send, skipping.')
        }

        // After attempting to send, close the WebSocket.
        if (websocketRef.current?.readyState === WebSocket.OPEN) {
          console.log('📞 Closing WebSocket from onstop handler.')
          websocketRef.current.close()
        }

        // Stop the media stream tracks.
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
          streamRef.current = null
          console.log('🎤 Media stream tracks stopped.')
        }
      }
      
      mediaRecorder.start()
      console.log('🎤 MediaRecorder started')
      setIsRecording(true)
      
    } catch (error) {
      console.error('❌ Error starting recording:', error)
    }
  }

  const stopRecording = () => {
    console.log('🛑 Stopping recording...')
    console.log('🛑 MediaRecorder exists:', !!mediaRecorderRef.current)
    console.log('🛑 Is recording:', isRecording)
    
    if (mediaRecorderRef.current && isRecording) {
      console.log('🛑 Calling MediaRecorder.stop()')
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      console.log('🛑 Recording stopped')
    } else {
      console.log('🛑 Cannot stop recording - conditions not met')
    }
  }

  // Helper function to convert large Uint8Array to base64 without stack overflow
  const uint8ArrayToBase64 = (uint8Array: Uint8Array): string => {
    const CHUNK_SIZE = 0x8000; // 32k chunks
    let result = '';
    for (let i = 0; i < uint8Array.length; i += CHUNK_SIZE) {
      const chunk = uint8Array.subarray(i, i + CHUNK_SIZE);
      result += String.fromCharCode.apply(null, Array.from(chunk));
    }
    return btoa(result);
  }

  const sendAudioMessage = async (audioBlob: Blob) => {
    console.log('📤 Sending audio message...')
    console.log('📤 Audio blob size:', audioBlob.size, 'bytes')
    console.log('📤 WebSocket state:', websocketRef.current?.readyState)
    console.log('📤 WebSocket exists:', !!websocketRef.current)
    
    if (!websocketRef.current) {
      console.error('❌ WebSocket reference is null')
      return
    }
    
    if (websocketRef.current.readyState !== WebSocket.OPEN) {
      console.error('❌ WebSocket not open, state:', websocketRef.current.readyState)
      return
    }

    try {
      setIsLoading(true)
      console.log('📤 Converting audio to base64...')
      
      // Convert blob to base64
      const arrayBuffer = await audioBlob.arrayBuffer()
      console.log('📤 ArrayBuffer size:', arrayBuffer.byteLength, 'bytes')
      
      const uint8Array = new Uint8Array(arrayBuffer)
      const base64 = uint8ArrayToBase64(uint8Array); // Use the robust function
      console.log('📤 Base64 length:', base64.length, 'characters')
      
      // Send audio message via WebSocket
      if (!realConversationId) {
        console.error('❌ No real conversation ID available')
        return
      }
      
      const message = {
        type: 'audio_message',
        conversation_id: realConversationId,
        audio_data: base64,
        audio_format: 'webm',
        persona_id: personaId
      }
      
      console.log('📤 Sending WebSocket message:', {
        type: message.type,
        conversation_id: message.conversation_id,
        audio_data_length: message.audio_data.length,
        audio_format: message.audio_format,
        persona_id: message.persona_id
      })
      
      websocketRef.current.send(JSON.stringify(message))
      console.log('✅ Audio message sent successfully!')

      // Add placeholder message to UI
      const userMessage: Message = {
        id: `user_audio_${Date.now()}`,
        content: '[Audio message]',
        sender: 'user',
        timestamp: new Date(),
        isAudio: true,
      }
      setMessages(prev => [...prev, userMessage])
      
    } catch (error) {
      console.error('❌ Error sending audio message:', error)
      setIsLoading(false)
    } finally {
      setIsLoading(false)
    }
  }

  const playAudio = async (audioUrl: string) => {
    try {
      if (currentAudio) {
        currentAudio.pause()
        currentAudio.currentTime = 0
      }
      
      const audio = new Audio(audioUrl)
      setCurrentAudio(audio)
      setIsPlaying(true)
      
      audio.onended = () => {
        setIsPlaying(false)
        setCurrentAudio(null)
      }
      
      audio.onerror = () => {
        console.error('Error playing audio')
        setIsPlaying(false)
        setCurrentAudio(null)
      }
      
      await audio.play()
    } catch (error) {
      console.error('Error playing audio:', error)
      setIsPlaying(false)
    }
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