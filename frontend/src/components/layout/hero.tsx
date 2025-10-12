import { Button } from '@/components/ui/button'
import { ArrowRight, Mic, Brain, BarChart3, Play, Sparkles, History } from 'lucide-react'
import Link from 'next/link'

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%239C92AC%22%20fill-opacity%3D%220.1%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%222%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
      
      {/* Gradient Orbs */}
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      
      <div className="container mx-auto px-4 py-20 relative z-10">
        <div className="text-center max-w-5xl mx-auto">
          {/* Main Title with Enhanced Typography */}
          <div className="mb-8">
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tight mb-6 bg-gradient-to-r from-white via-purple-200 to-blue-200 bg-clip-text text-transparent leading-tight">
              Practica Ventas con
              <br />
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                IA Realista
              </span>
            </h1>
            
            {/* Subtitle with better spacing */}
            <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
              Mejora tus habilidades de ventas conversando con clientes simulados por IA. 
              Recibe feedback detallado y recomendaciones personalizadas.
            </p>
          </div>
          
          {/* Enhanced CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-20">
            <Button 
              asChild 
              size="lg" 
              className="group relative text-lg px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white border-0 rounded-xl shadow-2xl hover:shadow-purple-500/25 transition-all duration-300 transform hover:scale-105"
            >
              <Link href="#personas" className="flex items-center">
                <Play className="mr-3 h-6 w-6 group-hover:rotate-12 transition-transform" />
                Comenzar Conversación
                <ArrowRight className="ml-3 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </Button>
            
            <Button 
              asChild
              variant="outline" 
              size="lg" 
              className="text-lg px-8 py-4 border-2 border-white/20 text-white hover:bg-white/10 rounded-xl backdrop-blur-sm transition-all duration-300 transform hover:scale-105"
            >
              <Link href="/history" className="flex items-center">
                <History className="mr-3 h-5 w-5" />
                Ver Historial
              </Link>
            </Button>
          </div>
        </div>
        
        {/* Enhanced Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div className="group text-center p-8 rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-all duration-300 transform hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/20">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:rotate-6 transition-transform duration-300 shadow-lg">
              <Mic className="h-10 w-10 text-white" />
            </div>
            <h3 className="text-2xl font-bold mb-4 text-white">Conversación de Voz</h3>
            <p className="text-gray-300 text-lg leading-relaxed">
              Interactúa naturalmente con clientes simulados usando tu voz
            </p>
          </div>
          
          <div className="group text-center p-8 rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-all duration-300 transform hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/20">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:rotate-6 transition-transform duration-300 shadow-lg">
              <Brain className="h-10 w-10 text-white" />
            </div>
            <h3 className="text-2xl font-bold mb-4 text-white">IA Avanzada</h3>
            <p className="text-gray-300 text-lg leading-relaxed">
              Personalidades realistas con acentos regionales auténticos
            </p>
          </div>
          
          <div className="group text-center p-8 rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-all duration-300 transform hover:scale-105 hover:shadow-2xl hover:shadow-green-500/20">
            <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:rotate-6 transition-transform duration-300 shadow-lg">
              <BarChart3 className="h-10 w-10 text-white" />
            </div>
            <h3 className="text-2xl font-bold mb-4 text-white">Análisis Detallado</h3>
            <p className="text-gray-300 text-lg leading-relaxed">
              Recibe feedback cuantificable y recomendaciones de mejora
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
