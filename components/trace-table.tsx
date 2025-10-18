"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useGrammar } from "@/contexts/grammar-context"
import { useState, useEffect } from "react"

interface TraceStep {
  step: number
  state: number
  stack: number[]
  input_position: number
  current_token: string
  action: string
  description: string
}

interface TraceResponse {
  success: boolean
  accepted: boolean
  operation: string
  input_string: string
  trace_steps: TraceStep[]
  summary: {
    total_steps: number
    final_state: number
    stack_depth: number
    tokens_processed: number
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

export default function TraceTable() {
  const { lr1TableData } = useGrammar()
  const [inputString, setInputString] = useState("")
  const [traceData, setTraceData] = useState<TraceStep[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [accepted, setAccepted] = useState<boolean | null>(null)

  // Función para hacer el trace
  const performTrace = async () => {
    if (!inputString.trim()) {
      setError("Please enter an input string")
      return
    }
    
    if (!lr1TableData) {
      setError("LR1 table data is not loaded. Please wait for it to load or refresh the page.")
      return
    }
    
    // Validar que tenemos los datos necesarios
    if (!lr1TableData.action_table || !lr1TableData.goto_table) {
      setError("LR1 table data is incomplete. Missing action_table or goto_table.")
      return
    }

    try {
      setLoading(true)
      setError(null)

      const requestData = {
        lr1_table: lr1TableData,
        input_string: inputString.trim(),
        options: {
          end_marker: "$",
          accept_token: "acc"
        }
      }

      console.log('📤 Sending trace request:', requestData)
      console.log('📤 Request JSON:', JSON.stringify(requestData, null, 2))
      console.log('📤 LR1 Table data from context:', lr1TableData)
      console.log('📤 Input string:', inputString.trim())
      console.log("TRACE INPUT:", inputString.trim())
      console.log('📤 Action table keys:', Object.keys(lr1TableData.action_table || {}))
      console.log('📤 Goto table keys:', Object.keys(lr1TableData.goto_table || {}))

      const response = await fetch('https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/lr1-trace', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      })

      const result: TraceResponse = await response.json()

      console.log('📥 Trace response:', result)
      console.log('📥 Response status:', response.status)
      console.log('📥 Response ok:', response.ok)

      if (result.success) {
        setTraceData(result.trace_steps)
        setSummary(result.summary)
        setAccepted(result.accepted)
      } else {
        // Mostrar más detalles del error
        const errorMessage = result.error || 'Failed to perform trace'
        console.error('❌ Trace failed:', errorMessage)
        setError(`Trace failed: ${errorMessage}`)
      }
    } catch (err) {
      console.error('❌ Error in performTrace:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }


  // Función para formatear el stack como string
  const formatStack = (stack: number[]): string => {
    return stack.join(' ')
  }

  // Función para formatear la entrada restante
  const formatInput = (inputString: string, position: number): string => {
    const tokens = inputString.split(' ')
    return tokens.slice(position).join(' ')
  }

  return (
    <Card className="p-6">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">LR(1) Parsing Trace</h2>
        
        {/* Input section */}
        <div className="flex gap-4 items-end mb-4">
          <div className="flex-1">
            <Label htmlFor="input-string" className="text-sm font-medium text-gray-700">
              Input String (separate tokens with spaces)
            </Label>
            <Input
              id="input-string"
              type="text"
              placeholder="e.g., a b c"
              value={inputString}
              onChange={(e) => setInputString(e.target.value)}
              className="mt-1"
            />
          </div>
          <Button
            onClick={performTrace}
            disabled={loading || !inputString.trim() || !lr1TableData}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {loading ? "Tracing..." : "Trace"}
          </Button>
        </div>

        {/* Status de datos LR1 */}
        <div className="mb-4">
          {lr1TableData ? (
            <div className="text-sm text-green-600 bg-green-50 p-2 rounded border border-green-200">
              ✅ LR1 Table loaded successfully
            </div>
          ) : (
            <div className="text-sm text-yellow-600 bg-yellow-50 p-2 rounded border border-yellow-200">
              ⏳ Loading LR1 Table data...
            </div>
          )}
        </div>

        {/* Status indicators */}
        {accepted !== null && (
          <div className={`mb-4 p-3 rounded border ${
            accepted 
              ? 'bg-green-50 border-green-200 text-green-700' 
              : 'bg-red-50 border-red-200 text-red-700'
          }`}>
            <div className="flex items-center">
              <span className="mr-2">{accepted ? '✅' : '❌'}</span>
              <span className="font-semibold">
                {accepted ? 'String ACCEPTED' : 'String REJECTED'}
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded text-red-700">
            Error: {error}
          </div>
        )}

        {/* Summary */}
        {summary && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
            <div className="text-sm text-blue-700">
              <div className="flex gap-4">
                <span>Steps: {summary.total_states}</span>
                <span>Final State: {summary.final_state}</span>
                <span>Stack Depth: {summary.stack_depth}</span>
                <span>Tokens: {summary.tokens_processed}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Trace table */}
      {traceData.length > 0 && (
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-md font-semibold text-gray-900 mb-3">Trace Steps</h3>
            <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
              <table className="w-full border-collapse text-sm font-mono">
                <thead className="sticky top-0 bg-white">
                  <tr className="border-b-2 border-gray-300">
                    <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Step</th>
                    <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">State</th>
                    <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Stack</th>
                    <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Input</th>
                    <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Token</th>
                    <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Action</th>
                    <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Description</th>
                  </tr>
                </thead>
                <tbody>
                  {traceData.map((row) => (
                    <tr key={row.step} className="border-b border-gray-200 hover:bg-gray-50">
                      <td className="p-3 text-gray-700 font-medium">{row.step}</td>
                      <td className="p-3 text-blue-600 font-bold">{row.state}</td>
                      <td className="p-3 text-gray-800 font-mono">{formatStack(row.stack)}</td>
                      <td className="p-3 text-gray-800 font-mono">{formatInput(inputString, row.input_position)}</td>
                      <td className="p-3 text-green-600 font-semibold">{row.current_token}</td>
                      <td className="p-3 text-purple-600 font-bold bg-purple-50">{row.action}</td>
                      <td className="p-3 text-gray-600 text-xs">{row.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Placeholder when no trace data */}
      {traceData.length === 0 && !loading && (
        <div className="text-center py-8 text-gray-500">
          <div className="text-gray-400 mb-2">🔍</div>
          <div>Enter an input string and click Trace to see the parsing steps.</div>
        </div>
      )}
    </Card>
  )
}
