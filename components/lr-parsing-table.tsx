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

export default function LRParsingTable() {
  const { getGrammarForAPI, grammarRules } = useGrammar()
  const [data, setData] = useState<TableData[]>([])
  const [terminals, setTerminals] = useState<string[]>([])
  const [nonterminals, setNonterminals] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [closureData, setClosureData] = useState<any[]>([])
  const [summary, setSummary] = useState<any>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Obtener la gramática del contexto
      const grammarData = getGrammarForAPI()
      
      // Preparar el request según el nuevo formato
      const requestData = {
        grammar: grammarData.grammar,
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
          const action = result.lr1_table.action_table[stateId] || {}
          const goto = result.lr1_table.goto_table[stateId] || {}
          
          // Convertir goto numbers a strings para la tabla
          const gotoStrings: Record<string, string> = {}
          Object.entries(goto).forEach(([symbol, targetState]) => {
            gotoStrings[symbol] = targetState.toString()
          })
          
          tableData.push({
            state,
            action,
            goto: gotoStrings
          })
        })
        
        setData(tableData)
        setTerminals(result.symbols.terminals)
        setNonterminals(result.symbols.nonterminals)
        setSummary(result.summary)
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
              <span>States: {summary.total_states}</span>
              <span>Terminals: {summary.total_terminals}</span>
              <span>Non-terminals: {summary.total_nonterminals}</span>
              <span>Productions: {summary.total_productions}</span>
              {summary.total_conflicts > 0 && (
                <span className="text-red-600">Conflicts: {summary.total_conflicts}</span>
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
                    {terminal}
                  </th>
                ))}
                {nonterminals.map((nonterminal) => (
                  <th key={nonterminal} className="p-3 text-center font-semibold text-gray-900 bg-green-50">
                    {nonterminal}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row) => (
                <tr key={row.state} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="p-3 text-center text-green-600 font-bold bg-green-50">{row.state}</td>
                  {terminals.map((terminal) => (
                    <td key={terminal} className="p-3 text-center text-gray-800">
                      {row.action[terminal] || ""}
                    </td>
                  ))}
                  {nonterminals.map((nonterminal) => (
                    <td key={nonterminal} className="p-3 text-center text-gray-800">
                      {row.goto[nonterminal] || ""}
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
    </Card>
  )
}