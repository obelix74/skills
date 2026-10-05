---
name: art-show-kit
description: Produce and check the printed materials for an art show or market booth where a photographer sells prints and a book - the book flyer, the show price list, the wall labels for each print, and insert cards such as an errata card - generated from the project's own data so prices, edition, page count and titles match the website. Regenerates each piece, checks the words on every PDF (stale page counts or prices, em dashes, leftover template text, wrong paper size), renders previews to look at, and lists anything the owner must reprint. Use for "I have an art show coming up", "make a flyer for the book", "regenerate the flyer", "print the price list", "make wall labels", "errata card", "are my show materials up to date".
argument-hint: "[which pieces, e.g. 'flyer and labels']"
allowed-tools: Bash(python3:*) Bash(npx:*) Bash(npm:*) Bash(ls:*) Bash(pdftoppm:*) Bash(pdftotext:*) Bash(find:*) Read Edit
---

# Art show kit

## Live context

- Generators in this project: !`ls scripts 2>/dev/null | grep -iE "flyer|price|label|errata|card|poster|sign" | head -12 || echo "(none)"`
- package.json scripts: !`python3 -c "import json;s=json.load(open('package.json')).get('scripts',{});print({k:v for k,v in s.items() if any(w in k for w in ('price','label','flyer','card'))})" 2>/dev/null`
- Existing print pieces: !`find . -path ./node_modules -prune -o \( -iname '*flyer*.pdf' -o -iname '*price*.pdf' -o -iname '*label*.pdf' -o -iname '*label*.docx' -o -iname '*errata*.pdf' \) -print 2>/dev/null | head -10`
- Request: $ARGUMENTS

## Principles

- **Generate, never hand-edit.** Every piece comes from the same data the
  website uses (book edition table, print price table, photo titles), so a
  price or page-count change flows to the show automatically. A hand-made
  document drifts; if one exists, replace it with a generator.
- **One sheet, real paper.** Flyers on US Letter; labels and cards on the die
  cut stock the owner already uses (for wall labels and insert cards: US
  Letter, 1in top margin, 0.25in sides, two columns of 4 x 3in, six per
  sheet). Keep text inset from each die cut.
- **No numbers that go stale on paper.** An insert card should not say "26
  corrections"; the list online can grow. Say "the full list is online" with a
  QR code.
- **House style**: no em dashes; the donation (e.g. all profits to a charity)
  in the headline if that is the point of the piece.

## Workflow

1. Pick the pieces asked for (default: everything the live context found).
2. Regenerate each with its generator. Book facts (edition, pages, price,
   pre-order date) must come from the project's edition source, not literals.
3. Check every PDF:

   ```bash
   python3 scripts/check_print_copy.py dist/print/book-flyer.pdf --pages 132 --price 65 \
       --expect "Search and Rescue" "Second edition" --preview /tmp/show-preview
   ```

   It fails on em/en dashes, a page count or book price that disagrees with
   the flags, missing or forbidden phrases, and template leftovers
   (TODO, lorem, undefined, NaN, {{ }}). Read the preview PNGs and look at
   them: QR code present and scannable size, nothing clipped at the die cuts.
4. Report each file's path and what it says (edition, pages, price, dates),
   and say which pieces the owner has already printed and must reprint.
