import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Console.log para ver qué llega al servidor
    console.log('🔍 Datos recibidos en LR1 Table API route:', body)
    console.log('🔍 Body completo recibido:', JSON.stringify(body, null, 2))
    console.log('🔍 Grammar recibido:', body.grammar)
    console.log('🔍 Closure table recibido:', body.closure_table)
    console.log('🔍 Options recibido:', body.options)
    
    // Validar que el body tenga la estructura esperada
    if (!body.grammar) {
      console.log('❌ Error: Campo grammar faltante en el body')
      return NextResponse.json(
        { 
          success: false, 
          error: 'Missing required field: grammar' 
        },
        { status: 400 }
      )
    }

    const apiUrl = 'https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/lr1-table'
    
    console.log('🚀 Enviando a AWS Lambda:', apiUrl)
    
    // Preparar el body según el nuevo formato
    const requestBody = {
      grammar: body.grammar,
      closure_table: body.closure_table || undefined, // Opcional
      options: body.options || { // Opcional con valores por defecto
        augment: true,
        epsilon_symbol: "ε",
        end_marker: "$",
        accept_token: "acc"
      }
    }
    
    console.log('📦 Body enviado a AWS:', JSON.stringify(requestBody, null, 2))
    console.log('📦 Request completo a AWS Lambda:')
    console.log('   - URL:', apiUrl)
    console.log('   - Method: POST')
    console.log('   - Headers: Content-Type: application/json')
    console.log('   - Body:', JSON.stringify(requestBody, null, 2))
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
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
          sentBody: requestBody,
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    console.log('✅ Respuesta de AWS Lambda:', data)
    console.log('✅ Respuesta completa de AWS:', JSON.stringify(data, null, 2))
    console.log('✅ Status de AWS:', response.status)
    console.log('✅ Success:', data.success)
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('💥 Error en LR1 Table API route:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch LR1 table data',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

// Mantener GET para compatibilidad (usando datos por defecto)
export async function GET(request: NextRequest) {
  try {
    const defaultData = {
      grammar: {
        productions: [
          "S -> A B C",
          "A -> a | ε",
          "B -> b | ε", 
          "C -> c"
        ],
        start_symbol: "S"
      },
      options: {
        augment: true,
        epsilon_symbol: "ε",
        end_marker: "$",
        accept_token: "acc"
      }
    }

    const apiUrl = 'https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/lr1-table'
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(defaultData)
    })

    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`)
    }

    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching LR1 table data:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch LR1 table data',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}
