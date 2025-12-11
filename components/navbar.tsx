"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Moon, Sun, Menu, X, Languages, MoreHorizontal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import { useLanguage } from "@/contexts/language-context"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

export function Navbar() {
  const [theme, setTheme] = useState<"light" | "dark">("light")
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const pathname = usePathname()
  const isHomePage = pathname === "/"
  const { language, setLanguage, t } = useLanguage()

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
    const initialTheme = savedTheme || (prefersDark ? "dark" : "light")
    setTheme(initialTheme)
    document.documentElement.classList.toggle("dark", initialTheme === "dark")
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light"
    setTheme(newTheme)
    localStorage.setItem("theme", newTheme)
    document.documentElement.classList.toggle("dark", newTheme === "dark")
  }

  const handleNavClick = () => {
    window.scrollTo({ top: 0, behavior: "smooth" })
    setIsMenuOpen(false)
  }

  const primaryNavLinks = [
    { href: "/", label: t.nav.home },
    { href: "/about", label: t.nav.about },
    { href: "/speakers", label: t.nav.speakers },
  ]

  const secondaryNavLinks = [
    { href: "/sponsorship", label: t.nav.sponsorship },
    { href: "/gallery", label: t.nav.gallery },
    { href: "/volunteer", label: t.nav.volunteer },
    { href: "/code-of-conduct", label: t.nav.codeOfConduct },
  ]

  const allNavLinks = [...primaryNavLinks, ...secondaryNavLinks]

  return (
    <nav className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-7xl">
      <div
        className={cn(
          "backdrop-blur-xl rounded-2xl shadow-lg px-6 py-4 border transition-colors duration-200",
          isHomePage
            ? "bg-primary/75 border-primary-foreground/20 dark:bg-background/75 dark:border-foreground/25"
            : "bg-card/90 border-border/80 dark:bg-background/80 dark:border-foreground/25",
        )}
      >
        <div className="flex items-center justify-between">
          <Link
            href="/"
            onClick={handleNavClick}
            className={cn(
              "text-xl font-bold transition-colors",
              isHomePage ? "text-primary-foreground dark:text-foreground" : "text-primary dark:text-foreground",
            )}
          >
            Django Mombasa
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            {primaryNavLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={handleNavClick}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-secondary",
                  pathname === link.href
                    ? isHomePage
                      ? "text-secondary"
                      : "text-secondary dark:text-primary"
                    : isHomePage
                      ? "text-primary-foreground/80"
                      : "text-foreground/80 dark:text-foreground",
                )}
              >
                {link.label}
              </Link>
            ))}

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "rounded-full gap-1",
                    isHomePage
                      ? "text-primary-foreground/80 hover:text-secondary"
                      : "text-foreground/80 dark:text-foreground hover:text-secondary",
                  )}
                >
                  <MoreHorizontal className="h-4 w-4" />
                  <span className="text-sm font-medium">{t.nav.more || "More"}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {secondaryNavLinks.map((link) => (
                  <DropdownMenuItem key={link.href} asChild>
                    <Link href={link.href} onClick={handleNavClick} className="cursor-pointer">
                      {link.label}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className={cn(
                "rounded-full",
                isHomePage
                  ? "text-primary-foreground hover:text-secondary"
                  : "text-foreground hover:text-secondary dark:text-foreground",
              )}
            >
              <Languages className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setLanguage("en")} className={language === "en" ? "bg-accent" : ""}>
                  English
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setLanguage("sw")} className={language === "sw" ? "bg-accent" : ""}>
                  Kiswahili
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className={cn(
                "rounded-full",
                isHomePage ? "text-primary-foreground hover:text-secondary" : "text-foreground hover:text-secondary",
              )}
            >
              {theme === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className={cn(
                "rounded-full",
                isHomePage
                  ? "text-primary-foreground hover:text-secondary"
                  : "text-foreground hover:text-secondary dark:text-foreground",
              )}
            >
              <Languages className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setLanguage("en")} className={language === "en" ? "bg-accent" : ""}>
                  English
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setLanguage("sw")} className={language === "sw" ? "bg-accent" : ""}>
                  Kiswahili
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className={cn(
                "rounded-full",
                isHomePage ? "text-primary-foreground hover:text-secondary" : "text-foreground hover:text-secondary",
              )}
            >
              {theme === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className={cn(
                "rounded-full",
                isHomePage ? "text-primary-foreground hover:text-secondary" : "text-foreground hover:text-secondary",
              )}
            >
              {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pt-4 border-t border-border space-y-2">
            {allNavLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={handleNavClick}
                className={cn(
                  "block px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                  pathname === link.href
                    ? "bg-primary text-primary-foreground"
                    : "text-foreground/80 dark:text-foreground hover:bg-muted hover:text-foreground dark:hover:text-primary-foreground",
                )}
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  )
}
