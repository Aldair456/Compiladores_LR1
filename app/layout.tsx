import type { Metadata } from 'next'
import './globals.css'
import { GrammarProvider } from '@/contexts/grammar-context'

export const metadata: Metadata = {
  title: 'LR Parser Visualizer',
  description: 'Interactive compiler theory educational tool',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body>
        <GrammarProvider>
          {children}
        </GrammarProvider>
      </body>
    </html>
  )
}
