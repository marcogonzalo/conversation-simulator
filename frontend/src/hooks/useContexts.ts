import { useState, useEffect } from 'react'

export interface ConversationContext {
  id: string
  name: string
  topic: string
}

export function useContexts() {
  const [contexts, setContexts] = useState<ConversationContext[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchContexts = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const response = await fetch('/api/contexts')
        
        if (!response.ok) {
          throw new Error('Failed to fetch contexts')
        }
        
        const data = await response.json()
        setContexts(data)
      } catch (err) {
        console.error('Error fetching contexts:', err)
        setError(err instanceof Error ? err.message : 'Unknown error')
        // Fallback to default contexts if API fails
        setContexts([
          { id: 'default', name: 'Default', topic: 'General' },
          { id: 'compra_vivienda', name: 'Compra de Vivienda', topic: 'Inmobiliaria' },
          { id: 'evaluacion_crm', name: 'Evaluación CRM', topic: 'Tecnología' },
          { id: 'negociacion_erp', name: 'Negociación ERP', topic: 'Tecnología' },
          { id: 'presentacion_marketing', name: 'Presentación Marketing', topic: 'Marketing' }
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchContexts()
  }, [])

  return { contexts, loading, error }
}
