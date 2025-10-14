"use client"

import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Check, Mail } from "lucide-react"
import { useLanguage } from "@/contexts/language-context"

export default function SponsorshipPage() {
  const { t } = useLanguage()

  return (
    <>
      <Navbar />
      <main className="min-h-screen pt-24">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-6xl mx-auto space-y-12">
            <div className="text-center space-y-4">
              <h1 className="text-5xl font-bold text-balance">{t.sponsorshipPage.title}</h1>
              <p className="text-xl text-muted-foreground text-balance max-w-3xl mx-auto">
                {t.sponsorshipPage.subtitle}
              </p>
            </div>

            <section className="bg-card rounded-2xl p-8 border border-border">
              <h2 className="text-3xl font-bold mb-4">{t.sponsorshipPage.whyTitle}</h2>
              <div className="grid md:grid-cols-3 gap-6 mt-6">
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-primary">{t.sponsorshipPage.brandVisibility.title}</h3>
                  <p className="text-muted-foreground">{t.sponsorshipPage.brandVisibility.description}</p>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-primary">{t.sponsorshipPage.talentAccess.title}</h3>
                  <p className="text-muted-foreground">{t.sponsorshipPage.talentAccess.description}</p>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-primary">{t.sponsorshipPage.communityImpact.title}</h3>
                  <p className="text-muted-foreground">{t.sponsorshipPage.communityImpact.description}</p>
                </div>
              </div>
            </section>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="bg-card rounded-2xl p-8 border border-border space-y-6">
                <div>
                  <h3 className="text-2xl font-bold">{t.sponsorshipPage.tiers.platinum.name}</h3>
                  <p className="text-3xl font-bold text-primary mt-2">{t.sponsorshipPage.tiers.platinum.price}</p>
                </div>
                <ul className="space-y-3">
                  {t.sponsorshipPage.tiers.platinum.benefits.map((benefit) => (
                    <li key={benefit} className="flex items-start gap-3">
                      <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                      <span className="text-muted-foreground">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-card rounded-2xl p-8 border border-border space-y-6">
                <div>
                  <h3 className="text-2xl font-bold">{t.sponsorshipPage.tiers.gold.name}</h3>
                  <p className="text-3xl font-bold text-primary mt-2">{t.sponsorshipPage.tiers.gold.price}</p>
                </div>
                <ul className="space-y-3">
                  {t.sponsorshipPage.tiers.gold.benefits.map((benefit) => (
                    <li key={benefit} className="flex items-start gap-3">
                      <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                      <span className="text-muted-foreground">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-card rounded-2xl p-8 border border-border space-y-6">
                <div>
                  <h3 className="text-2xl font-bold">{t.sponsorshipPage.tiers.silver.name}</h3>
                  <p className="text-3xl font-bold text-primary mt-2">{t.sponsorshipPage.tiers.silver.price}</p>
                </div>
                <ul className="space-y-3">
                  {t.sponsorshipPage.tiers.silver.benefits.map((benefit) => (
                    <li key={benefit} className="flex items-start gap-3">
                      <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                      <span className="text-muted-foreground">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-card rounded-2xl p-8 border border-border space-y-6">
                <div>
                  <h3 className="text-2xl font-bold">{t.sponsorshipPage.tiers.community.name}</h3>
                  <p className="text-3xl font-bold text-primary mt-2">{t.sponsorshipPage.tiers.community.price}</p>
                </div>
                <ul className="space-y-3">
                  {t.sponsorshipPage.tiers.community.benefits.map((benefit) => (
                    <li key={benefit} className="flex items-start gap-3">
                      <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                      <span className="text-muted-foreground">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <section className="bg-primary text-primary-foreground rounded-2xl p-8 text-center space-y-6">
              <h2 className="text-3xl font-bold">{t.sponsorshipPage.readyTitle}</h2>
              <p className="text-primary-foreground/90 max-w-2xl mx-auto">{t.sponsorshipPage.readyDescription}</p>
              <Button size="lg" variant="secondary" className="gap-2">
                <Mail className="h-5 w-5" />
                {t.sponsorshipPage.contactBtn}
              </Button>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border">
              <h2 className="text-3xl font-bold mb-4">{t.sponsorshipPage.inKindTitle}</h2>
              <p className="text-muted-foreground leading-relaxed mb-4">{t.sponsorshipPage.inKindDescription}</p>
              <ul className="space-y-2 text-muted-foreground">
                {t.sponsorshipPage.inKindItems.map((item) => (
                  <li key={item} className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </section>
          </div>
        </div>
        <Footer />
      </main>
    </>
  )
}
