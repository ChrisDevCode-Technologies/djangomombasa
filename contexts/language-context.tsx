"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { translations, type Language } from "@/lib/translations"
import { Button } from "@/components/ui/button"

interface LanguageContextType {
  language: Language
  setLanguage: (lang: Language) => void
  t: typeof translations.en
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined)

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>("sw")
  const [isPromptVisible, setIsPromptVisible] = useState(false)

  useEffect(() => {
    const savedLanguage = localStorage.getItem("language") as Language | null
    if (savedLanguage && (savedLanguage === "en" || savedLanguage === "sw")) {
      setLanguageState(savedLanguage)
    } else {
      localStorage.setItem("language", "sw")
      setIsPromptVisible(true)
    }
  }, [])

  const setLanguage = (lang: Language) => {
    setLanguageState(lang)
    localStorage.setItem("language", lang)
  }

  const t = translations[language]

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
      {isPromptVisible && (
        <div className="fixed inset-0 z-[999] flex items-center justify-center bg-black/70 px-4">
          <div className="w-full max-w-md rounded-2xl border border-border/60 bg-card/95 p-8 text-center shadow-2xl backdrop-blur">
            <h2 className="text-2xl font-semibold text-foreground">Karibu Django Mombasa</h2>
            <p className="mt-3 text-sm text-foreground/80">
              Tungependa kuendelea katika Kiswahili au ungependa kubadilisha hadi Kiingereza?
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center">
              <Button
                size="lg"
                className="sm:flex-1"
                onClick={() => {
                  setLanguage("sw")
                  setIsPromptVisible(false)
                }}
              >
                Endelea kwa Kiswahili
              </Button>
              <Button
                size="lg"
                variant="secondary"
                className="sm:flex-1"
                onClick={() => {
                  setLanguage("en")
                  setIsPromptVisible(false)
                }}
              >
                Switch to English
              </Button>
            </div>
          </div>
        </div>
      )}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (context === undefined) {
    throw new Error("useLanguage must be used within a LanguageProvider")
  }
  return context
}
