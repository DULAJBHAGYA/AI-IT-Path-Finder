import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // The download-cv-pdf endpoint expects cv_text field (raw text)
    const backendBody = {
      cv_text: body.cv_text
    };
    
    const backendUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://f4b626e1610f.ngrok-free.app'}/download-cv-pdf`;
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams(backendBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      throw new Error(`Backend request failed: ${response.status} ${response.statusText}`);
    }

    const pdfBuffer = await response.arrayBuffer();
    
    return new NextResponse(pdfBuffer, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="cv.pdf"',
      },
    });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to download PDF' },
      { status: 500 }
    );
  }
} 