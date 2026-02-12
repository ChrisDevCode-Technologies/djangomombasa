# Production Hardening Issue Backlog

This file tracks actionable issues derived from `DEPLOYMENT_READINESS_REPORT.md`.

## BLOCKERS

### ISSUE-001: Move `SECRET_KEY` to environment and rotate compromised key
- **Severity:** Blocker
- **Evidence:** `config/settings.py` has hardcoded `SECRET_KEY`.
- **Scope:** `config/settings.py`, deployment secrets
- **Acceptance criteria:**
  - `SECRET_KEY` is read from env var.
  - App fails fast in production when missing.
  - Existing committed key is rotated in deployed environments.

### ISSUE-002: Disable `DEBUG` in production via env-based config
- **Severity:** Blocker
- **Evidence:** `config/settings.py` sets `DEBUG = True`.
- **Scope:** settings management
- **Acceptance criteria:**
  - Production settings enforce `DEBUG=False`.
  - Local dev keeps explicit developer-friendly defaults.

### ISSUE-003: Configure `ALLOWED_HOSTS` and trusted origins from env
- **Severity:** Blocker
- **Evidence:** `config/settings.py` has `ALLOWED_HOSTS = []` and no `CSRF_TRUSTED_ORIGINS`.
- **Scope:** settings management
- **Acceptance criteria:**
  - `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` parsed from env CSV.
  - Production startup checks for non-empty `ALLOWED_HOSTS`.

### ISSUE-004: Add HTTPS and cookie hardening defaults for production
- **Severity:** Blocker
- **Evidence:** no HSTS/SSL/cookie security flags in settings.
- **Scope:** settings management
- **Acceptance criteria:**
  - `SECURE_SSL_REDIRECT=True` in prod.
  - `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`.
  - HSTS configured with preload/include subdomains.

### ISSUE-005: Convert state-changing membership actions from GET to POST
- **Severity:** Blocker
- **Evidence:** URLs + templates use links for `send_member_id`, `request_details`, `request_deletion`.
- **Scope:** `app/urls.py`, `app/views.py`, templates
- **Acceptance criteria:**
  - Routes accept POST only (e.g., `@require_POST`).
  - Templates use forms with CSRF tokens.
  - Direct GET requests return 405.

### ISSUE-006: Make member ID generation race-safe
- **Severity:** Blocker
- **Evidence:** `Member.save()` derives next ID from latest row without transaction-safe sequence.
- **Scope:** `app/models.py`, migration(s)
- **Acceptance criteria:**
  - No duplicate `member_id` under concurrent create attempts.
  - Add tests for concurrent/rapid creation behavior.

### ISSUE-007: Add dependency manifest with pinned versions
- **Severity:** Blocker
- **Evidence:** no `requirements*.txt` or `pyproject.toml` present.
- **Scope:** repo root dependency management
- **Acceptance criteria:**
  - Add reproducible dependency definition with exact/pinned versions.
  - Include install instructions in project docs.

### ISSUE-008: Add CI workflow for lint, tests, security, deploy checks
- **Severity:** Blocker
- **Evidence:** no CI workflow found.
- **Scope:** `.github/workflows/`
- **Acceptance criteria:**
  - CI runs lint + tests + `manage.py check --deploy`.
  - Dependency vulnerability scan included.
  - Required checks documented.

## HIGH PRIORITY

### ISSUE-009: Introduce settings split (`base/dev/prod`)
- **Severity:** High
- **Evidence:** single `config/settings.py` used by manage.py/wsgi/asgi.
- **Scope:** `config/settings/` package + entrypoints
- **Acceptance criteria:**
  - `base.py`, `dev.py`, `prod.py` in place.
  - `manage.py`, `wsgi.py`, `asgi.py` use environment-selected settings.

### ISSUE-010: Add production static file strategy (WhiteNoise or CDN)
- **Severity:** High
- **Evidence:** local-only static config.
- **Scope:** settings + deployment docs
- **Acceptance criteria:**
  - WhiteNoise middleware/storage enabled OR external static storage configured.
  - `collectstatic` integrated in release steps.

### ISSUE-011: Define media upload strategy for production
- **Severity:** High
- **Evidence:** local `MEDIA_ROOT` only.
- **Scope:** settings + infrastructure docs
- **Acceptance criteria:**
  - Choose and implement persistent volume or object storage backend.
  - Access controls and backup expectations documented.

### ISSUE-012: Add structured logging and error monitoring
- **Severity:** High
- **Evidence:** no `LOGGING` config or Sentry integration.
- **Scope:** settings + optional monitoring integration
- **Acceptance criteria:**
  - Structured logs emitted to stdout.
  - Error reporting pipeline documented and configurable.

## MEDIUM PRIORITY

### ISSUE-013: Move outbound email to background task queue
- **Severity:** Medium
- **Evidence:** synchronous `send_mail` calls in request/response cycle.
- **Scope:** app services + worker setup
- **Acceptance criteria:**
  - Membership emails dispatched asynchronously with retries.
  - User-facing response no longer blocks on SMTP.

### ISSUE-014: Improve query efficiency and cache social links context
- **Severity:** Medium
- **Evidence:** context processor queries DB on every request.
- **Scope:** `app/context_processors.py`
- **Acceptance criteria:**
  - Introduce low-TTL caching for social links.
  - Measure and reduce query count on common pages.

### ISSUE-015: Build core test suite for critical paths
- **Severity:** Medium
- **Evidence:** `app/tests.py` placeholder only.
- **Scope:** `app/tests/` or expanded test modules
- **Acceptance criteria:**
  - Tests cover join flow, lookup flow, privacy request actions, and permissions.
  - Tests validate POST-only protections and member ID generation behavior.

## Suggested implementation order
1. ISSUE-001 to ISSUE-006 (security/correctness blockers)
2. ISSUE-007 to ISSUE-008 (supply-chain + CI guardrails)
3. ISSUE-009 to ISSUE-012 (deployment architecture)
4. ISSUE-013 to ISSUE-015 (reliability and confidence)
