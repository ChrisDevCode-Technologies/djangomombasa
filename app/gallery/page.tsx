"use client"

import { useLanguage } from "@/contexts/language-context"
import { PageTransition } from "@/components/page-transition"
import { ScrollReveal } from "@/components/scroll-reveal"
import { Camera } from "lucide-react"

export default function GalleryPage() {
  const { t } = useLanguage()

  return (
    <PageTransition>
      <div className="min-h-screen pt-32 pb-20 px-4">
        <div className="max-w-7xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-16">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary mb-6">
                <Camera className="h-4 w-4" />
                <span className="text-sm font-medium">{t.gallery.title}</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 text-balance">{t.gallery.title}</h1>
              <p className="text-xl text-muted-foreground max-w-3xl mx-auto text-pretty">{t.gallery.subtitle}</p>
              <p className="text-lg text-muted-foreground mt-4 max-w-2xl mx-auto">{t.gallery.placeholder}</p>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </PageTransition>
  )
}
