"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useState } from "react"

export default function ParserControls() {
  const [tokens, setTokens] = useState("c d d")
  const [maxSteps, setMaxSteps] = useState("100")

  const handleParse = () => {
    console.log("[v0] Parsing tokens:", tokens, "with max steps:", maxSteps)
    // Parsing logic would go here
  }

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold mb-4 text-foreground">Parser Input</h2>
      <div className="space-y-4">
        <div>
          <Label htmlFor="tokens" className="text-sm font-medium text-foreground">
            Input (tokens):
          </Label>
          <Input
            id="tokens"
            value={tokens}
            onChange={(e) => setTokens(e.target.value)}
            className="mt-1 font-mono"
            placeholder="Enter tokens..."
          />
        </div>
        <div>
          <Label htmlFor="maxSteps" className="text-sm font-medium text-foreground">
            Maximum number of steps:
          </Label>
          <Input
            id="maxSteps"
            type="number"
            value={maxSteps}
            onChange={(e) => setMaxSteps(e.target.value)}
            className="mt-1 font-mono"
          />
        </div>
        <Button onClick={handleParse} className="w-full">
          PARSE
        </Button>
      </div>
    </Card>
  )
}
