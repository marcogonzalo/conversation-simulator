import { useState, useRef, useCallback } from 'react'
import { apiConfig } from '@/config/api'

interface UseWebSocketProps {
  onMessage: (data: any) => void
  onConnect: () => void
  onDisconnect: () => void
}

export function useWebSocket({ onMessage, onConnect, onDisconnect }: UseWebSocketProps) {
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [realConversationId, setRealConversationId] = useState<string | null>(null)
  
  const websocketRef = useRef<WebSocket | null>(null)

  const connect = useCallback(async (personaId: string) => {
    try {
      setIsLoading(true)
      console.log('Creating conversation...')
      
      // Create conversation
      const createResponse = await fetch(apiConfig.conversations, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          persona_id: personaId,
          metadata: { created_at: new Date().toISOString() }
        }),
      })
      
      if (!createResponse.ok) {
        throw new Error('Failed to create conversation')
      }
      
      const conversationData = await createResponse.json()
      const conversationId = conversationData.conversation_id
      setRealConversationId(conversationId)
      
      // Connect WebSocket
      const wsUrl = apiConfig.conversationWs(conversationId)
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setIsLoading(false)
        onConnect()
        
        // Start voice conversation
        ws.send(JSON.stringify({
          type: 'start_voice_conversation',
          persona_id: personaId
        }))
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('📨 Parsed WebSocket message:', data)
          onMessage(data)
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error)
          console.error('❌ Raw message:', event.data)
        }
      }
      
      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        onDisconnect()
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
        setIsLoading(false)
      }
      
      websocketRef.current = ws
      
    } catch (error) {
      console.error('Error connecting:', error)
      setIsLoading(false)
    }
  }, [onMessage, onConnect, onDisconnect])

  const sendMessage = useCallback((message: any) => {
    console.log('📤 sendMessage called:', message.type)
    console.log('📤 Message content:', message)
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      console.log('📤 WebSocket is open, sending message...')
      const messageString = JSON.stringify(message)
      console.log('📤 Sending message string:', messageString.substring(0, 200) + '...')
      websocketRef.current.send(messageString)
      console.log('✅ WebSocket message sent!')
    } else {
      console.error('❌ WebSocket not connected or not open. State:', websocketRef.current?.readyState)
    }
  }, [])

  const disconnect = useCallback(() => {
    if (websocketRef.current) {
      websocketRef.current.close()
      websocketRef.current = null
    }
    setIsConnected(false)
    setRealConversationId(null)
  }, [])

  return {
    isConnected,
    isLoading,
    realConversationId,
    connect,
    sendMessage,
    disconnect
  }
}
