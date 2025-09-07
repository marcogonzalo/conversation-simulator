import { create } from 'zustand'
import { Persona } from '@/types/persona'

interface PersonaState {
  selectedPersona: Persona | null
  selectPersona: (persona: Persona) => void
  clearPersona: () => void
}

export const usePersonaStore = create<PersonaState>((set) => ({
  selectedPersona: null,
  selectPersona: (persona) => set({ selectedPersona: persona }),
  clearPersona: () => set({ selectedPersona: null }),
}))
