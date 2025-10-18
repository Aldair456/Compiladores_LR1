import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    console.log('Request completo a AWS Lambda:');
    console.log('  - URL: https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/lr1-table');
    console.log('  - Method: POST');
    console.log('  - Headers: Content-Type: application/json');
    console.log('  - Body:', JSON.stringify(body, null, 2));

    const response = await fetch('https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/lr1-table', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Response de AWS Lambda:', JSON.stringify(data, null, 2));

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error en lr1-table:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Error desconocido',
        operation: 'lr1_table'
      },
      { status: 500 }
    );
  }
}