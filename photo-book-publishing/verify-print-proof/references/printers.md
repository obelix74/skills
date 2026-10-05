# What we know about printers' proofs

Learned the hard way on a 11 x 8.5in landscape hardcover photo book (2026).

## OnPress (onpress.com)

- **Proof files** are named `US-Letter-Landscape.pdf` (interior) and
  `US-Letter-Landscape-Hard-Cover.pdf` (cover); a re-download gets ` (1)`,
  ` (2)` appended. They are produced with PDFsharp, which keeps your file's
  `CreationDate`: compare it with your build's to see which build they got.
- **Interior overlay**: one RGB image per page (the overlay), red bands ~45pt
  in from the sides and 31pt from top/bottom, yellow safety lines at 72pt from
  the sides. Safe text area on an 810 x 630pt page (11 x 8.5 + bleed):
  x 72-738, y 31-599. Photos keep their colour space (CMYK stays CMYK).
- **Page count must be a multiple of 4.** Pad with blank leaves at the end.
- **Cover overlay**: red wrap bands 45.5-58.5pt from each edge; two fold
  (hinge) bands either side of the spine, about 43pt wide, straddling each
  spine edge (34pt outside, 9pt inside).
- **Spine width is computed by OnPress from the interior page count, and only
  when the cover is uploaded against that interior.** A proof of an old cover
  keeps the old geometry. Measured:
  - 108 and 116 pages: spread 24.183in, spine 0.683in
  - 132 pages: spread 1746.86pt = 24.262in, spine 0.762in
  Spread = 2 x 0.75in wrap + 2 x 11in boards + spine.
- **When the spine changes** OnPress centres your narrower file on the wider
  canvas: the proof's MediaBox starts at a negative x (e.g. -2.84pt) and the
  outer edges of the case would print unpainted. Regenerate at the new spine,
  re-upload, re-check.

## Lulu

- Publishes its cover maths in the Book Creation Guide; hardcover spines come
  from a page-count table, not a formula. Do not use Lulu's table for another
  printer: on the book above it gave 0.500in where OnPress needed 0.683in.
- Page count must be even.

## IngramSpark

- Spine from their free cover template generator for your exact paper; the
  formula is not published. Get the template, measure the spine off it.
- Page count must be even.

## General

- Never trust a computed spine; measure the printer's template or proof.
- A text-only difference in extraction order (same characters) is an
  artefact of the printer's PDF tool, not a change.
