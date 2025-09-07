"use client"

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Mic, MicOff, Square } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AudioRecorderProps {
  isRecording: boolean
  onStart: () => void
  onStop: (audioData: string) => void
  onError: (error: string) => void
}

export function AudioRecorder({ isRecording, onStart, onStop, onError }: AudioRecorderProps) {
  const [isSupported, setIsSupported] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    // Check if MediaRecorder is supported
    if (typeof window !== 'undefined' && navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function') {
      setIsSupported(true)
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        const reader = new FileReader()
        reader.onload = () => {
          const base64 = reader.result as string
          const audioData = base64.split(',')[1] // Remove data:audio/webm;base64, prefix
          onStop(audioData)
        }
        reader.readAsDataURL(audioBlob)
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      onStart()
      
      // Start timer
      setRecordingTime(0)
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
      
    } catch (error) {
      console.error('Error starting recording:', error)
      onError('No se pudo acceder al micrófono')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
    }
    
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    
    setRecordingTime(0)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (!isSupported) {
    return (
      <div className="text-center text-muted-foreground">
        <p>Grabación de audio no soportada en este navegador</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <Button
          size="lg"
          variant={isRecording ? "destructive" : "default"}
          onClick={isRecording ? stopRecording : startRecording}
          className={cn(
            "w-16 h-16 rounded-full",
            isRecording && "animate-pulse"
          )}
        >
          {isRecording ? (
            <Square className="h-6 w-6" />
          ) : (
            <Mic className="h-6 w-6" />
          )}
        </Button>
        
        {isRecording && (
          <div className="absolute inset-0 rounded-full border-2 border-red-500 animate-ping" />
        )}
      </div>
      
      {isRecording && (
        <div className="text-center">
          <p className="text-sm text-muted-foreground">Grabando...</p>
          <p className="text-lg font-mono">{formatTime(recordingTime)}</p>
        </div>
      )}
      
      {!isRecording && (
        <p className="text-sm text-muted-foreground text-center">
          Presiona para grabar tu mensaje
        </p>
      )}
    </div>
  )
}
