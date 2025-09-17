"use client"

import { Badge } from '@/components/ui/badge'
import { Clock, Wifi, WifiOff } from 'lucide-react'

interface CallStatusProps {
  status: 'idle' | 'connecting' | 'connected' | 'disconnected'
  duration?: number
  isConnected: boolean
  isRecording?: boolean
  isReadyToSpeak?: boolean
}

export function CallStatus({ status, duration, isConnected, isRecording, isReadyToSpeak }: CallStatusProps) {
  const getStatusInfo = () => {
    switch (status) {
      case 'idle':
        return { text: 'Listo para comenzar', color: 'bg-gray-500', icon: null }
      case 'connecting':
        return { text: 'Conectando...', color: 'bg-yellow-500', icon: <Wifi className="h-4 w-4 animate-pulse" /> }
      case 'connected':
        if (isReadyToSpeak) {
          return { text: 'Listo para hablar', color: 'bg-green-500', icon: <Wifi className="h-4 w-4" /> }
        } else {
          return { text: 'Conectado', color: 'bg-blue-500', icon: <Wifi className="h-4 w-4" /> }
        }
      case 'disconnected':
        return { text: 'Desconectado', color: 'bg-red-500', icon: <WifiOff className="h-4 w-4" /> }
      default:
        return { text: 'Desconocido', color: 'bg-gray-500', icon: null }
    }
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const statusInfo = getStatusInfo()

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Status Badge */}
      <Badge 
        variant="default" 
        className={`${statusInfo.color} text-white px-4 py-2 text-sm font-medium flex items-center gap-2`}
      >
        {statusInfo.icon}
        {statusInfo.text}
      </Badge>

      {/* Duration */}
      {duration !== undefined && status === 'connected' && (
        <div className="flex items-center gap-2 text-white/80">
          <Clock className="h-4 w-4" />
          <span className="font-mono text-lg">{formatDuration(duration)}</span>
        </div>
      )}

      {/* Microphone Status */}
      {isConnected && isRecording && (
        <div className="text-center">
          <div className="flex items-center gap-2 text-green-400">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">Grabando audio...</span>
          </div>
        </div>
      )}

      {/* Ready to Speak Status */}
      {isConnected && isReadyToSpeak && !isRecording && (
        <div className="text-center">
          <span className="text-sm font-medium text-green-400">Puedes empezar a hablar</span>
        </div>
      )}

      {/* Connection Status */}
      <div className="text-center">
        <p className="text-sm text-white/60">
          {isConnected 
            ? (isReadyToSpeak ? 'Conexión estable - Listo para conversar' : 'Estableciendo comunicación...')
            : 'Verificando conexión...'
          }
        </p>
      </div>
    </div>
  )
}
