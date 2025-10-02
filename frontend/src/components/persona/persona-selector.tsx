import { Mic, Users, Target, Clock, MapPin, Building, TrendingUp, Star, Loader2, AlertCircle } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { usePersonaStore } from '@/store/persona-store'
import { humanizeAccent } from '@/utils/accentUtils'

export function PersonaSelector() {
  const router = useRouter()
  const { 
    availablePersonas, 
    loading, 
    error, 
    loadPersonas, 
    selectPersona 
  } = usePersonaStore()
  
  // Load personas on component mount
  useEffect(() => {
    loadPersonas()
  }, [loadPersonas])
  
  // Helper function to get avatar initials
  const getAvatarInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }
  
  // Helper function to get difficulty level based on personality traits
  const getDifficultyLevel = (traits: string[]) => {
    if (traits.includes('skeptical') || traits.includes('analytical')) {
      return 'Intermedio'
    } else if (traits.includes('conservative') || traits.includes('pragmatic')) {
      return 'Avanzado'
    }
    return 'Principiante'
  }
  
  // Helper function to get duration based on personality traits
  const getDuration = (traits: string[]) => {
    if (traits.includes('skeptical') || traits.includes('analytical')) {
      return '8-12 min'
    } else if (traits.includes('conservative') || traits.includes('pragmatic')) {
      return '10-15 min'
    }
    return '5-8 min'
  }
  

  // Helper function to get characteristics based on personality traits
  const getCharacteristics = (traits: string[]) => {
    const characteristics: string[] = []
    
    if (traits.includes('innovative')) {
      characteristics.push('Hace preguntas específicas', 'Busca ROI claro', 'Toma decisiones rápidas')
    }
    if (traits.includes('skeptical') || traits.includes('analytical')) {
      characteristics.push('Analiza cada propuesta', 'Busca evidencia de resultados', 'Proceso de decisión lento')
    }
    if (traits.includes('conservative') || traits.includes('pragmatic')) {
      characteristics.push('Prefiere métodos probados', 'Cautelosa con nuevas tecnologías', 'Se enfoca en la experiencia del usuario')
    }
    if (traits.includes('friendly')) {
      characteristics.push('Muy cálida y amigable', 'Muestra interés pero con precaución', 'Siempre piensa en el equipo')
    }
    
    return characteristics.length > 0 ? characteristics : ['Busca soluciones prácticas', 'Valora la experiencia', 'Toma decisiones informadas']
  }
  
  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Cargando personas...</h2>
          <p className="text-slate-600">Preparando las personalidades para tu simulación</p>
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
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Error al cargar personas</h2>
          <p className="text-slate-600 mb-4">{error}</p>
          <button 
            onClick={() => loadPersonas()}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    )
  }
  
  // No personas state
  if (availablePersonas.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <Users className="h-12 w-12 text-slate-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">No hay personas disponibles</h2>
          <p className="text-slate-600">No se encontraron personas para simular</p>
        </div>
      </div>
    )
  }

  return (
    <div id="personas" className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-slate-900 mb-4">
            Selecciona tu Persona
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Elige con quién quieres practicar tu conversación de ventas. 
            Cada persona tiene su propia personalidad, objetivos y desafíos únicos.
          </p>
        </div>

        {/* Personas Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {availablePersonas.map((persona) => {
            const difficulty = getDifficultyLevel(persona.personality_traits)
            const duration = getDuration(persona.personality_traits)
            const characteristics = getCharacteristics(persona.personality_traits)
            const avatar = getAvatarInitials(persona.name)
            
            return (
              <div 
                key={persona.id}
                className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 border border-slate-200 overflow-hidden"
              >
                {/* Card Header */}
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-lg font-bold">
                      {avatar}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold">{persona.name}</h3>
                      <p className="text-blue-100 text-sm">{persona.metadata?.role || 'Ejecutivo'}</p>
                    </div>
                  </div>
                  
                  <p className="text-blue-100 text-sm leading-relaxed">
                    {persona.description}
                  </p>
                </div>

                {/* Card Body */}
                <div className="p-6 space-y-6">
                  {/* Basic Info */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2 text-slate-600">
                      <Building className="h-4 w-4 text-blue-500" />
                      <span>{persona.metadata?.company || 'Empresa'}</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-600">
                      <MapPin className="h-4 w-4 text-blue-500" />
                      <span>{humanizeAccent(persona.accent)}</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-600">
                      <TrendingUp className="h-4 w-4 text-blue-500" />
                      <span>{persona.metadata?.industry || 'Industria'}</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-600">
                      <Users className="h-4 w-4 text-blue-500" />
                      <span>{persona.metadata?.team_size || 'Equipo'}</span>
                    </div>
                  </div>

                  {/* Difficulty and Duration */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Star className="h-4 w-4 text-yellow-500" />
                      <span className="text-sm font-medium text-slate-700">{difficulty}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-green-500" />
                      <span className="text-sm font-medium text-slate-700">{duration}</span>
                    </div>
                  </div>

                  {/* Characteristics */}
                  <div>
                    <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                      <Target className="h-4 w-4 text-blue-500" />
                      Características:
                    </h4>
                    <ul className="space-y-2">
                      {characteristics.map((char, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-slate-600">
                          <span className="text-blue-500 mt-1">•</span>
                          <span>{char}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Action Button */}
                  <button 
                    onClick={() => {
                      selectPersona(persona)
                      // Generate a random conversation ID for demo
                      const conversationId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
                      router.push(`/conversation/${conversationId}`)
                    }}
                    className="w-full group/btn bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-3 px-6 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                  >
                    <Mic className="h-5 w-5 group-hover/btn:rotate-12 transition-transform" />
                    Iniciar Simulación
                  </button>
                </div>
              </div>
            )
          })}
        </div>

        {/* Footer Info */}
        <div className="mt-20 grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div className="text-center lg:text-left">
            <h3 className="text-2xl font-bold text-slate-900 mb-4">
              ¿Cómo funciona la simulación?
            </h3>
            <p className="text-slate-600 leading-relaxed">
              Cada persona está diseñada con personalidades únicas, objetivos específicos y 
              desafíos reales que encontrarás en el mundo de las ventas. La IA asumirá su 
              identidad y responderá de manera auténtica a tus preguntas y propuestas.
            </p>
          </div>
          
          <div className="text-center lg:text-left">
            <h3 className="text-2xl font-bold text-slate-900 mb-4">
              Consejos para el éxito
            </h3>
            <ul className="space-y-2 text-slate-600">
              <li className="flex items-center gap-2">
                <span className="text-blue-500">•</span>
                <span>Escucha activamente las respuestas</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-blue-500">•</span>
                <span>Adapta tu enfoque a su personalidad</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-blue-500">•</span>
                <span>Haz preguntas abiertas y específicas</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-blue-500">•</span>
                <span>Enfócate en sus objetivos y desafíos</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}