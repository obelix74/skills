#!/usr/bin/env python3
"""
Lint book chapters written as Markdown/MDX with [[marker]] blocks before they
go to the web or the printer.

    check_chapter.py CHAPTER.mdx [...] [--markers-src markers.tsx] [--photos-suffix .photos.json] [--json]

Checks:
  * house style: no em dashes (or spaced en dashes standing in for them),
    no doubled words
  * every [[marker]] is a known type. Known types are read from the renderer
    (`case "photo":` lines in --markers-src) so new markers are picked up
    without editing this script; a built-in list is the fallback.
  * photo keys ([[photo:KEY]], [[duo:A|B]], [[gallery:A,B]], [[stack:A|B]])
    resolve against the chapter's photo list (CHAPTER.photos.json beside the
    file: [{title, hash}, ...]) the way the site does: 1-based index, exact
    title, then case-insensitive substring. Flags keys that miss, keys that
    match more than one title by substring, and photos used twice.
  * markers sit on their own line, with a blank line between them and prose
    (markers may stack on consecutive lines).
"""
import argparse, json, re, sys
from pathlib import Path

FALLBACK = {"photo", "gallery", "duo", "stack", "dateline", "pullquote", "epigraph", "aside", "note", "divider",
            "stats", "elevation", "map", "flyby", "trailmap", "video"}
PHOTO_MARKERS = {"photo": None, "duo": "|", "stack": "|", "gallery": ","}
MARKER = re.compile(r"\[\[([a-z]+)(?::(.*?))?\]\]", re.S)


def known_markers(src):
    if src and Path(src).exists():
        found = set(re.findall(r'case\s+"([a-z]+)"', Path(src).read_text()))
        if found:
            return found
    return FALLBACK


def resolve(key, photos):
    t = key.strip()
    if re.fullmatch(r"\d+", t):
        i = int(t) - 1
        return ([photos[i]] if 0 <= i < len(photos) else []), "index"
    lc = t.lower()
    exact = [p for p in photos if (p.get("title") or "").lower() == lc]
    if exact:
        return exact[:1], "exact"
    return [p for p in photos if lc in (p.get("title") or "").lower()], "substring"


def check(path, a, markers):
    text = Path(path).read_text()
    rep = {"file": str(path), "problems": [], "warnings": [], "markers": {}}
    photos_file = Path(str(path).rsplit(".", 1)[0] + a.photos_suffix)
    photos = json.loads(photos_file.read_text()) if photos_file.exists() else None
    if photos is None:
        rep["warnings"].append(f"no photo list at {photos_file.name}; photo keys not checked")
    lines = text.splitlines()
    for n, line in enumerate(lines, 1):
        if "—" in line:
            rep["problems"].append(f"line {n}: em dash: ...{line.strip()[:90]}")
        # An en dash in a range (3–4 days, 11,000–13,000 ft) is right; a spaced
        # one is an em dash in disguise.
        if re.search(r"\s–\s", line):
            rep["problems"].append(f"line {n}: spaced en dash used as a dash: ...{line.strip()[:90]}")
        for m in re.finditer(r"\b(\w+)\s+\1\b", line, re.I):
            if not re.fullmatch(r"\d+", m.group(1)) and m.group(1).lower() not in {"had", "that", "is"}:
                rep["warnings"].append(f"line {n}: doubled word {m.group(0)!r}")
    used = {}
    for m in MARKER.finditer(text):
        kind, arg = m.group(1), (m.group(2) or "")
        n = text.count("\n", 0, m.start()) + 1
        rep["markers"][kind] = rep["markers"].get(kind, 0) + 1
        if kind not in markers:
            rep["problems"].append(f"line {n}: unknown marker [[{kind}]] (known: {', '.join(sorted(markers))})")
            continue
        line = lines[n - 1].strip()
        if line != m.group(0).strip() and "\n" not in m.group(0):
            rep["warnings"].append(f"line {n}: [[{kind}]] shares its line with other text; markers need their own line")
        elif any(nb.strip() and not MARKER.fullmatch(nb.strip())
                 for nb in ([lines[n - 2]] if n > 1 else []) + ([lines[n]] if n < len(lines) else [])):
            # Markers may stack on consecutive lines; prose may not touch one.
            rep["warnings"].append(f"line {n}: [[{kind}]] needs a blank line above and below")
        if kind in PHOTO_MARKERS and photos is not None:
            sep = PHOTO_MARKERS[kind]
            keys = [arg.split("|")[0]] if sep is None else arg.split(sep)
            for key in keys:
                key = key.strip().removeprefix("photo:")
                if not key or key == "full":
                    continue
                hits, how = resolve(key, photos)
                if not hits:
                    rep["problems"].append(f"line {n}: [[{kind}]] key {key!r} matches no photo in this chapter")
                    continue
                if how == "substring" and len(hits) > 1:
                    rep["warnings"].append(f"line {n}: key {key!r} matches {len(hits)} titles by substring; "
                                           f"the first wins ({hits[0].get('title')!r}). Use the exact title.")
                t = hits[0].get("title")
                if t in used:
                    rep["warnings"].append(f"line {n}: photo {t!r} already placed at line {used[t]}")
                used[t] = n
    if photos is not None:
        rep["unplaced_photos"] = [p.get("title") for p in photos if p.get("title") not in used]
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--markers-src", help="renderer source with `case \"name\":` per marker")
    ap.add_argument("--photos-suffix", default=".photos.json")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    markers = known_markers(a.markers_src)
    reps = [check(f, a, markers) for f in a.files]
    if a.json:
        print(json.dumps(reps, indent=1))
    else:
        for r in reps:
            print(f"{r['file']}: markers {r['markers'] or '-'}"
                  + (f"; {len(r.get('unplaced_photos', []))} photo(s) not placed inline (go to the chapter-end gallery)"
                     if r.get("unplaced_photos") else ""))
            for p in r["problems"]:
                print(f"  PROBLEM: {p}")
            for w in r["warnings"]:
                print(f"  warn: {w}")
    sys.exit(1 if any(r["problems"] for r in reps) else 0)


if __name__ == "__main__":
    main()
