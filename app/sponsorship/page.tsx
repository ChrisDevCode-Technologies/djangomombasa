"use client"

import Image from "next/image"
import Link from "next/link"
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
              <p className="text-xl text-foreground/90 dark:text-foreground text-balance max-w-3xl mx-auto">
                {t.sponsorshipPage.subtitle}
              </p>
            </div>

            <section className="bg-card rounded-2xl p-8 border border-border">
              <h2 className="text-3xl font-bold mb-4">{t.sponsorshipPage.whyTitle}</h2>
              <div className="grid md:grid-cols-3 gap-6 mt-6">
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-primary">{t.sponsorshipPage.brandVisibility.title}</h3>
                  <p className="text-foreground/80 dark:text-foreground/95">
                    {t.sponsorshipPage.brandVisibility.description}
                  </p>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-primary">{t.sponsorshipPage.talentAccess.title}</h3>
                  <p className="text-foreground/80 dark:text-foreground/95">
                    {t.sponsorshipPage.talentAccess.description}
                  </p>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-primary">{t.sponsorshipPage.communityImpact.title}</h3>
                  <p className="text-foreground/80 dark:text-foreground/95">
                    {t.sponsorshipPage.communityImpact.description}
                  </p>
                </div>
              </div>
            </section>

            <section className="space-y-8">
              <div className="bg-card rounded-2xl p-8 border border-border">
                <h2 className="text-3xl font-bold mb-6">{t.sponsorshipPage.supportTitle}</h2>
                <div className="grid md:grid-cols-2 gap-6">
                  {t.sponsorshipPage.supportAreas.map((area) => (
                    <div key={area.name} className="bg-background/60 dark:bg-background/40 rounded-xl border border-border/60 p-6 space-y-4">
                      <div className="space-y-2">
                        <h3 className="text-2xl font-semibold">{area.name}</h3>
                        <p className="text-foreground/80 dark:text-foreground/95">{area.description}</p>
                      </div>
                      <ul className="space-y-3">
                        {area.benefits.map((benefit: string) => (
                          <li key={benefit} className="flex items-start gap-3">
                            <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                            <span className="text-foreground/80 dark:text-foreground/95">{benefit}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            <section className="bg-primary text-primary-foreground rounded-2xl p-8 text-center space-y-6">
              <h2 className="text-3xl font-bold">{t.sponsorshipPage.readyTitle}</h2>
              <p className="text-primary-foreground/90 max-w-2xl mx-auto">{t.sponsorshipPage.readyDescription}</p>
              <Button size="lg" variant="secondary" className="gap-2" asChild>
                <a href="mailto:chris@chrisdevcode.com?subject=Sponsorship%20-%20Django%20Day%20Mombasa">
                  <Mail className="h-5 w-5" />
                  {t.sponsorshipPage.contactBtn}
                </a>
              </Button>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border">
              <h2 className="text-3xl font-bold mb-4">{t.sponsorshipPage.inKindTitle}</h2>
              <p className="text-foreground/80 dark:text-foreground/95 leading-relaxed mb-4">
                {t.sponsorshipPage.inKindDescription}
              </p>
              <ul className="space-y-2 text-foreground/80 dark:text-foreground/95">
                {t.sponsorshipPage.inKindItems.map((item) => (
                  <li key={item} className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
              {t.sponsorshipPage.inKindPartners?.length ? (
                <div className="mt-10 space-y-4">
                  <h3 className="text-2xl font-semibold text-center md:text-left">
                    {t.sponsorshipPage.inKindPartnersTitle}
                  </h3>
                  <p className="text-foreground/80 dark:text-foreground/95 leading-relaxed text-center md:text-left max-w-3xl">
                    {t.sponsorshipPage.inKindPartnersDescription}
                  </p>
                  <div className="grid gap-6 pt-4 sm:grid-cols-2 lg:grid-cols-3">
                    {t.sponsorshipPage.inKindPartners.map(
                      (partner: { name: string; role: string; link: string; logo: string }) => (
                        <Link
                          key={partner.name}
                          href={partner.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="group flex flex-col items-center rounded-xl border border-border/60 bg-background/60 p-6 text-center transition hover:border-primary/60 hover:shadow-lg dark:bg-background/40"
                        >
                          <div className="flex h-20 w-full items-center justify-center">
                            <Image
                              src={partner.logo}
                              alt={`${partner.name} logo`}
                              width={200}
                              height={80}
                              className="max-h-16 w-auto object-contain transition group-hover:scale-[1.03]"
                            />
                          </div>
                          <div className="mt-4 space-y-1">
                            <h4 className="text-xl font-semibold">{partner.name}</h4>
                            <p className="text-sm text-foreground/70 dark:text-foreground/80">{partner.role}</p>
                          </div>
                        </Link>
                      ),
                    )}
                  </div>
                </div>
              ) : null}
            </section>
          </div>
        </div>
        <Footer />
      </main>
    </>
  )
}
