import { CheckCircle, Clock, Target, Users, Zap, Shield, Award, TrendingUp } from 'lucide-react'

export function Features() {
  const features = [
    {
      icon: <Users className="h-8 w-8" />,
      title: "Múltiples Personalidades",
      description: "Practica con diferentes tipos de clientes: escépticos, entusiastas, analíticos y más.",
      gradient: "from-blue-500 to-cyan-500",
      bgColor: "bg-blue-50",
      textColor: "text-blue-600"
    },
    {
      icon: <Clock className="h-8 w-8" />,
      title: "Tiempo Real",
      description: "Conversaciones fluidas con latencia menor a 500ms para una experiencia natural.",
      gradient: "from-green-500 to-emerald-500",
      bgColor: "bg-green-50",
      textColor: "text-green-600"
    },
    {
      icon: <Target className="h-8 w-8" />,
      title: "Objetivos Específicos",
      description: "Cada cliente tiene objetivos, objeciones y factores de decisión únicos.",
      gradient: "from-purple-500 to-pink-500",
      bgColor: "bg-purple-50",
      textColor: "text-purple-600"
    },
    {
      icon: <CheckCircle className="h-8 w-8" />,
      title: "Feedback Inmediato",
      description: "Análisis automático de tu performance con recomendaciones accionables.",
      gradient: "from-orange-500 to-red-500",
      bgColor: "bg-orange-50",
      textColor: "text-orange-600"
    }
  ]

  const stats = [
    { icon: <Zap className="h-6 w-6" />, value: "< 500ms", label: "Latencia" },
    { icon: <Shield className="h-6 w-6" />, value: "100%", label: "Seguro" },
    { icon: <Award className="h-6 w-6" />, value: "24/7", label: "Disponible" },
    { icon: <TrendingUp className="h-6 w-6" />, value: "95%", label: "Satisfacción" }
  ]

  return (
    <section className="py-24 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2240%22%20height%3D%2240%22%20viewBox%3D%220%200%2040%2040%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22%23e2e8f0%22%20fill-opacity%3D%220.3%22%3E%3Cpath%20d%3D%22M20%2020c0-11.046-8.954-20-20-20v20h20z%22/%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
      
      <div className="container mx-auto px-4 relative z-10">
        {/* Header */}
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-full text-sm font-medium mb-8 shadow-lg">
            <Award className="h-4 w-4" />
            Plataforma Avanzada
          </div>
          
          <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
            ¿Por qué elegir nuestro simulador?
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Una plataforma completa para desarrollar tus habilidades de ventas de manera efectiva y realista.
          </p>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-20">
          {stats.map((stat, index) => (
            <div key={index} className="text-center p-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4 text-white shadow-lg">
                {stat.icon}
              </div>
              <div className="text-2xl font-bold text-slate-900 mb-2">{stat.value}</div>
              <div className="text-slate-600 font-medium">{stat.label}</div>
            </div>
          ))}
        </div>
        
        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="group relative bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105 border border-white/20 overflow-hidden"
            >
              {/* Background Gradient */}
              <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
              
              <div className="relative z-10 text-center">
                <div className={`w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mx-auto mb-6 text-white shadow-lg group-hover:rotate-6 transition-transform duration-300`}>
                  {feature.icon}
                </div>
                
                <h3 className="text-xl font-bold text-slate-900 mb-4 group-hover:text-slate-800 transition-colors">
                  {feature.title}
                </h3>
                
                <p className="text-slate-600 leading-relaxed group-hover:text-slate-700 transition-colors">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-20">
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-12 shadow-2xl border border-white/20 max-w-4xl mx-auto">
            <h3 className="text-3xl font-bold text-slate-900 mb-6">
              ¿Listo para mejorar tus habilidades de ventas?
            </h3>
            <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
              Únete a miles de profesionales que ya están desarrollando sus habilidades con nuestro simulador de IA.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center gap-2">
                <Zap className="h-5 w-5 group-hover:rotate-12 transition-transform" />
                Comenzar Ahora
              </button>
              <button className="px-8 py-4 border-2 border-slate-300 text-slate-700 hover:border-slate-400 hover:bg-slate-50 rounded-xl font-medium transition-all duration-300 transform hover:scale-105">
                Ver Demo
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
