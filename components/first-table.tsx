"use client"

import { Card } from "@/components/ui/card"
import { useState, useEffect } from "react"
import { useGrammar } from "@/contexts/grammar-context"

interface FirstTableData {
  symbol: string
  first_set: string[]
  first_string: string
}

interface FollowTableData {
  symbol: string
  follow_set: string[]
  follow_string: string
}

interface ApiResponse {
  success: boolean
  operation: string
  grammar: {
    original_productions: string[]
    augmented_productions: string[]
    start_symbol: string
    expanded_productions: string[]
    is_augmented: boolean
    real_start_symbol: string
  }
  symbols: {
    terminals: string[]
    nonterminals: string[]
  }
  tables: {
    first_table: FirstTableData[]
    follow_table: FollowTableData[]
    productions_table: Array<{
      id: number
      production: string
      left_side: string
      right_side: string
    }>
  }
  raw_data: {
    first_sets: Record<string, string[]>
    follow_sets: Record<string, string[]>
  }
  summary: {
    total_terminals: number
    total_nonterminals: number
    total_productions: number
  }
}

export default function FirstTable() {
  const { getGrammarForAPI } = useGrammar()
  const [firstData, setFirstData] = useState<FirstTableData[]>([])
  const [followData, setFollowData] = useState<FollowTableData[]>([])
  const [terminals, setTerminals] = useState<string[]>([])
  const [nonterminals, setNonterminals] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const grammarData = getGrammarForAPI()
      
      // Console.log para ver qué se envía
      console.log('📤 Enviando datos al endpoint:', grammarData)
      
      const response = await fetch('/api/first-table', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(grammarData)
      })
      
      const result: ApiResponse = await response.json()
      
      // Console.log para ver la respuesta
      console.log('📥 Respuesta del endpoint:', result)
      
      if (result.success && result.tables) {
        setFirstData(result.tables.first_table)
        setFollowData(result.tables.follow_table)
        setTerminals(result.symbols.terminals)
        setNonterminals(result.symbols.nonterminals)
      } else {
        setError('Failed to load first table data')
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
      <Card className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">FIRST & FOLLOW Analysis</h2>
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
      <Card className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">FIRST & FOLLOW Analysis</h2>
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
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">FIRST & FOLLOW Analysis</h2>
        <button 
          onClick={handleRefresh}
          className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Refresh
        </button>
      </div>


      {/* FIRST Table */}
      <div className="mb-6">
        <h3 className="text-md font-semibold mb-3 text-gray-900">FIRST Sets</h3>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm font-mono">
            <thead>
              <tr className="border-b-2 border-gray-300">
                <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Nonterminal</th>
                <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">FIRST Set</th>
                <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Elements</th>
              </tr>
            </thead>
            <tbody>
              {firstData.map((row, idx) => (
                <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="p-3 text-gray-800 font-semibold">{row.symbol}</td>
                  <td className="p-3 text-blue-700 font-medium">{`{${row.first_string}}`}</td>
                  <td className="p-3 text-gray-600">{row.first_set.join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* FOLLOW Table */}
      <div>
        <h3 className="text-md font-semibold mb-3 text-gray-900">FOLLOW Sets</h3>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm font-mono">
            <thead>
              <tr className="border-b-2 border-gray-300">
                <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Nonterminal</th>
                <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">FOLLOW Set</th>
                <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Elements</th>
              </tr>
            </thead>
            <tbody>
              {followData.map((row, idx) => (
                <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="p-3 text-gray-800 font-semibold">{row.symbol}</td>
                  <td className="p-3 text-green-700 font-medium">{`{${row.follow_string}}`}</td>
                  <td className="p-3 text-gray-600">{row.follow_set.join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Card>
  )
}
