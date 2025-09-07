import { ConversationInterface } from '@/components/conversation/conversation-interface'
import { notFound } from 'next/navigation'

interface ConversationPageProps {
  params: Promise<{ id: string }>
}

// Mock data - in real app, this would come from API
const mockPersonas = {
  'carlos_mendoza': {
    name: 'Carlos Mendoza',
    accent: 'Mexicano (CDMX)',
    description: 'CEO de una startup tecnológica'
  },
  'maria_rodriguez': {
    name: 'María Rodríguez', 
    accent: 'Peruano (Lima)',
    description: 'Directora de Marketing'
  },
  'ana_garcia': {
    name: 'Ana García',
    accent: 'Venezolano (Caracas)', 
    description: 'Gerente de Ventas'
  }
}

export default async function ConversationPage({ params }: ConversationPageProps) {
  const { id } = await params
  
  // In a real app, you would fetch the conversation and persona data from the API
  const conversationId = id
  const personaId = 'carlos_mendoza' // This should come from the conversation data
  const persona = mockPersonas[personaId as keyof typeof mockPersonas]
  
  if (!persona) {
    notFound()
  }

  return (
    <div className="min-h-screen">
      <ConversationInterface
        conversationId={conversationId}
        personaId={personaId}
        personaName={persona.name}
        personaAccent={persona.accent}
      />
    </div>
  )
}