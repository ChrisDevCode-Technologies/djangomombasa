"use client"

import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Sparkles, Code, Users, Ticket, BadgeCheck, GraduationCap, Mail } from "lucide-react"
import { useLanguage } from "@/contexts/language-context"

export default function RegistrationPage() {
  const { t } = useLanguage()

  const highlightIcons = [Sparkles, Code, Users] as const
  const passIcons = [Ticket, BadgeCheck, GraduationCap] as const

  return (
    <>
      <Navbar />
      <main className="min-h-screen pt-24">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-5xl mx-auto space-y-12">
            <div className="text-center space-y-4">
              <h1 className="text-5xl font-bold text-balance">{t.registrationPage.title}</h1>
              <p className="text-xl text-muted-foreground text-balance max-w-3xl mx-auto">
                {t.registrationPage.subtitle}
              </p>
            </div>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-6">
              <h2 className="text-3xl font-bold text-center">{t.registrationPage.highlightsTitle}</h2>
              <div className="grid md:grid-cols-3 gap-6">
                {t.registrationPage.highlights.map((highlight: { title: string; description: string }, index: number) => {
                  const Icon = highlightIcons[index]
                  return (
                    <div key={highlight.title} className="space-y-3 text-center">
                      <Icon className="h-10 w-10 mx-auto text-primary" />
                      <h3 className="text-xl font-bold">{highlight.title}</h3>
                      <p className="text-muted-foreground leading-relaxed">{highlight.description}</p>
                    </div>
                  )
                })}
              </div>
            </section>

            <section className="space-y-6">
              <h2 className="text-3xl font-bold text-center">{t.registrationPage.passesTitle}</h2>
              <div className="grid md:grid-cols-3 gap-6">
                {t.registrationPage.passes.map(
                  (pass: { name: string; price: string; description: string }, index: number) => {
                    const Icon = passIcons[index] ?? Ticket
                    return (
                      <div key={pass.name} className="bg-card rounded-2xl p-6 border border-border space-y-4 text-center">
                        <Icon className="h-10 w-10 mx-auto text-primary" />
                        <div className="space-y-1">
                          <h3 className="text-2xl font-bold">{pass.name}</h3>
                          <p className="text-3xl font-bold text-primary">{pass.price}</p>
                        </div>
                        <p className="text-muted-foreground leading-relaxed">{pass.description}</p>
                      </div>
                    )
                  },
                )}
              </div>
            </section>

            <section className="grid md:grid-cols-2 gap-8">
              <div className="bg-card rounded-2xl p-8 border border-border space-y-4">
                <h2 className="text-3xl font-bold">{t.registrationPage.stepsTitle}</h2>
                <ol className="space-y-3 text-muted-foreground">
                  {t.registrationPage.steps.map((step: string, index: number) => (
                    <li key={step} className="flex items-start gap-3">
                      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary font-semibold">
                        {index + 1}
                      </span>
                      <span className="leading-relaxed">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>

              <div className="bg-card rounded-2xl p-8 border border-border space-y-4">
                <h2 className="text-3xl font-bold">{t.registrationPage.whatsIncludedTitle}</h2>
                <ul className="space-y-3 text-muted-foreground">
                  {t.registrationPage.whatsIncluded.map((item: string) => (
                    <li key={item} className="flex items-start gap-3">
                      <span className="text-primary font-bold">•</span>
                      <span className="leading-relaxed">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </section>

            <section className="bg-primary text-primary-foreground rounded-2xl p-8 text-center space-y-6">
              <h2 className="text-3xl font-bold">{t.registrationPage.ctaTitle}</h2>
              <p className="text-primary-foreground/90 max-w-3xl mx-auto leading-relaxed">
                {t.registrationPage.ctaDescription}
              </p>
              <Button asChild size="lg" variant="secondary" className="gap-2">
                <a href={t.registrationPage.ctaLink}>
                  <Mail className="h-5 w-5" />
                  {t.registrationPage.ctaBtn}
                </a>
              </Button>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-3 text-center">
              <h2 className="text-2xl font-bold">{t.registrationPage.supportTitle}</h2>
              <p className="text-muted-foreground leading-relaxed">{t.registrationPage.supportDescription}</p>
              <a href={`mailto:${t.registrationPage.supportEmail}`} className="text-primary font-semibold">
                {t.registrationPage.supportEmail}
              </a>
            </section>
          </div>
        </div>
        <Footer />
      </main>
    </>
  )
}
