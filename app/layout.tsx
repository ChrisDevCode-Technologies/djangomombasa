import type React from "react"
import type { Metadata } from "next"
import { Mulish } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { Suspense } from "react"
import { Navbar } from "@/components/navbar"
import { LanguageProvider } from "@/contexts/language-context"
import { PageTransition } from "@/components/page-transition"
import "./globals.css"

const mulish = Mulish({
  subsets: ["latin"],
  weight: ["200", "300", "400", "500", "600", "700", "800", "900"],
  variable: "--font-mulish",
  display: "swap",
})

export const metadata: Metadata = {
  title: "Django Day Mombasa - Celebrating 20 Years",
  description:
    "Join us on December 5th in Mombasa to celebrate 20 years of Django - the web framework for perfectionists with deadlines.",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`font-sans ${mulish.variable}`}>
        <LanguageProvider>
          <Navbar />
          <PageTransition>
            <Suspense fallback={null}>{children}</Suspense>
          </PageTransition>
        </LanguageProvider>
        <Analytics />
      </body>
    </html>
  )
}
