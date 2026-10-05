---
name: verify-print-proof
description: Verify a printer's proof (OnPress, Lulu, IngramSpark, Blurb, any printer that returns your PDF with a guide overlay) against the interior and cover PDFs you uploaded, before you approve it for printing. Checks page count and size, page-by-page text, every photo and its colour space, text and images against the safety area read off the proof's own guides, and on a hardcover cover the spread width, the spine width the printer computed, the spine text between the fold guides, and a pixel comparison outside the guides. Catches the expensive mistakes - a stale build uploaded, a cover whose spine the printer silently recalculated, art centred on a wider canvas with white slivers at the edges. Use whenever someone says "verify the proof", "check the proofs", "can I approve", "is the proof OK", "review the print proof", or hands over a proof PDF from a printer.
argument-hint: "[proof.pdf ...]"
allowed-tools: Bash(python3:*) Bash(ls:*) Bash(pdfinfo:*) Bash(pdftoppm:*) Bash(pdftotext:*) Bash(pdfimages:*) Bash(find:*) Read
---

# Verify a print proof

The printer sends back what you uploaded with a translucent overlay: red bands
at trim and bleed, yellow lines at the safety area, and on a hardcover cover
fold bands either side of the spine. Approving a bad proof costs a print run,
so check it against the file you sent, by measurement, not by eye.

## Live context

- Proof-like PDFs in Downloads, newest first:
  !`ls -t ~/Downloads/*.pdf 2>/dev/null | head -8 || echo "(none)"`
- Print PDFs in this project, newest first:
  !`find . -path ./node_modules -prune -o -path '*/print/*' -name '*.pdf' -print 2>/dev/null | xargs ls -t 2>/dev/null | head -8 || echo "(none found)"`
- Arguments given: $ARGUMENTS

## Workflow

1. **Pair each proof with the file it was made from.** Interior proofs are
   multi-page at trim plus bleed; cover proofs are one wide page. Match by page
   count and size against the project's print output (above). If a proof path
   the user gave does not exist, list `~/Downloads` and say so plainly: people
   clear Downloads; ask for it to be downloaded again rather than guessing.

2. **Run the checker** from this skill's `scripts/` directory (the base
   directory is printed when the skill loads):

   ```bash
   python3 scripts/verify_proof.py interior --proof PROOF.pdf --ours OURS.pdf
   python3 scripts/verify_proof.py cover    --proof COVER_PROOF.pdf --ours OUR_COVER.pdf --wrap 0.75 --panel 11
   ```

   `--panel` is the trim width of one cover board (11 for an 11 x 8.5 landscape
   book), `--wrap` the case-wrap allowance per side (0.75in at OnPress). Add
   `--placement` to the interior run to also test every non-bleed image against
   the safety box; it is slow on a 90 MB book (a few minutes), so run it once,
   in the background if needed. `--json` gives everything machine-readable.

3. **Read the result, then decide:**
   - `VERDICT: OK to approve` with no PROBLEM lines: say so, with the numbers
     (pages, photos, colour space, safety box, spine).
   - A **width / spine** problem on the cover: the printer recalculated the
     spine for the new page count. The printer's spine is
     `proof width - 2 x wrap - 2 x panel`. Regenerate the cover at exactly that
     spine (see `references/printers.md`), check the new cover's size equals
     the proof's to the hundredth of a point, and have it re-uploaded. Never
     approve a cover whose proof is wider than your file: the art was centred
     and the outer edges print white.
   - **Text differs** on pages: render those pages from both PDFs
     (`pdftoppm -r 50 -f N -l N`) and compare. A stale upload shows as a
     shifted page; the creation-date note tells you which build they got.
   - **Photos differ** (page, w, h): a photo changed size or went missing.
     Same build mismatch as above, or the printer re-sampled.
   - **Images crossing the safety box** are notes, not verdicts: render the
     page and look. A full-width title scrim behind a chapter opener crosses by
     design; a photo cut by the trim does not.
   - A cover made from an **older file** (creation-date note) but pixel
     identical is fine. Say it, so nobody is surprised later.

4. **Report** in this order: verdict first, then the cover, then the interior,
   each with the few numbers that prove it, then anything the user has to do
   (re-download, regenerate, re-upload). If both proofs pass, say plainly that
   they can approve.

## Testing without a printer

`scripts/make_test_proof.py` paints OnPress-style guides onto your own PDF so
the checker can be exercised before a real proof exists, including the
failure that matters most:

```bash
python3 scripts/make_test_proof.py cover  OUR_COVER.pdf good.pdf --spine 0.762
python3 scripts/make_test_proof.py cover  OLD_COVER.pdf stale.pdf --spine 0.683 --canvas-spine 0.762   # printer recalculated
python3 scripts/make_test_proof.py interior OUR_BOOK.pdf proof.pdf
```

`references/printers.md` has what is known about each printer's overlay,
page multiples and spine behaviour.
