"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  ArrowLeft,
  BarChart3,
  Lightbulb,
  BookOpen
} from 'lucide-react'
import { useRouter } from 'next/navigation'

interface AnalysisData {
  id: string
  conversation_id: string
  status: string
  sales_metrics: {
    opening_qualification: {
      open_questions_rate: number
      listen_speak_ratio: number
      pain_point_identified: boolean
    }
    presentation_objections: {
      value_points_connected: number
      objections_handled: number
      evidence_used: number
    }
    closing_next_steps: {
      close_attempted: boolean
      close_successful: boolean
      next_steps_defined: boolean
    }
    overall_score: number
  }
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  skill_level: string
  phase_analysis: Record<string, any>
  sentiment_analysis: {
    overall_sentiment: string
    confidence_level: number
    key_emotions: string[]
  }
  key_insights: string[]
  content_recommendations: string[]
  created_at: string
  completed_at: string
}

interface AnalysisViewerProps {
  analysisId: string
}

export function AnalysisViewer({ analysisId }: AnalysisViewerProps) {
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    fetchAnalysis()
  }, [analysisId])

  const fetchAnalysis = async () => {
    try {
      const response = await fetch(`/api/v1/analyses/${analysisId}`)
      const data = await response.json()
      setAnalysis(data)
    } catch (error) {
      console.error('Error fetching analysis:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSkillLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      'beginner': 'bg-red-500/20 text-red-600',
      'intermediate': 'bg-yellow-500/20 text-yellow-600',
      'advanced': 'bg-blue-500/20 text-blue-600',
      'expert': 'bg-green-500/20 text-green-600'
    }
    return colors[level] || 'bg-gray-500/20 text-gray-600'
  }

  const getSentimentColor = (sentiment: string) => {
    const colors: Record<string, string> = {
      'positive': 'bg-green-500/20 text-green-600',
      'neutral': 'bg-yellow-500/20 text-yellow-600',
      'negative': 'bg-red-500/20 text-red-600'
    }
    return colors[sentiment] || 'bg-gray-500/20 text-gray-600'
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-dots">
            <div></div>
            <div></div>
            <div></div>
          </div>
          <p className="mt-4 text-muted-foreground">Cargando análisis...</p>
        </div>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Análisis no encontrado</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">
              No se pudo cargar el análisis solicitado.
            </p>
            <Button onClick={() => router.push('/')} className="w-full">
              Volver al inicio
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.back()}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Volver
            </Button>
            <div>
              <h1 className="text-2xl font-bold">Análisis de Conversación</h1>
              <p className="text-muted-foreground">
                Completado el {new Date(analysis.completed_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          <Badge className={getSkillLevelColor(analysis.skill_level)}>
            Nivel: {analysis.skill_level}
          </Badge>
        </div>

        {/* Overall Score */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Puntuación General
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="text-4xl font-bold">
                {analysis.sales_metrics.overall_score.toFixed(1)}
              </div>
              <div className="flex-1">
                <Progress 
                  value={analysis.sales_metrics.overall_score} 
                  className="h-3"
                />
                <p className="text-sm text-muted-foreground mt-2">
                  Basado en técnicas de ventas, manejo de objeciones y cierre
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Strengths */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-600">
                <TrendingUp className="h-5 w-5" />
                Fortalezas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {analysis.strengths.map((strength, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{strength}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Weaknesses */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-600">
                <TrendingDown className="h-5 w-5" />
                Áreas de Mejora
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {analysis.weaknesses.map((weakness, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <XCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{weakness}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-blue-600">
                <Lightbulb className="h-5 w-5" />
                Recomendaciones
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {analysis.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Content Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-purple-600">
                <BookOpen className="h-5 w-5" />
                Contenido Recomendado
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {analysis.content_recommendations.map((content, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <Target className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{content}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Key Insights */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Insights Clave</CardTitle>
            <CardDescription>
              Observaciones importantes sobre tu performance en esta conversación
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysis.key_insights.map((insight, index) => (
                <div key={index} className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm">{insight}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Sentiment Analysis */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Análisis de Sentimiento</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Badge className={getSentimentColor(analysis.sentiment_analysis.overall_sentiment)}>
                {analysis.sentiment_analysis.overall_sentiment}
              </Badge>
              <div className="flex-1">
                <Progress 
                  value={analysis.sentiment_analysis.confidence_level * 100} 
                  className="h-2"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Confianza: {(analysis.sentiment_analysis.confidence_level * 100).toFixed(1)}%
                </p>
              </div>
            </div>
            {analysis.sentiment_analysis.key_emotions.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium mb-2">Emociones detectadas:</p>
                <div className="flex flex-wrap gap-2">
                  {analysis.sentiment_analysis.key_emotions.map((emotion, index) => (
                    <Badge key={index} variant="outline">
                      {emotion}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
