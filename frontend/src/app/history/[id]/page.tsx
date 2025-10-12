'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ArrowLeft, Clock, User, MessageCircle, TrendingUp, AlertCircle, CheckCircle2, XCircle } from 'lucide-react';
import { humanizePersona, humanizeContext } from '@/utils/humanize';

interface Message {
  id: string;
  role: string;
  content: string;
  timestamp: string;
}

interface Analysis {
  analysis_id: string;
  overall_score?: number;
  summary?: string;
  strengths?: string[];
  areas_for_improvement?: string[];
  recommendations?: string[];
  metrics?: {
    opening_qualification?: number;
    needs_assessment?: number;
    value_presentation?: number;
    objection_handling?: number;
    closing_effectiveness?: number;
    communication_rapport?: number;
  };
  // Legacy format
  analysis?: string; // Markdown text
  metadata?: {
    duration_seconds?: number;
    message_count?: number;
    persona_name?: string;
    context_id?: string;
    conversation_metadata?: any;
  };
}

interface ConversationDetail {
  conversation: {
    id: string;
    persona_id: string;
    context_id: string;
    status: string;
    created_at: string;
    completed_at: string | null;
    duration_seconds: number | null;
  };
  transcription: {
    messages: Message[];
  } | null;
  analysis: Analysis | null;
}

export default function ConversationDetailPage() {
  const [data, setData] = useState<ConversationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const params = useParams();
  const conversationId = params.id as string;

  useEffect(() => {
    if (conversationId) {
      fetchConversationDetail();
    }
  }, [conversationId]);

  const fetchConversationDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/conversations/${conversationId}/full-detail`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch conversation detail');
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(date);
  };

  const getPersonaName = (personaId: string) => {
    return humanizePersona(personaId);
  };

  const getContextName = (contextId: string) => {
    return humanizeContext(contextId);
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 8) return 'bg-green-100';
    if (score >= 6) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando conversación...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center max-w-md">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-6">{error || 'Conversación no encontrada'}</p>
          <button
            onClick={() => router.push('/history')}
            className="bg-purple-600 text-white py-2 px-6 rounded-lg hover:bg-purple-700 transition-colors"
          >
            Volver al Historial
          </button>
        </div>
      </div>
    );
  }

  const { conversation, transcription, analysis } = data;

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-6 px-4 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <button
            onClick={() => router.push('/history')}
            className="flex items-center gap-2 text-white/90 hover:text-white mb-4 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Volver al Historial</span>
          </button>
          
          <h1 className="text-3xl font-bold mb-2">
            {getContextName(conversation.context_id)}
          </h1>
          
          <div className="flex items-center gap-6 text-white/90 text-sm">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4" />
              <span>{getPersonaName(conversation.persona_id)}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>{formatDate(conversation.created_at)}</span>
            </div>
            {conversation.duration_seconds && (
              <div className="flex items-center gap-2">
                <span className="font-medium">Duración:</span>
                <span>{Math.floor(conversation.duration_seconds / 60)}m {conversation.duration_seconds % 60}s</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Transcription */}
          <div className="lg:col-span-1">
            <div className="bg-gray-50 rounded-lg shadow-md p-6 sticky top-6">
              <div className="flex items-center gap-2 mb-4">
                <MessageCircle className="w-5 h-5 text-purple-600" />
                <h2 className="text-xl font-bold text-gray-900">Transcripción</h2>
              </div>
              
              {transcription && transcription.messages && transcription.messages.length > 0 ? (
                <div className="space-y-4 max-h-[calc(100vh-250px)] overflow-y-auto pr-2">
                  {transcription.messages.map((message) => (
                    <div
                      key={message.id}
                      className={`p-3 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-blue-100 border-l-4 border-blue-500'
                          : 'bg-purple-100 border-l-4 border-purple-500'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold text-gray-700">
                          {message.role === 'user' ? 'Vendedor' : getPersonaName(conversation.persona_id)}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatTime(message.timestamp)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-800">{message.content}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <MessageCircle className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                  <p>No hay transcripción disponible</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Analysis */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-8">
              {analysis ? (
                <div className="space-y-8">
                  {/* Header */}
                  <div className="text-center pb-6 border-b border-gray-200">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <TrendingUp className="w-6 h-6 text-purple-600" />
                      <h2 className="text-2xl font-bold text-gray-900">Análisis de la Conversación</h2>
                    </div>
                  </div>
                  
                  {/* Check if we have structured data or markdown */}
                  {analysis.overall_score !== undefined ? (
                    <>
                      {/* Structured Format - Overall Score */}
                      <div className="text-center pb-6 border-b border-gray-200">
                        <div className={`inline-block px-8 py-4 rounded-lg ${getScoreBgColor(analysis.overall_score)} mt-4`}>
                          <div className="text-sm font-medium text-gray-700 mb-1">Puntuación General</div>
                          <div className={`text-5xl font-bold ${getScoreColor(analysis.overall_score)}`}>
                            {analysis.overall_score.toFixed(1)}/10
                          </div>
                        </div>
                      </div>
                    </>
                  ) : analysis.analysis ? (
                    <>
                      {/* Legacy Markdown Format */}
                      <div className="prose prose-lg max-w-none">
                        <div 
                          className="text-gray-700 leading-relaxed"
                          dangerouslySetInnerHTML={{ 
                            __html: analysis.analysis
                              .replace(/\n/g, '<br />')
                              .replace(/#{3} /g, '<h3 class="text-lg font-semibold text-gray-900 mt-6 mb-3">')
                              .replace(/#{2} /g, '<h2 class="text-xl font-bold text-gray-900 mt-8 mb-4">')
                              .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
                              .replace(/- (.*?)(<br \/>|$)/g, '<li class="ml-4 mb-2">$1</li>')
                          }}
                        />
                      </div>
                    </>
                  ) : null}

                  {/* Summary */}
                  {analysis.summary && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <AlertCircle className="w-5 h-5 text-blue-600" />
                        Resumen
                      </h3>
                      <p className="text-gray-700 leading-relaxed bg-blue-50 p-4 rounded-lg">
                        {analysis.summary}
                      </p>
                    </div>
                  )}

                  {/* Strengths */}
                  {analysis.strengths && analysis.strengths.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                        Fortalezas
                      </h3>
                      <ul className="space-y-2">
                        {analysis.strengths.map((strength, index) => (
                          <li key={index} className="flex items-start gap-3 bg-green-50 p-3 rounded-lg">
                            <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Areas for Improvement */}
                  {analysis.areas_for_improvement && analysis.areas_for_improvement.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <AlertCircle className="w-5 h-5 text-yellow-600" />
                        Áreas de Mejora
                      </h3>
                      <ul className="space-y-2">
                        {analysis.areas_for_improvement.map((area, index) => (
                          <li key={index} className="flex items-start gap-3 bg-yellow-50 p-3 rounded-lg">
                            <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{area}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommendations */}
                  {analysis.recommendations && analysis.recommendations.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-purple-600" />
                        Recomendaciones
                      </h3>
                      <ul className="space-y-2">
                        {analysis.recommendations.map((recommendation, index) => (
                          <li key={index} className="flex items-start gap-3 bg-purple-50 p-3 rounded-lg">
                            <TrendingUp className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{recommendation}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Metrics */}
                  {analysis.metrics && (
                    <div className="pt-6 border-t border-gray-200">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Evaluación por Categorías</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {analysis.metrics.opening_qualification !== undefined && (
                          <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="text-2xl">🚀</span>
                                <span className="font-medium text-gray-700">Apertura y Calificación</span>
                              </div>
                              <div className={`text-2xl font-bold ${getScoreColor(analysis.metrics.opening_qualification)}`}>
                                {analysis.metrics.opening_qualification}/10
                              </div>
                            </div>
                          </div>
                        )}
                        {analysis.metrics.needs_assessment !== undefined && (
                          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="text-2xl">🔍</span>
                                <span className="font-medium text-gray-700">Evaluación de Necesidades</span>
                              </div>
                              <div className={`text-2xl font-bold ${getScoreColor(analysis.metrics.needs_assessment)}`}>
                                {analysis.metrics.needs_assessment}/10
                              </div>
                            </div>
                          </div>
                        )}
                        {analysis.metrics.value_presentation !== undefined && (
                          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="text-2xl">💎</span>
                                <span className="font-medium text-gray-700">Presentación de Valor</span>
                              </div>
                              <div className={`text-2xl font-bold ${getScoreColor(analysis.metrics.value_presentation)}`}>
                                {analysis.metrics.value_presentation}/10
                              </div>
                            </div>
                          </div>
                        )}
                        {analysis.metrics.objection_handling !== undefined && (
                          <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border border-red-200">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="text-2xl">🛡️</span>
                                <span className="font-medium text-gray-700">Manejo de Objeciones</span>
                              </div>
                              <div className={`text-2xl font-bold ${getScoreColor(analysis.metrics.objection_handling)}`}>
                                {analysis.metrics.objection_handling}/10
                              </div>
                            </div>
                          </div>
                        )}
                        {analysis.metrics.closing_effectiveness !== undefined && (
                          <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="text-2xl">🎯</span>
                                <span className="font-medium text-gray-700">Efectividad de Cierre</span>
                              </div>
                              <div className={`text-2xl font-bold ${getScoreColor(analysis.metrics.closing_effectiveness)}`}>
                                {analysis.metrics.closing_effectiveness}/10
                              </div>
                            </div>
                          </div>
                        )}
                        {analysis.metrics.communication_rapport !== undefined && (
                          <div className="bg-gradient-to-br from-pink-50 to-pink-100 p-4 rounded-lg border border-pink-200">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="text-2xl">💬</span>
                                <span className="font-medium text-gray-700">Comunicación y Rapport</span>
                              </div>
                              <div className={`text-2xl font-bold ${getScoreColor(analysis.metrics.communication_rapport)}`}>
                                {analysis.metrics.communication_rapport}/10
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Metadata - Information */}
                  {analysis.metadata && (
                    <div className="pt-4 border-t border-gray-200">
                      <h3 className="text-sm font-semibold text-gray-500 mb-3">ℹ️ Información General</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {analysis.metadata.duration_seconds !== undefined && (
                          <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
                            <div className="text-lg font-bold text-gray-700">
                              {Math.floor(analysis.metadata.duration_seconds / 60)}:{String(analysis.metadata.duration_seconds % 60).padStart(2, '0')}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">⏱️ Duración</div>
                          </div>
                        )}
                        {analysis.metadata.message_count !== undefined && (
                          <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
                            <div className="text-lg font-bold text-gray-700">{analysis.metadata.message_count}</div>
                            <div className="text-xs text-gray-500 mt-1">💬 Mensajes</div>
                          </div>
                        )}
                        {analysis.metadata.persona_name && (
                          <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
                            <div className="text-sm font-bold text-gray-700 truncate">{analysis.metadata.persona_name}</div>
                            <div className="text-xs text-gray-500 mt-1">👤 Persona</div>
                          </div>
                        )}
                        {analysis.metadata.context_id && (
                          <div className="bg-gray-50 p-3 rounded-lg text-center border border-gray-200">
                            <div className="text-sm font-bold text-gray-700 truncate">{analysis.metadata.context_id}</div>
                            <div className="text-xs text-gray-500 mt-1">🎭 Contexto</div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <AlertCircle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-xl font-semibold mb-2">No hay análisis disponible</h3>
                  <p>El análisis aún no se ha generado para esta conversación</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

