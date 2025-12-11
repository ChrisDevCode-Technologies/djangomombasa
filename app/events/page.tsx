"use client"

import events from "@/lib/events.json"
import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"
import { ScrollReveal } from "@/components/scroll-reveal"
import { Calendar } from "lucide-react"
import { useLanguage } from "@/contexts/language-context"

type EventItem = {
  title: string
  displayDate: string
  description?: string
}

export default function EventsPage() {
  const { t } = useLanguage()

  return (
    <>
      <Navbar />
      <main className="min-h-screen pt-24">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto space-y-10">
            <ScrollReveal>
              <div className="text-center space-y-4">
                <h1 className="text-5xl font-bold text-balance">{t.eventsPage.title}</h1>
                <p className="text-xl text-muted-foreground text-balance">{t.eventsPage.subtitle}</p>
              </div>
            </ScrollReveal>

            <ScrollReveal delay={100}>
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <h2 className="text-2xl font-semibold">{t.eventsPage.listTitle}</h2>
                <div className="h-px flex-1 bg-border hidden sm:block" />
              </div>
            </ScrollReveal>

            <div className="grid gap-6">
              {(events as EventItem[]).map((event, index) => (
                <ScrollReveal key={event.title} delay={index * 75}>
                  <div className="bg-card rounded-2xl p-6 border border-border shadow-sm hover:border-primary/50 transition-colors duration-200 space-y-4">
                    <div className="flex items-center justify-between gap-3 flex-wrap">
                      <div>
                        <h3 className="text-2xl font-semibold">{event.title}</h3>
                      </div>
                      <span className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
                        <Calendar className="h-4 w-4" />
                        {event.displayDate}
                      </span>
                    </div>
                    {event.description ? (
                      <p className="text-muted-foreground leading-relaxed">{event.description}</p>
                    ) : null}
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Calendar className="h-4 w-4" />
                      <span>
                        {t.eventsPage.dateLabel}: {event.displayDate}
                      </span>
                    </div>
                  </div>
                </ScrollReveal>
              ))}
            </div>
          </div>
        </div>
        <Footer />
      </main>
    </>
  )
}
