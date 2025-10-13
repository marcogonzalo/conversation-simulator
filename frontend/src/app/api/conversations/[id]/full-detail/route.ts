import { NextResponse } from 'next/server';

// Use backend service name in Docker, localhost for local development
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://backend:8000';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const response = await fetch(
      `${BACKEND_URL}/api/v1/conversations/${id}/full-detail`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching conversation detail:', error);
    return NextResponse.json(
      { error: 'Failed to fetch conversation detail' },
      { status: 500 }
    );
  }
}

