'use client'

import { ConversationInterface } from '@/components/conversation/conversation-interface'
import { usePersonaStore } from '@/store/persona-store'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { Loader2, AlertCircle, ArrowLeft } from 'lucide-react'

interface ConversationPageProps {
  params: Promise<{ id: string }>
}

export default function ConversationPage({ params }: ConversationPageProps) {
  const router = useRouter()
  const { selectedPersona, loadPersonaById, loading, error } = usePersonaStore()
  
  useEffect(() => {
    // Get conversation ID from URL params
    params.then(({ id }) => {
      // If no persona is selected, try to load from URL or redirect to persona selection
      if (!selectedPersona) {
        // For now, redirect to persona selection if no persona is selected
        router.push('/')
      }
    })
  }, [params, selectedPersona, router])

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Cargando conversación...</h2>
          <p className="text-slate-600">Preparando la simulación</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Error al cargar la conversación</h2>
          <p className="text-slate-600 mb-4">{error}</p>
          <button 
            onClick={() => router.push('/')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors flex items-center gap-2 mx-auto"
          >
            <ArrowLeft className="h-4 w-4" />
            Volver a seleccionar persona
          </button>
        </div>
      </div>
    )
  }

  // No persona selected
  if (!selectedPersona) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">No hay persona seleccionada</h2>
          <p className="text-slate-600 mb-4">Por favor selecciona una persona para comenzar la conversación</p>
          <button 
            onClick={() => router.push('/')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors flex items-center gap-2 mx-auto"
          >
            <ArrowLeft className="h-4 w-4" />
            Seleccionar persona
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen">
      <ConversationInterface
        conversationId={params.then(p => p.id)}
        personaId={selectedPersona.id}
        personaName={selectedPersona.name}
        personaAccent={selectedPersona.accent}
        persona={selectedPersona}
      />
    </div>
  )
}