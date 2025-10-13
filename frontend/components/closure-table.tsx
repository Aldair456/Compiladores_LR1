import { Card } from "@/components/ui/card"

interface ClosureRow {
  goto: string
  kernel: string
  state: string
  closure: string
}

const closureData: ClosureRow[] = [
  {
    goto: "",
    kernel: "[{S' → .S, $}]",
    state: "0",
    closure: "[{S' → .S, $}; {S → .C c, $}; {C → .c C, c/d}; {C → .d, c/d}]",
  },
  {
    goto: "goto(0, S)",
    kernel: "[{S' → S., $}]",
    state: "1",
    closure: "[{S' → S., $}]",
  },
  {
    goto: "goto(0, C)",
    kernel: "[{S → C.c, $}]",
    state: "2",
    closure: "[{S → C.c, $}]; [{C → .c C, $}]; [{C → .d, $}]",
  },
  {
    goto: "goto(0, c)",
    kernel: "[{C → c.C, c/d}]",
    state: "3",
    closure: "[{C → c.C, c/d}]; [{C → .c C, c/d}]; [{C → .d, c/d}]",
  },
  {
    goto: "goto(0, d)",
    kernel: "[{C → d., c/d}]",
    state: "4",
    closure: "[{C → d., c/d}]",
  },
  {
    goto: "goto(2, c)",
    kernel: "[{S → c C., $}]",
    state: "5",
    closure: "[{S → c C., $}]",
  },
  {
    goto: "goto(2, C)",
    kernel: "[{C → c.C, $}]",
    state: "6",
    closure: "[{C → c.C, $}]; [{C → .c C, $}]; [{C → .d, $}]",
  },
  {
    goto: "goto(2, d)",
    kernel: "[{C → d., $}]",
    state: "7",
    closure: "[{C → d., $}]",
  },
  {
    goto: "goto(3, C)",
    kernel: "[{C → c C., c/d}]",
    state: "8",
    closure: "[{C → c C., c/d}]",
  },
  {
    goto: "goto(3, c)",
    kernel: "[{C → c.c, c/d}]",
    state: "3",
    closure: "",
  },
  {
    goto: "goto(3, d)",
    kernel: "[{C → d., c/d}]",
    state: "4",
    closure: "",
  },
  {
    goto: "goto(6, C)",
    kernel: "[{C → c C., $}]",
    state: "9",
    closure: "[{C → c C., $}]",
  },
  {
    goto: "goto(6, c)",
    kernel: "[{C → c.C, $}]",
    state: "6",
    closure: "",
  },
  {
    goto: "goto(6, d)",
    kernel: "[{C → d., $}]",
    state: "7",
    closure: "",
  },
]

export default function ClosureTable() {
  return (
    <Card className="p-4 overflow-auto">
      <h2 className="text-lg font-semibold mb-4 text-foreground">LR(1) closure table</h2>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm font-mono">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Goto</th>
              <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Kernel</th>
              <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">State</th>
              <th className="text-left p-3 font-semibold text-gray-900 bg-gray-100">Closure</th>
            </tr>
          </thead>
          <tbody>
            {closureData.map((row, idx) => (
              <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="p-3 text-gray-700">{row.goto}</td>
                <td className="p-3 text-blue-700 font-medium">{row.kernel}</td>
                <td className="p-3 text-center text-green-600 font-bold bg-green-50">{row.state}</td>
                <td className="p-3 text-gray-800">{row.closure}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
