"use client"

import { Card } from "@/components/ui/card"
import { useState, useEffect } from "react"
import { useGrammar } from "@/contexts/grammar-context"

interface ClosureItem {
  item: string
  production: string
  dot_position: number
  lookahead: string
  type: "kernel" | "closure"
}

interface Transition {
  symbol: string
  item_count: number
  items: string[]
}

interface ClosureState {
  state: number
  kernel_items: ClosureItem[]
  closure_items: ClosureItem[]
  total_items: number
  transitions: Record<string, Transition>
  all_items: string[]
}

interface FirstTableData {
  symbol: string
  first_set: string[]
  first_string: string
}

interface ApiResponse {
  success: boolean
  operation: string
  grammar: {
    productions: string[]
    start_symbol: string
  }
  closure_table: ClosureState[]
  terminals: string[]
  nonterminals: string[]
  summary: {
    total_states: number
    total_terminals: number
    total_nonterminals: number
    total_items: number
  }
}

export default function ClosureTable() {
  const { getGrammarForAPI } = useGrammar()
  const [data, setData] = useState<ClosureState[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [firstTableData, setFirstTableData] = useState<Record<string, string[]>>({})

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Primero obtener la gramática
      const grammarData = getGrammarForAPI()
      
      // Obtener FIRST table primero
      const firstResponse = await fetch('/api/first-table', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(grammarData)
      })
      
      const firstResult = await firstResponse.json()
      
      if (!firstResult.success) {
        throw new Error('Failed to get FIRST table data')
      }
      
      // Construir first_table object
      const firstTable: Record<string, string[]> = {}
      if (firstResult.table_data) {
        firstResult.table_data.forEach((item: any) => {
          firstTable[item.symbol] = item.first_set
        })
      }
      
      setFirstTableData(firstTable)
      
      // Ahora obtener closure table con gramática y first_table
      const closureData = {
        grammar: grammarData.grammar,
        first_table: firstTable,
        operation: "lr1_closure_table"
      }
      
      console.log('📤 Enviando datos al LR1 Closure endpoint:', closureData)
      
      const closureResponse = await fetch('/api/lr1-closure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(closureData)
      })
      
      const closureResult: ApiResponse = await closureResponse.json()
      
      console.log('📥 Respuesta del LR1 Closure endpoint:', closureResult)
      
      if (closureResult.success && closureResult.closure_table) {
        setData(closureResult.closure_table)
        setFirstTableData(firstResult.first_table)
      } else {
        setError('Failed to load closure table data')
      }
    } catch (err) {
      console.error('❌ Error en fetchData:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = () => {
    fetchData()
  }

  useEffect(() => {
    fetchData()
  }, [])
  if (loading) {
    return (
      <Card className="p-4 overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">LR(1) Closure Table</h2>
          <button 
            onClick={handleRefresh}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Refresh
          </button>
        </div>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading...</span>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="p-4 overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">LR(1) Closure Table</h2>
          <button 
            onClick={handleRefresh}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
        <div className="text-center py-8">
          <div className="text-red-600 mb-2">⚠️ Error loading data</div>
          <div className="text-gray-600 text-sm">{error}</div>
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-4 overflow-auto">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">LR(1) Closure Table</h2>
        <button 
          onClick={handleRefresh}
          className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Refresh
        </button>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-xs font-mono">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="text-left p-2 font-semibold text-gray-900 bg-gray-100">State</th>
              <th className="text-left p-2 font-semibold text-gray-900 bg-gray-100">Kernel Items</th>
              <th className="text-left p-2 font-semibold text-gray-900 bg-gray-100">Closure Items</th>
              <th className="text-left p-2 font-semibold text-gray-900 bg-gray-100">Transitions</th>
            </tr>
          </thead>
          <tbody>
            {data.map((state, idx) => (
              <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="p-2 text-center text-green-600 font-bold bg-green-50">{state.state}</td>
                <td className="p-2 text-gray-800">
                  <div className="space-y-1">
                    {state.kernel_items.map((item, i) => (
                      <div key={i} className="text-blue-700 font-medium">
                        {item.item}
                      </div>
                    ))}
                  </div>
                </td>
                <td className="p-2 text-gray-700">
                  <div className="space-y-1">
                    {state.closure_items.map((item, i) => (
                      <div key={i} className="text-gray-600">
                        {item.item}
                      </div>
                    ))}
                  </div>
                </td>
                <td className="p-2 text-gray-800">
                  <div className="space-y-1">
                    {Object.entries(state.transitions).map(([symbol, transition]) => (
                      <div key={symbol} className="text-purple-600">
                        {symbol} → {transition.item_count} items
                      </div>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
