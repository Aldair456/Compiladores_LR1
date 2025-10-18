"use client"

import { createContext, useContext, useState, ReactNode } from 'react'

interface GrammarRule {
  id: number
  left: string
  right: string
}

interface GrammarContextType {
  grammarRules: GrammarRule[]
  setGrammarRules: (rules: GrammarRule[]) => void
  addRule: (left: string, right: string) => void
  deleteRule: (id: number) => void
  getGrammarForAPI: () => {
    grammar: {
      productions: string[]
      start_symbol: string
    }
    operation: string
  }
  getGrammarForLR1Closure: () => {
    start_symbol: string
    productions: string[]
    options: {
      augment: boolean
      expand_alternatives: boolean
    }
  }
  // Nueva función para agregar gramática compleja
  setComplexGrammar: (grammarString: string) => void
  // LR1 Table data
  lr1TableData: any
  setLr1TableData: (data: any) => void
}

const GrammarContext = createContext<GrammarContextType | undefined>(undefined)

export function GrammarProvider({ children }: { children: ReactNode }) {
  const [grammarRules, setGrammarRules] = useState<GrammarRule[]>([
    { id: 0, left: "S'", right: "S" },
    { id: 1, left: "S", right: "C C | e | a | b | c | d" },
    { id: 2, left: "C", right: "c C | Dd" },
  ])
  const [lr1TableData, setLr1TableData] = useState<any>(null)

  const addRule = (left: string, right: string) => {
    const newRule: GrammarRule = {
      id: grammarRules.length,
      left: left.trim(),
      right: right.trim(),
    }
    setGrammarRules([...grammarRules, newRule])
  }

  const deleteRule = (id: number) => {
    setGrammarRules(grammarRules.filter((rule) => rule.id !== id))
  }

  // Nueva función para parsear gramática compleja
  const setComplexGrammar = (grammarString: string) => {
    const lines = grammarString.split('\n').filter(line => line.trim())
    const newRules: GrammarRule[] = []
    
    lines.forEach((line, index) => {
      const trimmedLine = line.trim()
      
      // Buscar diferentes patrones de flecha
      let left = '', right = ''
      
      if (trimmedLine.includes(' -> ')) {
        // Formato: S -> C C
        [left, right] = trimmedLine.split(' -> ').map(s => s.trim())
      } else if (trimmedLine.includes('->')) {
        // Formato: S->C C (sin espacios)
        [left, right] = trimmedLine.split('->').map(s => s.trim())
      } else if (trimmedLine.includes(' → ')) {
        // Formato: S → C C (flecha Unicode)
        [left, right] = trimmedLine.split(' → ').map(s => s.trim())
      } else if (trimmedLine.includes('→')) {
        // Formato: S→C C (flecha Unicode sin espacios)
        [left, right] = trimmedLine.split('→').map(s => s.trim())
      }
      
      // Validar que tenemos ambos lados
      if (left && right && left.length > 0 && right.length > 0) {
        newRules.push({
          id: index,
          left: left.trim(),
          right: right.trim()
        })
      }
    })
    
    console.log('📝 Parsed grammar rules:', newRules)
    setGrammarRules(newRules)
  }

  const getGrammarForAPI = () => {
    // Expandir gramáticas complejas con | en múltiples producciones
    const expandedProductions: string[] = []
    
    grammarRules.forEach(rule => {
      const rightSide = rule.right.trim()
      
      // Si contiene |, dividir en múltiples producciones
      if (rightSide.includes('|')) {
        const alternatives = rightSide.split('|').map(alt => alt.trim()).filter(alt => alt.length > 0)
        alternatives.forEach(alternative => {
          expandedProductions.push(`${rule.left} -> ${alternative}`)
        })
      } else {
        // Si no contiene |, usar tal como está
        expandedProductions.push(`${rule.left} -> ${rightSide}`)
      }
    })
    
    const startSymbol = grammarRules.find(rule => rule.left === "S'")?.left || grammarRules[0]?.left || "S'"
    
    console.log('🔍 Gramática expandida para API:', expandedProductions)
    
    return {
      grammar: {
        productions: expandedProductions,
        start_symbol: startSymbol
      },
      operation: "first_table"
    }
  }

  const getGrammarForLR1Closure = () => {
    // Expandir gramáticas complejas con | en múltiples producciones
    const expandedProductions: string[] = []
    
    grammarRules.forEach(rule => {
      const rightSide = rule.right.trim()
      
      // Si contiene |, dividir en múltiples producciones
      if (rightSide.includes('|')) {
        const alternatives = rightSide.split('|').map(alt => alt.trim()).filter(alt => alt.length > 0)
        alternatives.forEach(alternative => {
          expandedProductions.push(`${rule.left} -> ${alternative}`)
        })
      } else {
        // Si no contiene |, usar tal como está
        expandedProductions.push(`${rule.left} -> ${rightSide}`)
      }
    })
    
    const startSymbol = grammarRules.find(rule => rule.left === "S'")?.left || grammarRules[0]?.left || "S'"
    
    console.log('🔍 Gramática expandida para LR1 Closure API:', expandedProductions)
    
    return {
      start_symbol: startSymbol,
      productions: expandedProductions,
      options: {
        augment: true,
        expand_alternatives: true
      }
    }
  }

  const value = {
    grammarRules,
    setGrammarRules,
    addRule,
    deleteRule,
    getGrammarForAPI,
    getGrammarForLR1Closure,
    setComplexGrammar,
    lr1TableData,
    setLr1TableData
  }

  return (
    <GrammarContext.Provider value={value}>
      {children}
    </GrammarContext.Provider>
  )
}

export function useGrammar() {
  const context = useContext(GrammarContext)
  if (context === undefined) {
    throw new Error('useGrammar must be used within a GrammarProvider')
  }
  return context
}