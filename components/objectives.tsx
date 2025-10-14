"use client"

import { Target, Sparkles, Users2, TrendingUp, Heart, Globe } from "lucide-react"
import { ScrollReveal } from "@/components/scroll-reveal"
import { useLanguage } from "@/contexts/language-context"

const icons = [Sparkles, Target, Users2, TrendingUp, Heart, Globe] as const

export function Objectives() {
  const { t } = useLanguage()

  return (
    <section className="py-20 md:py-32 bg-background">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto space-y-12">
          <ScrollReveal>
            <div className="text-center space-y-4">
              <h2 className="text-4xl md:text-5xl font-bold text-balance">{t.objectives.title}</h2>
              <p className="text-xl text-muted-foreground text-pretty leading-relaxed max-w-3xl mx-auto">
                {t.objectives.subtitle}
              </p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {t.objectives.items.map((objective, index) => {
              const Icon = icons[index] ?? Sparkles
              return (
                <ScrollReveal key={index} delay={index * 50}>
                  <div className="group p-6 rounded-xl bg-card border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg h-full">
                    <div className="space-y-4">
                      <div className="h-12 w-12 rounded-lg bg-primary/10 group-hover:bg-primary/20 flex items-center justify-center transition-colors">
                        <Icon className="h-6 w-6 text-primary" />
                      </div>
                      <h3 className="text-xl font-semibold text-balance">{objective.title}</h3>
                      <p className="text-muted-foreground leading-relaxed text-pretty">{objective.description}</p>
                    </div>
                  </div>
                </ScrollReveal>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
