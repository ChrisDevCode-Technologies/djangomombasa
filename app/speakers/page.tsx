"use client"

import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Mic, Clock, Users, Award } from "lucide-react"
import { useLanguage } from "@/contexts/language-context"

export default function SpeakersPage() {
  const { t } = useLanguage()

  return (
    <>
      <Navbar />
      <main className="min-h-screen pt-24">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto space-y-12">
            <div className="text-center space-y-4">
              <h1 className="text-5xl font-bold text-balance">{t.speakersPage.title}</h1>
              <p className="text-xl text-muted-foreground text-balance">{t.speakersPage.subtitle}</p>
            </div>

            <section className="bg-primary text-primary-foreground rounded-2xl p-8 text-center space-y-4">
              <h2 className="text-3xl font-bold">{t.speakersPage.wantToHearTitle}</h2>
              <p className="text-primary-foreground/90 max-w-2xl mx-auto leading-relaxed">
                {t.speakersPage.wantToHearDescription}
              </p>
            </section>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-card rounded-2xl p-6 border border-border">
                <Mic className="h-10 w-10 text-primary mb-4" />
                <h3 className="text-xl font-bold mb-2">{t.speakersPage.talkFormats.title}</h3>
                <ul className="space-y-2 text-muted-foreground">
                  {t.speakersPage.talkFormats.items.map((item) => (
                    <li key={item}>• {item}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-card rounded-2xl p-6 border border-border">
                <Clock className="h-10 w-10 text-primary mb-4" />
                <h3 className="text-xl font-bold mb-2">{t.speakersPage.importantDates.title}</h3>
                <ul className="space-y-2 text-muted-foreground">
                  {t.speakersPage.importantDates.items.map((item) => (
                    <li key={item}>• {item}</li>
                  ))}
                </ul>
              </div>
            </div>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-6">
              <h2 className="text-3xl font-bold">{t.speakersPage.suggestedTopicsTitle}</h2>
              <p className="text-muted-foreground">{t.speakersPage.suggestedTopicsDescription}</p>
              <div className="grid md:grid-cols-2 gap-4">
                <ul className="space-y-2 text-muted-foreground">
                  {t.speakersPage.topicsColumn1.map((topic) => (
                    <li key={topic}>• {topic}</li>
                  ))}
                </ul>
                <ul className="space-y-2 text-muted-foreground">
                  {t.speakersPage.topicsColumn2.map((topic) => (
                    <li key={topic}>• {topic}</li>
                  ))}
                </ul>
              </div>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-6">
              <h2 className="text-3xl font-bold">{t.speakersPage.lookingForTitle}</h2>
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <Users className="h-6 w-6 text-primary shrink-0 mt-1" />
                  <div>
                    <h3 className="font-bold mb-1">{t.speakersPage.practicalValue.title}</h3>
                    <p className="text-muted-foreground">{t.speakersPage.practicalValue.description}</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <Award className="h-6 w-6 text-primary shrink-0 mt-1" />
                  <div>
                    <h3 className="font-bold mb-1">{t.speakersPage.clearCommunication.title}</h3>
                    <p className="text-muted-foreground">{t.speakersPage.clearCommunication.description}</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <Mic className="h-6 w-6 text-primary shrink-0 mt-1" />
                  <div>
                    <h3 className="font-bold mb-1">{t.speakersPage.engagingContent.title}</h3>
                    <p className="text-muted-foreground">{t.speakersPage.engagingContent.description}</p>
                  </div>
                </div>
              </div>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border space-y-4">
              <h2 className="text-3xl font-bold">{t.speakersPage.speakerBenefitsTitle}</h2>
              <ul className="space-y-3 text-muted-foreground">
                {t.speakersPage.speakerBenefits.map((benefit) => (
                  <li key={benefit} className="flex items-start gap-3">
                    <span className="text-primary font-bold">•</span>
                    <span>{benefit}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="bg-primary text-primary-foreground rounded-2xl p-8 text-center space-y-6">
              <h2 className="text-3xl font-bold">{t.speakersPage.submitTitle}</h2>
              <p className="text-primary-foreground/90 max-w-2xl mx-auto">{t.speakersPage.submitDescription}</p>
              <Button size="lg" variant="secondary">
                {t.speakersPage.submitBtn}
              </Button>
            </section>

            <section className="bg-card rounded-2xl p-8 border border-border">
              <h2 className="text-3xl font-bold mb-4">{t.speakersPage.firstTimeTitle}</h2>
              <p className="text-muted-foreground leading-relaxed">{t.speakersPage.firstTimeDescription}</p>
            </section>
          </div>
        </div>
        <Footer />
      </main>
    </>
  )
}
