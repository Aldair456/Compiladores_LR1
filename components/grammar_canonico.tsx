"use client"

import type React from "react"

import { useEffect, useRef, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useGrammar } from "@/contexts/grammar-context"

interface StateData {
  id: number
  items: string[] // LR(1) items as strings like "[E -> E • + T, $]"
  transitions: Record<string, number>
}

interface ClosureTable {
  states: StateData[]
}

interface GrammarInfo {
  augmented: boolean
  start_symbol: string
  original_start_symbol: string
  epsilon: string
  end_marker: string
  original_productions: string[]
  expanded_productions: string[]
}

interface GrammarData {
  success?: boolean
  grammar: GrammarInfo
  closure_table: ClosureTable
}

interface ApiResponse {
  success: boolean
  grammar: GrammarInfo
  closure_table: ClosureTable
}

interface Transition {
  from: number
  to: number
  symbol: string
}

export default function GrammarClosureVisualizer() {
  const { getGrammarForLR1Closure } = useGrammar()
  const [grammarData, setGrammarData] = useState<GrammarData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [states, setStates] = useState<StateData[]>([])
  const [transitions, setTransitions] = useState<Transition[]>([])
  const [scale, setScale] = useState(1)
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [selectedState, setSelectedState] = useState<StateData | null>(null)
  const [showSidePanel, setShowSidePanel] = useState(false)

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const grammarData = getGrammarForLR1Closure()
      
      // Console.log para ver qué se envía
      console.log('📤 Enviando datos al LR1 Closure endpoint:', grammarData)
      console.log('📤 JSON stringify:', JSON.stringify(grammarData, null, 2))
      
      const response = await fetch('/api/lr1-closure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(grammarData)
      })
      
      console.log('📡 Response status:', response.status)
      console.log('📡 Response ok:', response.ok)
      console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()))
      
      if (!response.ok) {
        const errorText = await response.text()
        console.log('❌ Error response text:', errorText)
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const result: ApiResponse = await response.json()
      
      // Console.log para ver la respuesta
      console.log('📥 Respuesta del LR1 Closure endpoint:', result)
      console.log('📊 Success status:', result.success)
      console.log('📋 Grammar data:', result.grammar)
      console.log('🗂️ Closure table:', result.closure_table)
      
      if (result.success) {
        setGrammarData(result)
      } else {
        setError('Failed to load LR1 closure data')
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

  const handleStateClick = (stateId: number) => {
    const state = states.find(s => s.id === stateId)
    if (state) {
      setSelectedState(state)
      setShowSidePanel(true)
    }
  }

  const closeSidePanel = () => {
    setShowSidePanel(false)
    setSelectedState(null)
  }

  const handleDebugTest = () => {
    const testData = {
      "start_symbol": "S'",
      "productions": [
        "S' -> S",
        "S -> C C",
        "S -> e",
        "S -> a",
        "S -> b",
        "S -> c",
        "S -> d",
        "C -> c C",
        "C -> d"
      ],
      "options": {
        "augment": true,
        "expand_alternatives": true
      }
    }
    
    console.log('🧪 Test data (Postman working):', testData)
    console.log('🧪 Our data:', getGrammarForLR1Closure())
    console.log('🧪 Are they equal?', JSON.stringify(testData) === JSON.stringify(getGrammarForLR1Closure()))
  }

  const processClosureTable = () => {
    if (!grammarData) {
      console.log('❌ No grammar data available for processing')
      return
    }
    
    const statesList = grammarData.closure_table.states
    const transitionsList: Transition[] = []

    // Extract all transitions from states
    statesList.forEach((state) => {
      Object.entries(state.transitions).forEach(([symbol, toStateId]) => {
        transitionsList.push({
          from: state.id,
          to: toStateId,
          symbol,
        })
      })
    })

    setStates(statesList)
    setTransitions(transitionsList)
    
    console.log(`✅ Processed ${statesList.length} states and ${transitionsList.length} transitions`)
  }

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    processClosureTable()
  }, [grammarData])

  // Draw the graph
  useEffect(() => {
    if (!canvasRef.current || states.length === 0) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas size
    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Apply transformations
    ctx.save()
    ctx.translate(offset.x, offset.y)
    ctx.scale(scale, scale)

    // Calculate positions (improved grid layout with more spacing)
    const positions = new Map<number, { x: number; y: number }>()
    const cols = Math.ceil(Math.sqrt(states.length * 1.8)) // More columns for better spacing
    const cellWidth = 350  // Increased width
    const cellHeight = 280 // Increased height
    const startX = 200     // More margin from left
    const startY = 150     // More margin from top

    states.forEach((state) => {
      const col = state.id % cols
      const row = Math.floor(state.id / cols)
      positions.set(state.id, {
        x: startX + col * cellWidth,
        y: startY + row * cellHeight,
      })
    })

    // Draw transitions with improved styling
    ctx.strokeStyle = "#666"
    ctx.fillStyle = "#666"
    ctx.lineWidth = 2.5  // Slightly thicker lines

    transitions.forEach((trans) => {
      const from = positions.get(trans.from)
      const to = positions.get(trans.to)

      if (from && to) {
        // Highlight transitions from selected state
        if (selectedState && trans.from === selectedState.id) {
          ctx.strokeStyle = "#3b82f6"
          ctx.fillStyle = "#3b82f6"
          ctx.lineWidth = 4  // Thicker highlighted lines
        } else {
          ctx.strokeStyle = "#666"
          ctx.fillStyle = "#666"
          ctx.lineWidth = 2.5
        }

        // Draw arrow with better spacing
        const angle = Math.atan2(to.y - from.y, to.x - from.x)
        const startX = from.x + 120 * Math.cos(angle) // Increased start distance
        const startY = from.y + 80 * Math.sin(angle)  // Increased start distance
        const endX = to.x - 120 * Math.cos(angle)     // Increased end distance
        const endY = to.y - 80 * Math.sin(angle)      // Increased end distance

        // Self-loop
        if (trans.from === trans.to) {
          ctx.beginPath()
          ctx.arc(from.x, from.y - 90, 35, 0, Math.PI * 2)
          ctx.stroke()

          ctx.fillStyle = "#000"
          ctx.font = "bold 14px monospace"
          ctx.fillText(trans.symbol, from.x - 10, from.y - 135)
          ctx.fillStyle = "#666"
        } else {
          ctx.beginPath()
          ctx.moveTo(startX, startY)
          ctx.lineTo(endX, endY)
          ctx.stroke()

          // Arrow head with better size
          const headLength = 15  // Increased arrow head size
          ctx.beginPath()
          ctx.moveTo(endX, endY)
          ctx.lineTo(
            endX - headLength * Math.cos(angle - Math.PI / 6),
            endY - headLength * Math.sin(angle - Math.PI / 6),
          )
          ctx.lineTo(
            endX - headLength * Math.cos(angle + Math.PI / 6),
            endY - headLength * Math.sin(angle + Math.PI / 6),
          )
          ctx.closePath()
          ctx.fill()

          // Label with better background
          const midX = (startX + endX) / 2
          const midY = (startY + endY) / 2
          ctx.fillStyle = "#fff"
          ctx.fillRect(midX - 3, midY - 14, ctx.measureText(trans.symbol).width + 12, 20)  // Larger background
          ctx.fillStyle = "#000"
          ctx.font = "bold 16px monospace"  // Slightly larger font
          ctx.fillText(trans.symbol, midX + 3, midY + 3)
          ctx.fillStyle = "#666"
        }
      }
    })

    // Draw states
    states.forEach((state) => {
      const pos = positions.get(state.id)
      if (!pos) return

      // Highlight selected state
      if (selectedState && state.id === selectedState.id) {
        ctx.fillStyle = "#dbeafe"
        ctx.strokeStyle = "#3b82f6"
        ctx.lineWidth = 3
      } else if (isAcceptingState(state)) {
        ctx.fillStyle = "#dcfce7"
        ctx.strokeStyle = "#16a34a"
        ctx.lineWidth = 2.5
      } else {
        ctx.fillStyle = "#fff"
        ctx.strokeStyle = "#333"
        ctx.lineWidth = 2.5
      }

      const boxWidth = 300  // Increased width for better spacing
      const boxHeight = Math.max(100, state.items.length * 24 + 70) // Increased height and spacing

      ctx.fillRect(pos.x - boxWidth / 2, pos.y - boxHeight / 2, boxWidth, boxHeight)
      ctx.strokeRect(pos.x - boxWidth / 2, pos.y - boxHeight / 2, boxWidth, boxHeight)

      // Draw state number with background
      ctx.fillStyle = selectedState && state.id === selectedState.id ? "#3b82f6" : "#f0f0f0"
      ctx.fillRect(pos.x - boxWidth / 2, pos.y - boxHeight / 2, boxWidth, 28)
      ctx.strokeRect(pos.x - boxWidth / 2, pos.y - boxHeight / 2, boxWidth, 28)

      ctx.fillStyle = selectedState && state.id === selectedState.id ? "#fff" : "#000"
      ctx.font = "bold 18px sans-serif"
      ctx.textAlign = "center"
      ctx.fillText(state.id.toString(), pos.x, pos.y - boxHeight / 2 + 20)

      // Draw items (only show first few if not selected)
      ctx.font = "12px monospace"
      ctx.textAlign = "left"
      const itemsToShow = selectedState && state.id === selectedState.id ? state.items : state.items.slice(0, 3)
      
      itemsToShow.forEach((itemStr, idx) => {
        const y = pos.y - boxHeight / 2 + 60 + idx * 24  // Increased spacing between items
        const maxWidth = boxWidth - 20  // More padding

        // Clean up the item string (remove brackets)
        let displayStr = itemStr.replace(/^\[|\]$/g, "")

        // Truncate if too long
        if (ctx.measureText(displayStr).width > maxWidth) {
          while (ctx.measureText(displayStr + "...").width > maxWidth && displayStr.length > 0) {
            displayStr = displayStr.slice(0, -1)
          }
          displayStr += "..."
        }

        ctx.fillStyle = selectedState && state.id === selectedState.id ? "#1e40af" : "#000"
        ctx.fillText(displayStr, pos.x - boxWidth / 2 + 15, y)  // Increased padding
      })

      // Show "..." if there are more items
      if (!selectedState || state.id !== selectedState.id) {
        const remainingItems = state.items.length - 3
        if (remainingItems > 0) {
          ctx.fillStyle = "#666"
          ctx.font = "12px monospace"
          ctx.textAlign = "left"
          ctx.fillText(`... and ${remainingItems} more`, pos.x - boxWidth / 2 + 15, pos.y - boxHeight / 2 + 60 + 3 * 24)
        }
      }
    })

    ctx.restore()
  }, [states, transitions, scale, offset, selectedState])

  // Mouse handlers for pan and zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    setScale((prev) => Math.max(0.1, Math.min(3, prev * delta)))
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y })
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setOffset({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      })
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  const handleCanvasClick = (e: React.MouseEvent) => {
    if (isDragging) return

    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = (e.clientX - rect.left - offset.x) / scale
    const y = (e.clientY - rect.top - offset.y) / scale

    // Check if click is on a state with updated dimensions
    const cols = Math.ceil(Math.sqrt(states.length * 1.8))
    const cellWidth = 350
    const cellHeight = 280
    const startX = 200
    const startY = 150

    states.forEach((state) => {
      const col = state.id % cols
      const row = Math.floor(state.id / cols)
      const stateX = startX + col * cellWidth
      const stateY = startY + row * cellHeight
      const boxWidth = 300
      const boxHeight = Math.max(100, state.items.length * 24 + 70)

      if (x >= stateX - boxWidth / 2 && x <= stateX + boxWidth / 2 &&
          y >= stateY - boxHeight / 2 && y <= stateY + boxHeight / 2) {
        handleStateClick(state.id)
      }
    })
  }

  const resetView = () => {
    setScale(1)
    setOffset({ x: 0, y: 0 })
  }

  // Helper function to check if a state is accepting
  const isAcceptingState = (state: StateData) => {
    return state.items.some(item => item.includes('S\' -> S •') || item.includes('S -> A A •'))
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">LR(1) Canonical Automaton</h2>
            <p className="text-sm text-muted-foreground">Loading...</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleRefresh} variant="outline" size="sm">
              Refresh
            </Button>
            <Button onClick={handleDebugTest} variant="outline" size="sm" className="bg-yellow-100">
              Debug Test
            </Button>
          </div>
        </div>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading automaton...</span>
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">LR(1) Canonical Automaton</h2>
            <p className="text-sm text-muted-foreground">Error loading data</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleRefresh} variant="outline" size="sm">
              Retry
            </Button>
            <Button onClick={handleDebugTest} variant="outline" size="sm" className="bg-yellow-100">
              Debug Test
            </Button>
          </div>
        </div>
        <div className="text-center py-8">
          <div className="text-red-600 mb-2">⚠️ Error loading automaton</div>
          <div className="text-gray-600 text-sm">{error}</div>
        </div>
      </Card>
    )
  }

  if (!grammarData) {
    return (
      <Card className="p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">LR(1) Canonical Automaton</h2>
            <p className="text-sm text-muted-foreground">No data available</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleRefresh} variant="outline" size="sm">
              Refresh
            </Button>
            <Button onClick={handleDebugTest} variant="outline" size="sm" className="bg-yellow-100">
              Debug Test
            </Button>
          </div>
        </div>
        <div className="text-center py-8">
          <div className="text-gray-600">No grammar data available</div>
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">
            LR(1) Canonical Automaton - {grammarData.grammar.original_start_symbol}
          </h2>
          <p className="text-sm text-muted-foreground">
            {states.length} states, {transitions.length} transitions • Click on nodes to see details
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={resetView} variant="outline" size="sm">
            Reset View
          </Button>
          <Button onClick={handleRefresh} variant="outline" size="sm">
            Refresh
          </Button>
        </div>
      </div>

      <div className="relative">
        {/* Canvas */}
        <div className="relative h-[700px] overflow-hidden rounded-lg border bg-muted/20">
          <canvas
            ref={canvasRef}
            className="h-full w-full cursor-pointer"
            onWheel={handleWheel}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onClick={handleCanvasClick}
          />

          <div className="absolute bottom-4 left-4 rounded bg-background/90 px-3 py-2 text-xs text-muted-foreground">
            <p>Scroll to zoom • Drag to pan • Click nodes for details</p>
            <p>Zoom: {(scale * 100).toFixed(0)}%</p>
          </div>
        </div>

        {/* Side Panel */}
        {showSidePanel && selectedState && (
          <div className="absolute top-0 right-0 w-96 h-full bg-white border-l shadow-lg overflow-y-auto">
            <div className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">
                  State {selectedState.id}
                  {isAcceptingState(selectedState) && (
                    <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      Accepting
                    </span>
                  )}
                </h3>
                <Button onClick={closeSidePanel} variant="outline" size="sm">
                  ✕
                </Button>
              </div>

              {/* LR(1) Items */}
              <div className="mb-6">
                <h4 className="font-semibold mb-3 text-gray-900">LR(1) Items:</h4>
                <div className="space-y-2">
                  {selectedState.items.map((item, idx) => (
                    <div key={idx} className="p-3 bg-gray-50 rounded font-mono text-sm">
                      {item.replace(/^\[|\]$/g, '')}
                    </div>
                  ))}
                </div>
              </div>

              {/* Transitions */}
              <div className="mb-6">
                <h4 className="font-semibold mb-3 text-gray-900">Outgoing Transitions:</h4>
                <div className="space-y-2">
                  {Object.entries(selectedState.transitions).length > 0 ? (
                    Object.entries(selectedState.transitions).map(([symbol, toStateId]) => (
                      <div key={`${symbol}-${toStateId}`} className="flex items-center gap-3 p-3 bg-blue-50 rounded">
                        <span className="font-semibold text-blue-800">{symbol}</span>
                        <span className="text-gray-400">→</span>
                        <span className="px-2 py-1 bg-blue-200 text-blue-900 rounded text-sm font-medium">
                          State {toStateId}
                        </span>
                      </div>
                    ))
                  ) : (
                    <div className="p-3 bg-gray-50 rounded text-gray-500 text-sm">
                      No outgoing transitions (terminal state)
                    </div>
                  )}
                </div>
              </div>

              {/* Incoming Transitions */}
              <div>
                <h4 className="font-semibold mb-3 text-gray-900">Incoming Transitions:</h4>
                <div className="space-y-2">
                  {transitions.filter(t => t.to === selectedState.id).length > 0 ? (
                    transitions.filter(t => t.to === selectedState.id).map((trans, idx) => (
                      <div key={idx} className="flex items-center gap-3 p-3 bg-green-50 rounded">
                        <span className="px-2 py-1 bg-green-200 text-green-900 rounded text-sm font-medium">
                          State {trans.from}
                        </span>
                        <span className="text-gray-400">→</span>
                        <span className="font-semibold text-green-800">{trans.symbol}</span>
                      </div>
                    ))
                  ) : (
                    <div className="p-3 bg-gray-50 rounded text-gray-500 text-sm">
                      No incoming transitions (initial state)
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Grammar Productions */}
      <div className="mt-4 rounded-lg border bg-muted/30 p-4">
        <h3 className="mb-2 font-semibold">Grammar Productions:</h3>
        <div className="space-y-1 text-sm font-mono">
          {grammarData.grammar.expanded_productions.map((prod, idx) => (
            <div key={idx} className="text-muted-foreground">
              {prod}
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}
