# SkiTunes

A searchable database of the songs used in ski and snowboard films, with one-click
export of any search result into a real Spotify playlist. Live at
`skitunes.nickknows.net`.

Users log in with Google or a local account, link their Spotify account, browse or
filter the catalog by movie, year, production company, skier, song, artist, album,
segment type, or location, tick the tracks they want, and the app creates the
playlist on their Spotify account.

Project status and the working to-do list live in [IDEA.md](IDEA.md).

## Running locally

```
export FLASK_APP=wsgi.py
export FLASK_DEBUG=1
flask db upgrade
flask run
```

Without `DATABASE_URL` set, the app falls back to a local SQLite database.
`FLASK_SECRET` and `MAIL_PASSWORD` also come from the environment, and the Google
and Spotify OAuth credentials from `skitunes/skitunes/variables/variables.py`.

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
| CI | GitHub Actions (`.github/workflows/build_and_deploy.yaml`) |

## Layout

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
skitunes/skitunes/metrics/        health check
skitunes/skitunes/logs/           report viewer (not currently registered)
skitunes/migrations/              Alembic
helm-chart/                       rollout, CNPG cluster, ExternalSecret, ingress, services
```

## Data model

`Movie` is the parent, `ski_movie_song_info` (songs) the child, joined by
`songs.movie_id → movies.movie_id`.

## Deploys

Pushes touching `skitunes/**` or `Dockerfile` build and push `ncging/skitunes-app`,
then commit the new tag into `helm-chart/values.yaml`, which Argo picks up and rolls
out blue/green. Schema changes are **not** applied automatically — run
`flask db upgrade` against the cluster.
