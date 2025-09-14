import { useState, useCallback } from 'react'

export interface Message {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
  isAudio?: boolean
}

export function useConversation() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false)

  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: `${message.sender}_${Date.now()}`,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newMessage])
  }, [])

  const updateLastMessage = useCallback((content: string) => {
    setMessages(prev => {
      const updated = [...prev]
      const lastMessage = updated[updated.length - 1]
      if (lastMessage && lastMessage.sender === 'user' && lastMessage.content === '[Audio message]') {
        lastMessage.content = content
      }
      return updated
    })
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  return {
    messages,
    isWaitingForResponse,
    setIsWaitingForResponse,
    addMessage,
    updateLastMessage,
    clearMessages
  }
}
