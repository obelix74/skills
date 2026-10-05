---
name: chapter-edit
description: Edit the chapters of a photo book written as Markdown/MDX with [[marker]] blocks (photos, duos, galleries, stacks, pull quotes, maps, elevation profiles, datelines, asides) - rewrite prose in the author's voice, place or swap photos, add a pull quote, correct a fact and record it in the errata - then lint the chapter (house style, unknown markers, photo keys that match nothing or match two photos, photos placed twice) and preview it on the web page and in print. Use for "change this paragraph", "make it gentler", "put the sunrise photo after this", "swap these two photos", "add a pull quote", "fix the mileage in chapter 1", "check the chapters".
argument-hint: "[chapter and change]"
allowed-tools: Bash(python3:*) Bash(git:*) Bash(ls:*) Bash(curl:*) Read Edit
---

# Edit a book chapter

## Live context

- Chapters: !`ls src/content/*/*.mdx 2>/dev/null | head -20 || echo "(no src/content/*/*.mdx; find the chapter sources)"`
- Marker renderer: !`grep -rl 'case "pullquote"' src 2>/dev/null | head -2`
- Authoring guide: !`ls docs/*author* 2>/dev/null`
- Chapters changed but not committed: !`git status --short -- 'src/content' 2>/dev/null | head`
- Request: $ARGUMENTS

## The author's voice (keep it)

- First person, plain and specific: what happened, where, how it felt. No
  marketing language, no superlatives the author did not use.
- **No em dashes.** Use a comma, a colon, or two sentences. En dashes only in
  ranges (3–4 days, 11,000–13,000 ft).
- Prefer gentler words when describing hardship or other people; never mock.
- Do not invent facts (distances, dates, names). If a fact is needed and not
  in the sources, ask or leave it out.
- A factual correction to a printed edition is also an errata entry, quoted
  verbatim from the printed text.

## Markers

Each marker sits on its own line, with a blank line between it and prose.
Photo keys resolve against the photos assigned to that chapter only: a
1-based index, the exact title, or else the first title containing the key.
Prefer the exact title (index breaks when photos are reordered; a substring
can match two titles). The full marker list is in the project's authoring
guide; the renderer's `case "..."` lines are the source of truth.

Layout choices that read well in print:
- `[[duo:A|B]]` for two landscapes of similar weight; `[[stack:A|B]]` for a
  portrait with a panorama (the panorama needs the full width).
- A pull quote only for a line that earns it, at most one or two a chapter.

## Workflow

1. Read the chapter and its photo list (`CHAPTER.photos.json` beside it, or
   the admin's assignment list).
2. Make the change.
3. Lint:

   ```bash
   python3 scripts/check_chapter.py src/content/jmt/*.mdx --markers-src "<renderer>.tsx"
   ```

   Problems (em dash, unknown marker, a photo key that matches nothing) must be
   fixed; warnings (doubled word, key matching two titles, photo placed
   twice, marker touching prose) should be.
4. Preview: the web chapter on the dev server, and if the page is in the
   printed book, rebuild and look at the changed pages (`build-print-book`
   skill). A prose change can move every page after it.
5. Report the diff in words, the lint result, and any page-count change.
