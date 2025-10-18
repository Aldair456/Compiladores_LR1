import GrammarDisplay from "@/components/grammar-display"
import GrammarClosureVisualizer from "@/components/grammar_canonico"
import FirstTable from "@/components/first-table"
import LRParsingTable from "@/components/lr-parsing-table"
import TraceTable from "@/components/trace-table"

export default function LRParserPage() {
  return (
    <div className="min-h-screen p-6 bg-background">
      <div className="max-w-[1600px] mx-auto space-y-6">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">LR(1) Parser Visualizer</h1>
          <p className="text-muted-foreground mt-2">Interactive compiler theory educational tool</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column - Grammar and Tables */}
          <div className="space-y-6">
            <GrammarDisplay />
            <FirstTable />
            <LRParsingTable />
          </div>

          {/* Middle column - Autómata Canónico LR(1) */}
          <div className="lg:col-span-2">
            <GrammarClosureVisualizer />
          </div>
        </div>

        <div className="grid grid-cols-1">
          <TraceTable />
        </div>
        {/* </CHANGE> */}
      </div>
    </div>
  )
}
