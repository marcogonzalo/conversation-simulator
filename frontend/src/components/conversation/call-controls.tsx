"use client"

import { Mic, MicOff, Phone, PhoneOff, Volume2, VolumeX } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface CallControlsProps {
  isRecording: boolean
  isPlaying: boolean
  isConnected: boolean
  onStartRecording: () => void
  onStopRecording: () => void
  onStartCall: () => void
  onEndCall: () => void
  onPlayAudio: () => void
  onStopAudio: () => void
}

export function CallControls({
  isRecording,
  isPlaying,
  isConnected,
  onStartRecording,
  onStopRecording,
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

      {/* Recording Controls */}
      {isConnected && (
        <>
          <Button
            onClick={isRecording ? onStopRecording : onStartRecording}
            className={`w-16 h-16 rounded-full shadow-2xl transition-all duration-300 transform hover:scale-105 ${
              isRecording 
                ? 'bg-red-500 hover:bg-red-600 shadow-red-500/25' 
                : 'bg-blue-500 hover:bg-blue-600 shadow-blue-500/25'
            }`}
          >
            {isRecording ? (
              <MicOff className="h-8 w-8 text-white" />
            ) : (
              <Mic className="h-8 w-8 text-white" />
            )}
          </Button>

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
