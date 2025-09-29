"use client"

import { useState, useEffect } from 'react'
import { browserCompatibility } from '@/utils/browserCompatibility'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { RefreshCw, Info } from 'lucide-react'

interface BrowserInfoProps {
  showDetails?: boolean
}

export function BrowserInfo({ showDetails = false }: BrowserInfoProps) {
  const [capabilities, setCapabilities] = useState(browserCompatibility.detectCapabilities())
  const [isExpanded, setIsExpanded] = useState(showDetails)

  const refreshCapabilities = () => {
    setCapabilities(browserCompatibility.detectCapabilities())
  }

  const getBrowserIcon = (browserName: string) => {
    switch (browserName) {
      case 'Chrome':
        return '🟢'
      case 'Firefox':
        return '🟠'
      case 'Safari':
        return '🔵'
      case 'Edge':
        return '🔷'
      default:
        return '❓'
    }
  }

  const getCompatibilityStatus = () => {
    const issues = []
    if (!capabilities.hasMediaRecorder) issues.push('MediaRecorder')
    if (!capabilities.hasWebAudioAPI) issues.push('Web Audio API')
    if (!capabilities.hasWebSocket) issues.push('WebSocket')
    
    return {
      isCompatible: issues.length === 0,
      issues
    }
  }

  const status = getCompatibilityStatus()

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Info className="h-5 w-5" />
            <CardTitle className="text-lg">Browser Compatibility</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge 
              variant={status.isCompatible ? "default" : "destructive"}
              className="text-xs"
            >
              {status.isCompatible ? "✅ Compatible" : "❌ Issues Found"}
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={refreshCapabilities}
              className="h-8 w-8 p-0"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <CardDescription>
          Current browser capabilities and optimizations
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Browser Info */}
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getBrowserIcon(capabilities.browserName)}</span>
          <div>
            <div className="font-medium">{capabilities.browserName} {capabilities.browserVersion}</div>
            <div className="text-sm text-muted-foreground">
              Preferred format: {capabilities.preferredAudioFormat}
            </div>
          </div>
        </div>

        {/* Compatibility Issues */}
        {!status.isCompatible && (
          <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
            <div className="text-sm font-medium text-destructive mb-1">
              Compatibility Issues:
            </div>
            <ul className="text-sm text-destructive/80 space-y-1">
              {status.issues.map((issue) => (
                <li key={issue}>• {issue} not supported</li>
              ))}
            </ul>
          </div>
        )}

        {/* API Support */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center gap-2">
            <span className={capabilities.hasMediaRecorder ? "text-green-600" : "text-red-600"}>
              {capabilities.hasMediaRecorder ? "✅" : "❌"}
            </span>
            MediaRecorder
          </div>
          <div className="flex items-center gap-2">
            <span className={capabilities.hasWebAudioAPI ? "text-green-600" : "text-red-600"}>
              {capabilities.hasWebAudioAPI ? "✅" : "❌"}
            </span>
            Web Audio API
          </div>
          <div className="flex items-center gap-2">
            <span className={capabilities.hasWebSocket ? "text-green-600" : "text-red-600"}>
              {capabilities.hasWebSocket ? "✅" : "❌"}
            </span>
            WebSocket
          </div>
          <div className="flex items-center gap-2">
            <span className="text-blue-600">🎵</span>
            Audio Formats: {capabilities.supportedAudioFormats.length}
          </div>
        </div>

        {/* Expandable Details */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full"
        >
          {isExpanded ? "Hide Details" : "Show Details"}
        </Button>

        {isExpanded && (
          <div className="space-y-3 pt-2 border-t">
            <div>
              <div className="text-sm font-medium mb-2">Supported Audio Formats:</div>
              <div className="flex flex-wrap gap-1">
                {capabilities.supportedAudioFormats.map((format) => (
                  <Badge key={format} variant="secondary" className="text-xs">
                    {format}
                  </Badge>
                ))}
              </div>
            </div>

            <div>
              <div className="text-sm font-medium mb-2">Performance Recommendations:</div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>VAD Threshold: {browserCompatibility.getPerformanceRecommendations().vadThreshold}</div>
                <div>Silence Duration: {browserCompatibility.getPerformanceRecommendations().silenceDuration}ms</div>
                <div>Chunk Size: {browserCompatibility.getPerformanceRecommendations().audioChunkSize}</div>
                <div>Preload: {browserCompatibility.getPerformanceRecommendations().preloadStrategy}</div>
              </div>
            </div>

            <div>
              <div className="text-sm font-medium mb-2">User Agent:</div>
              <div className="text-xs text-muted-foreground font-mono bg-muted p-2 rounded">
                {typeof window !== 'undefined' ? navigator.userAgent : 'Server-side rendering'}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
