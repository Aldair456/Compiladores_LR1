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
    productions: string[]
    start_symbol: string
  }
  augmented_productions: string[]
  table_data: TableData[]
  terminals: string[]
  nonterminals: string[]
  summary: {
    total_states: number
    total_terminals: number
    total_nonterminals: number
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

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Primero obtener la gramática
      const grammarData = getGrammarForAPI()

      // Primero obtener FIRST table para el closure table
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

      // Ahora obtener closure data del closure table
      const closureResponse = await fetch('/api/lr1-closure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          grammar: grammarData.grammar,
          first_table: firstTable,
          operation: "lr1_closure_table"
        })
      })

      const closureResult = await closureResponse.json()

      if (!closureResult.success) {
        throw new Error('Failed to get closure data')
      }

      // Normalizar closure_data al formato que funciona en Postman
      const normalizeSpaces = (str: string) => str.replace(/\s+/g, ' ').trim()
      const normalizeEpsilon = (str: string) => normalizeSpaces(str.replace(/ε/g, 'e'))
      const grammarSet = new Set((grammarData.grammar.productions || []).map((p: string) => normalizeEpsilon(p)))
      const simplifiedClosure = (closureResult.closure_table || []).map((s: any) => ({
        state: s.state,
        kernel_items: (s.kernel_items || [])
          .map((it: any) => ({
            ...it,
            production: normalizeEpsilon(it.production),
            item: normalizeEpsilon(it.item),
          }))
          .filter((it: any) => !it.production || grammarSet.has(it.production)),
        closure_items: (s.closure_items || [])
          .map((it: any) => ({
            ...it,
            production: normalizeEpsilon(it.production),
            item: normalizeEpsilon(it.item),
          }))
          .filter((it: any) => !it.production || grammarSet.has(it.production)),
        all_items: (s.all_items || []).map((t: string) => normalizeEpsilon(t)),
      }))

      console.log('🧹 closure_data normalizado y filtrado:', simplifiedClosure)

      setClosureData(simplifiedClosure)

      // Construir gramática cruda (sin expandir |) tal como la requiere el endpoint
      const rawProductions: string[] = (grammarRules || []).map((r: any) => `${r.left} -> ${r.right}`)
      const rawStart = (grammarRules || []).find((r: any) => r.left === "S'")?.left || (grammarRules?.[0]?.left ?? "S'")
      const lr1Grammar = { productions: rawProductions, start_symbol: rawStart }

      // Ahora obtener LR1 table con gramática cruda y closure_data simplificado
      const lr1Data = {
        grammar: lr1Grammar,
        closure_data: simplifiedClosure,
        operation: "lr1_table",
      }

      console.log('📤 Enviando datos al LR1 Table endpoint (normalizado y gramática cruda):', JSON.stringify(lr1Data, null, 2))

      const response = await fetch('/api/lr1-table', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(lr1Data)
      })

      const result: ApiResponse = await response.json()

      console.log('📥 Respuesta del LR1 Table endpoint:', result)

      if (result.success && result.table_data) {
        setData(result.table_data)
        setTerminals(result.terminals)
        setNonterminals(result.nonterminals)
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
        <h2 className="text-lg font-semibold text-gray-900">LR Table</h2>
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
          Loading LR1 Parsing Table...
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
        <div className="text-center py-4 text-gray-500">
          No LR1 table data available. Click Refresh to load data.
        </div>
      )}
    </Card>
  )
}