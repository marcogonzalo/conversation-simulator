import { useState, useEffect, useCallback } from 'react'

interface UseMicrophonePermissionProps {
  onPermissionGranted?: () => void
  onPermissionDenied?: () => void
}

export function useMicrophonePermission({ 
  onPermissionGranted, 
  onPermissionDenied 
}: UseMicrophonePermissionProps = {}) {
  const [permissionStatus, setPermissionStatus] = useState<'checking' | 'granted' | 'denied' | 'prompt'>('checking')
  const [isRequesting, setIsRequesting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const checkPermission = useCallback(async () => {
    try {
      setError(null)
      setPermissionStatus('checking')

      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError('El navegador no soporta acceso al micrófono')
        setPermissionStatus('denied')
        onPermissionDenied?.()
        return
      }

      // Check permission status
      if ('permissions' in navigator) {
        try {
          const permission = await navigator.permissions.query({ name: 'microphone' as PermissionName })
          
          switch (permission.state) {
            case 'granted':
              setPermissionStatus('granted')
              onPermissionGranted?.()
              break
            case 'denied':
              setPermissionStatus('denied')
              onPermissionDenied?.()
              break
            case 'prompt':
              setPermissionStatus('prompt')
              break
          }

          // Listen for permission changes
          permission.onchange = () => {
            checkPermission()
          }
        } catch (permissionError) {
          // Fallback: try to get user media to check permission
          console.log('Permission API not available, checking via getUserMedia')
          await requestPermission()
        }
      } else {
        // Fallback: try to get user media to check permission
        await requestPermission()
      }
    } catch (err) {
      console.error('Error checking microphone permission:', err)
      setError('Error al verificar permisos del micrófono')
      setPermissionStatus('denied')
      onPermissionDenied?.()
    }
  }, [onPermissionGranted, onPermissionDenied])

  const requestPermission = useCallback(async () => {
    try {
      setIsRequesting(true)
      setError(null)

      // Try to get user media to request permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Permission granted
      setPermissionStatus('granted')
      onPermissionGranted?.()
      
      // Stop the stream immediately as we just needed to check permission
      stream.getTracks().forEach(track => track.stop())
      
    } catch (err: any) {
      console.error('Error requesting microphone permission:', err)
      
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setError('Permisos del micrófono denegados')
        setPermissionStatus('denied')
        onPermissionDenied?.()
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setError('No se encontró ningún micrófono')
        setPermissionStatus('denied')
        onPermissionDenied?.()
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        setError('El micrófono está siendo usado por otra aplicación')
        setPermissionStatus('denied')
        onPermissionDenied?.()
      } else if (err.name === 'OverconstrainedError' || err.name === 'ConstraintNotSatisfiedError') {
        setError('El micrófono no cumple con los requisitos')
        setPermissionStatus('denied')
        onPermissionDenied?.()
      } else if (err.name === 'NotSupportedError') {
        setError('El navegador no soporta acceso al micrófono')
        setPermissionStatus('denied')
        onPermissionDenied?.()
      } else if (err.name === 'SecurityError') {
        setError('Error de seguridad al acceder al micrófono')
        setPermissionStatus('denied')
        onPermissionDenied?.()
      } else {
        setError('Error desconocido al acceder al micrófono')
        setPermissionStatus('denied')
        onPermissionDenied?.()
      }
    } finally {
      setIsRequesting(false)
    }
  }, [onPermissionGranted, onPermissionDenied])

  // Check permission on mount only once
  useEffect(() => {
    checkPermission()
  }, []) // Empty dependency array to run only once

  return {
    permissionStatus,
    isRequesting,
    error,
    checkPermission,
    requestPermission
  }
}
