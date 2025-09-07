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
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const websocketRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const callDurationRef = useRef<NodeJS.Timeout | null>(null)

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
      // Connect to WebSocket
      const wsUrl = `ws://localhost:8000/api/v1/ws/conversation/${conversationId}`
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setCallStatus('connected')
        setIsLoading(false)
        
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
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      }
      
      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        setCallStatus('disconnected')
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
    if (websocketRef.current) {
      websocketRef.current.close()
    }
    setCallStatus('idle')
    setIsConnected(false)
    setCallDuration(0)
    setMessages([])
    setIsSpeaking(false)
    
    // Stop any ongoing recording
    if (isRecording) {
      stopRecording()
    }
    
    // Stop any playing audio
    if (currentAudio) {
      currentAudio.pause()
      setCurrentAudio(null)
      setIsPlaying(false)
    }
  }

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = `ws://localhost:8000/api/v1/ws/conversation/${conversationId}`
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
      }
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      }
      
      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000)
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
      }
      
      websocketRef.current = ws
    }

    connectWebSocket()

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close()
      }
    }
  }, [conversationId])

  const handleWebSocketMessage = (data: any) => {
    if (data.type === 'ai_message') {
      const newMessage: Message = {
        id: data.message_id,
        content: data.content,
        sender: 'ai',
        timestamp: new Date(data.timestamp),
        isAudio: data.is_audio || false,
        audioUrl: data.audio_url
      }
      setMessages(prev => [...prev, newMessage])
    } else if (data.type === 'error') {
      console.error('WebSocket error:', data.message)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
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
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        sendAudioMessage(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error starting recording:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const sendAudioMessage = async (audioBlob: Blob) => {
    if (!websocketRef.current || websocketRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected')
      return
    }

    try {
      setIsLoading(true)
      
      // Convert blob to base64
      const arrayBuffer = await audioBlob.arrayBuffer()
      const base64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)))
      
      // Send audio message via WebSocket
      websocketRef.current.send(JSON.stringify({
        type: 'audio_message',
        conversation_id: conversationId,
        audio_data: base64,
        audio_format: 'webm',
        persona_id: personaId
      }))
      
      // Add user message to UI
      const userMessage: Message = {
        id: Date.now().toString(),
        content: '[Audio message]',
        sender: 'user',
        timestamp: new Date(),
        isAudio: true
      }
      setMessages(prev => [...prev, userMessage])
      
    } catch (error) {
      console.error('Error sending audio message:', error)
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
              <p className="text-sm text-gray-300">{personaAccent}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={isConnected ? "default" : "destructive"}>
              {isConnected ? 'Online' : 'Offline'}
            </Badge>
          </div>
        </div>
      </div>

      {/* Main Call Interface */}
      <div className="flex-1 flex flex-col items-center justify-center p-8">
        {/* Avatar */}
        <div className="mb-8">
          <Avatar 
            size="xl" 
            isActive={callStatus === 'connected'} 
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
          />
        </div>

        {/* Call Controls */}
        <div className="mb-8">
          <CallControls
            isRecording={isRecording}
            isPlaying={isPlaying}
            isConnected={isConnected}
            onStartRecording={startRecording}
            onStopRecording={stopRecording}
            onStartCall={startCall}
            onEndCall={endCall}
            onPlayAudio={() => {}}
            onStopAudio={stopAudio}
          />
        </div>

        {/* Messages (only show when connected) */}
        {callStatus === 'connected' && messages.length > 0 && (
          <div className="w-full max-w-2xl bg-white/5 backdrop-blur-sm rounded-2xl p-4 max-h-64 overflow-y-auto">
            <div className="space-y-3">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start gap-3 max-w-xs ${
                    message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}>
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                      message.sender === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-purple-500 text-white'
                    }`}>
                      {message.sender === 'user' ? <User className="h-3 w-3" /> : <Bot className="h-3 w-3" />}
                    </div>
                    
                    <div className={`rounded-xl px-3 py-2 ${
                      message.sender === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-white/20 text-white'
                    }`}>
                      {message.isAudio ? (
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => message.audioUrl ? playAudio(message.audioUrl) : undefined}
                            className="p-1 h-auto"
                          >
                            {isPlaying && currentAudio?.src === message.audioUrl ? (
                              <VolumeX className="h-3 w-3" />
                            ) : (
                              <Volume2 className="h-3 w-3" />
                            )}
                          </Button>
                          <span className="text-xs">Audio message</span>
                        </div>
                      ) : (
                        <p className="text-sm">{message.content}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-purple-500 flex items-center justify-center">
                      <Bot className="h-3 w-3 text-white" />
                    </div>
                    <div className="bg-white/20 rounded-xl px-3 py-2">
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        <span className="text-xs text-white">AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}