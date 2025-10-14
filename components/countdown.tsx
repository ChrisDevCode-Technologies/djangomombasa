"use client"

import { useEffect, useState } from "react"
import { useLanguage } from "@/contexts/language-context"

interface TimeLeft {
  days: number
  hours: number
  minutes: number
  seconds: number
}

export function Countdown() {
  const { t } = useLanguage()
  const [timeLeft, setTimeLeft] = useState<TimeLeft>({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  })
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    // Event date: December 5, 2025 at 9:30 AM EAT (UTC+3)
    const eventDate = new Date("2025-12-05T06:30:00Z").getTime()

    const calculateTimeLeft = () => {
      const now = new Date().getTime()
      const difference = eventDate - now

      if (difference > 0) {
        setTimeLeft({
          days: Math.floor(difference / (1000 * 60 * 60 * 24)),
          hours: Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
          minutes: Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60)),
          seconds: Math.floor((difference % (1000 * 60)) / 1000),
        })
      }
    }

    calculateTimeLeft()
    const timer = setInterval(calculateTimeLeft, 1000)

    return () => clearInterval(timer)
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <div className="flex items-center justify-center gap-4 md:gap-6">
      <TimeUnit value={timeLeft.days} label={t.hero.countdown.days} />
      <TimeUnit value={timeLeft.hours} label={t.hero.countdown.hours} />
      <TimeUnit value={timeLeft.minutes} label={t.hero.countdown.minutes} />
      <TimeUnit value={timeLeft.seconds} label={t.hero.countdown.seconds} />
    </div>
  )
}

function TimeUnit({ value, label }: { value: number; label: string }) {
  const [displayValue, setDisplayValue] = useState(value)
  const [isFlipping, setIsFlipping] = useState(false)

  useEffect(() => {
    if (value !== displayValue) {
      setIsFlipping(true)
      const timeout = setTimeout(() => {
        setDisplayValue(value)
        setIsFlipping(false)
      }, 300)
      return () => clearTimeout(timeout)
    }
  }, [value, displayValue])

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-16 h-20 md:w-20 md:h-24 perspective-1000">
        <div
          className={`absolute inset-0 bg-secondary/20 backdrop-blur-sm rounded-lg border border-secondary/30 flex items-center justify-center transition-transform duration-300 ${
            isFlipping ? "animate-flip" : ""
          }`}
        >
          <span className="text-3xl md:text-4xl font-bold text-secondary tabular-nums">
            {String(displayValue).padStart(2, "0")}
          </span>
        </div>
        {/* Top and bottom divider for flip effect */}
        <div className="absolute inset-x-0 top-1/2 h-px bg-secondary/20" />
      </div>
      <span className="text-xs md:text-sm font-medium text-primary-foreground/70 uppercase tracking-wider">
        {label}
      </span>
    </div>
  )
}
