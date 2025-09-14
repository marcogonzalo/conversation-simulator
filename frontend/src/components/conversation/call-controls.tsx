"use client"

import { Phone, PhoneOff, VolumeX } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface CallControlsProps {
  isPlaying: boolean
  isConnected: boolean
  isRecording: boolean
  isSpeaking: boolean
  isWaitingForResponse: boolean
  onStartCall: () => void
  onEndCall: () => void
  onPlayAudio: () => void
  onStopAudio: () => void
}

export function CallControls({
  isPlaying,
  isConnected,
  isRecording,
  isSpeaking,
  isWaitingForResponse,
  onStartCall,
  onEndCall,
  onPlayAudio,
  onStopAudio
}: CallControlsProps) {
  return (
    <div className="flex items-center justify-center gap-6">
      {/* Start Call Button */}
      {!isConnected && (
        <Button
          onClick={onStartCall}
          className="w-16 h-16 rounded-full bg-green-500 hover:bg-green-600 text-white shadow-2xl hover:shadow-green-500/25 transition-all duration-300 transform hover:scale-105"
        >
          <Phone className="h-8 w-8" />
        </Button>
      )}

      {/* Connected Controls */}
      {isConnected && (
        <>
          {/* Recording Status */}
          {isRecording && (
            <div className="flex items-center gap-2 text-white/80">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm">Grabando...</span>
            </div>
          )}

          {/* Speaking Status */}
          {isSpeaking && (
            <div className="flex items-center gap-2 text-white/80">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm">Hablando...</span>
            </div>
          )}

          {/* Waiting for Response Status */}
          {isWaitingForResponse && (
            <div className="flex items-center gap-2 text-white/80">
              <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse"></div>
              <span className="text-sm">Esperando respuesta...</span>
            </div>
          )}

          {/* Audio Playback Controls */}
          {isPlaying && (
            <Button
              onClick={onStopAudio}
              className="w-12 h-12 rounded-full bg-purple-500 hover:bg-purple-600 text-white shadow-lg transition-all duration-300 transform hover:scale-105"
            >
              <VolumeX className="h-6 w-6" />
            </Button>
          )}

          {/* End Call Button */}
          <Button
            onClick={onEndCall}
            className="w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 text-white shadow-2xl hover:shadow-red-500/25 transition-all duration-300 transform hover:scale-105"
          >
            <PhoneOff className="h-8 w-8" />
          </Button>
        </>
      )}
    </div>
  )
}
