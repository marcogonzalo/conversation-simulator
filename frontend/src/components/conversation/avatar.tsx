"use client"

import { User } from 'lucide-react'

interface AvatarProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  isActive?: boolean
  isSpeaking?: boolean
  className?: string
}

export function Avatar({ 
  size = 'lg', 
  isActive = false, 
  isSpeaking = false,
  className = '' 
}: AvatarProps) {
  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24', 
    lg: 'w-32 h-32',
    xl: 'w-40 h-40'
  }

  const iconSizes = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16', 
    xl: 'h-20 w-20'
  }

  return (
    <div className={`relative ${sizeClasses[size]} ${className}`}>
      {/* Avatar Circle */}
      <div className={`
        w-full h-full rounded-full flex items-center justify-center
        bg-gradient-to-br from-slate-600 to-slate-800
        border-4 border-white/20
        shadow-2xl
        transition-all duration-300
        ${isActive ? 'ring-4 ring-blue-500/50' : ''}
        ${isSpeaking ? 'animate-pulse' : ''}
      `}>
        <User className={`${iconSizes[size]} text-white/80`} />
      </div>
      
      
      {/* Speaking Waves Animation */}
      {isSpeaking && (
        <>
          <div className="absolute inset-0 rounded-full border-2 border-green-400/40 animate-ping"></div>
          <div className="absolute inset-0 rounded-full border-2 border-green-400/30 animate-ping" style={{ animationDelay: '0.5s' }}></div>
          <div className="absolute inset-0 rounded-full border-2 border-green-400/20 animate-ping" style={{ animationDelay: '1s' }}></div>
        </>
      )}
      
      {/* Active Ring Animation */}
      {isActive && !isSpeaking && (
        <div className="absolute inset-0 rounded-full border-4 border-blue-500/30 animate-ping"></div>
      )}
    </div>
  )
}
