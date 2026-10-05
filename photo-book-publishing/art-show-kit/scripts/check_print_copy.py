#!/usr/bin/env python3
"""
Check the words on generated print pieces (flyer, price list, wall labels,
insert cards) before they go to the printer or the home printer, and render a
preview to look at.

    check_print_copy.py FILE.pdf [FILE2.pdf ...] [--expect TEXT ...] [--forbid TEXT ...]
                        [--pages N] [--price 65] [--preview DIR] [--json]

Checks:
  * em/en dashes (house style: none in copy)
  * every --expect phrase is present, no --forbid phrase is
  * any "NNN pages" agrees with --pages
  * any "$NN" for the book agrees with --price
  * leftover template text (lorem, TODO, XXX, {{ }}, undefined, NaN, null)
  * page size and count, so a US Letter sheet is US Letter
Exit 1 if anything fails. Needs poppler (pdftotext, pdfinfo, pdftoppm).
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

PLACEHOLDERS = r"lorem ipsum|\bTODO\b|\bXXX\b|\{\{|\}\}|\bundefined\b|\bNaN\b|\bnull\b|\[object Object\]"


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def norm(s):
    return re.sub(r"\s+", " ", s.replace(" ", " ")).strip().lower()


def check(pdf: str, a) -> dict:
    txt = run("pdftotext", "-layout", pdf, "-")
    flat = norm(txt)
    inf = run("pdfinfo", pdf)
    size = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", inf)
    pages = int(re.search(r"Pages:\s+(\d+)", inf).group(1))
    rep = {"file": pdf, "pages": pages, "size_in": [round(float(size.group(1)) / 72, 2), round(float(size.group(2)) / 72, 2)],
           "problems": [], "notes": []}
    for ch, name in (("—", "em dash"), ("–", "en dash")):
        n = txt.count(ch)
        if n:
            ctx = [re.sub(r"\s+", " ", txt[max(0, m.start() - 30): m.end() + 30]) for m in re.finditer(ch, txt)][:3]
            rep["problems"].append(f"{n} {name}(es): {ctx}")
    for e in a.expect:
        if norm(e) not in flat:
            rep["problems"].append(f"missing expected text: {e!r}")
    for f in a.forbid:
        if norm(f) in flat:
            rep["problems"].append(f"contains forbidden text: {f!r}")
    counts = sorted({int(n) for n in re.findall(r"\b(\d{2,4})\s*pages\b", txt, re.I)})
    rep["page_counts_stated"] = counts
    if a.pages and counts and counts != [a.pages]:
        rep["problems"].append(f"states {counts} pages; the book is {a.pages}")
    prices = sorted({p.replace(",", "") for p in re.findall(r"\$\s?(\d{1,3}(?:,\d{3})+(?:\.\d\d)?|\d{1,6}(?:\.\d\d)?)", txt)},
                    key=lambda v: float(v))
    rep["prices_stated"] = prices
    if a.price is not None and prices and str(a.price) not in [p.split(".")[0] for p in prices]:
        rep["problems"].append(f"book price ${a.price} not found; prices on the page: {prices}")
    ph = sorted({m.group(0) for m in re.finditer(PLACEHOLDERS, txt, re.I)})
    if ph:
        rep["problems"].append(f"template leftovers: {ph}")
    if not flat:
        rep["problems"].append("no extractable text (blank page, or text drawn as an image)")
    if a.preview:
        Path(a.preview).mkdir(parents=True, exist_ok=True)
        stem = Path(a.preview) / Path(pdf).stem
        subprocess.run(["pdftoppm", "-r", "50", "-png", "-l", "4", pdf, str(stem)], check=False)
        rep["preview"] = sorted(str(p) for p in Path(a.preview).glob(Path(pdf).stem + "*.png"))
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+")
    ap.add_argument("--expect", nargs="*", default=[])
    ap.add_argument("--forbid", nargs="*", default=[])
    ap.add_argument("--pages", type=int)
    ap.add_argument("--price", type=int)
    ap.add_argument("--preview")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    reps = [check(p, a) for p in a.pdfs if Path(p).exists()]
    missing = [p for p in a.pdfs if not Path(p).exists()]
    if a.json:
        print(json.dumps({"reports": reps, "missing": missing}, indent=1))
    else:
        for r in reps:
            print(f"{r['file']}: {r['pages']} page(s), {r['size_in'][0]} x {r['size_in'][1]} in; "
                  f"pages stated {r['page_counts_stated'] or '-'}; prices {r['prices_stated'][:8] or '-'}")
            for p in r["problems"]:
                print(f"  PROBLEM: {p}")
            if r.get("preview"):
                print(f"  preview: {', '.join(r['preview'])}")
            if not r["problems"]:
                print("  OK")
        for m in missing:
            print(f"{m}: NOT FOUND")
    sys.exit(1 if missing or any(r["problems"] for r in reps) else 0)


if __name__ == "__main__":
    main()
