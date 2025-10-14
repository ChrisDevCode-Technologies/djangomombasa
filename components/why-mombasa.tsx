"use client"

import { Waves, Building2, Network } from "lucide-react"
import { ScrollReveal } from "@/components/scroll-reveal"
import { useLanguage } from "@/contexts/language-context"

export function WhyMombasa() {
  const { t } = useLanguage()
  const icons = [Waves, Building2, Network] as const

  return (
    <section className="py-20 md:py-32 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto space-y-12">
          <ScrollReveal>
            <div className="text-center space-y-4">
              <h2 className="text-4xl md:text-5xl font-bold text-balance">{t.whyMombasa.title}</h2>
              <p className="text-xl text-muted-foreground text-pretty leading-relaxed">{t.whyMombasa.description}</p>
            </div>
          </ScrollReveal>

          <div className="space-y-8">
            {t.whyMombasa.reasons.map(
              (
                reason: {
                  title: string
                  description: string
                },
                index: number,
              ) => {
                const iconBg = index === 1 ? "bg-secondary/10" : "bg-primary/10"
                const iconColor = index === 1 ? "text-secondary" : "text-primary"
                const Icon = icons[index] ?? Waves

                return (
                  <ScrollReveal key={reason.title} delay={index * 100}>
                    <div className="bg-card border border-border rounded-2xl p-8 md:p-10 space-y-6">
                      <div className="flex items-start gap-4">
                        <div
                          className={`h-12 w-12 rounded-lg flex items-center justify-center flex-shrink-0 ${iconBg}`}
                        >
                          <Icon className={`h-6 w-6 ${iconColor}`} />
                        </div>
                        <div className="space-y-3">
                          <h3 className="text-2xl font-semibold">{reason.title}</h3>
                          <p className="text-lg text-muted-foreground leading-relaxed">{reason.description}</p>
                        </div>
                      </div>
                    </div>
                  </ScrollReveal>
                )
              },
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
