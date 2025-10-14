"use client"

import { Button } from "@/components/ui/button"
import { Award, Eye, Handshake, Megaphone } from "lucide-react"
import { useLanguage } from "@/contexts/language-context"
import { ScrollReveal } from "@/components/scroll-reveal"

export function Sponsors() {
  const { t } = useLanguage()

  const benefits = [
    {
      icon: Eye,
      title: "Brand Visibility",
      description: "Across all digital campaigns, social media, and tech community channels",
    },
    {
      icon: Award,
      title: "Logo Placement",
      description: "On event collateral including posters, T-shirts, banners, and digital backdrops",
    },
    {
      icon: Megaphone,
      title: "Live Mentions",
      description: "Recognition during sessions and comprehensive online coverage",
    },
    {
      icon: Handshake,
      title: "Networking Access",
      description: "Direct connection with developers, startups, and ecosystem builders",
    },
  ]

  return (
    <section className="py-20 md:py-32 bg-background">
      <div className="container mx-auto px-4">
        <div className="max-w-5xl mx-auto space-y-12">
          <ScrollReveal>
            <div className="text-center space-y-4">
              <h2 className="text-4xl md:text-5xl font-bold text-balance">Become a Sponsor</h2>
              <p className="text-xl text-muted-foreground text-pretty leading-relaxed max-w-3xl mx-auto">
                Position your brand at the heart of one of the most developer-driven events on the coast
              </p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-2 gap-6">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon
              return (
                <ScrollReveal key={index} delay={index * 50}>
                  <div className="flex items-start gap-4 p-6 rounded-xl bg-card border border-border h-full">
                    <div className="h-12 w-12 rounded-lg bg-secondary/10 flex items-center justify-center flex-shrink-0">
                      <Icon className="h-6 w-6 text-secondary" />
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-lg font-semibold">{benefit.title}</h3>
                      <p className="text-muted-foreground leading-relaxed text-pretty">{benefit.description}</p>
                    </div>
                  </div>
                </ScrollReveal>
              )
            })}
          </div>

          <ScrollReveal delay={200}>
            <div className="bg-primary text-primary-foreground rounded-2xl p-8 md:p-12 space-y-6 text-center">
              <h3 className="text-2xl md:text-3xl font-bold text-balance">Your Support Will:</h3>
              <ul className="space-y-3 text-lg max-w-2xl mx-auto">
                <li className="flex items-center justify-center gap-3">
                  <span className="h-2 w-2 rounded-full bg-secondary flex-shrink-0"></span>
                  <span className="text-pretty">Strengthen the Django and Python ecosystem in Mombasa</span>
                </li>
                <li className="flex items-center justify-center gap-3">
                  <span className="h-2 w-2 rounded-full bg-secondary flex-shrink-0"></span>
                  <span className="text-pretty">Empower developers building impactful digital solutions</span>
                </li>
                <li className="flex items-center justify-center gap-3">
                  <span className="h-2 w-2 rounded-full bg-secondary flex-shrink-0"></span>
                  <span className="text-pretty">Connect your brand with innovation and opportunity</span>
                </li>
              </ul>
              <div className="pt-4">
                <Button
                  size="lg"
                  className="bg-secondary text-secondary-foreground hover:bg-secondary/90 text-lg px-8 py-6"
                >
                  Sponsor This Event
                </Button>
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={300}>
            <div className="text-center space-y-4 pt-8">
              <p className="text-sm text-muted-foreground">Organized by Django & Python Community Mombasa</p>
              <p className="text-sm text-muted-foreground">
                Supported by ChrisDevCode and connected to the Django Software Foundation (DSF) network
              </p>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  )
}
