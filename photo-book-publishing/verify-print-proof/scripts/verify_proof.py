#!/usr/bin/env python3
"""
Verify a printer's proof against the PDF you sent them.

    verify_proof.py interior --proof PROOF.pdf --ours OURS.pdf [--placement] [--json]
    verify_proof.py cover    --proof PROOF.pdf --ours OURS.pdf [--wrap 0.75] [--panel 11] [--json]

Needs poppler (pdfinfo, pdftotext, pdfimages, pdftoppm, pdftohtml). Standard
library only otherwise. Exit code 0 = nothing blocks approval, 1 = problems.

Printers (OnPress, Lulu, IngramSpark ...) return the file you uploaded with a
translucent guide overlay painted on top: red bands for trim/bleed, yellow
lines for the safety area, and on a hardcover cover the hinge/fold bands
either side of the spine. Everything here is measured off that overlay, so
nothing is hard-coded to one printer: the safety box, the spine folds and the
spread width are all read from the proof itself.
"""
import argparse, json, re, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path

PT = 72.0


def run(*cmd: str) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=False).stdout


def info(pdf: str) -> dict:
    out = run("pdfinfo", "-box", pdf)
    d = {}
    for line in out.splitlines():
        k, _, v = line.partition(":")
        d[k.strip()] = v.strip()
    w, h = (float(x) for x in re.findall(r"[\d.]+", d.get("Page size", "0 x 0"))[:2])
    mb = [float(x) for x in re.findall(r"-?[\d.]+", d.get("MediaBox", "0 0 0 0"))]
    return {"pages": int(d.get("Pages", "0")), "w": w, "h": h, "mediabox": mb,
            "created": d.get("CreationDate", ""), "modified": d.get("ModDate", ""),
            "producer": d.get("Producer", "")}


def squash(t: str) -> str:
    # Whitespace-free: letter-spaced headings extract with different spacing
    # depending on which tool last wrote the PDF (the printer's, Ghostscript).
    return re.sub(r"\s+", "", t)


def page_texts(pdf: str) -> list[str]:
    return [squash(t) for t in run("pdftotext", pdf, "-").split("\f")]


def image_list(pdf: str) -> list[tuple]:
    rows = run("pdfimages", "-list", pdf).splitlines()[2:]
    out = []
    for r in rows:
        s = r.split()
        if len(s) > 6:
            out.append((int(s[0]), s[2], int(s[3]), int(s[4]), s[5]))  # page, type, w, h, color
    return out


def render(pdf: str, dpi: int, page: int = 1, crop: tuple | None = None):
    """Render one page to an RGB raster: (width, height, bytes)."""
    with tempfile.TemporaryDirectory() as td:
        args = ["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page), "-singlefile"]
        if crop:
            x, y, w, h = crop
            args += ["-x", str(x), "-y", str(y), "-W", str(w), "-H", str(h)]
        subprocess.run(args + [pdf, f"{td}/p"], check=True)
        return read_ppm(f"{td}/p.ppm")


def read_ppm(path: str):
    data = Path(path).read_bytes()
    parts, i = [], 0
    while len(parts) < 4:                     # P6 <w> <h> <max>, comments allowed
        while data[i:i + 1].isspace():
            i += 1
        if data[i:i + 1] == b"#":
            i = data.index(b"\n", i) + 1
            continue
        j = i
        while not data[j:j + 1].isspace():
            j += 1
        parts.append(data[i:j]); i = j
    i += 1
    w, h = int(parts[1]), int(parts[2])
    return w, h, data[i:i + w * h * 3]


def is_guide(px) -> bool:
    r, g, b = px
    red = r > 120 and g < 75 and b < 65
    yellow = r > 120 and g > 105 and b < 45
    return red or yellow


def runs_along(raster, fixed: int, horizontal: bool, dpi: int, min_len_pt=1.5):
    """Guide-coloured runs along one row (horizontal=True) or column, in points."""
    w, h, buf = raster
    n = w if horizontal else h
    out, start = [], None
    for k in range(n):
        x, y = (k, fixed) if horizontal else (fixed, k)
        o = (y * w + x) * 3
        g = is_guide(buf[o:o + 3])
        if g and start is None:
            start = k
        if not g and start is not None:
            if (k - start) * PT / dpi >= min_len_pt:
                out.append((start * PT / dpi, k * PT / dpi))
            start = None
    if start is not None:
        out.append((start * PT / dpi, n * PT / dpi))
    return out


def consensus(lists, tol=2.5):
    """Runs that appear (within tol pt) in most of the sampled lines."""
    flat = [r for l in lists for r in l]
    keep = []
    for a, b in flat:
        hits = sum(any(abs(a - c) <= tol and abs(b - d) <= tol for c, d in l) for l in lists)
        if hits >= max(1, len(lists) // 2 + 1) and not any(abs(a - c) <= tol and abs(b - d) <= tol for c, d in keep):
            keep.append((round(a, 1), round(b, 1)))
    return sorted(keep)


def guides(pdf: str, page: int, dpi: int = 72):
    r = render(pdf, dpi, page)
    w, h, _ = r
    rows = [int(h * f) for f in (0.2, 0.35, 0.5, 0.65, 0.8)]
    cols = [int(w * f) for f in (0.12, 0.3, 0.7, 0.88)]
    vertical = consensus([runs_along(r, y, True, dpi) for y in rows])     # bands crossing rows -> vertical bands
    horizontal = consensus([runs_along(r, x, False, dpi) for x in cols])
    return {"vertical": vertical, "horizontal": horizontal, "w_pt": w * PT / dpi, "h_pt": h * PT / dpi}


def safe_box(g):
    """Innermost guide edge on each side of the page = the line text must stay inside."""
    W, H = g["w_pt"], g["h_pt"]
    left = max([b for a, b in g["vertical"] if b < W / 2] or [0])
    right = min([a for a, b in g["vertical"] if a > W / 2] or [W])
    top = max([b for a, b in g["horizontal"] if b < H / 2] or [0])
    bottom = min([a for a, b in g["horizontal"] if a > H / 2] or [H])
    return left, top, right, bottom


# ── interior ────────────────────────────────────────────────────────────────

def check_interior(a) -> dict:
    P, O = info(a.proof), info(a.ours)
    rep = {"kind": "interior", "proof": P, "ours": O, "problems": [], "notes": []}
    if P["pages"] != O["pages"]:
        rep["problems"].append(f"page count differs: proof {P['pages']}, ours {O['pages']}")
    if abs(P["w"] - O["w"]) > 0.5 or abs(P["h"] - O["h"]) > 0.5:
        rep["problems"].append(f"page size differs: proof {P['w']}x{P['h']}pt, ours {O['w']}x{O['h']}pt")
    if O["created"] and P["created"] and O["created"] != P["created"]:
        rep["notes"].append(f"proof was made from a file created {P['created']}; yours was created {O['created']}. "
                            "If those differ you may have uploaded an older build.")

    pt, ot = page_texts(a.proof), page_texts(a.ours)
    # Same characters in a different order is an extraction artefact (text
    # runs re-ordered by the printer's tool), not a change to the page.
    diff = [i + 1 for i, (x, y) in enumerate(zip(pt, ot)) if x != y and sorted(x) != sorted(y)]
    reordered = [i + 1 for i, (x, y) in enumerate(zip(pt, ot)) if x != y and sorted(x) == sorted(y)]
    if reordered:
        rep["notes"].append(f"text extracts in a different order on page(s) {reordered[:20]} (same characters): not a change")
    rep["text_differs_on"] = diff
    if diff:
        rep["problems"].append(f"text differs on {len(diff)} page(s): {diff[:20]}")

    pi, oi = image_list(a.proof), image_list(a.ours)
    our_colors = Counter(c for *_, c in oi)
    # Our photos, by colour space; the proof keeps them and adds overlay images.
    main_cs = our_colors.most_common(1)[0][0] if our_colors else "cmyk"
    ours_main = [(p, w, h) for p, _, w, h, c in oi if c == main_cs]
    proof_main = [(p, w, h) for p, _, w, h, c in pi if c == main_cs]
    rep["photos"] = {"ours": len(ours_main), "proof": len(proof_main), "colorspace": main_cs,
                     "proof_colorspaces": dict(Counter(c for *_, c in pi)), "ours_colorspaces": dict(our_colors)}
    if ours_main != proof_main:
        missing = sorted(set(ours_main) - set(proof_main))[:10]
        rep["problems"].append(f"photos differ from ours ({main_cs}): {len(ours_main)} ours vs {len(proof_main)} in proof; "
                               f"first missing/changed (page,w,h): {missing}")
    overlay = Counter(p for p, _, _, _, c in pi if c == "rgb") if main_cs != "rgb" else Counter()
    if overlay:
        per = Counter(overlay.values())
        rep["notes"].append(f"RGB images in proof: {sum(overlay.values())} on {len(overlay)} pages "
                            f"(per-page counts {dict(per)}). One per page is the printer's guide overlay, not your art.")
        if set(per) - {1}:
            rep["problems"].append("some pages carry more than one RGB image: check whether a photo was converted to RGB")

    g = guides(a.proof, page=min(3, P["pages"]) or 1)
    L, T, R, B = safe_box(g)
    rep["safe_box_pt"] = [round(v, 1) for v in (L, T, R, B)]
    rep["guides_page3"] = g
    bad = []
    page = 0
    for line in run("pdftotext", "-bbox", a.proof, "-").splitlines():
        if "<page " in line:
            page += 1
        m = re.search(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*)</word>', line)
        if m:
            x0, y0, x1, y1 = map(float, m.groups()[:4])
            if x0 < L - 0.5 or x1 > R + 0.5 or y0 < T - 0.5 or y1 > B + 0.5:
                bad.append((page, m.group(5)[:30], round(x0), round(y0)))
    rep["text_outside_safe"] = bad[:50]
    if bad:
        rep["problems"].append(f"{len(bad)} word(s) outside the safety box {rep['safe_box_pt']}: {bad[:8]}")

    if a.placement:
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["pdftohtml", "-xml", "-zoom", "1", "-q", a.ours, f"{td}/x"], capture_output=True)
            xml = Path(f"{td}/x.xml").read_text(errors="replace")
        crossing = []
        for pm in re.finditer(r'<page number="(\d+)"[^>]*width="([\d.]+)"[^>]*>(.*?)</page>', xml, re.S):
            pw = float(pm.group(2))
            for t, l, w, h in re.findall(r'<image top="([-\d.]+)" left="([-\d.]+)" width="([\d.]+)" height="([\d.]+)"', pm.group(3)):
                t, l, w, h = map(float, (t, l, w, h))
                if w >= pw * 0.95:
                    continue                      # full-bleed by design
                if l < L or l + w > R or t < T or t + h > B:
                    crossing.append({"page": int(pm.group(1)), "x": round(l), "y": round(t), "w": round(w), "h": round(h)})
        rep["images_crossing_safe"] = crossing
        if crossing:
            rep["notes"].append(f"{len(crossing)} non-full-bleed image(s) cross the safety box: {crossing[:6]}. "
                                "Render those pages and look: a full-width title scrim is fine, a cropped photo is not.")
    return rep


# ── cover ───────────────────────────────────────────────────────────────────

def check_cover(a) -> dict:
    P, O = info(a.proof), info(a.ours)
    rep = {"kind": "cover", "proof": P, "ours": O, "problems": [], "notes": []}
    wrap, panel = a.wrap * PT, a.panel * PT
    rep["proof_width_in"] = round(P["w"] / PT, 3)
    rep["ours_width_in"] = round(O["w"] / PT, 3)
    rep["spine_from_proof_in"] = round((P["w"] - 2 * wrap - 2 * panel) / PT, 4)
    rep["spine_ours_in"] = round((O["w"] - 2 * wrap - 2 * panel) / PT, 4)

    # A printer that recalculates the spine centres your file on its wider
    # canvas: OnPress shows it as a negative MediaBox origin; other tools just
    # shift the art. Either way our art starts `pad` points in.
    pad = -P["mediabox"][0] if P["mediabox"] and P["mediabox"][0] < 0 else max(0.0, (P["w"] - O["w"]) / 2)
    if abs(P["w"] - O["w"]) > 0.5:
        rep["problems"].append(
            f"spread width differs: proof {P['w']:.2f}pt ({rep['proof_width_in']}in), ours {O['w']:.2f}pt "
            f"({rep['ours_width_in']}in). The printer's spine is {rep['spine_from_proof_in']}in; ours is "
            f"{rep['spine_ours_in']}in. Regenerate the cover at the printer's spine and upload it again.")
        if pad:
            rep["notes"].append(f"the proof's MediaBox starts at {-pad:.2f}pt: the printer centred your narrower file on its "
                                f"wider canvas, leaving {pad:.2f}pt unprinted at each outer edge")
    if O["created"] and P["created"] and O["created"] != P["created"]:
        rep["notes"].append(f"proof was made from a cover created {P['created']}; your current cover was created "
                            f"{O['created']}. You may have uploaded an older cover.")

    tp, to = squash(run("pdftotext", a.proof, "-")), squash(run("pdftotext", a.ours, "-"))
    rep["text_identical"] = tp == to
    if tp != to:
        rep["problems"].append("cover text differs from yours")

    g = guides(a.proof, 1)
    rep["guides"] = g
    mid = P["w"] / 2
    folds = sorted(g["vertical"], key=lambda r: abs((r[0] + r[1]) / 2 - mid))[:2]
    folds = sorted(folds)
    if len(folds) == 2:
        rep["fold_bands_pt"] = folds
        rep["spine_area_pt"] = [folds[0][1], folds[1][0]]
        # Our spine text (in proof coordinates: ours sits at +pad).
        dpi = 144
        x0, x1 = int((folds[0][0] - pad) * dpi / PT), int((folds[1][1] - pad) * dpi / PT)
        r = render(a.ours, dpi, 1, (max(0, x0), 0, max(1, x1 - x0), int(O["h"] * dpi / PT)))
        w, h, buf = r
        lum = sorted(buf[i] * 3 + buf[i + 1] * 6 + buf[i + 2] for i in range(0, len(buf), 3 * 7))
        bg = lum[len(lum) // 2] / 10
        xs = []
        for y in range(0, h, 2):
            for x in range(w):
                o = (y * w + x) * 3
                if abs((buf[o] * 3 + buf[o + 1] * 6 + buf[o + 2]) / 10 - bg) > 110:
                    xs.append(x)
        if xs:
            lo = pad + (x0 + min(xs)) * PT / dpi
            hi = pad + (x0 + max(xs)) * PT / dpi
            centre = (folds[0][1] + folds[1][0]) / 2
            rep["spine_text_pt"] = [round(lo, 1), round(hi, 1)]
            rep["spine_text_offset_pt"] = round((lo + hi) / 2 - centre, 1)
            clear = min(lo - folds[0][1], folds[1][0] - hi)
            rep["spine_text_clearance_pt"] = round(clear, 1)
            if clear < 4:
                rep["problems"].append(f"spine text comes within {clear:.1f}pt of a fold guide")
            if abs(rep["spine_text_offset_pt"]) > 4:
                rep["problems"].append(f"spine text is {rep['spine_text_offset_pt']}pt off the centre of the spine")
        else:
            rep["notes"].append("no spine text found between the folds (none on this cover?)")
    else:
        rep["notes"].append("could not find two fold guides near the centre; is this a hardcover proof?")

    # Pixel comparison outside the guide bands.
    dpi = 72
    rp, ro = render(a.proof, dpi), render(a.ours, dpi)
    (wp, hp, bp), (wo, ho, bo) = rp, ro
    off = round(pad * dpi / PT)
    bandx = [(int(a_ * dpi / PT) - 3, int(b_ * dpi / PT) + 3) for a_, b_ in g["vertical"]]
    bandy = [(int(a_ * dpi / PT) - 3, int(b_ * dpi / PT) + 3) for a_, b_ in g["horizontal"]]
    edge = max([b for a_, b in g["vertical"] if b < P["w"] / 4] + [0]) * dpi / PT + 3
    diff = tot = 0
    for y in range(hp):
        if any(a_ <= y <= b_ for a_, b_ in bandy) or y >= ho:
            continue
        for x in range(wp):
            if x < edge or x > wp - edge or any(a_ <= x <= b_ for a_, b_ in bandx):
                continue
            xo = x - off
            if not 0 <= xo < wo:
                continue
            tot += 1
            i, j = (y * wp + x) * 3, (y * wo + xo) * 3
            if max(abs(bp[i + k] - bo[j + k]) for k in range(3)) > 40:
                diff += 1
    rep["pixels_compared"], rep["pixels_differing"] = tot, diff
    if tot and diff / tot > 0.002:
        rep["problems"].append(f"{diff} of {tot} pixels differ outside the guide bands ({100 * diff / tot:.2f}%)")
    return rep


def summary(rep: dict) -> str:
    out = [f"{rep['kind'].upper()}: proof {rep['proof']['pages']}p {rep['proof']['w']:.2f}x{rep['proof']['h']:.2f}pt, "
           f"ours {rep['ours']['pages']}p {rep['ours']['w']:.2f}x{rep['ours']['h']:.2f}pt"]
    if rep["kind"] == "interior":
        out.append(f"  text identical on all pages: {not rep['text_differs_on']}")
        ph = rep["photos"]
        out.append(f"  photos ({ph['colorspace']}): ours {ph['ours']}, proof {ph['proof']}; proof colour spaces {ph['proof_colorspaces']}")
        out.append(f"  safety box read off the proof's guides: {rep['safe_box_pt']}; words outside: {len(rep['text_outside_safe'])}")
        if "images_crossing_safe" in rep:
            out.append(f"  non-bleed images crossing the safety box: {len(rep['images_crossing_safe'])}")
    else:
        out.append(f"  width: proof {rep['proof_width_in']}in, ours {rep['ours_width_in']}in -> spine proof "
                   f"{rep['spine_from_proof_in']}in, ours {rep['spine_ours_in']}in")
        if "fold_bands_pt" in rep:
            out.append(f"  fold guides {rep['fold_bands_pt']}, spine area {rep['spine_area_pt']}")
        if "spine_text_pt" in rep:
            out.append(f"  spine text {rep['spine_text_pt']}pt, offset from centre {rep['spine_text_offset_pt']}pt, "
                       f"clearance {rep['spine_text_clearance_pt']}pt")
        out.append(f"  text identical: {rep['text_identical']}; pixels differing outside guides: "
                   f"{rep['pixels_differing']} of {rep['pixels_compared']}")
    for n in rep["notes"]:
        out.append(f"  note: {n}")
    for p in rep["problems"]:
        out.append(f"  PROBLEM: {p}")
    out.append("  VERDICT: " + ("OK to approve" if not rep["problems"] else "do NOT approve yet"))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="kind", required=True)
    for k in ("interior", "cover"):
        s = sub.add_parser(k)
        s.add_argument("--proof", required=True)
        s.add_argument("--ours", required=True)
        s.add_argument("--json", action="store_true")
        if k == "interior":
            s.add_argument("--placement", action="store_true", help="also check image positions (slow on big books)")
        else:
            s.add_argument("--wrap", type=float, default=0.75, help="cover wrap per side, inches")
            s.add_argument("--panel", type=float, default=11.0, help="front/back panel width (trim width), inches")
    a = ap.parse_args()
    for f in (a.proof, a.ours):
        if not Path(f).exists():
            sys.exit(f"not found: {f}")
    rep = check_interior(a) if a.kind == "interior" else check_cover(a)
    print(json.dumps(rep, indent=1, default=str) if a.json else summary(rep))
    sys.exit(1 if rep["problems"] else 0)


if __name__ == "__main__":
    main()
