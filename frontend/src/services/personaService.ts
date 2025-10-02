/**
 * Persona Service
 * Service for managing persona data and API calls
 */

import { apiConfig } from '@/config/api'
import { Persona, PersonaResponse } from '@/types/persona'

export interface PersonaFilters {
  accent_filter?: string
  trait_filter?: string[]
}

export interface PersonasResponse {
  personas: PersonaResponse[]
  total_count: number
  success: boolean
  message?: string
}

export interface PersonaByIdResponse {
  persona: PersonaResponse
  success: boolean
  message?: string
}

class PersonaService {
  private baseUrl = apiConfig.personas

  /**
   * Get all available personas with optional filters
   */
  async getPersonas(filters?: PersonaFilters): Promise<PersonasResponse> {
    try {
      const params = new URLSearchParams()
      
      if (filters?.accent_filter) {
        params.append('accent_filter', filters.accent_filter)
      }
      
      if (filters?.trait_filter && filters.trait_filter.length > 0) {
        filters.trait_filter.forEach(trait => {
          params.append('trait_filter', trait)
        })
      }

      const queryString = params.toString()
      const url = queryString ? `${this.baseUrl}?${queryString}` : this.baseUrl

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error fetching personas:', error)
      throw new Error('Failed to fetch personas')
    }
  }

  /**
   * Get a specific persona by ID
   */
  async getPersonaById(personaId: string): Promise<PersonaByIdResponse> {
    try {
      const response = await fetch(`${this.baseUrl}${personaId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Persona not found')
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error fetching persona:', error)
      throw new Error('Failed to fetch persona')
    }
  }

  /**
   * Get personas by accent
   */
  async getPersonasByAccent(accent: string): Promise<PersonasResponse> {
    try {
      const response = await fetch(`${this.baseUrl}accent/${accent}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Error fetching personas by accent:', error)
      throw new Error('Failed to fetch personas by accent')
    }
  }

  /**
   * Convert PersonaResponse to Persona
   */
  convertToPersona(personaResponse: PersonaResponse): Persona {
    return {
      id: personaResponse.id,
      name: personaResponse.name,
      description: personaResponse.description,
      background: personaResponse.background,
      personality_traits: personaResponse.personality_traits,
      accent: personaResponse.accent,
      conversation_goals: personaResponse.conversation_goals,
      pain_points: personaResponse.pain_points,
      objections: personaResponse.objections,
      decision_factors: personaResponse.decision_factors,
      budget_range: personaResponse.budget_range,
      timeline: personaResponse.timeline,
      company_size: personaResponse.company_size,
      industry: personaResponse.industry,
      metadata: personaResponse.metadata,
    }
  }
}

export const personaService = new PersonaService()
export default personaService
