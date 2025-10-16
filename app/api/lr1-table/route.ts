import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Console.log para ver qué llega al servidor
    console.log('🔍 Datos recibidos en LR1 Table API route:', body)
    
    // Validar que el body tenga la estructura esperada
    if (!body.grammar || !body.closure_data || !body.operation) {
      console.log('❌ Error: Campos faltantes en el body')
      return NextResponse.json(
        { 
          success: false, 
          error: 'Missing required fields: grammar, closure_data, and operation' 
        },
        { status: 400 }
      )
    }

    const apiUrl = 'https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/lr1-table'
    
    console.log('🚀 Enviando a AWS Lambda:', apiUrl)
    // Normalizar espacios en closure_data por seguridad
    const normalizeSpaces = (str: string) => (typeof str === 'string' ? str.replace(/\s+/g, ' ').trim() : str)
    const normalizedBody = {
      ...body,
      closure_data: Array.isArray(body.closure_data)
        ? body.closure_data.map((s: any) => ({
            state: s.state,
            kernel_items: (s.kernel_items || []).map((it: any) => ({
              ...it,
              item: normalizeSpaces(it.item),
              production: normalizeSpaces(it.production),
            })),
            closure_items: (s.closure_items || []).map((it: any) => ({
              ...it,
              item: normalizeSpaces(it.item),
              production: normalizeSpaces(it.production),
            })),
            all_items: (s.all_items || []).map((t: any) => normalizeSpaces(t)),
          }))
        : body.closure_data,
    }
    console.log('📦 Body enviado a AWS (normalizado):', normalizedBody)
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(normalizedBody)
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
          sentBody: normalizedBody,
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    console.log('✅ Respuesta de AWS Lambda:', data)
    
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
          "S' -> S",
          "S -> C C",
          "C -> c C",
          "C -> d"
        ],
        start_symbol: "S'"
      },
      closure_data: [
        {
          state: 0,
          kernel_items: [
            {
              item: "S' -> •S, $",
              production: "S' -> S",
              dot_position: 0,
              lookahead: "$",
              type: "kernel"
            }
          ],
          closure_items: [
            {
              item: "S -> •C C, $",
              production: "S -> C C",
              dot_position: 0,
              lookahead: "$",
              type: "closure"
            }
          ],
          all_items: [
            "S' -> •S, $",
            "S -> •C C, $",
            "C -> •c C, c",
            "C -> •d, c",
            "C -> •c C, d",
            "C -> •d, d"
          ]
        }
      ],
      operation: "lr1_table"
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
