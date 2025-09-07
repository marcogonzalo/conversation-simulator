import { AnalysisViewer } from '@/components/analysis/analysis-viewer'
import { notFound } from 'next/navigation'

interface AnalysisPageProps {
  params: Promise<{
    id: string
  }>
}

export default async function AnalysisPage({ params }: AnalysisPageProps) {
  const { id: analysisId } = await params

  if (!analysisId) {
    notFound()
  }

  return (
    <main className="min-h-screen bg-background">
      <AnalysisViewer analysisId={analysisId} />
    </main>
  )
}
