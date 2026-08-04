---
status: active
progress: 70
---

# SkiTunes

<!--
IdeaBRD parses this file. It is the source of truth for this idea's tile:
the app re-reads it on every open and commits its own edits back here, so
the shape below matters more than it looks. Anything the parser
(backend/app/ideafile.py) can't read is dropped silently.

  frontmatter  status: one of idea, active, paused, done. progress: 0-100.
               Any other key is ignored.
  # heading    The idea title (first H1).
  prose        Everything outside the Todos section becomes the tile's
               notes, shown on the board — so keep it short. Documentation
               written here is published, not filed away.
  ## Todos     That heading exactly (or "## To-Dos"); "## ToDo", "## TODO"
               and "## Tasks" do not match and the whole list is lost.
               Inside it, only "- [ ] open" / "- [x] done" lines survive:
               sub-headings and blank-line grouping are discarded, and a
               wrapped item is cut at the line break, so keep each to-do on
               one line. The next "## " heading ends the list.
  (#12)        A to-do ending in an issue reference is backed by that issue
               in this repo. The issue wins: its title becomes the to-do's
               text and its open/closed state the checkbox, both here and on
               the board. Ticking the box in the app closes the issue.

Working in this repo? This file is the to-do list — use it rather than
starting a parallel one. Tick items off as you finish them, add new ones as
you find them, and keep status/progress honest: a TODO.md, a plan in a chat
window or a checklist in a commit message is invisible to everyone reading
the board. For work worth assigning, discussing, or writing up at length,
open a real issue and append its "(#12)" to the line — the item is then
tracked by number instead of text, and the issue holds the detail this file
has no room for (prose here is published to the board, not filed away).

To-dos without an issue are matched to the board by exact text, so rewording
one replaces it rather than editing it in place — expect a checked item to
come back unchecked if you reword it. Issue-backed to-dos are matched by
number instead, so keep the "(#12)" and reword freely; drop the reference and
the item becomes an ordinary to-do again (the issue itself is left alone).

HTML comments are stripped on read, so this block never reaches the board.
-->

A searchable database of the songs used in ski and snowboard films, with
one-click export of any search result into a real Spotify playlist. Live at
skitunes.nickknows.net.

Flask and SQLAlchemy over Postgres, Google and Spotify OAuth, deployed to
Kubernetes with Helm and Argo Rollouts blue/green. See README.md for the
stack and module layout.

## Todos

- [x] Browse the full catalog with pagination, plus a lightweight mobile variant
- [x] Filter by movie, production company, year, skier, song, artist, album, location and segment type
- [x] Combined song, artist and year search form
- [x] Select tracks from any result set and create a Spotify playlist, batched 100 at a time
- [x] Google OAuth and local email/password login on Flask-Login
- [x] Spotify account linking, with a clear error for users not in the developer dashboard
- [x] Correction-suggestion form that emails a field-level diff for approval
- [x] Admin CRUD for entries plus an admin user list
- [x] Rebuild the schema so Movie is the parent and songs the child
- [x] Crowdsourced submission queue with five-vote auto-promotion and admin override
- [x] CSV bulk import with a downloadable template, plus a JSON importer that skips duplicates
- [x] Add Flask-Migrate and drop db.create_all() from before_request
- [x] Add /health for the Kubernetes readiness and liveness probes
- [x] Read DATABASE_URL, FLASK_SECRET and MAIL_PASSWORD from the environment
- [x] Gate OAUTHLIB_INSECURE_TRANSPORT behind FLASK_DEBUG
- [x] Switch user IDs to UUIDs, killing the max(id)+1 race and collision risk
- [x] Fix edit_entry inserting a duplicate row instead of updating in place
- [x] Move Postgres onto a CloudNativePG cluster with secrets from OpenBao
- [x] Deploy blue/green with Argo Rollouts behind preview and active ingresses
- [x] Set real CPU and memory requests instead of 0
- [x] Move the build off the ARC runner to ubuntu-latest with GHA-cached buildx
- [ ] Implement User.generate_reset_token and verify_reset_token — password reset 500s without them
- [ ] Add reset_token and reset_token_expiration columns to User, with a migration
- [ ] Import bcrypt in auth/views.py so reset_password stops raising NameError
- [ ] Write the missing reset_password_request.html and reset_password.html templates
- [ ] Replace the placeholder your-email@gmail.com reset sender in auth/views.py
- [ ] Fix the inverted year-range comparison in findmovie — no range search ever returns results
- [ ] Add @login_required to /correct_entry so anonymous visitors cannot trigger email
- [ ] Fix the ski_type, location and video_link correction diffs that all interpolate orig_song_name
- [ ] Get-or-create Movie on insert instead of creating a duplicate row for every song
- [ ] Clean up the duplicate Movie rows already in the database
- [ ] Delete the orphaned Movie row when delete_entry removes its last song
- [ ] Remove the duplicate /health route — metrics/views.py is shadowed by main/views.py
- [ ] Either register the logs blueprint behind auth or delete the dead /Reports routes
- [ ] Collapse the triplicated findmovie iPhone, Android and desktop branches into one
- [ ] Replace the four hardcoded admin allowlists with an is_admin column and a decorator
- [ ] Move the hardcoded NickCo7@gmail.com contact address into config
- [ ] Paginate the filter and search routes, which still load every match at once
- [ ] Run gunicorn in the container instead of the Flask development server
- [ ] Run flask db upgrade on deploy via a Helm hook or init container
- [ ] Fix rollout.yaml reading .Values.replicaCount instead of .Values.webapp.replicaCount
- [ ] Delete build_image.yaml, which duplicates every build and pushes to a stale repo
- [ ] Pin dependency versions in requirements.txt
- [ ] Add a test suite — CI only checks that the app imports
- [ ] Remove esos copy.yaml, tracked .DS_Store files and the committed CSV and JSON data dumps
- [ ] Add a donation link
- [ ] Add a contribute page
