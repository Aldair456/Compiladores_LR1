"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useGrammar } from "@/contexts/grammar-context"
import { useState } from "react"

export default function GrammarDisplay() {
  const { grammarRules, setComplexGrammar } = useGrammar()
  const [grammarText, setGrammarText] = useState(`S' -> S
S -> C C | e | a | b | c | d
C -> c C | Dd`)

  const handleLoadGrammar = () => {
    if (grammarText.trim()) {
      setComplexGrammar(grammarText.trim())
    }
  }

  const handleLoadExample1 = () => {
    const example = `S' -> S
S -> C C | e | a | b | c | d
C -> c C | Dd`
    setGrammarText(example)
  }

  const handleLoadExample2 = () => {
    const example = `S' -> S
S -> C C
C -> c C
C -> d
d -> A`
    setGrammarText(example)
  }

  const handleClear = () => {
    setGrammarText("")
  }
  // </CHANGE>

  return (
    <Card className="p-4">
      <h2 className="text-lg font-semibold mb-4 text-gray-900">LR(1) Grammar</h2>

      {/* Editor de gramática principal */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Enter Grammar Rules (one per line):
        </label>
        <textarea
          value={grammarText}
          onChange={(e) => setGrammarText(e.target.value)}
          placeholder="S' -> S&#10;S -> C C | e | a | b | c | d&#10;C -> c C | Dd&#10;&#10;Or:&#10;S' -> S&#10;S -> C C&#10;C -> c C&#10;C -> d&#10;d -> A"
          className="w-full p-4 border border-gray-300 rounded-lg font-mono text-sm h-40 resize-y focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Botones de acción */}
      <div className="flex flex-wrap gap-2 mb-4">
        <Button 
          onClick={handleLoadGrammar} 
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          Load Grammar
        </Button>
        <Button 
          onClick={handleLoadExample1} 
          variant="outline"
          size="sm"
        >
          Example 1 (with |)
        </Button>
        <Button 
          onClick={handleLoadExample2} 
          variant="outline"
          size="sm"
        >
          Example 2 (separate rules)
        </Button>
        <Button 
          onClick={handleClear} 
          variant="outline"
          size="sm"
          className="text-red-600 hover:text-red-700"
        >
          Clear
        </Button>
      </div>

      {/* Vista previa de reglas cargadas */}
      <div className="border-t pt-4">
        <h3 className="text-md font-semibold mb-3 text-gray-900">Current Grammar Rules:</h3>
        <div className="space-y-1 font-mono text-sm bg-gray-50 p-3 rounded">
          {grammarRules.length > 0 ? (
            grammarRules.map((rule, index) => (
              <div key={rule.id} className="flex items-center gap-2">
                <span className="text-blue-600 font-medium">({index})</span>
                <span className="text-gray-900 font-semibold">{rule.left}</span>
                <span className="text-gray-500">→</span>
                <span className="text-gray-700">{rule.right}</span>
              </div>
            ))
          ) : (
            <div className="text-gray-500 italic">No grammar rules loaded</div>
          )}
        </div>
      </div>
    </Card>
  )
}
