#!/usr/bin/env python3
"""
Report on a built book PDF: page count against the printer's page multiple,
trailing blank pages, near-empty pages (stubs worth combining), and photo
resolution.

    page_report.py BOOK.pdf [--multiple 4] [--stub-words 60] [--min-ppi 240] [--json]

Needs poppler (pdfinfo, pdftotext, pdfimages).
"""
import argparse, json, re, subprocess


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--multiple", type=int, default=4, help="printer's page multiple (OnPress 4, most others 2)")
    ap.add_argument("--stub-words", type=int, default=60, help="a page with no image and fewer words is a stub")
    ap.add_argument("--min-ppi", type=int, default=240)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    pages = int(re.search(r"Pages:\s+(\d+)", run("pdfinfo", a.pdf)).group(1))
    texts = run("pdftotext", "-layout", a.pdf, "-").split("\f")[:pages]
    imgs = {}
    low = []
    for line in run("pdfimages", "-list", a.pdf).splitlines()[2:]:
        s = line.split()
        if len(s) > 13 and s[2] == "image":
            p = int(s[0]); imgs[p] = imgs.get(p, 0) + 1
            try:
                ppi = min(int(s[12]), int(s[13]))
                if ppi < a.min_ppi and int(s[3]) > 300:
                    low.append({"page": p, "px": f"{s[3]}x{s[4]}", "ppi": ppi})
            except ValueError:
                pass
    words = [len(t.split()) for t in texts]
    trailing = 0
    for i in range(pages - 1, -1, -1):
        if words[i] == 0 and not imgs.get(i + 1):
            trailing += 1
        else:
            break
    content = pages - trailing
    stubs = [{"page": i + 1, "words": w, "first": " ".join(texts[i].split()[:8])}
             for i, w in enumerate(words) if 0 < w < a.stub_words and not imgs.get(i + 1)]
    short_by = (a.multiple - content % a.multiple) % a.multiple
    rep = {
        "pages": pages, "content_pages": content, "trailing_blank": trailing,
        "multiple": a.multiple, "pages_to_next_multiple_from_content": short_by,
        "pages_to_remove_to_drop_a_signature": content % a.multiple or a.multiple,
        "stubs": stubs, "low_resolution_images": low,
        "last_pages": [{"page": i + 1, "words": words[i], "images": imgs.get(i + 1, 0),
                        "first": " ".join(texts[i].split()[:8])} for i in range(max(0, pages - 6), pages)],
    }
    if a.json:
        print(json.dumps(rep, indent=1)); return
    print(f"{pages} pages ({content} with content, {trailing} blank at the end); printer multiple {a.multiple}")
    shed = rep["pages_to_remove_to_drop_a_signature"]
    if trailing:
        print(f"  the {trailing} blank page(s) at the end are padding to the multiple of {a.multiple}")
    print(f"  remove {shed} content page(s) and the book drops to {content - shed + (a.multiple - (content - shed) % a.multiple) % a.multiple} pages")
    if stubs:
        print(f"  {len(stubs)} near-empty text page(s) (< {a.stub_words} words, no image), candidates to combine:")
        for s in stubs[:15]:
            print(f"    p{s['page']}: {s['words']} words  \"{s['first']}\"")
    if low:
        print(f"  {len(low)} image(s) under {a.min_ppi} ppi: {low[:8]}")
    print("  last pages:")
    for l in rep["last_pages"]:
        print(f"    p{l['page']}: {l['words']} words, {l['images']} image(s)  \"{l['first']}\"")


if __name__ == "__main__":
    main()
