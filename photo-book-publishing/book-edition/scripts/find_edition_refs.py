#!/usr/bin/env python3
"""
List every place in a repo (and its generated print files) that states a fact
about the book's edition: page count, edition name, pre-order/ship date, price,
spine width, stock. Run it before and after an edition change so nothing is
missed (the flyer and the cover spine are the usual misses).

    find_edition_refs.py [REPO] [--pages 132] [--old-pages 116] [--extra REGEX ...] [--pdfs DIR] [--json]

--pages / --old-pages flag lines that still say the old count. --pdfs also
greps the text of generated PDFs (flyer, labels, price list) under DIR.
"""
import argparse, json, os, re, subprocess
from pathlib import Path

SKIP_DIRS = {"node_modules", ".next", ".git", "dist", "build", ".vercel", "coverage", "__pycache__", ".print-cache"}
EXTS = {".ts", ".tsx", ".js", ".mjs", ".py", ".md", ".mdx", ".json", ".sql", ".sh", ".html", ".css", ".yaml", ".yml"}
PATTERNS = {
    "page count":   r"\b\d{2,4}[ -]?(?:pages|pp)\b|\bpages?:\s*\d{2,4}\b",
    "edition":      r"\b(?:first|second|third|fourth|1st|2nd|3rd|4th)[ -]edition\b|\bEDITIONS\b|\bBOOK_EDITION\b",
    "pre-order":    r"\bpre-?order\b|\bships(?:On| on)\b|\bshipsOn\b",
    "spine":        r"\bSPINE[_A-Z]*\b|\bspine(?:Width|_width|WidthIn)\b",
    "stock":        r"\b[a-z_]*edition[a-z_]*_stock\b|\bfirstEditionLeft\b|\bclaimFirstEdition\b",
    "price":        r"\bbookPriceLabel\b|\bBOOK\.priceCents\b|\$\d{2,3}(?:\.\d\d)?\b.*\b(?:book|hardcover)\b",
}


# High-volume kinds: listed per file unless --detail.
SUMMARISE = {"edition", "stock"}


def scan_repo(root: Path, extra: list[str]):
    pats = {**PATTERNS, **{f"extra {i + 1}": p for i, p in enumerate(extra)}}
    hits = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in fns:
            p = Path(dp) / fn
            if p.suffix not in EXTS or p.stat().st_size > 2_000_000:
                continue
            try:
                lines = p.read_text(errors="ignore").splitlines()
            except OSError:
                continue
            for n, line in enumerate(lines, 1):
                for kind, rx in pats.items():
                    if re.search(rx, line, re.I if kind != "spine" else 0):
                        hits.append({"file": str(p.relative_to(root)), "line": n, "kind": kind, "text": line.strip()[:160]})
                        break
    return hits


def scan_pdfs(d: Path):
    hits = []
    for pdf in sorted(d.rglob("*.pdf")):
        txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
        for kind, rx in PATTERNS.items():
            for m in re.finditer(rx, txt, re.I):
                line = txt[max(0, txt.rfind("\n", 0, m.start()) + 1): txt.find("\n", m.end())].strip()
                hits.append({"file": str(pdf), "line": 0, "kind": kind, "text": re.sub(r"\s+", " ", line)[:160]})
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--pages", type=int, help="the new page count")
    ap.add_argument("--old-pages", type=int, nargs="*", default=[], help="page counts that are now stale")
    ap.add_argument("--extra", nargs="*", default=[], help="extra regexes (e.g. a ship date)")
    ap.add_argument("--pdfs", help="also grep generated PDFs under this dir")
    ap.add_argument("--detail", action="store_true", help="print every line, not a per-file summary, for edition/stock")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = Path(a.repo).resolve()
    hits = scan_repo(root, a.extra) + (scan_pdfs(Path(a.pdfs)) if a.pdfs else [])
    for h in hits:
        nums = [int(x) for x in re.findall(r"\b(\d{2,4})[ -]?(?:pages|pp)\b", h["text"], re.I)]
        h["stale"] = any(n in a.old_pages for n in nums) or (a.pages is not None and h["kind"] == "page count"
                                                              and nums and a.pages not in nums and not a.old_pages)
    if a.json:
        print(json.dumps(hits, indent=1)); return
    by_kind = {}
    for h in hits:
        by_kind.setdefault(h["kind"], []).append(h)
    for kind, hs in by_kind.items():
        print(f"\n## {kind} ({len(hs)})")
        if kind in SUMMARISE and not a.detail:
            files = {}
            for h in hs:
                files.setdefault(h["file"], []).append(h["line"])
            for f, ls in sorted(files.items(), key=lambda kv: -len(kv[1])):
                print(f"  {f}: {len(ls)} line(s) {ls[:8]}")
            continue
        for h in hs[:60]:
            flag = "  STALE" if h["stale"] else ""
            loc = f"{h['file']}:{h['line']}" if h["line"] else h["file"]
            print(f"  {loc}{flag}\n      {h['text']}")
    stale = [h for h in hits if h["stale"]]
    print(f"\n{len(hits)} reference(s); {len(stale)} flagged stale")


if __name__ == "__main__":
    main()
