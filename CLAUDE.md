# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Rules

- **NEVER** delete or remove content from any file (code, config, requirements, etc.) without first asking for permission and explaining clearly why the deletion is necessary.
- When editing files, preserve existing content unless explicitly told to remove it.
- If a change would result in lost functionality or removed lines, flag it and wait for approval before proceeding.
- **When creating or editing a Django app, do not change any "batteries-included" format from the default Django app.** Keep the default `apps.py`, `admin.py`, `models.py`, `views.py`, `tests.py`, and `migrations/` layout that `startapp` produces. Don't restructure or remove the default files even if they're empty stubs.
- **Do not make any git commit unless explicitly told to.** Stage and edit files freely, but never run `git commit` (or `git push`) until the user explicitly asks for it.

## Project Overview

Django Mombasa is a community website for the Django Mombasa developer community, built with **Django 6.0.2**. It manages member registrations, events, CMS pages, organizers, partners, sponsors, and social media links.

Runtime note: project documentation references Python 3.14 as the target runtime, but the production `Dockerfile` currently pins `python:3.12-slim`. Confirm the intended runtime before changing either.

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
python manage.py test membership.tests.MemberIdSequenceTest.test_get_next_id_starts_at_zero

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
  urls.py             Root URL configuration (mounts admin at /dashboard/)
  wsgi.py             WSGI entrypoint (defaults to prod settings)
  asgi.py             ASGI entrypoint (defaults to prod settings)
accounts/             Email-based custom user model and authentication
  models.py           User model (AbstractUser, email login)
  managers.py         CustomUserManager (create_user, create_superuser)
  backends.py         EmailBackend authentication
  admin.py            UserAdmin with import/export
app/                  Core pages, CMS content, team, partner/sponsor, and social link models
  models.py           Page, Organizer, Partner, Sponsor, SocialLink
  views.py            Homepage, team, apps, and CMS page views
  urls.py             App-level routing under app_name='app'
  forms.py            Default Django app file, currently unused
  admin.py            Import/export + Summernote admin registrations for app models
  context_processors.py  Injects social_links globally
  tests.py            Default Django app test file
membership/           Member registration, lookup, data request flows, and member ID generation
  models.py           MemberIdSequence, Member
  forms.py            MemberJoinForm, MemberLookupForm
  views.py            Membership page, join, lookup, email/data request flows
  urls.py             Routes mounted at /membership/
  tests.py            Member ID generation tests, including concurrency coverage
events_and_activities/ Event and tag models plus event list/detail pages
  models.py           Tag, Event
  views.py            Event listing and detail views
  urls.py             Routes for /events/ and /event/<slug>/
  templatetags/
    text_utils.py     truncate_sentences filter
templates/
  layout/             Shared components (base.html, navbar.html, footer.html)
  admin/              Admin overrides (base_site.html, color_theme_toggle.html)
  app/                App-specific templates (list_apps.html)
  membership/         Membership templates
  events_and_activities/ Event list/detail templates
  *.html              Top-level page templates (index, team, page, error pages)
static/
  css/                styles.css (site theme), admin.css (admin branding)
  images/             logo.jpg
  geojson/            kenya-counties.geojson
deploy/               Server deployment helpers (DEPLOY.md, gunicorn.service, nginx.conf, setup.sh)
Dockerfile            Production container image (python:3.12-slim + gunicorn)
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

Domain models are split by responsibility. `accounts.User` is the custom auth model; `membership` owns members and ID sequencing; `events_and_activities` owns events and tags; `app` owns CMS/team/partner/sponsor/social-link content.

- **User** (`accounts`) — custom user model with email-based authentication (`USERNAME_FIELD = 'email'`). Extends `AbstractUser` with `username` removed. `AUTH_USER_MODEL = 'accounts.User'`.
- **MemberIdSequence** (`membership`) — singleton table for race-safe member ID generation. `get_next_id()` uses `select_for_update()` inside an atomic transaction and returns IDs starting at `DM-000`, zero-padded to three digits.
- **Member** (`membership`) — registered members with auto-generated ID (`DM-XXX`). Fields: `member_id`, `name`, `email` (unique), `phone`, `gender`, `year_of_birth`, `experience_level`, `primary_language`, `receive_regular_updates`, `receive_email_communications`, `joined_at`. ID generated via `MemberIdSequence.get_next_id()` on first save.
- **Tag** (`events_and_activities`) — event categorisation (`name`, unique).
- **Event** (`events_and_activities`) — community events. Fields: `name`, `slug` (unique `SlugField`, auto-generated from `name` on save when blank), `tags` (M2M to `Tag`), `date`, `rsvp_link`, `details` (TextField). Default ordering: ascending by `date`.
- **Page** (`app`) — CMS pages edited with Summernote WYSIWYG (`title`, `slug`, `content`, `updated_at`).
- **Organizer** (`app`) — powers the `/team/` page. Fields: `first_name`, `last_name`, `community_role`, `professional_role`, `location`, `photo` (→ `organizers/`), `github_url`, `linkedin_url`, `twitter_url`, `website_url`, `order`.
- **Partner** (`app`) — `name`, `description`, `logo` (→ `partners/`), `website_url`, `events` (M2M to `events_and_activities.Event`), `order`.
- **Sponsor** (`app`) — same shape as `Partner` plus `tier` choices (`platinum`, `gold`, `silver`, `bronze`, `community`; default `community`). Logos upload to `sponsors/`.
- **SocialLink** (`app`) — social media links rendered in the footer (`name`, `icon_class`, `url`, `order`).

## URL Structure

```
/                                           Homepage
/events/                                    Events listing (upcoming + past)
/event/<slug>/                              Event detail
/team/                                      Organizers / team page
/apps/                                      Apps listing page
/membership/                                Membership info page
/membership/join/                           Member registration form
/membership/join/success/<member_id>/       Registration confirmation
/membership/join/send-id/<member_id>/       Email member ID
/membership/lookup/                         Member lookup
/membership/lookup/request-details/<id>/    Data access request (sends email)
/membership/lookup/request-deletion/<id>/   Data deletion request (sends email)
/page/<slug>/                               Dynamic CMS pages
/dashboard/                                 Django admin
/summernote/                                Summernote editor endpoints
```

## Third-Party Packages

- **django-import-export** — CSV/Excel import/export for all admin models
- **django-summernote** — WYSIWYG editor for `Page.content`
- **whitenoise** — Serves static files in production with compression and cache-busting
- **gunicorn** — Production WSGI server
- **psycopg** / **psycopg-binary** — PostgreSQL adapter (production)
- **pillow** — Required for `ImageField` (organizers, partners, sponsors)
- **python-telegram-bot**, **httpx** — Listed in `requirements.txt` but no consumer code is checked in; treat as reserved/unused until referenced.

## Key Patterns

- All templates extend `templates/layout/base.html`, which includes `navbar.html` and `footer.html`.
- `app/context_processors.social_links` is registered in `TEMPLATES.OPTIONS.context_processors` and injects `social_links` globally.
- Admin uses `SummernoteModelAdmin` + `ImportExportModelAdmin` for `Page`; all other admin classes use `ImportExportModelAdmin` with `ModelResource` classes.
- Admin is branded with project logo and colors (`static/css/admin.css`, `templates/admin/base_site.html`, `templates/admin/color_theme_toggle.html`).
- Forms use Bootstrap 5 CSS classes (`form-control`, `form-select`, `form-check-input`).
- Member ID generation is race-safe via `membership.models.MemberIdSequence` with atomic transactions and `select_for_update()`.
- Event listings use the `truncate_sentences` template filter from `events_and_activities/templatetags/text_utils.py`.

## Environment Variables

### Development (config.settings.dev)
No environment variables required. Sensible defaults are provided.

### Production (config.settings.prod)
| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `ALLOWED_HOSTS` | Yes | Comma-separated hosts (e.g., `example.com,www.example.com`) |
| `CSRF_TRUSTED_ORIGINS` | No | Comma-separated origins with scheme (e.g., `https://example.com`) |
| `ENABLE_HTTPS` | No | Set to `true` to enable SSL redirect, secure cookies, and HSTS |
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
- **Static files**: WhiteNoise middleware serves compressed static files in production (`CompressedManifestStaticFilesStorage`)
- **Media files**: `MEDIA_ROOT = BASE_DIR / 'media'` (organizer/partner/sponsor logos and Summernote uploads)
- **Admin**: Mounted at `/dashboard/` — branded with project logo and color scheme

## Testing

- Run all tests: `python manage.py test`
- `membership/tests.py` covers `MemberIdSequence` (start at `DM-000`, increment, formatting, persistence) and `Member` ID auto-assignment (auto-id, sequential, immutability on update, uniqueness, no-reuse-after-delete).
- A concurrent-creation test (`ConcurrentMemberCreationTest.test_concurrent_creation_no_duplicates`) is skipped under SQLite because SQLite does not support the same concurrent-write semantics as PostgreSQL — run it against PostgreSQL when changing member ID logic.
- `app/tests.py` and `events_and_activities/tests.py` are currently stubs.

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
- `Dockerfile` — Builds the app image (currently `python:3.12-slim`), installs dependencies, runs collectstatic
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

### Manual / VM

The `deploy/` directory contains `DEPLOY.md`, a `gunicorn.service` unit, an `nginx.conf` example, and a `setup.sh` for non-containerised server deployments.

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
