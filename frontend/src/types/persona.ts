export interface Persona {
  id: string
  name: string
  description: string
  background: string
  personality_traits: string[]
  accent: string
  conversation_goals: string[]
  pain_points: string[]
  objections: string[]
  decision_factors: string[]
  budget_range?: string
  timeline?: string
  company_size?: string
  industry?: string
  metadata: Record<string, any>
}

export interface PersonaResponse {
  id: string
  name: string
  description: string
  background: string
  personality_traits: string[]
  accent: string
  conversation_goals: string[]
  pain_points: string[]
  objections: string[]
  decision_factors: string[]
  budget_range?: string
  timeline?: string
  company_size?: string
  industry?: string
  metadata: Record<string, any>
}
