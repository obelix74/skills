---
name: book-edition
description: Change what a self-published book's store says about its edition - a new edition, a new page count, going to pre-order with a ship date, sold out, "N copies left", switching to the next edition when the last copy sells, a price change - and make every place that states it agree - the product page and checkout, order emails, stock settings, the print cover spine, the art show flyer and other generated print pieces. Finds every reference first, changes them together, regenerates the print pieces, deploys only when asked, and checks the live page. Use for "we're out of first editions", "make it a pre-order shipping Oct 19", "one copy left", "the second edition is 132 pages now", "update the flyer", "change the book price".
argument-hint: "[what changed, e.g. 'second edition is 132 pages']"
allowed-tools: Bash(python3:*) Bash(git:*) Bash(curl:*) Bash(npx:*) Bash(pdftotext:*) Read Edit
---

# Change the book's edition facts

## Live context

- Edition facts in this repo right now (summary):
  !`python3 "$(dirname "$(find ~/.claude/skills ~/projects/skills -path '*book-edition/scripts/find_edition_refs.py' 2>/dev/null | head -1)")/find_edition_refs.py" . --pdfs dist/print 2>/dev/null | grep -E "^## |STALE|pages\b" | head -30 || echo "(run scripts/find_edition_refs.py from this skill)"`
- Last commits: !`git log --oneline -3 2>/dev/null`
- Request: $ARGUMENTS

## Workflow

1. **Map every reference before editing anything.**

   ```bash
   python3 scripts/find_edition_refs.py . --pages NEW --old-pages OLD [OLD2] --pdfs dist/print [--extra "October 19"]
   ```

   It groups hits by kind (page count, edition, pre-order/ship date, spine,
   stock, price) and marks lines that still state an old page count STALE.
   Generated PDFs (flyer, labels, cards) are included: they are the usual
   miss.

2. **Find the single source of truth** and change it there: usually an
   editions table (edition name, size label with page count, pre-order flag,
   ship date) that the product page, checkout, order emails and flyer all
   read. Change a historical comment only if it is now false; a line that
   records what an earlier edition was is history, leave it.

3. **Stock-driven switches** (sell edition N until it runs out, then N+1 as a
   pre-order): keep the count in a setting the owner can edit in the admin,
   claim copies atomically when an order is paid (`UPDATE ... SET v = v - n
   ... WHERE v > 0 RETURNING`), and split a basket that wants more than are
   left into an edition-N line and an edition-N+1 line. Do not show "only N
   left" unless the owner wants it: it can make buyers wait for the next
   edition instead.

4. **Regenerate what is printed from it**: the flyer and any cards
   (`npx tsx scripts/book-flyer.ts` or the project's equivalent), then check
   their text with the `art-show-kit` skill's `check_print_copy.py --pages NEW`.

5. **Page count changed?** The cover spine changes with it, and only the
   printer knows by how much. Do not compute it. Re-upload the cover, measure
   the returned proof (`verify-print-proof` skill), then set the spine.

6. **Type-check**, show the diff, and **commit / deploy only when asked**.
   After a deploy, fetch the live product page and confirm the new text is
   there (strip React's `<!-- -->` comments before matching).

7. **Report**: each place changed, what the live page now says, and anything
   still to do by hand (reprint flyers already printed, re-upload the cover).
