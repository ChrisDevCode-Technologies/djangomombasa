"use client"

import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { Shield, Heart, Users, AlertCircle } from "lucide-react"
import { useLanguage } from "@/contexts/language-context"

export default function CodeOfConductPage() {
  const { t } = useLanguage()

  return (
    <>
      <Navbar />
      <main className="min-h-screen pt-24">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto space-y-12">
            <div className="text-center space-y-4">
              <Shield className="h-16 w-16 text-primary mx-auto" />
              <h1 className="text-5xl font-bold text-balance">{t.codeOfConductPage.title}</h1>
              <p className="text-xl text-muted-foreground text-balance">{t.codeOfConductPage.subtitle}</p>
            </div>

            <section className="bg-primary text-primary-foreground rounded-2xl p-8 space-y-4">
              <h2 className="text-3xl font-bold">{t.codeOfConductPage.commitmentTitle}</h2>
              <p className="text-primary-foreground/90 leading-relaxed">{t.codeOfConductPage.commitmentDescription}</p>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-6">
              <div className="flex items-start gap-4">
                <Heart className="h-8 w-8 text-primary shrink-0 mt-1" />
                <div>
                  <h2 className="text-2xl font-bold mb-3">{t.codeOfConductPage.expectedTitle}</h2>
                  <ul className="space-y-3 text-muted-foreground">
                    {t.codeOfConductPage.expectedBehaviors.map((behavior) => (
                      <li key={behavior} className="flex items-start gap-3">
                        <span className="text-primary font-bold">•</span>
                        <span>{behavior}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-6">
              <div className="flex items-start gap-4">
                <AlertCircle className="h-8 w-8 text-destructive shrink-0 mt-1" />
                <div>
                  <h2 className="text-2xl font-bold mb-3">{t.codeOfConductPage.unacceptableTitle}</h2>
                  <p className="text-muted-foreground mb-4">{t.codeOfConductPage.unacceptableDescription}</p>
                  <ul className="space-y-3 text-muted-foreground">
                    {t.codeOfConductPage.unacceptableBehaviors.map((behavior) => (
                      <li key={behavior} className="flex items-start gap-3">
                        <span className="text-destructive font-bold">•</span>
                        <span>{behavior}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-6">
              <div className="flex items-start gap-4">
                <Users className="h-8 w-8 text-primary shrink-0 mt-1" />
                <div>
                  <h2 className="text-2xl font-bold mb-3">{t.codeOfConductPage.scopeTitle}</h2>
                  <p className="text-muted-foreground leading-relaxed mb-4">{t.codeOfConductPage.scopeDescription}</p>
                  <ul className="space-y-2 text-muted-foreground">
                    {t.codeOfConductPage.scopeItems.map((item) => (
                      <li key={item} className="flex items-start gap-3">
                        <span className="text-primary font-bold">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-4">
              <h2 className="text-2xl font-bold">{t.codeOfConductPage.consequencesTitle}</h2>
              <p className="text-muted-foreground leading-relaxed">{t.codeOfConductPage.consequencesDescription}</p>
              <ul className="space-y-2 text-muted-foreground">
                {t.codeOfConductPage.consequencesItems.map((item) => (
                  <li key={item} className="flex items-start gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="bg-primary text-primary-foreground rounded-2xl p-8 space-y-4">
              <h2 className="text-2xl font-bold">{t.codeOfConductPage.reportingTitle}</h2>
              <p className="text-primary-foreground/90 leading-relaxed mb-4">
                {t.codeOfConductPage.reportingDescription}
              </p>
              <div className="space-y-3 text-primary-foreground/90">
                <p>
                  <strong>{t.codeOfConductPage.reportingDuring}</strong>
                </p>
                <p>
                  <strong>{t.codeOfConductPage.reportingEmail}</strong>
                </p>
                <p>
                  <strong>{t.codeOfConductPage.reportingEmergency}</strong>
                </p>
              </div>
              <p className="text-primary-foreground/90 leading-relaxed mt-4">{t.codeOfConductPage.reportingNote}</p>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border">
              <h2 className="text-2xl font-bold mb-4">{t.codeOfConductPage.grievancesTitle}</h2>
              <p className="text-muted-foreground leading-relaxed">{t.codeOfConductPage.grievancesDescription}</p>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border">
              <h2 className="text-2xl font-bold mb-4">{t.codeOfConductPage.licenseTitle}</h2>
              <p className="text-muted-foreground leading-relaxed">{t.codeOfConductPage.licenseDescription}</p>
            </section>
          </div>
        </div>
        <Footer />
      </main>
    </>
  )
}
