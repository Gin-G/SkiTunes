---
status: in-progress
progress: 70
---

# SkiTunes

A searchable database of the songs used in ski and snowboard films, with one-click
export of any search result into a real Spotify playlist. Live at
`skitunes.nickknows.net` (public domain: skimoviesongs.com).

Users log in with Google or a local account, link their Spotify account, browse or
filter the catalog by movie, year, production company, skier, song, artist, album,
segment type, or location, tick the tracks they want, and the app creates the
playlist on their Spotify account.

---

## Stack

| Layer | Choice |
| --- | --- |
| Backend | Python 3.10, Flask, SQLAlchemy ORM, Flask-Migrate |
| Auth | Flask-Login + Google OAuth (oauthlib) + local email/password |
| Third-party | Spotify OAuth + Web API (playlist create, track add, song search) |
| Templates | Jinja2 + vanilla JS (`static/app.js`, `static/export.js`) |
| Database | SQLite (dev) → PostgreSQL via CloudNativePG (prod) |
| Packaging | Docker → Docker Hub (`ncging/skitunes-app`) |
| Deploy | Kubernetes via Helm, Argo Rollouts blue/green, External Secrets ← OpenBao |
| CI | GitHub Actions on a self-hosted ARC runner set |

### Layout

```
skitunes/wsgi.py                  entrypoint, port 8000
skitunes/skitunes/__init__.py     app factory: Flask, SQLAlchemy, Migrate, Login
skitunes/skitunes/config.py       config from env (DATABASE_URL, FLASK_SECRET, MAIL_PASSWORD)
skitunes/skitunes/main/           home, browse, filter/search, playlist create, CRUD
skitunes/skitunes/auth/           Google OAuth, local login/register, Spotify OAuth
skitunes/skitunes/spotify/        Movie + ski_movie_song_info models, Spotify API calls
skitunes/skitunes/account/        User model
skitunes/skitunes/crowd/          PendingEntry + EntryVote, suggest/vote/approve queue
skitunes/skitunes/imports/        CSV bulk import, template download, manual entry
skitunes/skitunes/metrics/        health check (currently shadowed — see below)
skitunes/skitunes/logs/           report viewer (not registered — see below)
skitunes/migrations/              Alembic
helm-chart/                       rollout, CNPG cluster, ExternalSecret, ingress, services
```

---

## Done

### Core product
- Full catalog browse (`/skitunes/skibase`) plus a lightweight mobile variant
  (`skibase_lite`), auto-selected by User-Agent.
- Filter routes for movie, production company, year, skier, song, artist, album,
  location, and segment type — each with a desktop and a `_lite` mobile variant.
- Combined search form (song name / artist / year / year range) at `/skitunes/findmovie`.
- Movie detail, movie-by-year, and movie-by-production-company views.
- Select / select-all across a filtered result set, then **Create Playlist** →
  builds the playlist on the user's Spotify account and adds the tracks,
  chunked in batches of 100 to stay inside Spotify's per-request limit.
- Deduplication of track URIs before submission.
- Correction-suggestion form that diffs a user's edits against the stored record
  and emails the changes for approval.
- Admin CRUD: new entry, edit entry, delete entry, admin user list.

### Data model
- **Rebuilt from the original inverted schema.** `Movie` is now the parent and
  `ski_movie_song_info` (songs) the child, joined by `songs.movie_id → movies.movie_id`.
  Previously the song table was the parent, which made every movie-level query awkward.
- `format()` on the song model resolves movie name / year / production company
  through the relationship, so the JSON export survived the schema change.

### Crowdsourced submissions (shipped Mar 2026)
- `PendingEntry` and `EntryVote` tables with a unique constraint so a user can
  only confirm a given entry once.
- `/skitunes/suggest` — any logged-in user can propose a song/movie pair.
- `/skitunes/pending` — queue showing confirmation counts.
- Auto-promotion into the live catalog at **5 confirmations**; submitters cannot
  vote for their own entry.
- Admin approve / reject overrides.

### Bulk import
- CSV upload with a downloadable template, plus a JSON bulk importer that
  skips duplicates on (song name, artist, movie name, movie year).

### Infrastructure & hardening
- **Flask-Migrate added**; the old `db.create_all()` on `before_request` removed.
  Schema now comes from `flask db upgrade`.
- `/health` endpoint added — the K8s readiness and liveness probes depend on it.
- `DATABASE_URL` read from the environment (falls back to SQLite for local dev);
  the CNPG-generated `skitunes-pgdb-app` secret supplies the URI in-cluster.
- `MAIL_PASSWORD` replaces the old hardcoded `PEANUT_BRITTLE` value and is
  injected from OpenBao through the ExternalSecret.
- `OAUTHLIB_INSECURE_TRANSPORT` now only set when `FLASK_DEBUG=1`, instead of
  unconditionally disabling TLS enforcement on OAuth in production.
- **User IDs are UUIDs.** Local registration previously used `max(id)+1`, which
  was both a race condition and a collision risk against Google's `sub` IDs.
- Passwords hashed with Werkzeug `generate_password_hash` / `check_password_hash`.
- Debug `print()` statements stripped from `auth/views.py` and `account/models.py`.
- Registration errors no longer leak password-related internals to the user.
- Pagination (50/page) on `skibase` and `skibase_lite`.
- `edit_entry` fixed — it used to insert a duplicate row instead of updating.
- `new_entry` restricted to admins.
- K8s resource requests corrected from `0` to 100m CPU / 128Mi memory.
- PostgreSQL migrated to a CloudNativePG-managed cluster.
- Blue/green rollout with a preview service and ingress, auto-promoting after 30s.
- ARC-runner CI: verifies the Flask app imports, builds with remote BuildKit,
  pushes `skitunes-app:latest` and a dated tag, then rewrites `values.yaml`
  with the new tag and pushes the commit back.
- Log files removed from git tracking.

---

## Remaining work

### Broken — user-visible

1. **Password reset is completely non-functional.** `/reset_password_request` and
   `/reset_password/<token>` exist and are linked, but every dependency is missing:
   - `User.generate_reset_token()` and `User.verify_reset_token()` are not
     implemented (`account/models.py`)
   - there are no `reset_token` / `reset_token_expiration` columns on `User`
   - `bcrypt` is never imported in `auth/views.py:227`, so the handler would
     `NameError` even if it got that far
   - the templates `reset_password_request.html` and `reset_password.html`
     don't exist
   - the sender is hardcoded to the placeholder `your-email@gmail.com`
     (`auth/views.py:193`)

   Hitting either route today is a 500. Needs the token methods (itsdangerous or
   a signed column), a migration, the two templates, and the import.

2. **Year-range search silently returns nothing.** In `findmovie`
   (`main/views.py:138`, `:197`, `:256`) the comparison and the range are
   inverted in both branches — when `movie_year > movie_year2` it builds
   `range(movie_year, movie_year2 + 1)`, which is empty, and the mirrored branch
   has the same defect. No year range ever produces results.

3. **`/correct_entry` is not login-gated** (`main/views.py:529`). Every other
   mutating route has `@login_required`; this one lets an anonymous visitor
   trigger outbound email through the app's SMTP credentials. Rate-limit or gate it.

4. **Wrong original value in three correction diffs.** The ski_type, location,
   and video_link messages all interpolate `orig_song_name`
   (`main/views.py:591`, `:594`, `:597`), so correction emails report nonsense
   for those fields.

5. **Movie rows are duplicated on every insert.** `new_entry`
   (`main/views.py:471`), `bulk_import` (`:645`), and the crowd promoter
   (`crowd/views.py:14`) each construct a fresh `Movie` rather than looking one
   up. Adding a second song from an existing film creates a second movie row,
   which fragments the by-movie and by-year views. Needs a get-or-create keyed on
   (name, year, company) — and a cleanup pass over whatever duplicates already exist.

6. **`delete_entry` orphans the movie.** It deletes the song and leaves the
   `Movie` row behind with no children.

### Correctness / dead code

7. **Two routes claim `/health`** — `main/views.py:22` and
   `metrics/views.py:4`. `main` is imported first and wins; the entire `metrics`
   module is dead. Delete one.

8. **The `logs` blueprint is never imported** in `__init__.py`, so `/Reports`,
   `/Reports/<filename>`, and `/Reports/download/<filename>` are unregistered
   dead code. If they're ever wired up they need auth first — they read
   arbitrary filenames out of the log directory with no access control.

### Tech debt

9. **`findmovie` is triplicated.** ~180 lines copy-pasted three times
   (`main/views.py:105–287`) for iPhone / Android / desktop, differing only in
   which template is rendered. One search implementation plus a template
   selector would remove ~120 lines and mean bugs like #2 get fixed once.

10. **The admin allowlist is hardcoded in four places** with two different
    memberships — `main/views.py:463`, `main/views.py:684`, `crowd/views.py:10`,
    and `imports/views.py` (which also grants `ncote@ucar.edu`). Needs an
    `is_admin` column on `User` and a single decorator.

11. **Contact email hardcoded** as `NickCo7@gmail.com` in `main/views.py:599`
    and `config.py:11–12`. Move to config/env.

12. **Filter routes have no pagination.** Only `skibase` and `skibase_lite` were
    paginated; all fifteen filter and search routes still `.all()` the full
    result set into memory and render it in one page.

13. **The container runs the Flask development server.** `Dockerfile` ends with
    `CMD ["python3", "wsgi.py", "--hot=0.0.0.0"]` — single-threaded, not
    production-grade, and the `--hot` flag isn't a real argument. Should be
    gunicorn behind the existing nginx config.

14. **No migration step in the deploy.** The Helm chart never runs
    `flask db upgrade`; schema changes have to be applied by hand against the
    CNPG cluster. Wants an init container or a Helm pre-upgrade hook Job.

15. **`rollout.yaml` reads the wrong values key.** Line 12 uses
    `.Values.replicaCount`, but `values.yaml` defines `webapp.replicaCount` —
    so `replicas:` renders empty and the rollout falls back to the default.

16. **Redundant legacy CI workflow.** `build_image.yaml` fires on the same paths
    as the ARC workflow and pushes to the stale `ncging/skitunes` repo (the
    chart pulls `ncging/skitunes-app`). It also references
    `steps.meta.output.labels`, a step that doesn't exist. Delete it.

17. **No dependency pinning.** `requirements.txt` lists fifteen packages with no
    versions, so any build can pull a breaking release.

18. **No test suite.** `skitunes/test.py` is a one-off CSV-to-Spotify data
    munging script, not tests. CI's only check is that the app imports.

19. **Repo hygiene** — `helm-chart/templates/esos copy.yaml` is a stray
    duplicate, several `.DS_Store` files are tracked, and raw data files
    (`songs.csv`, `SkiMovieSongs.csv`, `Steve_data.csv`, `out.csv`,
    `clean_data.json`, `playlist.json`, `instance/skitunes.db`) sit alongside
    application code. `bulk_import` reads `clean_data.json` from a hardcoded
    relative path.

### Never built (from the original TODO)

20. **Donation link / setup** — listed in `TODO`, no implementation.
21. **Contribute page** — partially superseded by the crowdsourced suggestion
    queue, but there's still no standalone contribute/about page.
