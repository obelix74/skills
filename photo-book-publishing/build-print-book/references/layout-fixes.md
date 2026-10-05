# Print layout recipes

Each is a change to the HTML/CSS generator, followed by a rebuild. Measure the
page count before and after.

## Combine two pages (a photo or block spilled onto its own page)

1. Render both pages and find what spilled: usually a photo whose height plus
   caption plus top margin is a little more than the free space left.
2. Measure the free space: `pdftotext -bbox -f N -l N` gives the y of the last
   text on page N; content bottom = page height - bottom margin - bleed.
3. Shrink that one photo just enough: a per-photo max-height override (the
   fitter's JSON, keyed by the photo's content hash). Shrink to clear by
   0.2-0.3in; the fitter may shave more, but never below its floor.
4. If shrinking would make the photo too small (under ~2.2in tall), move
   something else instead: a pull quote, or the paragraph after the photo.

## Shed pages to drop a signature

Printers bind in signatures (OnPress: multiples of 4). Content of 133 pages
prints 136. Find the cheapest pages with `page_report.py`: near-empty stubs,
lists set one item per line, headings whose keep-with-next space pushes a
short block to the next page. Typical wins:
- **Short lists in columns**: `ul { columns: 3; column-gap: .3in }` with
  `li { break-inside: avoid }`, scoped to that section only (add a class in a
  post-processing step rather than changing every list in the book).
- **Smaller keep-with-next reserve** for headings that introduce a few lines:
  a heading's `::after` spacer reserves room so it is not stranded at a page
  foot; 1.4in is right before prose, 0.6-0.7in before a three-line list.

## Photo beside its text (two columns)

For a portrait photo sitting small and alone under a few paragraphs: wrap the
heading, its text (and a pull quote just above it) and the photo in a grid,
`grid-template-columns: 1fr auto; gap: .4in; align-items: center`, photo up to
~3.9 x 5.8in. Lift the photo out of the gallery/duo it was in; leave the rest
of that gallery where it was. Drop any fit override on that photo (the old
size no longer applies). Keep the caption to the photo's width
(`figcaption { width: 0; min-width: 100% }`).

## Full-width photos

Pairs and galleries one photo per row at up to 8.25 x 5.5in; let the gallery
break between photos (`break-inside: auto`) but never inside one
(`.item { break-inside: avoid }`). Shrink-wrap each item to its image
(`width: fit-content; margin: 0 auto`) so a fitted photo keeps its caption
under its own left edge. Expect roughly +15-25% pages; clear the fitter's old
overrides first.

## Two photos stacked on one page / side by side

A duo of a portrait and a panorama reads better stacked (the panorama gets the
full width); two landscapes of similar weight read better side by side. Swap
the marker (`[[duo:A|B]]` vs `[[stack:A|B]]`) and rebuild.
