"use client"

import type React from "react"

export function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <style jsx global>{`
        html {
          scroll-behavior: smooth;
        }
      `}</style>
      {children}
    </>
  )
}
