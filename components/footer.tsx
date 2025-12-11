"use client"

import { useLanguage } from "@/contexts/language-context"
import { useTheme } from "next-themes"
import Image from "next/image"
import { useEffect, useState } from "react"

export function Footer() {
  const { t } = useLanguage()
  const { theme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div className="container mx-auto px-4 pb-8">
      <footer className="bg-primary text-primary-foreground rounded-2xl shadow-lg py-12 px-6">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              {mounted && (
                <Image
                  src={theme === "dark" ? "/django-logo-negative.png" : "/django-logo-negative.png"}
                  alt="Django Logo"
                  width={200}
                  height={60}
                  className="h-12 w-auto"
                />
              )}
            </div>
            <h3 className="text-3xl font-bold">Django Mombasa</h3>
            <p className="text-primary-foreground/80 text-pretty">{t.footer.tagline}</p>
          </div>

          <div className="border-t border-primary-foreground/20 pt-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-primary-foreground/70">
              <p>
                © {new Date().getFullYear()} Django & Python Community Mombasa. {t.footer.rights}
              </p>
              <p>{t.footer.supportedBy} ChrisDevCode</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
