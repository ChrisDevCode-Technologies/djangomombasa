"use client"

import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Heart, Users, Calendar, Gift } from "lucide-react"
import { useLanguage } from "@/contexts/language-context"

export default function VolunteerPage() {
  const { t } = useLanguage()

  const roleIcons = [Users, Calendar, Gift, Heart]

  return (
    <>
      <Navbar />
      <main className="min-h-screen pt-24">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto space-y-12">
            <div className="text-center space-y-4">
              <h1 className="text-5xl font-bold text-balance">{t.volunteerPage.title}</h1>
              <p className="text-xl text-muted-foreground text-balance">{t.volunteerPage.subtitle}</p>
            </div>

            <section className="bg-primary text-primary-foreground rounded-2xl p-8 text-center space-y-4">
              <Heart className="h-16 w-16 mx-auto" />
              <h2 className="text-3xl font-bold">{t.volunteerPage.bePartTitle}</h2>
              <p className="text-primary-foreground/90 max-w-2xl mx-auto leading-relaxed">
                {t.volunteerPage.bePartDescription}
              </p>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-6">
              <h2 className="text-3xl font-bold">{t.volunteerPage.whyVolunteerTitle}</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-primary">{t.volunteerPage.networkLearn.title}</h3>
                  <p className="text-muted-foreground">{t.volunteerPage.networkLearn.description}</p>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-primary">{t.volunteerPage.gainExperience.title}</h3>
                  <p className="text-muted-foreground">{t.volunteerPage.gainExperience.description}</p>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-primary">{t.volunteerPage.giveBack.title}</h3>
                  <p className="text-muted-foreground">{t.volunteerPage.giveBack.description}</p>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-bold text-primary">{t.volunteerPage.exclusivePerks.title}</h3>
                  <p className="text-muted-foreground">{t.volunteerPage.exclusivePerks.description}</p>
                </div>
              </div>
            </section>

            <section className="space-y-6">
              <h2 className="text-3xl font-bold text-center">{t.volunteerPage.rolesTitle}</h2>
              <div className="grid md:grid-cols-2 gap-6">
                {t.volunteerPage.roles.map((role, index) => {
                  const Icon = roleIcons[index]
                  return (
                    <div key={role.title} className="bg-card rounded-2xl p-6 border border-border space-y-4">
                      <Icon className="h-10 w-10 text-primary" />
                      <h3 className="text-xl font-bold">{role.title}</h3>
                      <p className="text-muted-foreground">{role.description}</p>
                    </div>
                  )
                })}
              </div>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-4">
              <h2 className="text-3xl font-bold">{t.volunteerPage.whatToExpectTitle}</h2>
              <ul className="space-y-3 text-muted-foreground">
                {t.volunteerPage.whatToExpect.map((item) => (
                  <li key={item} className="flex items-start gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-4">
              <h2 className="text-3xl font-bold">{t.volunteerPage.benefitsTitle}</h2>
              <ul className="space-y-3 text-muted-foreground">
                {t.volunteerPage.benefits.map((benefit) => (
                  <li key={benefit} className="flex items-start gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>{benefit}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="bg-primary text-primary-foreground rounded-2xl p-8 text-center space-y-6">
              <h2 className="text-3xl font-bold">{t.volunteerPage.readyTitle}</h2>
              <p className="text-primary-foreground/90 max-w-2xl mx-auto">{t.volunteerPage.readyDescription}</p>
              <Button size="lg" variant="secondary">
                {t.volunteerPage.signUpBtn}
              </Button>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border">
              <h2 className="text-3xl font-bold mb-4">{t.volunteerPage.questionsTitle}</h2>
              <p className="text-muted-foreground leading-relaxed">{t.volunteerPage.questionsDescription}</p>
            </section>
          </div>
        </div>
        <Footer />
      </main>
    </>
  )
}
