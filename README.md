# Django Mombasa

Community website for the **Django Mombasa** developer community. Manages member registrations, events, CMS pages, and social media links.

Built with **Django 6.0.2** and **Python 3.14**.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development](#local-development)
  - [Docker (Production)](#docker-production)
- [Configuration](#configuration)
  - [Settings Structure](#settings-structure)
  - [Environment Variables](#environment-variables)
- [URL Routes](#url-routes)
- [Data Models](#data-models)
- [Admin Panel](#admin-panel)
- [Deployment](#deployment)
  - [Docker](#docker)
  - [PaaS (Heroku / Dokku)](#paas-heroku--dokku)
- [License](#license)

---

## Features

- **Member Registration** — Public sign-up form with auto-generated member IDs (`DM-000` format) using race-safe atomic sequences.
- **Member Lookup** — Search by member ID, name + phone, or phone + year of birth.
- **Data Privacy** — Members can request a copy of their data or request deletion, both handled via email.
- **Events** — Community events with date, RSVP link, details, and tag-based categorisation. Homepage shows upcoming events.
- **CMS Pages** — Dynamic pages with a WYSIWYG editor (Summernote) in the admin panel.
- **Social Links** — Footer social media links managed from the admin, rendered globally via a context processor.
- **Admin Panel** — Branded with project logo and colors. CSV/Excel import/export for all models.
- **Email Notifications** — Gmail SMTP in production, console backend in development.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Django 6.0.2 |
| Language | Python 3.14 |
| Database | SQLite (dev) / PostgreSQL 17 (production) |
| WSGI Server | Gunicorn |
| Static Files | WhiteNoise (compression + cache-busting) |
| Frontend | Bootstrap 5.3.8 |
| WYSIWYG Editor | django-summernote |
| Import/Export | django-import-export (CSV, Excel) |
| Containerisation | Docker + Docker Compose |

---

## Project Structure

```
djangomombasa/
├── config/                     # Project configuration
│   ├── settings/
│   │   ├── __init__.py         # Package marker
│   │   ├── base.py             # Common settings (apps, middleware, templates, DB)
│   │   ├── dev.py              # Development (DEBUG=True, SQLite, no env vars)
│   │   └── prod.py             # Production (DEBUG=False, PostgreSQL, env vars required)
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI entrypoint (defaults to prod settings)
│   └── asgi.py                 # ASGI entrypoint (defaults to prod settings)
├── app/                        # Main application
│   ├── models.py               # Data models (Member, Event, Page, Tag, SocialLink)
│   ├── views.py                # View functions
│   ├── forms.py                # MemberJoinForm, MemberLookupForm
│   ├── admin.py                # Admin configuration with import/export + Summernote
│   ├── urls.py                 # App URL patterns
│   ├── context_processors.py   # Injects social_links into all templates
│   ├── apps.py                 # App config
│   ├── tests.py                # Tests
│   └── migrations/             # Database migrations
├── templates/
│   ├── layout/                 # base.html, navbar.html, footer.html
│   ├── admin/                  # Admin template overrides (base_site.html)
│   ├── index.html              # Homepage
│   ├── events.html             # Events listing
│   ├── membership.html         # Membership info
│   ├── join.html               # Registration form
│   ├── join_success.html       # Registration confirmation
│   ├── lookup.html             # Member lookup
│   └── page.html               # Dynamic CMS page
├── static/
│   ├── css/
│   │   ├── styles.css          # Site theme (Bootstrap overrides)
│   │   └── admin.css           # Admin branding
│   └── images/
│       └── logo.jpg            # Project logo
├── manage.py                   # Django management (defaults to dev settings)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Production container image
├── docker-compose.yml          # Docker Compose (PostgreSQL + web)
├── entrypoint.sh               # Container entrypoint (migrate + gunicorn)
├── .dockerignore               # Files excluded from Docker build
├── .env.example                # Environment variable template
├── Procfile                    # PaaS deployment (Heroku/Dokku)
└── LICENSE                     # MIT License
```

---

## Getting Started

### Prerequisites

- **Python 3.14+**
- **Docker** and **Docker Compose** (for production / containerised setup)

### Local Development

No environment variables required. SQLite is used by default.

```bash
# Clone the repository
git clone https://github.com/your-username/djangomombasa.git
cd djangomombasa

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Visit `http://localhost:8000` for the site and `http://localhost:8000/admin/` for the admin panel.

### Docker (Production)

Runs Django with Gunicorn + PostgreSQL 17.

```bash
# Copy the environment template and fill in your values
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY, ALLOWED_HOSTS, and DB_PASSWORD
```

Required `.env` values for Docker:

```env
DJANGO_SETTINGS_MODULE=config.settings.prod
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com
DB_NAME=djangomombasa
DB_USER=postgres
DB_PASSWORD=a-strong-password
```

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Start the containers:

```bash
# Build and start in detached mode
docker compose up --build -d

# Create a superuser
docker compose exec web python manage.py createsuperuser

# View logs
docker compose logs -f web

# Stop containers
docker compose down
```

Visit `http://localhost:8000`.

---

## Configuration

### Settings Structure

The project uses a split settings pattern:

| Module | Purpose | Database | Usage |
|--------|---------|----------|-------|
| `config.settings.dev` | Local development | SQLite | Default for `manage.py`, no env vars needed |
| `config.settings.prod` | Production / Docker | PostgreSQL | Default for `wsgi.py`/`asgi.py`, requires env vars |

Both import from `config.settings.base` which contains shared configuration (installed apps, middleware, templates, email, static/media files, Summernote config).

Override the settings module with:

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py runserver
```

### Environment Variables

#### Development

No environment variables required. Sensible defaults are provided in `config/settings/dev.py`.

#### Production

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `ALLOWED_HOSTS` | Yes | Comma-separated hosts (e.g. `example.com,www.example.com`) |
| `CSRF_TRUSTED_ORIGINS` | No | Comma-separated origins with scheme (e.g. `https://example.com`) |
| `EMAIL_HOST_PASSWORD` | No | Gmail app password for SMTP |
| `DB_NAME` | No | PostgreSQL database name (default: `djangomombasa`) |
| `DB_USER` | No | PostgreSQL user (default: `postgres`) |
| `DB_PASSWORD` | Yes* | PostgreSQL password (*required when using Docker/PostgreSQL) |
| `DB_HOST` | No | Database host (default: `localhost`, set to `db` in Docker Compose) |
| `DB_PORT` | No | Database port (default: `5432`) |

See `.env.example` for a full template.

---

## URL Routes

| URL | Description |
|-----|-------------|
| `/` | Homepage with upcoming events |
| `/events/` | Events listing (upcoming + past) |
| `/membership/` | Membership info page |
| `/membership/join/` | Member registration form |
| `/membership/join/success/<member_id>/` | Registration confirmation |
| `/membership/join/send-id/<member_id>/` | Email member ID to member |
| `/membership/lookup/` | Member lookup |
| `/membership/lookup/request-details/<member_id>/` | Data access request (sends email) |
| `/membership/lookup/request-deletion/<member_id>/` | Data deletion request (sends email) |
| `/page/<slug>/` | Dynamic CMS pages |
| `/admin/` | Django admin panel |
| `/summernote/` | Summernote WYSIWYG editor endpoints |

---

## Data Models

### MemberIdSequence

Singleton table for race-safe member ID generation. Uses `select_for_update()` with atomic transactions to ensure unique, sequential IDs.

### Tag

Event categorisation labels.

| Field | Type |
|-------|------|
| `name` | CharField (max 50, unique) |

### Event

Community events.

| Field | Type |
|-------|------|
| `name` | CharField (max 200) |
| `tags` | ManyToManyField (Tag) |
| `date` | DateTimeField |
| `rsvp_link` | URLField (optional) |
| `details` | TextField |

### Member

Registered community members with auto-generated IDs.

| Field | Type |
|-------|------|
| `member_id` | CharField (auto-generated, format: `DM-000`) |
| `name` | CharField (max 200) |
| `email` | EmailField (unique) |
| `phone` | CharField (max 20, optional) |
| `gender` | CharField (choices: Male, Female) |
| `year_of_birth` | PositiveSmallIntegerField (optional) |
| `experience_level` | CharField (choices: Junior, Mid, Senior, For Fun) |
| `primary_language` | CharField (choices: Python, JavaScript, TypeScript, Java, C#, C++, C, Go, Rust, PHP, Ruby, Swift, Kotlin, Dart, R, SQL, Other) |
| `joined_at` | DateTimeField (auto) |

### Page

CMS pages editable with Summernote WYSIWYG in the admin.

| Field | Type |
|-------|------|
| `title` | CharField (max 200) |
| `slug` | SlugField (unique) |
| `content` | TextField (HTML via Summernote) |
| `updated_at` | DateTimeField (auto) |

### SocialLink

Social media links rendered in the site footer.

| Field | Type |
|-------|------|
| `name` | CharField (max 50) |
| `icon_class` | CharField (Bootstrap Icons class, e.g. `bi bi-linkedin`) |
| `url` | URLField |
| `order` | PositiveSmallIntegerField |

---

## Admin Panel

The admin panel is accessible at `/admin/` and features:

- **Branded interface** with the Django Mombasa logo and color scheme
- **CSV/Excel import/export** for all models via django-import-export
- **WYSIWYG editor** for Page content via django-summernote
- **Search and filters** on Member (by name, email, gender, experience level, language)
- **Tag management** with horizontal filter on Events

---

## Deployment

### Docker

The production Docker setup includes:

- **`Dockerfile`** — Python 3.14-slim base, installs PostgreSQL client libraries, copies the project, runs `collectstatic` at build time, and uses `entrypoint.sh` to run migrations and start Gunicorn.
- **`docker-compose.yml`** — Orchestrates two services:
  - `db` — PostgreSQL 17 (Alpine) with a persistent volume and health checks.
  - `web` — Django app served by Gunicorn on port 8000 with a media volume.

```bash
# Build and start
docker compose up --build -d

# Run management commands
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell

# Stop and remove containers
docker compose down

# Stop and remove containers + volumes (deletes database data)
docker compose down -v
```

### PaaS (Heroku / Dokku)

The `Procfile` handles deployment:

```
release: python manage.py collectstatic --noinput && python manage.py migrate --noinput
web: gunicorn config.wsgi --log-file -
```

Set the required environment variables on your PaaS platform, then deploy via `git push`.

---

## Development Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server
python manage.py runserver

# Run migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Run all tests
python manage.py test

# Run a specific test
python manage.py test app.tests.TestClassName.test_method_name

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic --noinput
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
