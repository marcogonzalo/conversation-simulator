'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Clock, User, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { humanizePersona, humanizeContext, humanize } from '@/utils/humanize';

interface Conversation {
  id: string;
  persona_id: string;
  context_id: string;
  status: string;
  created_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  metadata?: {
    industry_id?: string;
    situation_id?: string;
    psychology_id?: string;
    [key: string]: any;
  };
  transcription_id: string | null;
  analysis_id: string | null;
}

export default function HistoryPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/conversations/history');
      
      if (!response.ok) {
        throw new Error('Failed to fetch conversations');
      }
      
      const data = await response.json();
      setConversations(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'active':
        return <AlertCircle className="w-5 h-5 text-blue-500" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completada';
      case 'active':
        return 'Activa';
      case 'cancelled':
        return 'Cancelada';
      default:
        return 'Creada';
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

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  };

  const getPersonaName = (personaId: string) => {
    return humanizePersona(personaId);
  };

  const getContextName = (contextId: string) => {
    return humanizeContext(contextId);
  };

  const getConversationTitle = (conversation: Conversation) => {
    // If metadata has 5-layer configuration, generate descriptive title
    if (conversation.metadata?.industry_id && conversation.metadata?.situation_id) {
      const industry = humanize(conversation.metadata.industry_id);
      const situation = humanize(conversation.metadata.situation_id);
      
      // Format: "Industry - Situation Phase"
      // Example: "Real Estate - Discovery"
      const situationParts = situation.split(' ');
      const phase = situationParts[0] || 'Conversation'; // First word (Discovery, Closing, Objection, Presentation)
      
      return `${industry} - ${phase}`;
    }
    
    // Fallback for old conversations: try to use persona_id as hint
    if (conversation.context_id === 'default') {
      const personaName = humanizePersona(conversation.persona_id);
      return `Conversación con ${personaName}`;
    }
    
    // Final fallback to context_id
    return humanizeContext(conversation.context_id);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando conversaciones...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md">
          <div className="text-red-500 text-center mb-4">
            <XCircle className="w-16 h-16 mx-auto mb-2" />
            <h2 className="text-xl font-bold">Error</h2>
          </div>
          <p className="text-gray-600 text-center mb-4">{error}</p>
          <button
            onClick={fetchConversations}
            className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-4xl font-bold text-gray-900">
              Historial de Conversaciones
            </h1>
            <button
              onClick={() => router.push('/')}
              className="bg-white text-purple-600 py-2 px-6 rounded-lg shadow-md hover:shadow-lg transition-all font-medium border-2 border-purple-600"
            >
              Volver al Inicio
            </button>
          </div>
          <p className="text-gray-600">
            Revisa todas tus conversaciones y sus análisis
          </p>
        </div>

        {/* Conversations List */}
        {conversations.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Clock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-700 mb-2">
              No hay conversaciones aún
            </h2>
            <p className="text-gray-500 mb-6">
              Inicia tu primera conversación para verla aquí
            </p>
            <button
              onClick={() => router.push('/')}
              className="bg-purple-600 text-white py-3 px-8 rounded-lg hover:bg-purple-700 transition-colors font-medium"
            >
              Iniciar Conversación
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => router.push(`/history/${conversation.id}`)}
                className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all p-6 cursor-pointer border-2 border-transparent hover:border-purple-300"
              >
                <div className="flex items-start justify-between">
                  {/* Left Side - Main Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      {getStatusIcon(conversation.status)}
                      <h3 className="text-xl font-semibold text-gray-900">
                        {getConversationTitle(conversation)}
                      </h3>
                      <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                        {getStatusText(conversation.status)}
                      </span>
                    </div>

                    <div className="flex items-center gap-6 text-sm text-gray-600">
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
                          <span>{formatDuration(conversation.duration_seconds)}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right Side - Status Badges */}
                  <div className="flex gap-2">
                    {conversation.transcription_id && (
                      <div className="bg-blue-100 text-blue-700 text-xs px-3 py-1 rounded-full font-medium">
                        Transcripción
                      </div>
                    )}
                    {conversation.analysis_id && (
                      <div className="bg-green-100 text-green-700 text-xs px-3 py-1 rounded-full font-medium">
                        Análisis
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

