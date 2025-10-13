import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://backend:8000'

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/contexts`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching contexts:', error)
    return NextResponse.json(
      { error: 'Failed to fetch contexts' },
      { status: 500 }
    )
  }
}
