import { useState, useRef, useCallback } from 'react'
import { apiConfig } from '@/config/api'

interface ConversationConfig {
  industry_id?: string
  situation_id?: string
  psychology_id?: string
  identity_id: string
}

interface UseWebSocketProps {
  onMessage: (data: any) => void
  onConnect: () => void
  onDisconnect: () => void
  onAnalysis?: (analysis: any) => void
}

export function useWebSocket({ onMessage, onConnect, onDisconnect, onAnalysis }: UseWebSocketProps) {
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [realConversationId, setRealConversationId] = useState<string | null>(null)
  const [isEnding, setIsEnding] = useState(false)
  
  const websocketRef = useRef<WebSocket | null>(null)

  const connect = useCallback(async (config: ConversationConfig, contextId: string = "default") => {
    try {
      setIsLoading(true)
      setIsEnding(false) // Reset ending state for new conversation
      console.log('Creating conversation...')
      
      // Create conversation
      const createResponse = await fetch(apiConfig.conversations, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          persona_id: config.identity_id,
          context_id: contextId,
          metadata: { 
            created_at: new Date().toISOString(),
            industry_id: config.industry_id,
            situation_id: config.situation_id,
            psychology_id: config.psychology_id
          }
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
        
        // Start voice conversation with 5-layer configuration
        ws.send(JSON.stringify({
          type: 'start_voice_conversation',
          persona_id: config.identity_id,
          industry_id: config.industry_id || 'real_estate',
          situation_id: config.situation_id || 'discovery_no_urgency_price',
          psychology_id: config.psychology_id || 'conservative_analytical'
        }))
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type !== 'transcribed_text' && data.role != 'ai') {
            console.log('📨 Parsed WebSocket message:', data)
          }

          // Ignore audio messages if conversation is ending
          if (isEnding && data.type === 'audio') {
            console.log('📨 Ignoring audio message during conversation end')
            return
          }
          
          // Handle analysis result
          if (data.type === 'analysis_result' && onAnalysis) {
            console.log('📊 Received analysis result:', {
              hasAnalysis: !!data.analysis,
              hasAnalysisId: !!data.analysis_id,
              analysisLength: data.analysis ? data.analysis.length : 0
            })
            onAnalysis({
              analysis: data.analysis,
              analysis_id: data.analysis_id
            })
            return
          }
          
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
    
    // Mark as ending when sending end_voice_conversation
    if (message.type === 'end_voice_conversation') {
      setIsEnding(true)
    }
    
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
