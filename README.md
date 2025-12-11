# Django Mombasa
[![DjangoDayMombasa Web CI](https://github.com/ChrisDevCode-Technologies/djangodaymombasa/actions/workflows/nextjs.yml/badge.svg)](https://github.com/ChrisDevCode-Technologies/djangodaymombasa/actions/workflows/nextjs.yml)
[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://djangobirthdaymombasa.vercel.app/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)

Celebrating 20 years of Django with the Mombasa community. This site provides event details, sponsorship information, registration instructions, volunteer coordination, and speaker guidelines in both English and Kiswahili.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Getting Started](#getting-started)
4. [Project Structure](#project-structure)
5. [Content & Localization](#content--localization)
6. [Deployments](#deployments)
7. [Contributing](#contributing)
8. [Code of Conduct](#code-of-conduct)
9. [License](#license)

---

## Features

- **Bilingual experience** — English and Kiswahili translations for every page.
- **Sponsor outreach** — Updated messaging for impact-focused sponsorship and direct email CTA.
- **Registration & RSVP flow** — Humorous, clear instructions for securing a spot via the Luma RSVP link.
- **Speaker guidance** — Local-first call for speakers with topics, timelines, and expectations.
- **Volunteer call-to-action** — Concise pitch and direct email contact for helpers.
- **Responsive design** — Optimized for mobile and dark mode readability.
- **CI ready** — GitHub Actions workflow to build and validate deployments.

---

## Tech Stack

- **Framework:** [Next.js 15 (App Router)](https://nextjs.org/)
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **Styling:** [Tailwind CSS 4](https://tailwindcss.com/) + custom OKLCH design tokens
- **Icons:** [lucide-react](https://lucide.dev/)
- **State & Context:** React Context (for language switching)
- **Deployment:** [Vercel](https://vercel.com/)
- **Tooling:** ESLint, npm scripts

---

## Getting Started

### Prerequisites

- Node.js **20.x**
- npm **10.x** (ships with Node 20)

### Installation

```bash
git clone https://github.com/ChrisDevCode-Technologies/djangodaymombasa.git
cd djangodaymombasa
npm install
```

### Useful Scripts

```bash
# Start local development server with hot reload
npm run dev

# Lint the project (recommended before committing)
npm run lint

# Create a production build
npm run build

# Preview the production build locally
npm run start
```

---

## Project Structure

```
app/                     # Next.js App Router pages
  page.tsx               # Landing page
  sponsorship/           # Sponsorship microsite
  speakers/              # Speaker application instructions
  registration/          # RSVP instructions
  volunteer/             # Volunteer CTA page
  code-of-conduct/       # Event conduct guidelines
components/              # Shared UI components
contexts/                # React context (language switching)
lib/translations.ts      # English & Kiswahili copy
styles/globals.css       # Tailwind directives & design tokens
.github/workflows/       # CI configuration
```

---

## Content & Localization

- All page copy resides in `lib/translations.ts`. Every string must exist in **both** the `en` and `sw` sections.
- The active language is controlled via the `LanguageContext`. Kiswahili loads first, and visitors can switch languages via the navbar.
- When adding new content:
  1. Add matching keys in `lib/translations.ts` (English & Kiswahili).
  2. Reference the new keys from the relevant component.
  3. Avoid hard-coded text in components unless it is truly static (e.g., email addresses).

---

## Deployments

- **Production:** https://djangobirthdaymombasa.vercel.app/
- Pushing to `main` triggers the **Next.js build workflow** defined in `.github/workflows/nextjs.yml`.
- Secrets (if any) are managed in Vercel’s dashboard.

---

## Contributing

We welcome contributions that improve copy, accessibility, translations, or functionality.

1. **Fork** the repository and create a feature branch  
   ```bash
   git checkout -b feature/your-idea
   ```
2. **Install dependencies** and run `npm run dev` to work locally.
3. **Update translations** in both languages when adjusting copy.
4. **Run linting** (`npm run lint`) to catch formatting or type issues.
5. **Commit** with a clear message and open a pull request targeting `main`.

Please keep PRs focused and add context describing what changed and why. If you’re unsure about an idea, open an issue to discuss it first.

---

## Code of Conduct

This project follows the [Django Code of Conduct](https://www.djangoproject.com/conduct/).  
If you need to report a concern, email **chris@chrisdevcode.com** — reports are handled discreetly.
---

## License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for the full text.
