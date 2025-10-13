import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    console.log('🔍 Datos recibidos en LR1 Trace Pretty API route:', body)

    if (!body || !body.operation || !body.lr1_table || !body.input_string) {
      return NextResponse.json(
        {
          success: false,
          error: 'Missing required fields: operation, lr1_table, input_string',
        },
        { status: 400 }
      )
    }

    const apiUrl = 'https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/lr1-trace-pretty'

    console.log('🚀 Enviando a AWS Lambda:', apiUrl)
    console.log('📦 Body enviado a AWS:', body)

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const upstreamBody = await response.text().catch(() => '<no-body>')
      console.log('❌ Error de AWS Lambda:', response.status, response.statusText, '\nBody:', upstreamBody)
      return NextResponse.json(
        {
          success: false,
          error: 'Upstream Lambda error',
          upstreamStatus: response.status,
          upstreamStatusText: response.statusText,
          upstreamBody,
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    console.log('✅ Respuesta de AWS Lambda:', data)
    return NextResponse.json(data)
  } catch (error) {
    console.error('💥 Error en LR1 Trace Pretty API route:', error)
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch LR1 trace pretty data',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    )
  }
}


