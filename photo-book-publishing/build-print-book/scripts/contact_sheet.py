#!/usr/bin/env python3
"""
Thumbnail sheet of every page of a PDF, as one PNG, for a quick look at
layout (empty pages, orphaned photos, pages to combine). Read the PNG to see it.

    contact_sheet.py BOOK.pdf OUT.png [--cols 12] [--dpi 12] [--first N --last M] [--numbers]

Needs pdftoppm. Standard library only (writes the PNG with zlib).
"""
import argparse, glob, struct, subprocess, tempfile, zlib
from pathlib import Path


def read_ppm(path):
    data = Path(path).read_bytes()
    parts, i = [], 0
    while len(parts) < 4:
        while data[i:i + 1].isspace():
            i += 1
        j = i
        while not data[j:j + 1].isspace():
            j += 1
        parts.append(data[i:j]); i = j
    w, h = int(parts[1]), int(parts[2])
    return w, h, data[i + 1:i + 1 + w * h * 3]


def write_png(path, w, h, rgb: bytearray):
    raw = b"".join(b"\x00" + bytes(rgb[y * w * 3:(y + 1) * w * 3]) for y in range(h))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


# 3x5 digits for page numbers
DIGITS = {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111",
          "4": "101101111001001", "5": "111100111001111", "6": "111100111101111", "7": "111001010010010",
          "8": "111101111101111", "9": "111101111001111"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf"); ap.add_argument("out")
    ap.add_argument("--cols", type=int, default=12); ap.add_argument("--dpi", type=int, default=12)
    ap.add_argument("--first", type=int); ap.add_argument("--last", type=int)
    ap.add_argument("--numbers", action="store_true", help="stamp page numbers on each thumbnail")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as td:
        cmd = ["pdftoppm", "-r", str(a.dpi)]
        if a.first: cmd += ["-f", str(a.first)]
        if a.last: cmd += ["-l", str(a.last)]
        subprocess.run(cmd + [a.pdf, f"{td}/p"], check=True)
        files = sorted(glob.glob(f"{td}/p-*.ppm"), key=lambda f: int(f.rsplit("-", 1)[1].split(".")[0]))
        pages = [read_ppm(f) for f in files]
        nums = [int(f.rsplit("-", 1)[1].split(".")[0]) for f in files]
    w = max(p[0] for p in pages); h = max(p[1] for p in pages); gap = 4
    cols = min(a.cols, len(pages)); rows = -(-len(pages) // cols)
    W, H = cols * (w + gap) + gap, rows * (h + gap) + gap
    canvas = bytearray(b"\x88" * (W * H * 3))
    for k, (pw, ph, buf) in enumerate(pages):
        ox, oy = gap + (k % cols) * (w + gap), gap + (k // cols) * (h + gap)
        for y in range(ph):
            o = ((oy + y) * W + ox) * 3
            canvas[o:o + pw * 3] = buf[y * pw * 3:(y + 1) * pw * 3]
        if a.numbers:
            s, scale = str(nums[k]), max(1, h // 40)
            for di, ch in enumerate(s):
                for bit, on in enumerate(DIGITS[ch]):
                    if on == "1":
                        for yy in range(scale):
                            for xx in range(scale):
                                X = ox + 2 + di * 4 * scale + (bit % 3) * scale + xx
                                Y = oy + 2 + (bit // 3) * scale + yy
                                o = (Y * W + X) * 3
                                canvas[o:o + 3] = b"\xd0\x10\x10"
    write_png(a.out, W, H, canvas)
    print(f"wrote {a.out}: {len(pages)} pages, {cols} per row, {W}x{H}px")


if __name__ == "__main__":
    main()
