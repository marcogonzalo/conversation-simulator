import { ConversationConfigSelector } from '@/components/conversation/conversation-config-selector'
import { Hero } from '@/components/layout/hero'
import { Features } from '@/components/layout/features'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      <Hero />
      <section id="config-selector">
        <ConversationConfigSelector />
      </section>
      <Features />
    </main>
  )
}
