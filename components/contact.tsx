"use client"

import { Button } from "@/components/ui/button"
import { Mail, Phone, Users } from "lucide-react"
import { ScrollReveal } from "@/components/scroll-reveal"

export function Contact() {
  return (
    <section className="py-20 md:py-32 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <div className="bg-card border border-border rounded-2xl p-8 md:p-12 space-y-8">
              <div className="text-center space-y-4">
                <h2 className="text-4xl md:text-5xl font-bold text-balance">Get Involved</h2>
                <p className="text-xl text-muted-foreground text-pretty leading-relaxed">
                  Be part of the story — where community meets code, and innovation meets opportunity
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <ScrollReveal delay={100}>
                  <div className="space-y-4 p-6 rounded-xl bg-muted/50">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Users className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Event Lead</p>
                        <p className="font-semibold">Chris Achinga</p>
                      </div>
                    </div>
                  </div>
                </ScrollReveal>

                <ScrollReveal delay={150}>
                  <div className="space-y-4 p-6 rounded-xl bg-muted/50">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Mail className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Email</p>
                        <a
                          href="mailto:chris@chrisdevcode.com"
                          className="font-semibold hover:text-primary transition-colors"
                        >
                          chris@chrisdevcode.com
                        </a>
                      </div>
                    </div>
                  </div>
                </ScrollReveal>

                <ScrollReveal delay={200} className="md:col-span-2">
                  <div className="space-y-4 p-6 rounded-xl bg-muted/50">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Phone className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Phone</p>
                        <a href="tel:+254740428522" className="font-semibold hover:text-primary transition-colors">
                          +254 740 428 522
                        </a>
                      </div>
                    </div>
                  </div>
                </ScrollReveal>
              </div>

              <ScrollReveal delay={250}>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
                  <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 w-full sm:w-auto">
                    Register to Attend
                  </Button>
                  <Button size="lg" variant="outline" className="w-full sm:w-auto bg-transparent">
                    Submit a Talk Proposal
                  </Button>
                </div>
              </ScrollReveal>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </section>
  )
}
