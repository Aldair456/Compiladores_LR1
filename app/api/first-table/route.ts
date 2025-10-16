import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Console.log para ver qué llega al servidor
    console.log('🔍 Datos recibidos en API route:', body)
    
    // Validar que el body tenga la estructura esperada
    if (!body.grammar || !body.operation) {
      console.log('❌ Error: Campos faltantes en el body')
      return NextResponse.json(
        { 
          success: false, 
          error: 'Missing required fields: grammar and operation' 
        },
        { status: 400 }
      )
    }

    const apiUrl = 'https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/first-table'
    
    console.log('🚀 Enviando a AWS Lambda:', apiUrl)
    console.log('📦 Body enviado a AWS:', body)
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    })

    if (!response.ok) {
      console.log('❌ Error de AWS Lambda:', response.status, response.statusText)
      throw new Error(`API responded with status: ${response.status}`)
    }

    const data = await response.json()
    
    console.log('✅ Respuesta de AWS Lambda:', data)
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('💥 Error en API route:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch first table data',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

// Mantener GET para compatibilidad (usando gramática por defecto)
export async function GET(request: NextRequest) {
  try {
    const defaultGrammar = {
      grammar: {
        productions: [
          "S' -> S",
          "S -> C c",
          "C -> c C",
          "C -> d"
        ],
        start_symbol: "S'"
      },
      operation: "first_table"
    }

    const apiUrl = 'https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/first-table'
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(defaultGrammar)
    })

    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`)
    }

    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching first table data:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch first table data',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}
