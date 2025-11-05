'use client'

import { ConversationInterface } from '@/components/conversation/conversation-interface'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Loader2, AlertCircle, ArrowLeft } from 'lucide-react'

interface ConversationPageProps {
  params: Promise<{ id: string }>
}

interface ConversationConfig {
  industry_id: string
  situation_id: string
  psychology_id: string
  identity_id: string
}

export default function ConversationPage({ params }: ConversationPageProps) {
  const router = useRouter()
  const [config, setConfig] = useState<ConversationConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [conversationId, setConversationId] = useState<string>('')
  
  useEffect(() => {
    // Get conversation ID and configuration from localStorage
    params.then(({ id }) => {
      setConversationId(id)
      
      const storedConfig = localStorage.getItem(`conversation_config_${id}`)
      
      if (!storedConfig) {
        // No configuration found, redirect to home
        console.warn('No configuration found for conversation', id)
        router.push('/')
        return
      }
      
      try {
        const parsedConfig = JSON.parse(storedConfig)
        setConfig(parsedConfig)
        setLoading(false)
      } catch (error) {
        console.error('Error parsing conversation config:', error)
        router.push('/')
      }
    })
  }, [params, router])

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 dark:text-blue-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Cargando conversación...</h2>
          <p className="text-slate-600 dark:text-slate-300">Preparando la simulación</p>
        </div>
      </div>
    )
  }

  // No configuration found
  if (!config) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">No hay configuración</h2>
          <p className="text-slate-600 dark:text-slate-300 mb-4">Por favor selecciona una configuración para comenzar la conversación</p>
          <button 
            onClick={() => router.push('/')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors flex items-center gap-2 mx-auto"
          >
            <ArrowLeft className="h-4 w-4" />
            Configurar conversación
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <ConversationInterface
        conversationId={conversationId}
        config={config}
      />
    </div>
  )
}