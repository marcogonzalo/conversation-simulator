'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useConversationConfigStore } from '@/store/conversation-config-store'
import { Building, Target, Brain, User, ArrowRight, Loader2 } from 'lucide-react'

export function ConversationConfigSelector() {
  const router = useRouter()
  const {
    industries,
    situations,
    psychologies,
    identities,
    selectedIndustry,
    selectedSituation,
    selectedPsychology,
    selectedIdentity,
    loading,
    error,
    setIndustry,
    setSituation,
    setPsychology,
    setIdentity,
    loadOptions,
    isConfigComplete
  } = useConversationConfigStore()

  useEffect(() => {
    loadOptions()
  }, [loadOptions])

  const handleStartConversation = () => {
    if (isConfigComplete()) {
      const conversationId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      
      // Store configuration in localStorage for the conversation page
      const config = {
        industry_id: selectedIndustry,
        situation_id: selectedSituation,
        psychology_id: selectedPsychology,
        identity_id: selectedIdentity,
        timestamp: Date.now()
      }
      
      localStorage.setItem(`conversation_config_${conversationId}`, JSON.stringify(config))
      
      // Navigate to conversation page
      router.push(`/conversation/${conversationId}`)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-slate-600 dark:text-slate-300">Cargando configuraciones...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center text-red-600 dark:text-red-400">
          <p className="text-xl font-semibold mb-2">Error</p>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
            Configurar Simulación de Conversación
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-300">
            Selecciona una opción de cada capa para crear tu escenario personalizado
          </p>
        </div>

        {/* Configuration Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          
          {/* Layer 2: Industry */}
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Building className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                Industria
              </h2>
            </div>
            <div className="space-y-2">
              {industries.map((industry) => (
                <button
                  key={industry.id}
                  onClick={() => setIndustry(industry.id)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    selectedIndustry === industry.id
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-blue-400'
                  }`}
                >
                  <p className="font-medium text-slate-900 dark:text-white">{industry.name}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Layer 3: Sales Situation */}
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Target className="w-6 h-6 text-purple-600" />
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                Situación de Venta
              </h2>
            </div>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {situations.map((situation) => (
                <button
                  key={situation.id}
                  onClick={() => setSituation(situation.id)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    selectedSituation === situation.id
                      ? 'border-purple-600 bg-purple-50 dark:bg-purple-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-purple-400'
                  }`}
                >
                  <p className="font-medium text-slate-900 dark:text-white text-sm">{situation.name}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Layer 4: Client Psychology */}
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Brain className="w-6 h-6 text-green-600" />
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                Psicología del Cliente
              </h2>
            </div>
            <div className="space-y-2">
              {psychologies.map((psychology) => (
                <button
                  key={psychology.id}
                  onClick={() => setPsychology(psychology.id)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    selectedPsychology === psychology.id
                      ? 'border-green-600 bg-green-50 dark:bg-green-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-green-400'
                  }`}
                >
                  <p className="font-medium text-slate-900 dark:text-white">{psychology.name}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Layer 5: Client Identity */}
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <User className="w-6 h-6 text-orange-600" />
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                Identidad del Cliente
              </h2>
            </div>
            <div className="space-y-2">
              {identities.map((identity) => (
                <button
                  key={identity.id}
                  onClick={() => setIdentity(identity.id)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    selectedIdentity === identity.id
                      ? 'border-orange-600 bg-orange-50 dark:bg-orange-900/20'
                      : 'border-slate-200 dark:border-slate-700 hover:border-orange-400'
                  }`}
                >
                  <p className="font-medium text-slate-900 dark:text-white">{identity.name}</p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Selected Configuration Summary */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Configuración Seleccionada
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-slate-500 dark:text-slate-400 mb-1">Industria</p>
              <p className="font-medium text-slate-900 dark:text-white">
                {industries.find(i => i.id === selectedIndustry)?.name || 'No seleccionada'}
              </p>
            </div>
            <div>
              <p className="text-slate-500 dark:text-slate-400 mb-1">Situación</p>
              <p className="font-medium text-slate-900 dark:text-white">
                {situations.find(s => s.id === selectedSituation)?.name?.split(' - ')[0] || 'No seleccionada'}
              </p>
            </div>
            <div>
              <p className="text-slate-500 dark:text-slate-400 mb-1">Psicología</p>
              <p className="font-medium text-slate-900 dark:text-white">
                {psychologies.find(p => p.id === selectedPsychology)?.name || 'No seleccionada'}
              </p>
            </div>
            <div>
              <p className="text-slate-500 dark:text-slate-400 mb-1">Identidad</p>
              <p className="font-medium text-slate-900 dark:text-white">
                {identities.find(i => i.id === selectedIdentity)?.name?.split(' (')[0] || 'No seleccionada'}
              </p>
            </div>
          </div>
        </div>

        {/* Start Button */}
        <div className="text-center">
          <button
            onClick={handleStartConversation}
            disabled={!isConfigComplete()}
            className={`
              px-8 py-4 rounded-xl font-semibold text-lg transition-all transform
              ${isConfigComplete()
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl hover:scale-105'
                : 'bg-slate-300 dark:bg-slate-700 text-slate-500 dark:text-slate-400 cursor-not-allowed'
              }
            `}
          >
            <span className="flex items-center gap-2">
              Iniciar Conversación
              <ArrowRight className="w-5 h-5" />
            </span>
          </button>
          
          {!isConfigComplete() && (
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
              Selecciona una opción en cada capa para continuar
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

