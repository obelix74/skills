# Project profile: anands.net (John Muir Trail book)

- **Build**: `PRINT_TARGET=onpress npm run book:print` runs
  `scripts/build-print.sh`: export (`scripts/export-print-book.ts`) then fit
  (`scripts/fit-photos.py`), up to 5 rounds, until "layout has settled".
- **Needs the production database** (chapter rows and photo assignments). Start
  the Cloud SQL proxy and point DATABASE_URL at it for the run, then stop it:

  ```bash
  cloud-sql-proxy anandsnet:us-central1:anands-net-db-central --port 9471 &
  export DATABASE_URL="$(gcloud secrets versions access latest --secret=DATABASE_URL --project=anandsnet \
    | sed 's#@/anands_net?host=.*#@127.0.0.1:9471/anands_net#')"
  PRINT_TARGET=onpress npm run book:print
  pkill -f "cloud-sql-proxy anandsnet"
  ```
- **Output**: `dist/print/onpress/jmt-book.pdf` (interior, 810 x 630pt pages),
  `jmt-cover.pdf` (spread), `jmt-book.html`, `photo-fit.json` (overrides, keyed
  by photo hash; `dist/` is git-ignored).
- **Layout knobs in `export-print-book.ts`**: `PHOTO_W_IN`/`PHOTO_H_IN`
  (gallery/duo/stack photo size), `BESIDE_TEXT` (photo beside text, by heading
  and photo title), `compactCampLists` (three-column lists in "Where I
  camped"), heading `::after` reserve (1.4in default, 0.7in for camp years),
  `SPINE_OVERRIDE_IN` (measured off the printer's proof, see
  verify-print-proof/references/printers.md).
- **Chapter source**: `src/content/jmt/*.mdx` with `[[markers]]`; full marker
  reference in `docs/book-authoring.md`.
- **Printer**: OnPress, page multiple 4, hardcover 11 x 8.5 landscape, 0.75in
  wrap.
- **Never commit unless asked; the user approves deploys.**
