import { NextRequest, NextResponse } from 'next/server'

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/conversations/${id}/complete`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error('Failed to complete conversation')
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error completing conversation:', error)
    return NextResponse.json(
      { error: 'Failed to complete conversation' },
      { status: 500 }
    )
  }
}
