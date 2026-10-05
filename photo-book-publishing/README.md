# photo-book-publishing

Six [Claude Code skills](https://docs.claude.com/en/docs/claude-code/skills)
for publishing a self-printed photo book from a website and selling it, built
from the work of taking a John Muir Trail photo book (anands.net) from web
chapters to an OnPress hardcover, a store listing with editions and
pre-orders, art show materials and a newsletter-fed journal.

| Skill | Use it for |
|---|---|
| [`verify-print-proof`](verify-print-proof/SKILL.md) | Checking the printer's interior and cover proofs against what you uploaded, before you approve. Measures everything off the proof's own guide overlay: page count, text, every photo and its colour space, the safety area, the spine the printer computed, spine text between the folds. |
| [`build-print-book`](build-print-book/SKILL.md) | Rebuilding the print PDFs and changing their layout: combine pages, photo beside text, lists in columns, full-width photos, shed a signature, "how many pages if...". |
| [`book-edition`](book-edition/SKILL.md) | Changing edition facts (new edition, page count, pre-order and ship date, sold out, price) everywhere at once: store, checkout, emails, flyer, cover spine. |
| [`art-show-kit`](art-show-kit/SKILL.md) | Generating and checking the flyer, price list, wall labels and insert cards for a show. |
| [`newsletter-sync`](newsletter-sync/SKILL.md) | Pulling Substack or Beehiiv posts into the site's journal, keeping them in sync, and auditing what would break. |
| [`chapter-edit`](chapter-edit/SKILL.md) | Editing chapter prose and `[[marker]]` photo layouts in the author's voice, then linting them. |

They hand off to each other: a layout change (`build-print-book`) that moves
the page count needs the edition facts updated (`book-edition`) and the cover
re-proofed (`verify-print-proof`).

## Dynamic, not hard-coded

Each `SKILL.md` opens with a **Live context** block of `` !`command` `` lines
that Claude Code runs when the skill loads, so the skill starts from the real
state: the proof PDFs in `~/Downloads`, the project's build scripts, the
current page count, the image hosts the site allows, uncommitted chapter
edits. The workflow then branches on what it finds. Scripts read the facts
they need from the inputs (the printer's guides, the renderer's marker list,
`next.config` image hosts) instead of embedding them, so they work on another
book or another printer. Project specifics for anands.net live in
`build-print-book/references/anands-net.md`; printer knowledge in
`verify-print-proof/references/printers.md`.

## Scripts

Python 3 standard library only, plus poppler (`pdfinfo`, `pdftotext`,
`pdfimages`, `pdftoppm`, `pdftohtml`) and Ghostscript for the test fixtures.

| Script | Does |
|---|---|
| `verify-print-proof/scripts/verify_proof.py` | `interior` and `cover` proof checks; exit 1 on anything that blocks approval |
| `verify-print-proof/scripts/make_test_proof.py` | Paints printer-style guides on your own PDF, including a recalculated-spine canvas |
| `build-print-book/scripts/page_report.py` | Page count vs printer multiple, blank padding, stub pages, low-ppi photos |
| `build-print-book/scripts/contact_sheet.py` | One PNG of every page, numbered |
| `book-edition/scripts/find_edition_refs.py` | Every page count / edition / pre-order / spine / stock / price reference, stale ones flagged, generated PDFs included |
| `art-show-kit/scripts/check_print_copy.py` | Em dashes, stale page counts and prices, missing phrases, template leftovers, previews |
| `newsletter-sync/scripts/newsletter_audit.py` | What a Substack sync would bring over and what would break |
| `chapter-edit/scripts/check_chapter.py` | House style, unknown markers, photo keys that miss or are ambiguous |

## Install

```bash
# all six, for every project
cp -r photo-book-publishing/*/ ~/.claude/skills/        # copies each skill folder
# or link them so a git pull updates them
for d in photo-book-publishing/*/; do [ -f "$d/SKILL.md" ] && ln -s "$PWD/$d" ~/.claude/skills/; done
```

## Test

```bash
BOOK=dist/print/onpress/jmt-book.pdf COVER=dist/print/onpress/jmt-cover.pdf \
OLD_BOOK=older-build.pdf OLD_COVER=cover-at-old-spine.pdf OLD_SPINE=0.683 \
REPO=~/projects/anands.net SUBSTACK=https://www.norcalhiker.net \
  photo-book-publishing/tests/run_tests.sh
```

Builds fake proofs from your own PDFs and checks that the good ones pass and
the broken ones (old cover on a recalculated spine, an older build, a missing
page, text past the safety line) fail; lints seeded chapter errors; checks a
stale flyer; audits a live newsletter. Every variable is optional; tests for
missing inputs are skipped. Last run: 24 passed, 0 failed.
