import { Card } from "@/components/ui/card"

interface LRTableRow {
  state: string
  c: string
  d: string
  dollar: string
  S: string
  Sprime: string
  C: string
}

const lrTableData: LRTableRow[] = [
  { state: "0", c: "s3", d: "s4", dollar: "", S: "1", Sprime: "", C: "2" },
  { state: "1", c: "", d: "", dollar: "acc", S: "", Sprime: "", C: "" },
  { state: "2", c: "s6", d: "s7", dollar: "", S: "", Sprime: "", C: "5" },
  { state: "3", c: "s3", d: "s4", dollar: "", S: "", Sprime: "", C: "8" },
  { state: "4", c: "r3", d: "r3", dollar: "", S: "", Sprime: "", C: "" },
  { state: "5", c: "", d: "", dollar: "r1", S: "", Sprime: "", C: "" },
  { state: "6", c: "s6", d: "s7", dollar: "", S: "", Sprime: "", C: "9" },
  { state: "7", c: "", d: "", dollar: "r3", S: "", Sprime: "", C: "" },
  { state: "8", c: "r2", d: "r2", dollar: "", S: "", Sprime: "", C: "" },
  { state: "9", c: "", d: "", dollar: "r2", S: "", Sprime: "", C: "" },
]

export default function LRParsingTable() {
  return (
    <Card className="p-4">
      <h2 className="text-lg font-semibold mb-4 text-foreground">LR table</h2>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-xs font-mono">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="p-3 font-semibold text-gray-900 bg-gray-100">State</th>
              <th colSpan={3} className="p-3 text-center font-semibold text-gray-900 bg-blue-100">
                ACTION
              </th>
              <th colSpan={3} className="p-3 text-center font-semibold text-gray-900 bg-green-100">
                GOTO
              </th>
            </tr>
            <tr className="border-b border-gray-200">
              <th className="p-3 font-semibold text-gray-900 bg-gray-100"></th>
              <th className="p-3 text-center font-semibold text-gray-900 bg-blue-50">c</th>
              <th className="p-3 text-center font-semibold text-gray-900 bg-blue-50">d</th>
              <th className="p-3 text-center font-semibold text-gray-900 bg-blue-50">$</th>
              <th className="p-3 text-center font-semibold text-gray-900 bg-green-50">S&apos;</th>
              <th className="p-3 text-center font-semibold text-gray-900 bg-green-50">S</th>
              <th className="p-3 text-center font-semibold text-gray-900 bg-green-50">C</th>
            </tr>
          </thead>
          <tbody>
            {lrTableData.map((row) => (
              <tr key={row.state} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="p-3 text-center text-green-600 font-bold bg-green-50">{row.state}</td>
                <td className="p-3 text-center text-gray-800">{row.c}</td>
                <td className="p-3 text-center text-gray-800">{row.d}</td>
                <td className="p-3 text-center text-purple-600 font-semibold">{row.dollar}</td>
                <td className="p-3 text-center text-gray-800">{row.Sprime}</td>
                <td className="p-3 text-center text-gray-800">{row.S}</td>
                <td className="p-3 text-center text-gray-800">{row.C}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
