#!/usr/bin/env python3
"""Look up which of Swami Sarvapriyananda's Gita sessions covers a verse.

Why this exists: the SKILL wants to cite the *exact* video for a chapter/verse
instead of guessing. Reading the whole index into context and eyeballing ranges
is slower and more error-prone than a two-line lookup, so do it here.

Usage:
  python find_session.py --chapter 2 --verse 47      # the session covering 2.47
  python find_session.py --chapter 12                # every session in chapter 12
  python find_session.py --search "meditation"       # keyword match on titles
"""
import argparse
import json
import os
import sys

INDEX = os.path.join(os.path.dirname(__file__), "..", "references", "gita-video-index.json")


def load():
    with open(INDEX, encoding="utf-8") as f:
        return json.load(f)


def contains(row, verse):
    vs, ve = row["verse_start"], row["verse_end"]
    if vs is None:  # a chapter summary/intro session has no verse range
        return False
    return vs <= verse <= ve


def show(rows):
    if not rows:
        print("No matching session found in the index (Ch1–Ch13.10).")
        return
    for r in rows:
        print(f"[{r['n']}] {r['title']}\n    {r['url']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int)
    ap.add_argument("--verse", type=int)
    ap.add_argument("--search")
    a = ap.parse_args()
    rows = load()

    if a.search:
        q = a.search.lower()
        show([r for r in rows if q in r["title"].lower()])
        return

    if a.chapter is None:
        ap.error("give --chapter (optionally with --verse) or --search")

    ch = [r for r in rows if r["chapter"] == a.chapter]
    if not ch:
        print(f"Chapter {a.chapter} is not in the index (covers Ch1–Ch13.10).")
        sys.exit(0)
    if a.verse is None:
        show(sorted(ch, key=lambda r: r["n"]))
    else:
        hits = [r for r in ch if contains(r, a.verse)]
        if hits:
            show(hits)
        else:
            # fall back to the nearest sessions so the model still has a lead
            print(f"No session is labeled for {a.chapter}.{a.verse}. Nearest in chapter:")
            show(sorted(ch, key=lambda r: r["n"])[:3])


if __name__ == "__main__":
    main()
