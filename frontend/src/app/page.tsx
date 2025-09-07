import { PersonaSelectorWrapper } from '@/components/persona/persona-selector-wrapper'
import { Hero } from '@/components/layout/hero'
import { Features } from '@/components/layout/features'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      <Hero />
      <PersonaSelectorWrapper />
      <Features />
    </main>
  )
}
