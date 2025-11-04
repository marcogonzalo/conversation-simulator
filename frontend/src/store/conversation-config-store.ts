import { create } from 'zustand'
import { apiConfig } from '@/config/api'

interface ConfigOption {
  id: string
  name: string
}

interface ConversationConfigState {
  // Available options
  industries: ConfigOption[]
  situations: ConfigOption[]
  psychologies: ConfigOption[]
  identities: ConfigOption[]
  
  // Selected options
  selectedIndustry: string | null
  selectedSituation: string | null
  selectedPsychology: string | null
  selectedIdentity: string | null
  
  // UI state
  loading: boolean
  error: string | null
  
  // Actions
  setIndustry: (id: string) => void
  setSituation: (id: string) => void
  setPsychology: (id: string) => void
  setIdentity: (id: string) => void
  loadOptions: () => Promise<void>
  isConfigComplete: () => boolean
}

export const useConversationConfigStore = create<ConversationConfigState>((set, get) => ({
  // Initial state
  industries: [],
  situations: [],
  psychologies: [],
  identities: [],
  
  selectedIndustry: 'real_estate',  // Default
  selectedSituation: 'discovery_no_urgency_price',  // Default
  selectedPsychology: 'conservative_analytical',  // Default
  selectedIdentity: 'ana_garcia',  // Default
  
  loading: false,
  error: null,
  
  // Actions
  setIndustry: (id) => set({ selectedIndustry: id }),
  setSituation: (id) => set({ selectedSituation: id }),
  setPsychology: (id) => set({ selectedPsychology: id }),
  setIdentity: (id) => set({ selectedIdentity: id }),
  
  loadOptions: async () => {
    set({ loading: true, error: null })
    
    try {
      // Load options from backend API
      const response = await fetch(`${apiConfig.prompts}options`)
      
      if (!response.ok) {
        throw new Error(`Failed to load options: ${response.statusText}`)
      }
      
      const options = await response.json()
      
      set({ 
        industries: options.industries || [],
        situations: options.situations || [],
        psychologies: options.psychologies || [],
        identities: options.identities || [],
        loading: false 
      })
    } catch (error) {
      console.error('Error loading conversation config options:', error)
      
      // Fallback to hardcoded options if API fails
      const industries = [
        { id: 'real_estate', name: 'Bienes Raíces' },
        { id: 'health_insurance', name: 'Seguros Médicos' }
      ]
      
      const situations = [
        { id: 'discovery_no_urgency_price', name: 'Descubrimiento - Sin Urgencia - Precio' },
        { id: 'closing_high_urgency_fit', name: 'Cierre - Alta Urgencia - Ajuste' },
        { id: 'presentation_medium_urgency_value', name: 'Presentación - Media Urgencia - Valor' },
        { id: 'objection_handling_high_urgency_trust', name: 'Manejo Objeciones - Alta Urgencia - Confianza' }
      ]
      
      const psychologies = [
        { id: 'conservative_analytical', name: 'Conservador Analítico' },
        { id: 'impulsive_enthusiastic', name: 'Impulsivo Entusiasta' },
        { id: 'skeptical_pragmatic', name: 'Escéptico Pragmático' }
      ]
      
      const identities = [
        { id: 'ana_garcia', name: 'Ana García (Cubana, 45 años)' },
        { id: 'carlos_mendoza', name: 'Carlos Mendoza (Venezolano, 32 años)' },
        { id: 'maria_rodriguez', name: 'María Rodríguez (Peruana, 40 años)' }
      ]
      
      set({ 
        industries,
        situations,
        psychologies,
        identities,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load options (using fallback)'
      })
    }
  },
  
  isConfigComplete: () => {
    const state = get()
    return !!(
      state.selectedIndustry &&
      state.selectedSituation &&
      state.selectedPsychology &&
      state.selectedIdentity
    )
  }
}))

