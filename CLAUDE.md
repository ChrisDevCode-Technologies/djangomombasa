# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django Mombasa is a community website for the Django Mombasa developer community, built with **Django 6.0.2** and **Python 3.14**. It manages member registrations, events, CMS pages, and social media links.

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

# Run tests
python manage.py test

# Run a specific test
python manage.py test app.tests.TestClassName.test_method_name

# Create superuser for admin access
python manage.py createsuperuser

# Django shell
python manage.py shell
```

## Architecture

```
config/             Django project configuration (settings, urls, wsgi/asgi)
app/                Main application (models, views, forms, admin, context processors)
templates/          HTML templates
  layout/           Shared components (base.html, navbar.html, footer.html)
  admin/            Admin template overrides (base_site.html)
static/
  css/              styles.css (site theme), admin.css (admin branding)
  images/           logo.jpg
```

The settings module is `config.settings`. URLs are routed through `config.urls` → `app.urls`.

## Models

- **Tag** — event categorisation (name)
- **Event** — community events (name, date, rsvp_link, details, tags M2M)
- **Member** — registered members with auto-generated ID (DM-XXX format). Fields: name, email, phone, gender, year_of_birth, experience_level, primary_language
- **Page** — CMS pages edited with Summernote WYSIWYG (title, slug, content, updated_at). Used for Data Protection, Code of Conduct, etc.
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

## Key Patterns

- All templates extend `templates/layout/base.html`, which includes `navbar.html` and `footer.html`
- `app/context_processors.py` injects `social_links` globally into all templates
- Admin uses `SummernoteModelAdmin` + `ImportExportModelAdmin` for Page model
- All other admin classes use `ImportExportModelAdmin` with `ModelResource` classes
- Admin is branded with project logo and colors (`static/css/admin.css`, `templates/admin/base_site.html`)
- Forms use Bootstrap 5 CSS classes (`form-control`, `form-select`)
- Member ID auto-generates on save: DM-000, DM-001, etc.

## Configuration Notes

- **Database**: SQLite (`db.sqlite3`)
- **Timezone**: Africa/Nairobi
- **Email**: Gmail SMTP (`djangomombasake@gmail.com`), password via `EMAIL_HOST_PASSWORD` env var
- **Static files**: `STATICFILES_DIRS = [BASE_DIR / 'static']`, `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- **Media files**: `MEDIA_ROOT = BASE_DIR / 'media'` (Summernote uploads)
- **Admin**: `/admin/` — branded with project logo and color scheme

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
