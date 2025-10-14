"use client"

import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { Calendar, MapPin, Users, Heart } from "lucide-react"
import { useLanguage } from "@/contexts/language-context"
import { ScrollReveal } from "@/components/scroll-reveal"

export default function AboutPage() {
  const { t } = useLanguage()

  return (
    <>
      <Navbar />
      <main className="min-h-screen pt-24">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto space-y-12">
            <ScrollReveal>
              <div className="text-center space-y-4">
                <h1 className="text-5xl font-bold text-balance">{t.about.title}</h1>
                <p className="text-xl text-muted-foreground text-balance">{t.about.subtitle}</p>
              </div>
            </ScrollReveal>

            <div className="prose prose-lg max-w-none space-y-8">
              <ScrollReveal delay={100}>
                <section className="bg-card rounded-2xl p-8 border border-border">
                  <h2 className="text-3xl font-bold mb-4">{t.overview.title}</h2>
                  <p className="text-muted-foreground leading-relaxed">{t.about.intro}</p>
                </section>
              </ScrollReveal>

              <div className="grid md:grid-cols-2 gap-6">
                <ScrollReveal delay={0}>
                  <div className="bg-card rounded-2xl p-6 border border-border">
                    <Calendar className="h-10 w-10 text-primary mb-4" />
                    <h3 className="text-xl font-bold mb-2">{t.hero.date}</h3>
                    <p className="text-muted-foreground">{t.hero.date}</p>
                  </div>
                </ScrollReveal>

                <ScrollReveal delay={100}>
                  <div className="bg-card rounded-2xl p-6 border border-border">
                    <MapPin className="h-10 w-10 text-primary mb-4" />
                    <h3 className="text-xl font-bold mb-2">{t.hero.location}</h3>
                    <p className="text-muted-foreground">{t.hero.location}</p>
                  </div>
                </ScrollReveal>

                <ScrollReveal delay={200}>
                  <div className="bg-card rounded-2xl p-6 border border-border">
                    <Users className="h-10 w-10 text-primary mb-4" />
                    <h3 className="text-xl font-bold mb-2">{t.audience.title}</h3>
                    <p className="text-muted-foreground">{t.audience.description}</p>
                  </div>
                </ScrollReveal>

                <ScrollReveal delay={300}>
                  <div className="bg-card rounded-2xl p-6 border border-border">
                    <Heart className="h-10 w-10 text-primary mb-4" />
                    <h3 className="text-xl font-bold mb-2">{t.about.mission.title}</h3>
                    <p className="text-muted-foreground">{t.about.mission.description}</p>
                  </div>
                </ScrollReveal>
              </div>

              <ScrollReveal delay={100}>
                <section className="bg-card rounded-2xl p-8 border border-border">
                  <h2 className="text-3xl font-bold mb-4">{t.about.history.title}</h2>
                  <p className="text-muted-foreground leading-relaxed">{t.about.history.description}</p>
                </section>
              </ScrollReveal>

              <ScrollReveal delay={100}>
                <section className="bg-card rounded-2xl p-8 border border-border">
                  <h2 className="text-3xl font-bold mb-4">{t.about.community.title}</h2>
                  <p className="text-muted-foreground leading-relaxed">{t.about.community.description}</p>
                </section>
              </ScrollReveal>
            </div>
          </div>
        </div>
        <Footer />
      </main>
    </>
  )
}
