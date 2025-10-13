"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useState } from "react"

interface TraceRow {
  step: number
  stack_string: string
  input: string
  action: string
  action_type: string
}

export default function TraceTable() {
  const [tokens, setTokens] = useState<string>("a b")
  const [maxSteps, setMaxSteps] = useState<string>("100")
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [rows, setRows] = useState<TraceRow[]>([])

  const handleRunTrace = async () => {
    try {
      setLoading(true)
      setError(null)

      // Ejemplo fijo de tabla LR1 del prompt; en la app real, deberíamos
      // construirla a partir del componente de LR Table si ya está disponible.
      const lr1Table = {
        grammar: {
          productions: [
            "S' -> S",
            "S -> a b",
            "S -> c d",
            "S -> e",
          ],
        },
        table_data: [
          { state: 0, action: { a: "s2", c: "s1", e: "s3" }, goto: { S: 4 } },
          { state: 1, action: { "$": "r3" }, goto: {} },
          { state: 2, action: { b: "s6" }, goto: {} },
          { state: 3, action: { "$": "r4" }, goto: {} },
          { state: 4, action: { "$": "acc" }, goto: {} },
          { state: 5, action: { "$": "r2" }, goto: {} },
          { state: 6, action: { "$": "r1" }, goto: {} },
        ],
      }

      const body = {
        operation: "lr1_trace_pretty",
        lr1_table: lr1Table,
        input_string: tokens,
        max_steps: Number(maxSteps) || 100,
      }

      const resp = await fetch('/api/lr1-trace-pretty', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      const data = await resp.json()

      if (!resp.ok || !data.success) {
        throw new Error(data?.error || 'Failed to fetch LR1 trace')
      }

      setRows(data.trace_rows || [])
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-foreground mb-4">Trace</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
          <div>
            <Label htmlFor="tokens">Input (tokens)</Label>
            <Input
              id="tokens"
              value={tokens}
              onChange={(e) => setTokens(e.target.value)}
              placeholder="e.g. a b"
              className="font-mono"
            />
          </div>
          <div>
            <Label htmlFor="maxSteps">Maximum number of steps</Label>
            <Input
              id="maxSteps"
              type="number"
              value={maxSteps}
              onChange={(e) => setMaxSteps(e.target.value)}
              className="font-mono"
            />
          </div>
          <div className="flex md:justify-end">
            <Button onClick={handleRunTrace} disabled={loading} className="w-full md:w-auto">
              {loading ? 'Running…' : 'Run Trace'}
            </Button>
          </div>
        </div>
        {error && (
          <div className="mt-3 p-3 bg-red-100 border border-red-300 rounded text-red-700">
            Error: {error}
          </div>
        )}
      </div>

      <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
        <table className="w-full border-collapse text-sm font-mono">
          <thead className="sticky top-0 bg-white">
            <tr className="border-b-2 border-gray-300">
              <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Step</th>
              <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Stack</th>
              <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Input</th>
              <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.step} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="p-3 text-gray-700 font-medium">{row.step}</td>
                <td className="p-3 text-gray-800 font-mono">{row.stack_string}</td>
                <td className="p-3 text-gray-800 font-mono">{row.input}</td>
                <td className="p-3 text-purple-600 font-bold bg-purple-50">{row.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
