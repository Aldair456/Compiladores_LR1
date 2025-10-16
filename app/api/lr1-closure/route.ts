import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Console.log para ver qué llega al servidor
    console.log('🔍 Datos recibidos en LR1 Closure API route:', body)
    
    // Validar que el body tenga la estructura esperada para LR1 Closure
    if (!body.start_symbol || !body.productions || !body.options) {
      console.log('❌ Error: Campos faltantes en el body')
      console.log('❌ Body recibido:', body)
      return NextResponse.json(
        { 
          success: false, 
          error: 'Missing required fields: start_symbol, productions, and options' 
        },
        { status: 400 }
      )
    }

    const apiUrl = 'https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/lr1-closure'
    
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
      const errorText = await response.text()
      console.log('❌ Error response body:', errorText)
      throw new Error(`API responded with status: ${response.status} - ${errorText}`)
    }

    const data = await response.json()
    
    console.log('✅ Respuesta de AWS Lambda:', data)
    console.log('📊 Success en respuesta:', data.success)
    console.log('📋 Grammar en respuesta:', data.grammar)
    console.log('🗂️ Closure table en respuesta:', data.closure_table)
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('💥 Error en LR1 Closure API route:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch LR1 closure data',
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
      start_symbol: "S'",
      productions: [
        "S' -> S",
        "S -> C c",
        "C -> c C",
        "C -> d"
      ],
      options: {
        augment: true,
        expand_alternatives: true
      }
    }

    const apiUrl = 'https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/lr1-closure'
    
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
    console.error('Error fetching LR1 closure data:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch LR1 closure data',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}