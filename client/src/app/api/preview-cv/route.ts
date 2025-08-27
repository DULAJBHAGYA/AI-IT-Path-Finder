import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log('Request body:', body);
    
    // The preview-cv-json endpoint expects cv_json field (JSON string)
    const backendBody = {
      cv_json: body.cv_json || JSON.stringify(body)
    };
    console.log('Backend request body:', backendBody);
    
    // Use the backend URL from the notebook
    const backendUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://f4b626e1610f.ngrok-free.app'}/preview-cv-json`;
    console.log('Calling backend URL:', backendUrl);
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams(backendBody),
    });

    console.log('Backend response status:', response.status);
    console.log('Backend response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      
      // If backend is offline, return a mock response
      if (response.status === 404 && errorText.includes('ERR_NGROK_3200')) {
        console.log('Backend is offline, returning mock response');
        return NextResponse.json({
          message: 'Backend is currently offline. Please restart your ngrok tunnel.',
          mock_data: {
            name: 'Sample CV',
            email: 'sample@example.com',
            phone: '+1234567890',
            summary: 'This is a sample CV generated while the backend is offline.',
            experience: 'Sample experience data',
            education: 'Sample education data',
            skills: 'Sample skills data'
          }
        });
      }
      
      throw new Error(`Backend request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Backend response data:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('API Error details:', error);
    return NextResponse.json(
      { 
        error: 'Failed to generate preview',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 