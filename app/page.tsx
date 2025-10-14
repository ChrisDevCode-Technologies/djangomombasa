import { Hero } from "@/components/hero"
import { Overview } from "@/components/overview"
import { WhyMombasa } from "@/components/why-mombasa"
import { Objectives } from "@/components/objectives"
import { Audience } from "@/components/audience"
import { Agenda } from "@/components/agenda"
import { Sponsors } from "@/components/sponsors"
import { Contact } from "@/components/contact"
import { Footer } from "@/components/footer"
import { Navbar } from "@/components/navbar"

export default function Home() {
  return (
    <>
      <Navbar />
      <main className="min-h-screen pt-24">
        <Hero />
        <Overview />
        <WhyMombasa />
        <Objectives />
        <Audience />
        <Agenda />
        <Sponsors />
        <Contact />
        <Footer />
      </main>
    </>
  )
}
