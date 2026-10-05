---
name: build-print-book
description: Build or rebuild the print-ready PDFs of a photo book (interior and cover) from a web/HTML book pipeline, and adjust its layout - combine two pages, make a photo bigger or smaller, put a photo beside its text, run lists in columns, make photos full width, shed pages to drop a printer signature. Runs the project's build loop until the photo fitting settles, reports page count against the printer's page multiple, near-empty pages and low-resolution photos, renders a thumbnail sheet of every page, and keeps the cover's spine in step with the page count. Use for "rebuild the book PDF", "export the book", "combine pages 26 and 27", "make page 50 two columns", "make the photos bigger", "how many pages would it be if...", "drop 4 pages", or any print layout change.
argument-hint: "[what to change, e.g. 'combine pages 129-132']"
allowed-tools: Bash(python3:*) Bash(npm:*) Bash(pdfinfo:*) Bash(pdftoppm:*) Bash(pdftotext:*) Bash(pdfimages:*) Bash(git:*) Bash(ls:*) Bash(cat:*) Read Edit
---

# Build the print book

## Live context

- Project: !`basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`
- Build entry points in package.json: !`python3 -c "import json;s=json.load(open('package.json')).get('scripts',{});print({k:v for k,v in s.items() if any(w in k for w in ('book','print','pdf','export'))})" 2>/dev/null || echo "(no package.json)"`
- Current print PDFs: !`for f in $(find . -path ./node_modules -prune -o -path '*/print/*' -name '*.pdf' -print 2>/dev/null | head -6); do printf "%s  " "$f"; pdfinfo "$f" 2>/dev/null | awk '/^Pages/{p=$2} /^Page size/{s=$3"x"$5} END{print p" pages, "s"pt"}'; done`
- Uncommitted changes: !`git status --short 2>/dev/null | head -10`
- Request: $ARGUMENTS

## How this kind of pipeline works

Book pages are HTML (chapters + photos) rendered by headless Chrome to PDF,
converted to CMYK at 300 dpi with Ghostscript, then a fitter measures the PDF
and writes per-photo height overrides so a short tail of text does not spill
onto its own page. Rendering and fitting alternate until nothing changes
("settled"). The cover is built after the interior because its spine depends
on the page count. If this project has a `references/<project>.md` here, read
it first: it names the scripts, data sources and printer for that project.
For anands.net that is `references/anands-net.md`.

## Workflow

1. **Find the build.** Use the live context: a `book:print`-style script that
   loops export and fit is the one to run. Read it before running it; note any
   environment it needs (a database URL through a proxy, an env file).
2. **Before a layout change, record the baseline**: page count and a report.

   ```bash
   python3 scripts/page_report.py dist/print/<target>/book.pdf --multiple 4
   ```

3. **Make the change in the generator, not in the PDF.** Recipes for the
   common requests are in `references/layout-fixes.md` (combine pages, photo
   beside text, lists in columns, full-width photos, shed a signature). Prefer
   print-only CSS or a post-processing step on the generated HTML over editing
   chapter content, so the website is untouched unless the user asked for both.
4. **Rebuild** with the project's loop and wait for "settled". It takes
   minutes; run it in the background and check the output when it finishes.
5. **Verify**:
   - `page_report.py` again: page count, trailing blank padding, stubs,
     images under 240 ppi.
   - Render only the pages that changed at readable size and look at them:
     `pdftoppm -r 40 -png -f N -l M book.pdf /tmp/p` then Read the PNGs.
   - Whole book at a glance: `python3 scripts/contact_sheet.py book.pdf sheet.png --numbers`.
   - Text unchanged except where intended: `diff <(pdftotext old.pdf -) <(pdftotext new.pdf -)`.
6. **Report**: new page count (and blank padding), what moved where, anything
   the change cost (a photo shrunk to fit, a list split across a page).
7. **Page count changed?** The cover spine is now wrong. Say so, and tell the
   user to upload the new interior **and** re-upload the cover so the printer
   recalculates; then verify the returned proof with the `verify-print-proof`
   skill and set the spine to what it measures. Also run the `book-edition`
   skill to update every place the page count is printed (site, flyer).

## Predicting before committing

To answer "how many pages if the photos were bigger?" without touching the
repo, copy the generated HTML to a scratch directory, inject the CSS change,
render it through the same Chrome + Ghostscript + fitter loop there, and report
the settled page count. Fit overrides from the current layout do not apply to
a different layout: start the experiment with none.
