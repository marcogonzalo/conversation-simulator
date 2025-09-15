import React from 'react'
import { render, screen } from '@testing-library/react'
import { ConversationInterface } from '../conversation-interface'

// Mock the hooks directly with their return values
jest.mock('../../../hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    isConnected: true,
    sendMessage: jest.fn(),
    connect: jest.fn(),
    disconnect: jest.fn(),
    isLoading: false,
    realConversationId: null,
  }),
}))

jest.mock('../../../hooks/useAudioRecording', () => ({
  useAudioRecording: () => ({
    isRecording: false,
    startRecording: jest.fn(),
    stopRecording: jest.fn(),
    isSpeaking: false,
    cleanup: jest.fn(),
  }),
}))

jest.mock('../../../hooks/useConversation', () => ({
  useConversation: () => ({
    messages: [], // This was missing!
    isWaitingForResponse: false,
    setIsWaitingForResponse: jest.fn(),
    addMessage: jest.fn(),
    updateLastMessage: jest.fn(),
    clearMessages: jest.fn(),
  }),
}))

// Mock the audio service
jest.mock('../../../services/audioService', () => ({
  createAudioElement: jest.fn(() => ({
    play: jest.fn(() => Promise.resolve()),
    pause: jest.fn(),
    load: jest.fn(),
  })),
}))

describe('ConversationInterface', () => {
  const mockPersona = {
    id: 'test-persona-id',
    name: 'Test Persona',
    description: 'A test persona',
    accent: 'neutral',
    voice: 'alloy',
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders conversation interface correctly', () => {
    render(<ConversationInterface persona={mockPersona} />)
    
    // Check if the component renders without crashing
    expect(screen.getByTestId('conversation-interface')).toBeInTheDocument()
  })

  it('displays persona name in header', () => {
    render(<ConversationInterface persona={mockPersona} />)
    
    expect(screen.getByText('Test Persona')).toBeInTheDocument()
  })

  it('shows connection status badge', () => {
    render(<ConversationInterface persona={mockPersona} />)
    
    expect(screen.getByText('Online')).toBeInTheDocument()
  })

  it('displays conversation messages placeholder', () => {
    render(<ConversationInterface persona={mockPersona} />)
    
    expect(screen.getByText('La transcripción aparecerá aquí.')).toBeInTheDocument()
  })

  it('renders with individual props instead of persona object', () => {
    render(
      <ConversationInterface 
        personaId="test-id"
        personaName="Individual Persona"
        personaAccent="spanish"
      />
    )
    
    expect(screen.getByTestId('conversation-interface')).toBeInTheDocument()
    expect(screen.getByText('Individual Persona')).toBeInTheDocument()
  })

  it('displays conversation history section', () => {
    render(<ConversationInterface persona={mockPersona} />)
    
    expect(screen.getByText('Historial de la Conversación')).toBeInTheDocument()
  })
})