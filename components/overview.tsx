"use client"

import { Code2, Users, Rocket } from "lucide-react"
import { ScrollReveal } from "@/components/scroll-reveal"
import { useLanguage } from "@/contexts/language-context"

export function Overview() {
  const { t } = useLanguage()

  return (
    <section className="py-20 md:py-32 bg-background">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto space-y-12">
          <ScrollReveal>
            <div className="text-center space-y-4">
              <h2 className="text-4xl md:text-5xl font-bold text-balance">{t.milestone.title}</h2>
              <p className="text-xl text-muted-foreground text-pretty leading-relaxed">
                {t.milestone.intro}
              </p>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={100}>
            <div className="prose prose-lg max-w-none text-foreground/90 leading-relaxed space-y-6">
              <p className="text-lg">
                {t.milestone.bodyOne}
              </p>

              <p className="text-lg">
                {t.milestone.bodyTwo}
              </p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-3 gap-8 pt-8">
            <ScrollReveal delay={0}>
              <div className="flex flex-col items-center text-center space-y-4 p-6 rounded-xl bg-card border border-border">
                <div className="h-14 w-14 rounded-full bg-primary/10 flex items-center justify-center">
                  <Code2 className="h-7 w-7 text-primary" />
                </div>
                <h3 className="text-xl font-semibold">20 Years Strong</h3>
                <p className="text-muted-foreground text-pretty">
                  Celebrating two decades of innovation and community-driven development
                </p>
              </div>
            </ScrollReveal>

            <ScrollReveal delay={100}>
              <div className="flex flex-col items-center text-center space-y-4 p-6 rounded-xl bg-card border border-border">
                <div className="h-14 w-14 rounded-full bg-secondary/10 flex items-center justify-center">
                  <Users className="h-7 w-7 text-secondary" />
                </div>
                <h3 className="text-xl font-semibold">Global Community</h3>
                <p className="text-muted-foreground text-pretty">
                  Connecting local developers with a worldwide network of Django enthusiasts
                </p>
              </div>
            </ScrollReveal>

            <ScrollReveal delay={200}>
              <div className="flex flex-col items-center text-center space-y-4 p-6 rounded-xl bg-card border border-border">
                <div className="h-14 w-14 rounded-full bg-primary/10 flex items-center justify-center">
                  <Rocket className="h-7 w-7 text-primary" />
                </div>
                <h3 className="text-xl font-semibold">Local Innovation</h3>
                <p className="text-muted-foreground text-pretty">
                  Showcasing how Mombasa's tech ecosystem uses Django for growth
                </p>
              </div>
            </ScrollReveal>
          </div>
        </div>
      </div>
    </section>
  )
}
