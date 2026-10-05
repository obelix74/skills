---
name: newsletter-sync
description: Pull a photographer's or writer's newsletter posts (Substack, Beehiiv) into their own website's blog or journal and keep them in sync - new posts appear, edits follow, deleted or paid posts come off, cross-posted duplicates are skipped - and audit or debug that sync. Covers reading Substack's public archive JSON (no API key; the RSS feed stops at 20 posts), Beehiiv's API, sanitizing the HTML, turning YouTube and Instagram embeds into linked thumbnails, allowing cover image hosts for next/image, scheduling the sync, and verifying the live journal. Use for "pull my Substack into the blog", "my newsletter post isn't on the site", "add norcalhiker posts to the journal", "sync Beehiiv", "why is the journal page crashing", or after publishing a post.
argument-hint: "[newsletter URL or 'audit']"
allowed-tools: Bash(python3:*) Bash(curl:*) Bash(gcloud:*) Bash(git:*) Read Edit
---

# Newsletter sync

## Live context

- Sync code in this project: !`grep -rlE "substack|beehiiv" src/lib src/app/api 2>/dev/null | head -10 || echo "(none yet)"`
- Image hosts next/image allows: !`grep -oE 'hostname:\s*"[^"]+"' next.config.* 2>/dev/null | sed 's/hostname: *//' | tr '\n' ' '`
- Request: $ARGUMENTS

## Audit first

Before building or debugging, see exactly what the source has:

```bash
python3 scripts/newsletter_audit.py substack https://www.example.com \
    --allowed-hosts-from next.config.ts [--existing-titles titles.txt]
```

It lists every post with its audience (only `everyone` is free; a paid post's
public body is a teaser), whether it would sync, its embeds (YouTube,
Instagram, tweets, audio, galleries) and iframes, its cover host, and whether
next/image allows that host. **A cover on an unlisted host makes next/image
throw and takes the whole blog index down**, not just the one card. Pass the
site's current titles (one per line) to spot cross-posts.

## Building a sync (when the project has none)

1. **Storage**: reuse the blog table; add `source` ('local' | 'substack' |
   'beehiiv'), a unique external post id column per source, `body_html`
   (sanitized), and `external_url`. Migrations idempotent
   (`ADD COLUMN IF NOT EXISTS`, constraint in a `DO $$ ... EXCEPTION` block).
2. **Fetch**: Substack: `GET {base}/api/v1/archive?sort=new&limit=50&offset=N`
   until a short page, then `GET {base}/api/v1/posts/{slug}` for `body_html`,
   `cover_image`, `subtitle`, `canonical_url`, `audience`. Beehiiv: API v2
   posts with `status=confirmed` and `expand[]=free_web_content`; the article
   is the `#content-blocks` element of the web HTML.
3. **Clean**: before sanitizing, replace Substack's `.youtube-wrap` (videoId in
   `data-attrs`) and `.instagram-embed-wrap` (instagram_id, thumbnail_url)
   with a thumbnail image linked to the original, and drop
   `.image-link-expand`, `.subscription-widget-wrap`, `.button-wrapper`. Then
   sanitize to a whitelist (no script, iframe, style, on* handlers), links get
   `target=_blank rel=noopener`, strip `utm_*`, and drop wrappers left empty.
4. **Upsert by external id**; set the slug only on create (shared links keep
   working); suffix on a slug clash with a local post. Skip a post whose
   normalized title is already on the site from another source. Unpublish
   rows of that source whose id is no longer in the feed.
5. **Covers**: add every cover host to next/image `remotePatterns`, and in the
   sync keep a cover only if its host is on that list (drop and log it
   otherwise) so a new host can never break the page.
6. **Schedule** it (cron every 15 minutes with a shared secret), run Beehiiv
   before Substack so the Beehiiv copy of a cross-post wins, and keep a "Sync
   now" admin button. Synced posts are read-only in the admin.
7. **Test against a scratch database** (a local Postgres with a dump of the
   blog and settings tables), never by syncing into production: a production
   sync publishes immediately.

## Going live

Additive migration on production, deploy, then trigger the sync once through
the cron endpoint and check: the journal returns 200, the card count and
source labels are right, two or three posts render (one with video embeds).
