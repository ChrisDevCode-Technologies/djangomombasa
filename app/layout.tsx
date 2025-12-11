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
  title: "Django Mombasa - Celebrating 20 Years",
  description:
    "Join the open developer community in Mombasa—next up: Django Day Mombasa on February 7, 2026.",
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
