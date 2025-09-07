import { Mic, Users, Target, Clock, MapPin, Building, TrendingUp, Star } from 'lucide-react'
import { useRouter } from 'next/navigation'

export function PersonaSelector() {
  const router = useRouter()
  
  const personas = [
    {
      id: "carlos_mendoza",
      name: "Carlos Mendoza",
      title: "CEO",
      company: "TechStart México",
      industry: "Tecnología",
      location: "Mexicano (CDMX)",
      description: "CEO de una startup tecnológica, entusiasta de la innovación pero con presupuesto limitado",
      personality_traits: ["innovative", "friendly", "impatient"],
      difficulty: "Principiante",
      duration: "5-8 min",
      avatar: "CM",
      accent: "Caribeño (Cubano)",
      characteristics: [
        "Hace preguntas específicas",
        "Busca ROI claro", 
        "Toma decisiones rápidas"
      ]
    },
    {
      id: "maria_rodriguez", 
      name: "María Rodríguez",
      title: "Directora de Marketing",
      company: "FinServ Corp",
      industry: "Servicios Financieros",
      location: "Peruano (Lima)",
      description: "Directora de Marketing de una empresa mediana, escéptica pero abierta a nuevas tecnologías",
      personality_traits: ["skeptical", "analytical", "pragmatic"],
      difficulty: "Intermedio",
      duration: "8-12 min",
      avatar: "MR",
      accent: "Peruano",
      characteristics: [
        "Analiza cada propuesta",
        "Busca evidencia de resultados",
        "Proceso de decisión lento"
      ]
    },
    {
      id: "ana_garcia",
      name: "Ana García",
      title: "Gerente de Ventas", 
      company: "ManufacturaPlus",
      industry: "Manufactura",
      location: "Venezolano (Caracas)",
      description: "Gerente de Ventas de una empresa tradicional, conservadora pero interesada en modernizar procesos",
      personality_traits: ["conservative", "friendly", "pragmatic"],
      difficulty: "Avanzado",
      duration: "10-15 min",
      avatar: "AG",
      accent: "Venezolano",
      characteristics: [
        "Resistente al cambio",
        "Valora la estabilidad",
        "Necesita convencimiento"
      ]
    }
  ]

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      "Principiante": "bg-green-100 text-green-800 border-green-200",
      "Intermedio": "bg-yellow-100 text-yellow-800 border-yellow-200", 
      "Avanzado": "bg-orange-100 text-orange-800 border-orange-200",
      "Experto": "bg-red-100 text-red-800 border-red-200"
    }
    return colors[difficulty as keyof typeof colors] || "bg-gray-100 text-gray-800 border-gray-200"
  }

  const getTraitColor = (trait: string) => {
    const colors = {
      'innovative': 'bg-purple-100 text-purple-700',
      'friendly': 'bg-pink-100 text-pink-700',
      'impatient': 'bg-red-100 text-red-700',
      'skeptical': 'bg-yellow-100 text-yellow-700',
      'analytical': 'bg-blue-100 text-blue-700',
      'pragmatic': 'bg-green-100 text-green-700',
      'conservative': 'bg-gray-100 text-gray-700'
    }
    return colors[trait as keyof typeof colors] || 'bg-gray-100 text-gray-700'
  }

  return (
    <section id="personas" className="py-24 bg-gradient-to-b from-slate-50 to-white">
      <div className="container mx-auto px-4">
        {/* Header Section */}
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <Users className="h-4 w-4" />
            6 Perfiles Disponibles
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
            Perfiles de Clientes
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Selecciona un cliente para practicar
          </p>
        </div>

        {/* Filter Bar */}
        <div className="flex flex-wrap items-center justify-between mb-12 p-6 bg-white rounded-2xl shadow-lg border border-slate-200">
          <div className="flex items-center gap-4 mb-4 sm:mb-0">
            <span className="text-slate-700 font-medium">Filtrar por dificultad:</span>
          </div>
          <div className="flex flex-wrap gap-3">
            {["Todos", "Principiante", "Intermedio", "Avanzado", "Experto"].map((filter) => (
              <button
                key={filter}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                  filter === "Todos" 
                    ? "bg-blue-600 text-white shadow-lg" 
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>
        
        {/* Persona Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {personas.map((persona) => (
            <div 
              key={persona.id} 
              className="group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105 border border-slate-200 overflow-hidden"
            >
              {/* Card Header */}
              <div className="p-6 border-b border-slate-100">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg">
                      {persona.avatar}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-900 mb-1">{persona.name}</h3>
                      <p className="text-slate-600 font-medium">{persona.title}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getDifficultyColor(persona.difficulty)}`}>
                    {persona.difficulty}
                  </span>
                </div>
                
                <p className="text-slate-600 leading-relaxed mb-4">{persona.description}</p>
              </div>

              {/* Card Content */}
              <div className="p-6 space-y-6">
                {/* Company Info */}
                <div className="space-y-3">
                  <div className="flex items-center gap-3 text-slate-600">
                    <Building className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium">{persona.company}</span>
                  </div>
                  <div className="flex items-center gap-3 text-slate-600">
                    <TrendingUp className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium">{persona.industry}</span>
                  </div>
                  <div className="flex items-center gap-3 text-slate-600">
                    <Users className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium">{persona.personality_traits.join(", ")}</span>
                  </div>
                  <div className="flex items-center gap-3 text-slate-600">
                    <MapPin className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium">{persona.location}</span>
                  </div>
                  <div className="flex items-center gap-3 text-slate-600">
                    <Clock className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium">{persona.duration}</span>
                  </div>
                </div>

                {/* Characteristics */}
                <div>
                  <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                    <Target className="h-4 w-4 text-blue-500" />
                    Características:
                  </h4>
                  <ul className="space-y-2">
                    {persona.characteristics.map((char, index) => (
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
          ))}
        </div>

        {/* Footer Info */}
        <div className="mt-20 grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200">
            <h3 className="text-2xl font-bold text-slate-900 mb-6 flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Star className="h-5 w-5 text-white" />
              </div>
              Niveles de Dificultad
            </h3>
            <div className="space-y-4">
              {[
                { level: "Principiante", color: "green", desc: "Clientes receptivos y amigables" },
                { level: "Intermedio", color: "yellow", desc: "Algunos desafíos y objeciones" },
                { level: "Avanzado", color: "orange", desc: "Clientes exigentes con múltiples objeciones" },
                { level: "Experto", color: "red", desc: "Máximo desafío, clientes muy difíciles" }
              ].map((item) => (
                <div key={item.level} className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full bg-${item.color}-500`}></div>
                  <div>
                    <span className="font-medium text-slate-900">{item.level}</span>
                    <p className="text-sm text-slate-600">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200">
            <h3 className="text-2xl font-bold text-slate-900 mb-6 flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
                <Target className="h-5 w-5 text-white" />
              </div>
              Características Especiales
            </h3>
            <ul className="space-y-3">
              {[
                "Acentos Regionales: Inmersión total con voces auténticas",
                "Personalidades Únicas: Cada cliente tiene comportamientos específicos", 
                "Contexto Industrial: Escenarios realistas por sector",
                "Feedback Personalizado: Análisis específico por perfil"
              ].map((feature, index) => (
                <li key={index} className="flex items-start gap-3 text-slate-600">
                  <span className="text-purple-500 mt-1">•</span>
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  )
}
