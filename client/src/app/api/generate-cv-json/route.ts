import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log('Request body:', body);
    
    // The generate-cv-json endpoint expects cv_text field (raw text)
    const backendBody = {
      cv_text: body.cv_text
    };
    
    const backendUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://f4b626e1610f.ngrok-free.app'}/generate-cv-json`;
    console.log('Calling backend URL:', backendUrl);
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams(backendBody),
    });

    console.log('Backend response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      throw new Error(`Backend request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Backend response data:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('API Error details:', error);
    return NextResponse.json(
      { 
        error: 'Failed to generate CV JSON',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 