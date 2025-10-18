import { Card } from "@/components/ui/card"

interface TraceStep {
  step: number
  stack: string
  input: string
  action: string
}

const traceData: TraceStep[] = [
  { step: 1, stack: "0", input: "c d d $ s3", action: "S" },
  { step: 2, stack: "0 c 3", input: "d d $", action: "s4" },
  { step: 3, stack: "0 c 3 d 4", input: "d $", action: "r3" },
  { step: 4, stack: "0 c 3 C", input: "d $", action: "8" },
  { step: 5, stack: "0 c 3 C 8", input: "d $", action: "r2" },
  { step: 6, stack: "0 C", input: "d $", action: "2" },
  { step: 7, stack: "0 C 2", input: "d $", action: "s7" },
  { step: 8, stack: "0 C 2 d 7", input: "$", action: "r3" },
  { step: 9, stack: "0 C 2 C", input: "$", action: "5" },
  { step: 10, stack: "0 C 2 C 5", input: "$", action: "r1" },
  { step: 11, stack: "0 S", input: "$", action: "1" },
  { step: 12, stack: "0 S 1", input: "$", action: "acc" },
]

export default function TraceTable() {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h2 className="text-lg font-semibold text-foreground mb-4">Trace</h2>
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
                {traceData.map((row) => (
                  <tr key={row.step} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="p-3 text-gray-700 font-medium">{row.step}</td>
                    <td className="p-3 text-gray-800 font-mono">{row.stack}</td>
                    <td className="p-3 text-gray-800 font-mono">{row.input}</td>
                    <td className="p-3 text-purple-600 font-bold bg-purple-50">{row.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="ml-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Tree</h3>
          <div className="border border-gray-300 rounded-lg p-4 bg-gray-50">
            <div className="font-mono text-sm space-y-1">
              <div className="flex flex-col items-center">
                <div className="px-3 py-1 bg-blue-600 text-white rounded font-semibold">S</div>
                <div className="h-4 w-px bg-gray-400"></div>
                <div className="flex gap-8">
                  <div className="flex flex-col items-center">
                    <div className="px-3 py-1 bg-green-600 text-white rounded font-semibold">C</div>
                    <div className="h-4 w-px bg-gray-400"></div>
                    <div className="px-3 py-1 bg-orange-500 text-white rounded">c</div>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="px-3 py-1 bg-green-600 text-white rounded font-semibold">C</div>
                    <div className="h-4 w-px bg-gray-400"></div>
                    <div className="px-3 py-1 bg-orange-500 text-white rounded">d</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}
