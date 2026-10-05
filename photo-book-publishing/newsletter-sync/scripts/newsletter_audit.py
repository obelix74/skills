#!/usr/bin/env python3
"""
Audit a Substack newsletter before (or after) syncing it into a site's blog:
what would come over, what would be skipped, and what would break.

    newsletter_audit.py substack https://www.norcalhiker.net [--allowed-hosts-from next.config.ts]
                        [--allowed-hosts host ...] [--existing-titles titles.txt] [--json]

Reports, per post: audience (only "everyone" is free), cover host and whether
next/image allows it (an unlisted host makes next/image throw and takes the
whole blog index down), embed types in the body (YouTube, Instagram, tweets,
audio, galleries...) that a sanitizer strips, and title clashes with posts
already on the site (cross-posts). Standard library only.
"""
import argparse, json, re, sys, urllib.parse, urllib.request
from collections import Counter

UA = {"User-Agent": "Mozilla/5.0 (newsletter-audit)", "Accept": "application/json"}
EMBED_CLASSES = {
    "youtube-wrap": "YouTube", "instagram-embed-wrap": "Instagram", "tweet": "Tweet", "twitter-embed": "Tweet",
    "spotify-wrap": "Spotify", "vimeo-wrap": "Vimeo", "native-video-embed": "Substack video",
    "native-audio-embed": "Substack audio", "image-gallery-embed": "Image gallery", "embedded-post-wrap": "Embedded post",
    "subscription-widget-wrap": "Subscribe widget", "button-wrapper": "Button", "poll-embed": "Poll",
    "footnote": "Footnote", "latex-rendered": "LaTeX", "digest-post-embed": "Digest",
}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.loads(r.read().decode())


def hosts_from_next_config(path):
    src = open(path).read()
    return set(re.findall(r'hostname:\s*["\']([^"\']+)["\']', src))


def host_allowed(host, allowed):
    for a in allowed:
        if a == host or (a.startswith("**.") and host.endswith(a[2:])) or (a.startswith("*.") and host.count(".") == a.count(".") and host.endswith(a[1:])):
            return True
    return False


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def substack(base, a):
    base = base.rstrip("/")
    posts, off = [], 0
    while True:
        page = get(f"{base}/api/v1/archive?sort=new&limit=50&offset={off}")
        posts += page
        if len(page) < 50:
            break
        off += 50
    allowed = set(a.allowed_hosts or [])
    if a.allowed_hosts_from:
        allowed |= hosts_from_next_config(a.allowed_hosts_from)
    existing = set()
    if a.existing_titles:
        existing = {norm_title(l) for l in open(a.existing_titles) if l.strip()}
    rows, embeds_total = [], Counter()
    for p in posts:
        full = get(f"{base}/api/v1/posts/{urllib.parse.quote(p['slug'])}") if p.get("audience") == "everyone" else p
        body = full.get("body_html") or ""
        classes = Counter()
        for cl in re.findall(r'class="([^"]+)"', body):
            for c in cl.split():
                if c in EMBED_CLASSES:
                    classes[EMBED_CLASSES[c]] += 1
        iframes = len(re.findall(r"<iframe\b", body))
        embeds_total.update(classes)
        cover = full.get("cover_image") or ""
        host = urllib.parse.urlparse(cover).hostname or ""
        rows.append({
            "date": (p.get("post_date") or "")[:10], "slug": p["slug"], "title": p["title"].strip(),
            "audience": p.get("audience"), "type": p.get("type"),
            "will_sync": p.get("audience") == "everyone" and bool(body) and norm_title(p["title"]) not in existing,
            "duplicate_title": norm_title(p["title"]) in existing,
            "cover_host": host, "cover_ok": (not cover) or (host_allowed(host, allowed) if allowed else None),
            "embeds": dict(classes), "iframes": iframes, "images": len(re.findall(r"<img\b", body)),
        })
    return {"source": base, "posts": rows, "embed_totals": dict(embeds_total), "allowed_hosts": sorted(allowed)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("platform", choices=["substack"])
    ap.add_argument("base")
    ap.add_argument("--allowed-hosts", nargs="*")
    ap.add_argument("--allowed-hosts-from", help="next.config.ts/js to read images.remotePatterns hostnames from")
    ap.add_argument("--existing-titles", help="file with one existing blog title per line (to spot cross-posts)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rep = substack(a.base, a)
    if a.json:
        print(json.dumps(rep, indent=1)); return
    rows = rep["posts"]
    print(f"{rep['source']}: {len(rows)} posts; {sum(r['will_sync'] for r in rows)} would sync")
    print(f"  audiences: {dict(Counter(r['audience'] for r in rows))}; types: {dict(Counter(r['type'] for r in rows))}")
    print(f"  embeds across all posts: {rep['embed_totals'] or 'none'}")
    bad_cover = [r for r in rows if r["cover_ok"] is False]
    hosts = Counter(r["cover_host"] for r in rows if r["cover_host"])
    print(f"  cover hosts: {dict(hosts)}")
    if bad_cover:
        print(f"  PROBLEM: {len(bad_cover)} cover(s) on hosts next/image does not allow: "
              f"{sorted({r['cover_host'] for r in bad_cover})} (add them to remotePatterns, or drop the cover)")
    dups = [r for r in rows if r["duplicate_title"]]
    if dups:
        print(f"  {len(dups)} title(s) already on the site (cross-posts, skipped): {[r['title'] for r in dups]}")
    paid = [r for r in rows if r["audience"] != "everyone"]
    if paid:
        print(f"  {len(paid)} paid post(s) skipped (only a teaser is public): {[r['title'] for r in paid][:10]}")
    for r in rows:
        flags = []
        if r["embeds"]: flags.append(f"embeds {r['embeds']}")
        if r["iframes"]: flags.append(f"{r['iframes']} iframe(s)")
        if r["cover_ok"] is False: flags.append(f"cover host {r['cover_host']} NOT allowed")
        print(f"  {r['date']}  {'sync' if r['will_sync'] else 'skip'}  {r['title'][:60]:60}  {'; '.join(flags)}")
    sys.exit(1 if bad_cover else 0)


if __name__ == "__main__":
    main()
