"use client"

import { Card } from "@/components/ui/card"
import { useState, useEffect } from "react"
import { useGrammar } from "@/contexts/grammar-context"

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
  first_table: Record<string, string[]>
  table_data: FirstTableData[]
  summary: {
    total_symbols: number
    terminals: number
    nonterminals: number
  }
}

export default function FirstTable() {
  const { getGrammarForAPI } = useGrammar()
  const [data, setData] = useState<FirstTableData[]>([])
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
      
      if (result.success && result.table_data) {
        setData(result.table_data)
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
          <h2 className="text-lg font-semibold text-gray-900">FIRST table</h2>
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
          <h2 className="text-lg font-semibold text-gray-900">FIRST table</h2>
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
        <h2 className="text-lg font-semibold text-gray-900">FIRST table</h2>
        <button 
          onClick={handleRefresh}
          className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Refresh
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm font-mono">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Nonterminal</th>
              <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">FIRST</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="p-3 text-gray-800 font-semibold">{row.symbol}</td>
                <td className="p-3 text-blue-700 font-medium">{`{${row.first_string}}`}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
