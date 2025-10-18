"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useGrammar } from "@/contexts/grammar-context"
import { useState, useEffect } from "react"

interface TableData {
  state: number
  action: Record<string, string>
  goto: Record<string, string>
}

interface ApiResponse {
  success: boolean
  operation: string
  grammar: {
    augmented: boolean
    start_symbol: string
    original_start_symbol: string
    epsilon: string
    end_marker: string
    accept_token: string
    original_productions: string[]
    expanded_productions: string[]
  }
  lr1_table: {
    action_table: Record<string, Record<string, string>>
    goto_table: Record<string, Record<string, number>>
    reductions: Record<string, any>
    conflicts: any[]
  }
  closure_table: {
    states: Array<{
      id: number
      items: string[]
      transitions: Record<string, number>
    }>
  }
  productions_table: Array<{
    number: number
    production: string
    left_side: string
    right_side: string
  }>
  symbols: {
    terminals: string[]
    nonterminals: string[]
  }
  summary: {
    total_states: number
    total_terminals: number
    total_nonterminals: number
    total_productions: number
    total_conflicts: number
    conflict_types: string[]
  }
}

// Helper function to safely convert any value to string
const safeToString = (value: any): string => {
  if (value === null || value === undefined) {
    return ""
  }
  if (typeof value === 'string') {
    return value
  }
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  return String(value)
}

export default function LRParsingTable() {
  const { getGrammarForAPI, grammarRules } = useGrammar()
  const [data, setData] = useState<TableData[]>([])
  const [terminals, setTerminals] = useState<string[]>([])
  const [nonterminals, setNonterminals] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [closureData, setClosureData] = useState<any[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [reductions, setReductions] = useState<Record<string, any>>({})
  const [conflicts, setConflicts] = useState<any[]>([])
  const [productionsTable, setProductionsTable] = useState<any[]>([])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Obtener la gramática del contexto
      const grammarData = getGrammarForAPI()
      
      // PASO 1: Obtener las clausuras del endpoint lr1-closure
      console.log('🔄 PASO 1: Obteniendo clausuras del endpoint lr1-closure...')
      
      const closureRequestData = {
        start_symbol: grammarData.grammar.start_symbol,
        productions: grammarData.grammar.productions,
        options: {
          augment: true,
          epsilon_symbol: "ε",
          end_marker: "$",
          accept_token: "acc"
        }
      }

      console.log('📤 Request a lr1-closure:', closureRequestData)

      const closureResponse = await fetch('/api/lr1-closure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(closureRequestData)
      })

      const closureResult = await closureResponse.json()
      console.log('📥 Respuesta de lr1-closure:', closureResult)

      if (!closureResult.success) {
        throw new Error('Failed to get closure data')
      }

      // PASO 2: Preparar el request para lr1-table con las clausuras
      console.log('🔄 PASO 2: Preparando request para lr1-table con clausuras...')
      
      const requestData = {
        grammar: grammarData.grammar,
        closure_table: closureResult.closure_table, // ← CLAUSURAS OBLIGATORIAS
        options: {
          augment: true,
          epsilon_symbol: "ε",
          end_marker: "$",
          accept_token: "acc"
        }
      }

      console.log('📤 Enviando datos al LR1 Table endpoint:', requestData)
      console.log('📤 Body completo que se envía:', JSON.stringify(requestData, null, 2))
      console.log('📤 Grammar data:', requestData.grammar)
      console.log('📤 Closure table:', requestData.closure_table)
      console.log('📤 Options:', requestData.options)

      const response = await fetch('/api/lr1-table', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      })

      const result: ApiResponse = await response.json()

      console.log('📥 Respuesta del LR1 Table endpoint:', result)
      console.log('📥 Respuesta completa recibida:', JSON.stringify(result, null, 2))
      console.log('📥 Status de la respuesta:', response.status)
      console.log('📥 Success:', result.success)
      console.log('📥 LR1 Table data:', result.lr1_table)
      console.log('📥 Action Table:', result.lr1_table?.action_table)
      console.log('📥 Goto Table:', result.lr1_table?.goto_table)
      console.log('📥 Symbols:', result.symbols)
      console.log('📥 Summary:', result.summary)

      if (result.success && result.lr1_table) {
        // Convertir la respuesta al formato esperado por la tabla
        const tableData: TableData[] = []
        
        // Procesar action_table y goto_table
        const allStates = new Set([
          ...Object.keys(result.lr1_table.action_table),
          ...Object.keys(result.lr1_table.goto_table)
        ])
        
        allStates.forEach(stateId => {
          const state = parseInt(stateId)
          const actionRaw = result.lr1_table.action_table[stateId] || {}
          const gotoRaw = result.lr1_table.goto_table[stateId] || {}
          
          // Convertir action values a strings
          const actionStrings: Record<string, string> = {}
          Object.entries(actionRaw).forEach(([symbol, actionValue]) => {
            console.log(`Processing action for state ${stateId}, symbol ${symbol}:`, actionValue, typeof actionValue)
            actionStrings[symbol] = safeToString(actionValue)
          })
          
          // Convertir goto numbers a strings para la tabla
          const gotoStrings: Record<string, string> = {}
          Object.entries(gotoRaw).forEach(([symbol, targetState]) => {
            gotoStrings[symbol] = safeToString(targetState)
          })
          
          tableData.push({
            state,
            action: actionStrings,
            goto: gotoStrings
          })
        })
        
        setData(tableData)
        // Asegurar que el símbolo $ siempre esté incluido en los terminales
        const terminalsWithEndMarker = [...new Set([...result.symbols.terminals, "$"])]
        setTerminals(terminalsWithEndMarker)
        setNonterminals(result.symbols.nonterminals)
        setSummary(result.summary)
        setReductions(result.lr1_table.reductions)
        setConflicts(result.lr1_table.conflicts)
        setProductionsTable(result.productions_table)
        setClosureData(result.closure_table.states)
      } else {
        setError('Failed to load LR1 table data')
      }
    } catch (err) {
      console.error('❌ Error en fetchData:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <Card className="p-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">LR(1) Parsing Table</h2>
          <p className="text-sm text-gray-600">Action and Goto tables for LR(1) parsing</p>
          {summary && (
            <div className="flex gap-4 mt-2 text-xs text-gray-500">
              <span>States: {safeToString(summary.total_states)}</span>
              <span>Terminals: {safeToString(summary.total_terminals)}</span>
              <span>Non-terminals: {safeToString(summary.total_nonterminals)}</span>
              <span>Productions: {safeToString(summary.total_productions)}</span>
              {summary.total_conflicts > 0 && (
                <span className="text-red-600">Conflicts: {safeToString(summary.total_conflicts)}</span>
              )}
            </div>
          )}
        </div>
        <Button
          onClick={fetchData}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          {loading ? "Loading..." : "Refresh"}
        </Button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded text-red-700">
          Error: {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-4 text-gray-600">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          Loading LR(1) Parsing Table...
        </div>
      )}

      {!loading && data.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b-2 border-gray-300">
                <th className="p-3 font-semibold text-gray-900 bg-gray-100">State</th>
                <th colSpan={terminals.length} className="p-3 text-center font-semibold text-gray-900 bg-blue-100">
                  ACTION
                </th>
                <th colSpan={nonterminals.length} className="p-3 text-center font-semibold text-gray-900 bg-green-100">
                  GOTO
                </th>
              </tr>
              <tr className="border-b border-gray-200">
                <th className="p-3 font-semibold text-gray-900 bg-gray-100"></th>
                {terminals.map((terminal) => (
                  <th key={terminal} className="p-3 text-center font-semibold text-gray-900 bg-blue-50">
                    {safeToString(terminal)}
                  </th>
                ))}
                {nonterminals.map((nonterminal) => (
                  <th key={nonterminal} className="p-3 text-center font-semibold text-gray-900 bg-green-50">
                    {safeToString(nonterminal)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row) => (
                <tr key={row.state} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="p-3 text-center text-green-600 font-bold bg-green-50">{safeToString(row.state)}</td>
                  {terminals.map((terminal) => (
                    <td key={terminal} className="p-3 text-center text-gray-800">
                      {safeToString(row.action[terminal])}
                    </td>
                  ))}
                  {nonterminals.map((nonterminal) => (
                    <td key={nonterminal} className="p-3 text-center text-gray-800">
                      {safeToString(row.goto[nonterminal])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && data.length === 0 && !error && (
        <div className="text-center py-8 text-gray-500">
          <div className="text-gray-400 mb-2">📊</div>
          <div>No LR(1) table data available.</div>
          <div className="text-sm mt-1">Click Refresh to load data.</div>
        </div>
      )}

      {/* Sección de Conflictos */}
      {!loading && conflicts.length > 0 && (
        <div className="mt-6">
          <h3 className="text-md font-semibold text-red-600 mb-3">⚠️ Conflicts Detected</h3>
          <div className="bg-red-50 border border-red-200 rounded p-4">
            <div className="space-y-3">
              {conflicts.map((conflict, index) => (
                <div key={index} className="bg-white border border-red-200 rounded p-3">
                  <div className="font-semibold text-red-600 mb-2">
                    State {safeToString(conflict.state)}
                  </div>
                  <div className="ml-4 space-y-2">
                    <div className="text-sm">
                      <span className="font-semibold text-gray-700">Conflict Type:</span> 
                      <span className="ml-2 font-mono text-red-600">{safeToString(conflict.type)}</span>
                    </div>
                    <div className="text-sm">
                      <span className="font-semibold text-gray-700">Symbol:</span> 
                      <span className="ml-2 font-mono text-green-600">'{safeToString(conflict.symbol)}'</span>
                    </div>
                    {conflict.actions && conflict.actions.length > 0 && (
                      <div className="text-sm">
                        <span className="font-semibold text-gray-700">Conflicting Actions:</span>
                        <div className="ml-2 mt-1">
                          {conflict.actions.map((action, actionIndex) => (
                            <span key={actionIndex} className="inline-block bg-red-100 text-red-700 px-2 py-1 rounded text-xs font-mono mr-1 mb-1">
                              {safeToString(action)}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {conflict.description && (
                      <div className="text-sm">
                        <span className="font-semibold text-gray-700">Description:</span> 
                        <span className="ml-2 text-gray-600">{safeToString(conflict.description)}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sección cuando NO hay conflictos */}
      {!loading && conflicts.length === 0 && (
        <div className="mt-6">
          <h3 className="text-md font-semibold text-green-600 mb-3">✅ No Conflicts Detected</h3>
          <div className="bg-green-50 border border-green-200 rounded p-4">
            <div className="text-sm text-green-700">
              <div className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                <span>The grammar is LR(1) and has no conflicts.</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sección de Reducciones */}
      {!loading && Object.keys(reductions).length > 0 && (
        <div className="mt-6">
          <h3 className="text-md font-semibold text-gray-900 mb-3">🔄 Reductions</h3>
          <div className="bg-gray-50 border border-gray-200 rounded p-4">
            <div className="space-y-3">
              {Object.entries(reductions).map(([state, stateReductions]) => (
                <div key={state} className="bg-white border border-gray-200 rounded p-3">
                  <div className="font-semibold text-blue-600 mb-2">
                    State {safeToString(state)}
                  </div>
                  {Object.entries(stateReductions).map(([symbol, reduction]) => (
                    <div key={symbol} className="ml-4 mb-2 p-2 bg-blue-50 rounded">
                      <div className="text-sm">
                        <span className="font-semibold text-gray-700">Symbol:</span> 
                        <span className="ml-2 font-mono text-green-600">'{safeToString(symbol)}'</span>
                      </div>
                      <div className="text-sm mt-1">
                        <span className="font-semibold text-gray-700">Production:</span> 
                        <span className="ml-2 font-mono text-blue-600">{safeToString(reduction.production)}</span>
                      </div>
                      <div className="text-sm mt-1">
                        <span className="font-semibold text-gray-700">Production #:</span> 
                        <span className="ml-2 font-mono text-purple-600">{safeToString(reduction.production_number)}</span>
                      </div>
                      <div className="text-sm mt-1">
                        <span className="font-semibold text-gray-700">Item:</span> 
                        <span className="ml-2 font-mono text-gray-600">{safeToString(reduction.item)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sección de Tabla de Producciones */}
      {!loading && productionsTable.length > 0 && (
        <div className="mt-6">
          <h3 className="text-md font-semibold text-gray-900 mb-3">📋 Productions Table</h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-xs font-mono">
              <thead>
                <tr className="border-b-2 border-gray-300">
                  <th className="p-3 font-semibold text-gray-900 bg-gray-100">#</th>
                  <th className="p-3 font-semibold text-gray-900 bg-gray-100">Production</th>
                  <th className="p-3 font-semibold text-gray-900 bg-gray-100">Left Side</th>
                  <th className="p-3 font-semibold text-gray-900 bg-gray-100">Right Side</th>
                </tr>
              </thead>
              <tbody>
                {productionsTable.map((prod) => (
                  <tr key={prod.number} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="p-3 text-center text-blue-600 font-bold bg-blue-50">{safeToString(prod.number)}</td>
                    <td className="p-3 text-gray-800">{safeToString(prod.production)}</td>
                    <td className="p-3 text-center text-green-600 font-semibold">{safeToString(prod.left_side)}</td>
                    <td className="p-3 text-center text-gray-800">{safeToString(prod.right_side)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </Card>
  )
}