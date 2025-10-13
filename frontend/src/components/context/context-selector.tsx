'use client'

import { useState } from 'react'
import { ChevronDown, Target, Info } from 'lucide-react'
import { useContexts, ConversationContext } from '@/hooks/useContexts'
import { humanizeContext } from '@/utils/humanize'

interface ContextSelectorProps {
  selectedContextId: string
  onContextChange: (contextId: string) => void
  disabled?: boolean
}

export function ContextSelector({ 
  selectedContextId, 
  onContextChange, 
  disabled = false 
}: ContextSelectorProps) {
  const { contexts, loading, error } = useContexts()
  const [isOpen, setIsOpen] = useState(false)

  const selectedContext = contexts.find(ctx => ctx.id === selectedContextId)

  const handleContextSelect = (contextId: string) => {
    onContextChange(contextId)
    setIsOpen(false)
  }

  if (loading) {
    return (
      <div className="w-full">
        <div className="bg-white border border-gray-200 rounded-lg p-3 animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full">
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-center gap-2 text-red-600">
            <Info className="h-4 w-4" />
            <span className="text-sm">Error cargando contextos</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="relative w-full">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          w-full bg-white border border-gray-200 rounded-lg p-3 text-left
          flex items-center justify-between
          transition-colors duration-200
          ${disabled 
            ? 'bg-gray-50 text-gray-400 cursor-not-allowed' 
            : 'hover:border-blue-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
          }
        `}
      >
        <div className="flex items-center gap-2">
          <Target className="h-4 w-4 text-blue-500" />
          <div>
            <div className="font-medium text-gray-900">
              {selectedContext ? humanizeContext(selectedContext.name) : 'Seleccionar contexto'}
            </div>
            {selectedContext && (
              <div className="text-xs text-gray-500">
                {selectedContext.topic}
              </div>
            )}
          </div>
        </div>
        <ChevronDown 
          className={`h-4 w-4 text-gray-400 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`} 
        />
      </button>

      {isOpen && !disabled && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-20 max-h-60 overflow-y-auto">
            {contexts.map((context) => (
              <button
                key={context.id}
                type="button"
                onClick={() => handleContextSelect(context.id)}
                className={`
                  w-full p-3 text-left hover:bg-blue-50 transition-colors duration-150
                  flex items-center gap-2
                  ${selectedContextId === context.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''}
                `}
              >
                <Target className="h-4 w-4 text-blue-500" />
                <div>
                  <div className="font-medium text-gray-900">
                    {humanizeContext(context.name)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {context.topic}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
