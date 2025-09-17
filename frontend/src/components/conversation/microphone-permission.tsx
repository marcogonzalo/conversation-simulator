"use client"

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Mic, MicOff, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'

interface MicrophonePermissionProps {
  permissionStatus: 'checking' | 'granted' | 'denied' | 'prompt'
  isRequesting: boolean
  error: string | null
  onRequestPermission: () => void
}

export function MicrophonePermission({
  permissionStatus,
  isRequesting,
  error,
  onRequestPermission
}: MicrophonePermissionProps) {
  const getStatusInfo = () => {
    switch (permissionStatus) {
      case 'checking':
        return {
          icon: <Loader2 className="h-6 w-6 animate-spin" />,
          text: 'Verificando acceso al micrófono...',
          color: 'bg-blue-500',
          showButton: false
        }
      case 'granted':
        return {
          icon: <CheckCircle className="h-6 w-6 text-green-400" />,
          text: 'Micrófono autorizado',
          color: 'bg-green-500',
          showButton: false
        }
      case 'denied':
        return {
          icon: <MicOff className="h-6 w-6 text-red-400" />,
          text: 'Acceso al micrófono denegado',
          color: 'bg-red-500',
          showButton: true
        }
      case 'prompt':
        return {
          icon: <Mic className="h-6 w-6 text-yellow-400" />,
          text: 'Solicitar acceso al micrófono',
          color: 'bg-yellow-500',
          showButton: true
        }
      default:
        return {
          icon: <AlertCircle className="h-6 w-6 text-gray-400" />,
          text: 'Estado desconocido',
          color: 'bg-gray-500',
          showButton: true
        }
    }
  }

  const statusInfo = getStatusInfo()

  return (
    <div className="flex flex-col items-center justify-center gap-6 p-8 bg-black/20 rounded-2xl">
      {/* Icon */}
      <div className="flex items-center justify-center w-20 h-20 rounded-full bg-white/10 backdrop-blur-sm">
        {statusInfo.icon}
      </div>

      {/* Status Badge */}
      <Badge 
        variant="default" 
        className={`${statusInfo.color} text-white px-4 py-2 text-sm font-medium flex items-center gap-2`}
      >
        {statusInfo.text}
      </Badge>

      {/* Error Message */}
      {error && (
        <div className="text-center max-w-md">
          <p className="text-sm text-red-400 mb-2">{error}</p>
          <p className="text-xs text-white/60">
            Por favor, permite el acceso al micrófono en la configuración de tu navegador.
          </p>
        </div>
      )}

      {/* Instructions */}
      {permissionStatus === 'prompt' && (
        <div className="text-center max-w-md">
          <p className="text-sm text-white/80 mb-2">
            Necesitamos acceso a tu micrófono para la conversación de voz.
          </p>
          <p className="text-xs text-white/60">
            Haz clic en el botón de abajo y permite el acceso cuando tu navegador te lo solicite.
          </p>
        </div>
      )}

      {/* Request Permission Button */}
      {statusInfo.showButton && (
        <Button
          onClick={onRequestPermission}
          disabled={isRequesting}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          {isRequesting ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Solicitando...
            </>
          ) : (
            <>
              <Mic className="h-4 w-4 mr-2" />
              Permitir acceso al micrófono
            </>
          )}
        </Button>
      )}

      {/* Help Text */}
      {(permissionStatus === 'denied' || permissionStatus === 'prompt') && (
        <div className="text-center max-w-md">
          <p className="text-xs text-white/50">
            Si ya has denegado el acceso, puedes habilitarlo manualmente en la configuración de tu navegador.
          </p>
        </div>
      )}
    </div>
  )
}
