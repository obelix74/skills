#!/usr/bin/env python3
"""
Make a fake printer proof from your own PDF, for testing verify_proof.py
without waiting on the printer.

    make_test_proof.py interior IN.pdf OUT.pdf [--side 45 --topbot 31 --safety 72]
    make_test_proof.py cover    IN.pdf OUT.pdf --spine 0.762 [--canvas-spine 0.762] [--wrap 0.75 --panel 11]

Paints guide bands the way OnPress does (red trim bands, yellow safety lines,
fold bands either side of the spine) with Ghostscript, leaving the art and its
colour spaces untouched. `--canvas-spine` larger than the file's own spine
simulates a printer that recalculated the spine and centred your narrower
cover on a wider canvas, which is the failure verify_proof.py must catch.
"""
import argparse, subprocess

PT = 72.0
RED, YEL = "1 0 0 setrgbcolor", "1 0.9 0 setrgbcolor"


def rect(x, y, w, h, colour):
    return f"gsave {colour} {x:.2f} {y:.2f} {w:.2f} {h:.2f} rectfill grestore "


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["interior", "cover"])
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--side", type=float, default=45); ap.add_argument("--topbot", type=float, default=31)
    ap.add_argument("--safety", type=float, default=72)
    ap.add_argument("--spine", type=float, help="the cover file's own spine, in")
    ap.add_argument("--canvas-spine", type=float, help="the printer's spine, in (default: same as --spine)")
    ap.add_argument("--wrap", type=float, default=0.75); ap.add_argument("--panel", type=float, default=11.0)
    a = ap.parse_args()

    w, h = (float(v) for v in subprocess.run(["pdfinfo", a.src], capture_output=True, text=True).stdout
            .split("Page size:")[1].split("pts")[0].split(" x "))
    pad = 0.0
    if a.kind == "interior":
        W, H = w, h
        marks = (rect(a.side - 9, 0, 9, H, RED) + rect(W - a.side, 0, 9, H, RED) +
                 rect(0, a.topbot - 9, W, 9, RED) + rect(0, H - a.topbot, W, 9, RED) +
                 rect(a.safety - 2, 0, 2, H, YEL) + rect(W - a.safety, 0, 2, H, YEL))
    else:
        canvas = a.canvas_spine or a.spine
        W, H = 2 * (a.wrap + a.panel) * PT + canvas * PT, h
        pad = (W - w) / 2
        left = (a.wrap + a.panel) * PT
        right = left + canvas * PT
        marks = (rect(45.5, 0, 13, H, RED) + rect(W - 58.5, 0, 13, H, RED) +
                 rect(0, 45.5, W, 13, RED) + rect(0, H - 58.5, W, 13, RED) +
                 rect(left - 34, 0, 43, H, YEL) + rect(right - 9, 0, 43, H, YEL))
    ps = (f"<< /BeginPage {{ pop {pad:.3f} 0 translate }} "
          f"/EndPage {{ exch pop 0 eq {{ gsave {-pad:.3f} 0 translate {marks} grestore true }} {{ false }} ifelse }} >> setpagedevice")
    subprocess.run(["gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-sDEVICE=pdfwrite",
                    "-sColorConversionStrategy=LeaveColorUnchanged", "-dPassThroughJPEGImages=true",
                    "-dAutoRotatePages=/None", f"-dDEVICEWIDTHPOINTS={W:.2f}", f"-dDEVICEHEIGHTPOINTS={H:.2f}",
                    "-dFIXEDMEDIA", f"-sOutputFile={a.out}", "-c", ps, "-f", a.src], check=True)
    print(f"wrote {a.out} ({W:.2f}x{H:.2f}pt{f', art centred {pad:.2f}pt in' if pad else ''})")


if __name__ == "__main__":
    main()
