"use client"

import { Mic, MessageSquare, Users, Cake, ListTodo } from "lucide-react"
import { ScrollReveal } from "@/components/scroll-reveal"
import { useLanguage } from "@/contexts/language-context"

const icons = [Mic, MessageSquare, Users, Cake, ListTodo] as const

export function Agenda() {
  const { t } = useLanguage()
  const highlights = t.agenda.highlights ?? []

  return (
    <section className="py-20 md:py-32 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto space-y-12">
          <ScrollReveal>
            <div className="text-center space-y-4">
              <h2 className="text-4xl md:text-5xl font-bold text-balance">{t.agenda.title}</h2>
              <p className="text-xl text-muted-foreground text-pretty leading-relaxed">{t.agenda.description}</p>
            </div>
          </ScrollReveal>

          <div className="space-y-4">
            {highlights.map((item, index) => {
              const Icon = icons[index] ?? Mic
              return (
                <ScrollReveal key={item.title} delay={index * 50}>
                  <div className="flex items-start gap-6 p-6 rounded-xl bg-card border border-border hover:border-primary/50 transition-all duration-300">
                    <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <div className="space-y-2 flex-1">
                      <h3 className="text-xl font-semibold">{item.title}</h3>
                      <p className="text-muted-foreground leading-relaxed">{item.description}</p>
                    </div>
                    <div className="hidden sm:flex items-center justify-center h-8 w-8 rounded-full bg-muted text-muted-foreground text-sm font-medium flex-shrink-0">
                      {index + 1}
                    </div>
                  </div>
                </ScrollReveal>
              )
            })}
          </div>

          <ScrollReveal delay={300}>
            <div className="text-center pt-8">
              <p className="text-muted-foreground">{t.agenda.note}</p>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  )
}
