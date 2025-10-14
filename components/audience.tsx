"use client"

import { Code, Briefcase, GraduationCap, GitBranch, Building, BookOpen } from "lucide-react"
import { ScrollReveal } from "@/components/scroll-reveal"
import { useLanguage } from "@/contexts/language-context"

const icons = [Code, Briefcase, GraduationCap, GitBranch, Building, BookOpen] as const

export function Audience() {
  const { t } = useLanguage()

  return (
    <section className="py-20 md:py-32 bg-primary text-primary-foreground">
      <div className="container mx-auto px-4">
        <div className="max-w-5xl mx-auto space-y-12">
          <ScrollReveal>
            <div className="text-center space-y-4">
              <h2 className="text-4xl md:text-5xl font-bold text-balance">{t.audience.title}</h2>
              <p className="text-xl text-primary-foreground/90 text-pretty leading-relaxed">{t.audience.description}</p>
            </div>
          </ScrollReveal>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {t.audience.groups.map(
              (
                audience: {
                  title: string
                  description?: string
                },
                index: number,
              ) => {
                const Icon = icons[index] ?? Code

                return (
                  <ScrollReveal key={audience.title} delay={index * 50}>
                    <div className="flex items-center gap-4 p-6 rounded-xl bg-primary-foreground/10 backdrop-blur-sm border border-primary-foreground/20">
                      <div className="h-12 w-12 rounded-lg bg-secondary/20 flex items-center justify-center flex-shrink-0">
                        <Icon className="h-6 w-6 text-secondary" />
                      </div>
                      <div className="space-y-1 text-balance">
                        <p className="font-medium leading-snug">{audience.title}</p>
                        {audience.description ? (
                          <p className="text-sm text-primary-foreground/80 leading-snug">{audience.description}</p>
                        ) : null}
                      </div>
                    </div>
                  </ScrollReveal>
                )
              },
            )}
          </div>

          <ScrollReveal delay={300}>
            <div className="text-center pt-8">
              <p className="text-lg text-primary-foreground/80">{t.audience.note}</p>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  )
}
