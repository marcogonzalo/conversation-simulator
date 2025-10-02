import { create } from 'zustand'
import { Persona } from '@/types/persona'
import { personaService, PersonaFilters } from '@/services/personaService'

interface PersonaState {
  // State
  selectedPersona: Persona | null
  availablePersonas: Persona[]
  loading: boolean
  error: string | null
  
  // Actions
  selectPersona: (persona: Persona) => void
  clearPersona: () => void
  loadPersonas: (filters?: PersonaFilters) => Promise<void>
  loadPersonaById: (personaId: string) => Promise<void>
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const usePersonaStore = create<PersonaState>((set, get) => ({
  // Initial state
  selectedPersona: null,
  availablePersonas: [],
  loading: false,
  error: null,
  
  // Actions
  selectPersona: (persona) => set({ selectedPersona: persona }),
  
  clearPersona: () => set({ selectedPersona: null }),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),
  
  loadPersonas: async (filters) => {
    set({ loading: true, error: null })
    
    try {
      const response = await personaService.getPersonas(filters)
      
      if (response.success) {
        const personas = response.personas.map(personaService.convertToPersona)
        set({ availablePersonas: personas, loading: false })
      } else {
        set({ error: response.message || 'Failed to load personas', loading: false })
      }
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to load personas', 
        loading: false 
      })
    }
  },
  
  loadPersonaById: async (personaId) => {
    set({ loading: true, error: null })
    
    try {
      const response = await personaService.getPersonaById(personaId)
      
      if (response.success) {
        const persona = personaService.convertToPersona(response.persona)
        set({ selectedPersona: persona, loading: false })
      } else {
        set({ error: response.message || 'Failed to load persona', loading: false })
      }
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to load persona', 
        loading: false 
      })
    }
  },
}))
