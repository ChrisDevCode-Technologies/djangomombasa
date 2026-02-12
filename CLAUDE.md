# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django Mombasa is a community website for the Django Mombasa developer community, built with **Django 6.0.2** and **Python 3.14**. It manages member registrations, events, CMS pages, and social media links.

## Development Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server (uses config.settings.dev by default)
python manage.py runserver

# Run migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Run tests
python manage.py test

# Run a specific test
python manage.py test app.tests.TestClassName.test_method_name

# Create superuser for admin access
python manage.py createsuperuser

# Django shell
python manage.py shell

# Collect static files (required before production deployment)
python manage.py collectstatic --noinput
```

## Docker Commands

```bash
# Build and start production containers (PostgreSQL + Django/Gunicorn)
docker compose up --build -d

# View logs
docker compose logs -f web

# Run management commands inside the container
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell

# Stop containers
docker compose down

# Stop and remove volumes (deletes database data)
docker compose down -v
```

## Architecture

```
config/
  settings/
    __init__.py       Package marker
    base.py           Common settings (apps, middleware, templates, DB, etc.)
    dev.py            Development settings (DEBUG=True, SQLite, no env vars required)
    prod.py           Production settings (DEBUG=False, PostgreSQL, strict env var requirements)
  urls.py             Root URL configuration
  wsgi.py             WSGI entrypoint (defaults to prod settings)
  asgi.py             ASGI entrypoint (defaults to prod settings)
app/                  Main application (models, views, forms, admin, context processors)
templates/
  layout/             Shared components (base.html, navbar.html, footer.html)
  admin/              Admin template overrides (base_site.html)
static/
  css/                styles.css (site theme), admin.css (admin branding)
  images/             logo.jpg
Dockerfile            Production container image (python:3.14-slim + gunicorn)
docker-compose.yml    Docker Compose (postgres:17-alpine + web service)
entrypoint.sh         Container entrypoint (migrate + gunicorn)
Procfile              PaaS deployment config (Heroku/Dokku)
```

## Settings Structure

| Module | Purpose | Database | Usage |
|--------|---------|----------|-------|
| `config.settings.dev` | Local development | SQLite | `manage.py` default, no env vars needed |
| `config.settings.prod` | Production / Docker | PostgreSQL | `wsgi.py`/`asgi.py` default, requires env vars |

Override with: `DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py ...`

## Models

- **MemberIdSequence** — singleton table for race-safe member ID generation
- **Tag** — event categorisation (name)
- **Event** — community events (name, date, rsvp_link, details, tags M2M)
- **Member** — registered members with auto-generated ID (DM-XXX format). Fields: name, email, phone, gender, year_of_birth, experience_level, primary_language. ID generated via `MemberIdSequence.get_next_id()` with `select_for_update()` locking.
- **Page** — CMS pages edited with Summernote WYSIWYG (title, slug, content, updated_at)
- **SocialLink** — social media links rendered in footer (name, icon_class, url, order)

## URL Structure

```
/                                           Homepage
/events/                                    Events listing (upcoming + past)
/membership/                                Membership info page
/membership/join/                           Member registration form
/membership/join/success/<member_id>/       Registration confirmation
/membership/join/send-id/<member_id>/       Email member ID
/membership/lookup/                         Member lookup
/membership/lookup/request-details/<id>/    Data access request (sends email)
/membership/lookup/request-deletion/<id>/   Data deletion request (sends email)
/page/<slug>/                               Dynamic CMS pages
/admin/                                     Django admin
/summernote/                                Summernote editor endpoints
```

## Third-Party Packages

- **django-import-export** — CSV/Excel import/export for all models in admin
- **django-summernote** — WYSIWYG editor for Page content in admin
- **whitenoise** — Serves static files in production with compression and caching
- **gunicorn** — Production WSGI server
- **psycopg** — PostgreSQL database adapter (production)

## Key Patterns

- All templates extend `templates/layout/base.html`, which includes `navbar.html` and `footer.html`
- `app/context_processors.py` injects `social_links` globally into all templates
- Admin uses `SummernoteModelAdmin` + `ImportExportModelAdmin` for Page model
- All other admin classes use `ImportExportModelAdmin` with `ModelResource` classes
- Admin is branded with project logo and colors (`static/css/admin.css`, `templates/admin/base_site.html`)
- Forms use Bootstrap 5 CSS classes (`form-control`, `form-select`)
- Member ID generation is race-safe using `MemberIdSequence` with atomic transactions

## Environment Variables

### Development (config.settings.dev)
No environment variables required. Sensible defaults are provided.

### Production (config.settings.prod)
| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `ALLOWED_HOSTS` | Yes | Comma-separated hosts (e.g., `example.com,www.example.com`) |
| `CSRF_TRUSTED_ORIGINS` | No | Comma-separated origins with scheme (e.g., `https://example.com`) |
| `EMAIL_HOST_PASSWORD` | No | Gmail app password for SMTP |
| `DB_NAME` | No | PostgreSQL database name (default: `djangomombasa`) |
| `DB_USER` | No | PostgreSQL user (default: `postgres`) |
| `DB_PASSWORD` | Yes* | PostgreSQL password (*required when using Docker/PostgreSQL) |
| `DB_HOST` | No | Database host (default: `localhost`, `db` in Docker Compose) |
| `DB_PORT` | No | Database port (default: `5432`) |

See `.env.example` for full documentation.

## Configuration Notes

- **Database (dev)**: SQLite (`db.sqlite3`)
- **Database (prod)**: PostgreSQL via environment variables in `config/settings/prod.py`
- **Timezone**: Africa/Nairobi
- **Email**: Gmail SMTP (`djangomombasake@gmail.com`) in prod, console backend in dev
- **Static files**: WhiteNoise middleware serves compressed static files in production
- **Media files**: `MEDIA_ROOT = BASE_DIR / 'media'` (Summernote uploads)
- **Admin**: `/admin/` — branded with project logo and color scheme

## Deployment

### Docker (Recommended)

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with production values

# Build and start
docker compose up --build -d

# Create superuser
docker compose exec web python manage.py createsuperuser
```

The Docker setup includes:
- `Dockerfile` — Builds the app image, installs dependencies, runs collectstatic
- `docker-compose.yml` — PostgreSQL 17 + Django/Gunicorn with health checks
- `entrypoint.sh` — Runs migrations then starts Gunicorn (3 workers, port 8000)

### PaaS (Heroku/Dokku)

```bash
# Set environment variables
export SECRET_KEY=your-production-key
export ALLOWED_HOSTS=example.com,www.example.com
export CSRF_TRUSTED_ORIGINS=https://example.com
```

The `Procfile` handles collectstatic and migrations in the release phase.

## Branding Colors

```
--dm-primary:       #0D3F2E   (dark green — header, buttons, primary actions)
--dm-primary-hover: #08281D   (darker green — hover states)
--dm-secondary:     #1F6B4C   (medium green — accents, links)
--dm-bg-light:      #F2F4F3   (off-white background)
--dm-dark-text:     #1A1A1A   (body text)
--dm-muted-text:    #6B7280   (secondary text)
--dm-border:        #D6DDD9   (borders)
```

Bootstrap 5.3.8 CSS variables are overridden to match in `static/css/styles.css`.
