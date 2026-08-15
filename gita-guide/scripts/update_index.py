#!/usr/bin/env python3
"""Refresh the Gita session index from the live YouTube playlist.

Why: the playlist is ongoing — Swami Sarvapriyananda keeps adding sessions as he
works verse by verse through the Gita. A cited index that silently goes stale is
worse than useless, so the skill runs this at the start of a session to pick up
anything new. It re-fetches the playlist, and if the video set changed it
rewrites both `gita-video-index.json` and `gita-video-index.md` in place.

Design notes:
- Network-tolerant: if the fetch fails (offline, YouTube change), it prints a
  notice and leaves the existing index untouched, exiting 0 so it never blocks
  answering a question.
- Cheap when nothing changed: it compares the fetched video-id list against the
  stored one and only rewrites files on a difference.

Usage:
  python update_index.py            # refresh if the playlist changed
  python update_index.py --check    # report only; write nothing
  python update_index.py --quiet    # only print on change or error
"""
import argparse
import json
import os
import re
import sys
import urllib.request

PLAYLIST_ID = "PL2imXor63HtS4ewIKryBL4ZVeiaH8Ij4R"
PLAYLIST_URL = f"https://www.youtube.com/playlist?list={PLAYLIST_ID}"
REF = os.path.join(os.path.dirname(__file__), "..", "references")
JSON_PATH = os.path.join(REF, "gita-video-index.json")
MD_PATH = os.path.join(REF, "gita-video-index.md")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

CH_NAMES = {
    1: "Arjuna Vishada Yoga — Arjuna's Grief",
    2: "Sankhya Yoga — The Yoga of Knowledge",
    3: "Karma Yoga — The Yoga of Action",
    4: "Jnana Karma Sanyasa Yoga — Knowledge & Renunciation of Action",
    5: "Karma Sanyasa Yoga — Renunciation of Action",
    6: "Dhyana Yoga — The Yoga of Meditation",
    7: "Jnana Vijnana Yoga — Knowledge & Realization",
    8: "Akshara Brahma Yoga — The Imperishable Absolute",
    9: "Raja Vidya Raja Guhya Yoga — The Sovereign Knowledge & Secret",
    10: "Vibhuti Yoga — Divine Glories",
    11: "Vishwarupa Darshana Yoga — The Cosmic Form",
    12: "Bhakti Yoga — The Yoga of Devotion",
    13: "Kshetra Kshetrajna Vibhaga Yoga — The Field & Its Knower",
    14: "Gunatraya Vibhaga Yoga — The Three Gunas",
    15: "Purushottama Yoga — The Supreme Person",
    16: "Daivasura Sampad Vibhaga Yoga — Divine & Demoniac Natures",
    17: "Shraddhatraya Vibhaga Yoga — The Threefold Faith",
    18: "Moksha Sanyasa Yoga — Liberation & Renunciation",
}


def _get(url, data=None):
    req = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": UA, "Accept-Language": "en-US",
                 "Content-Type": "application/json"},
    )
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def _extract(node):
    """Pull (videoId, title) pairs from a ytInitialData / innertube blob."""
    out = []

    def title_of(lv):
        return (lv.get("metadata", {})
                  .get("lockupMetadataViewModel", {})
                  .get("title", {})
                  .get("content"))

    def walk(o):
        if isinstance(o, dict):
            if "lockupViewModel" in o:
                lv = o["lockupViewModel"]
                out.append((lv.get("contentId"), title_of(lv)))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(node)
    return out


def _find_token(o):
    if isinstance(o, dict):
        if "token" in o and o.get("request") == "CONTINUATION_REQUEST_TYPE_BROWSE":
            return o["token"]
        for v in o.values():
            r = _find_token(v)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = _find_token(v)
            if r:
                return r
    return None


def fetch_playlist():
    """Return an ordered, de-duplicated list of (videoId, title)."""
    html = _get(PLAYLIST_URL)
    data = json.loads(re.search(r"var ytInitialData = (\{.*?\});</script>", html).group(1))
    key = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html).group(1)
    cver = re.search(r'"INNERTUBE_CONTEXT_CLIENT_VERSION":"([^"]+)"', html).group(1)

    vids = _extract(data)
    tok = _find_token(data)
    api = f"https://www.youtube.com/youtubei/v1/browse?key={key}"
    guard = 0
    while tok and guard < 20:
        body = json.dumps({
            "context": {"client": {"clientName": "WEB", "clientVersion": cver}},
            "continuation": tok,
        }).encode()
        resp = json.loads(_get(api, body))
        vids += _extract(resp)
        tok = _find_token(resp)
        guard += 1

    seen, ordered = set(), []
    for vid, title in vids:
        if vid and vid not in seen:
            seen.add(vid)
            ordered.append((vid, title))
    return ordered


def parse_ref(title):
    """Extract (chapter, verse_start, verse_end) from a session title.

    Titles come in English ("Chapter 2 Verses 1-10", "Chapter 2 Verse 16") and
    Hindi ("अध्याय 2 श्लोक 20-22"), with assorted separators (| I l). Chapter 1 is
    a summary with no verse range.
    """
    m = re.search(r"Chapter\s*(\d+)\D*?(?:Verses?|श्लोक)\s*(\d+)\s*(?:[-–]\s*(\d+))?", title, re.I)
    if not m:
        m = re.search(r"अध्याय\s*(\d+)\D*?श्लोक\s*(\d+)\s*(?:[-–]\s*(\d+))?", title)
    if not m:
        mc = re.search(r"Chapter\s*(\d+)\s*Summary", title, re.I)
        if mc:
            return int(mc.group(1)), None, None
        return None, None, None
    ch = int(m.group(1))
    vs = int(m.group(2))
    ve = int(m.group(3)) if m.group(3) else vs
    return ch, vs, ve


def build_rows(ordered):
    rows = []
    for i, (vid, title) in enumerate(ordered, 1):
        ch, vs, ve = parse_ref(title or "")
        rows.append({
            "n": i,
            "chapter": ch,
            "verse_start": vs,
            "verse_end": ve,
            "title": title,
            "id": vid,
            "url": f"https://www.youtube.com/watch?v={vid}&list={PLAYLIST_ID}",
        })
    return rows


def verse_label(r):
    if r["verse_start"] is None:
        return "Chapter Summary / Intro"
    if r["verse_start"] == r["verse_end"]:
        return f"Verse {r['verse_start']}"
    return f"Verses {r['verse_start']}–{r['verse_end']}"


def render_md(rows):
    from collections import defaultdict
    lines = [
        "# Swami Sarvapriyananda — Bhagavad Gita Session Index\n",
        f"Source playlist (Vedanta Society of New York): {PLAYLIST_URL}\n",
        "This is the authoritative, verse-by-verse mapping of the recorded sessions. "
        "Use it to cite the **exact** session that covers a given chapter and verse. "
        "When a user asks about a specific verse, find the row whose verse range contains it. "
        "When they ask about a concept, identify the relevant verses (see `vedanta-core.md`) "
        "and cite those sessions.\n",
        "Each session URL keeps the `&list=` parameter so the viewer lands inside the playlist. "
        "The programmatic lookup is `scripts/find_session.py`; refresh with `scripts/update_index.py`.\n",
    ]
    cov = defaultdict(list)
    for r in rows:
        cov[r["chapter"]].append(r)
    last_ch = max(c for c in cov if c) if any(cov) else 0
    for c in sorted(k for k in cov if k is not None):
        lines.append(f"\n## Chapter {c} — {CH_NAMES.get(c, '')}\n")
        lines.append("| # | Covers | Session title | Link |")
        lines.append("|---|--------|---------------|------|")
        for r in sorted(cov[c], key=lambda x: x["n"]):
            t = (r["title"] or "").replace("|", "\\|")
            lines.append(f"| {r['n']} | {verse_label(r)} | {t} | [watch]({r['url']}) |")
    lines.append("\n---\n")
    lines.append(
        f"_Total: {len(rows)} sessions, through Chapter {last_ch}. The series is ongoing at the "
        "source; if a user asks about chapters/verses beyond this index, say so and fall back to "
        "search (see SKILL.md)._\n")
    return "\n".join(lines)


def load_existing_ids():
    try:
        with open(JSON_PATH, encoding="utf-8") as f:
            return [r["id"] for r in json.load(f)]
    except (OSError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    ap.add_argument("--quiet", action="store_true", help="print only on change or error")
    a = ap.parse_args()

    try:
        ordered = fetch_playlist()
    except Exception as e:  # network / parsing / YouTube change — never block answering
        print(f"[update_index] could not refresh playlist ({e}); using existing index.")
        return 0

    if not ordered:
        print("[update_index] fetched 0 videos; using existing index.")
        return 0

    new_ids = [vid for vid, _ in ordered]
    old_ids = load_existing_ids()

    if old_ids == new_ids:
        if not a.quiet:
            print(f"[update_index] up to date — {len(new_ids)} sessions.")
        return 0

    added = len(new_ids) - (len(old_ids) if old_ids else 0)
    msg = (f"[update_index] playlist changed: now {len(new_ids)} sessions"
           + (f" ({added:+d} vs stored)." if old_ids is not None else " (no prior index)."))
    print(msg)

    if a.check:
        return 0

    rows = build_rows(ordered)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(render_md(rows))
    print(f"[update_index] rewrote index files through Chapter {max(r['chapter'] for r in rows if r['chapter'])}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
