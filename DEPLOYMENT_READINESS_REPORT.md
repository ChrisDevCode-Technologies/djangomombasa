# Deployment Readiness Report

## Executive summary

The repository is currently **not production-ready**. The most critical blockers are insecure default settings (`DEBUG=True`, hardcoded `SECRET_KEY`, empty `ALLOWED_HOSTS`), missing dependency and deployment manifests, and unsafe state-changing GET endpoints for member data workflows.

## Top 10 issues (ranked)

### Blockers
1. Hardcoded `SECRET_KEY` in versioned settings.
2. `DEBUG=True` in the only settings module.
3. `ALLOWED_HOSTS` empty in default runtime settings.
4. No production security settings (`SECURE_SSL_REDIRECT`, HSTS, secure cookies, etc.).
5. State-changing actions are implemented as GET routes (`send_member_id`, `request_details`, `request_deletion`).
6. Member ID generation is race-prone and can produce duplicates under concurrent writes.
7. No dependency lock file or requirements manifest tracked in repository.
8. No CI/CD workflow for tests/lint/security checks.
9. No tests for critical auth/privacy/member workflows.
10. Static/media strategy is dev-oriented and lacks production storage/caching plan.

### Warnings
- Synchronous email sends in request cycle can increase latency and fail user requests.
- Global context processor executes DB query on every request.
- Default database is SQLite and unsuitable for most multi-instance production deployments.

## Deployment checklist (Django baseline)

| Item | Status | Evidence | Fix |
|---|---|---|---|
| `DEBUG=False` in production | ❌ | `config/settings.py` sets `DEBUG = True` | Use env-based settings and default to `False` in prod profile |
| `SECRET_KEY` from environment | ❌ | `config/settings.py` hardcodes key | Read from `DJANGO_SECRET_KEY`; fail fast if missing in prod |
| `ALLOWED_HOSTS` configured | ❌ | `config/settings.py` has `ALLOWED_HOSTS = []` | Parse CSV env var and enforce non-empty in prod |
| HTTPS/security headers | ❌ | no SSL/HSTS/cookie secure flags in settings | Add full secure settings block under prod mode |
| CSRF trusted origins | ❌ | no `CSRF_TRUSTED_ORIGINS` | Add env-driven origins list |
| Static file serving strategy | ⚠️ | only `STATIC_ROOT`, no WhiteNoise/CDN setup | Add WhiteNoise middleware/storage or external CDN |
| Media uploads strategy | ⚠️ | local `MEDIA_ROOT` only | Use S3-compatible storage in prod or dedicated volume |
| `check --deploy` | ⚠️ | command fails due missing Django env | Install dependencies and run in CI + release pipeline |
| Error monitoring/logging | ❌ | no logging dict, no Sentry integration | Add structured logging + optional Sentry DSN |
| Reproducible dependency install | ❌ | no `requirements*.txt` / `pyproject.toml` | Add pinned dependency manifest + lock process |

## Issue backlog

Track implementation work in `ISSUE_BACKLOG.md` (15 actionable issues grouped by severity and rollout order).

## PR-sized patch plan

### PR1 — Security blockers
- Introduce env-driven `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`.
- Add production security flags and CSRF trusted origins.
- Convert state-changing GET membership actions to POST-only forms + CSRF.
- Add rate-limiting approach note (e.g., django-axes or proxy-level limit).

### PR2 — Settings/env split
- Split into `config/settings/base.py`, `dev.py`, `prod.py` and thin loader.
- Add helper env parsing (`python-decouple` or `django-environ`).
- Keep dev defaults for local UX, strict fail-fast in prod.

### PR3 — Static/media + storage
- WhiteNoise for static assets and immutable caching.
- Define media strategy: local volume (small deploy) or S3 storage backend.
- Add `collectstatic` + migrate commands to deployment runbook.

### PR4 — Logging/monitoring/reliability
- Structured JSON logging and redaction filters.
- Configure admin email alerts and optional Sentry.
- Move email sends to background tasks (Celery/RQ) with retries.

### PR5 — CI/CD
- Add GitHub Actions for lint, test, `check --deploy`, and dependency audit.
- Add release checklist + smoke tests.

## Concrete snippets

### Env-driven security baseline
```python
# settings/base.py
import os
from django.core.exceptions import ImproperlyConfigured

DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY is required")

ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [u.strip() for u in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if u.strip()]
```

### Production-only hardening
```python
# settings/prod.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
```

### WhiteNoise static config
```python
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    # ...
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ...
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

### POST-only membership actions
```python
# app/urls.py
path("join/send-id/<str:member_id>/", views.send_member_id, name="send_member_id"),

# app/views.py
from django.views.decorators.http import require_POST

@require_POST
def send_member_id(request, member_id):
    ...
```

### Logging baseline
```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"}
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
```

## Runbook commands

```bash
# local prod-like run
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput

# start app (WSGI)
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60

# smoke tests
curl -I http://127.0.0.1:8000/
curl -I http://127.0.0.1:8000/admin/login/
```

## Notes on gaps
- Dependency and containerization files were not present in the repository root during inspection.
- `python manage.py check --deploy` could not execute because Django is not installed in this environment.
