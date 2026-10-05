#!/usr/bin/env bash
# Self-test for the photo-book-publishing skills' scripts.
#
#   BOOK=path/to/interior.pdf COVER=path/to/cover.pdf [OLD_BOOK=older-build.pdf] \
#   [OLD_COVER=cover-at-old-spine.pdf SPINE=0.762 OLD_SPINE=0.683] [REPO=path/to/book/repo] \
#   [SUBSTACK=https://www.example.com] tests/run_tests.sh
#
# Builds fake printer proofs from your own PDFs and checks that good ones pass
# and broken ones fail. Needs poppler and Ghostscript. Skips what it lacks.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
pass=0; fail=0
ok()   { echo "  PASS  $1"; pass=$((pass+1)); }
bad()  { echo "  FAIL  $1"; fail=$((fail+1)); }
expect() { # expect <exit code> <label> <cmd...>
  local want=$1 label=$2; shift 2
  "$@" > "$T/out.txt" 2>&1; local got=$?
  if [ "$got" = "$want" ]; then ok "$label"; else bad "$label (exit $got, wanted $want)"; sed 's/^/        /' "$T/out.txt" | tail -8; fi
}
V="$HERE/verify-print-proof/scripts"; B="$HERE/build-print-book/scripts"

echo "verify-print-proof"
if [ -n "${COVER:-}" ]; then
  SP="${SPINE:-$(python3 -c "import subprocess,re;w=float(re.search(r'Page size:\s+([\d.]+)',subprocess.run(['pdfinfo','$COVER'],capture_output=True,text=True).stdout).group(1));print(round((w-2*0.75*72-2*11*72)/72,4))")}"
  python3 "$V/make_test_proof.py" cover "$COVER" "$T/cg.pdf" --spine "$SP" >/dev/null
  expect 0 "good cover proof is approved" python3 "$V/verify_proof.py" cover --proof "$T/cg.pdf" --ours "$COVER"
  if [ -n "${OLD_COVER:-}" ]; then
    python3 "$V/make_test_proof.py" cover "$OLD_COVER" "$T/cs.pdf" --spine "${OLD_SPINE:-0.683}" --canvas-spine "$SP" >/dev/null
    expect 1 "old cover on a recalculated spine is rejected" python3 "$V/verify_proof.py" cover --proof "$T/cs.pdf" --ours "$OLD_COVER"
    grep -q "Regenerate the cover" "$T/out.txt" && ok "  ...and the fix (regenerate at the printer's spine) is named" || bad "  ...fix not named"
  fi
fi
if [ -n "${BOOK:-}" ]; then
  gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sColorConversionStrategy=LeaveColorUnchanged \
     -dFirstPage=1 -dLastPage=12 -sOutputFile="$T/slice.pdf" "$BOOK"
  python3 "$V/make_test_proof.py" interior "$T/slice.pdf" "$T/ig.pdf" >/dev/null
  expect 0 "good interior proof is approved" python3 "$V/verify_proof.py" interior --proof "$T/ig.pdf" --ours "$T/slice.pdf"
  python3 "$V/make_test_proof.py" interior "$T/slice.pdf" "$T/it.pdf" --safety 160 >/dev/null
  expect 1 "text outside a tight safety line is caught" python3 "$V/verify_proof.py" interior --proof "$T/it.pdf" --ours "$T/slice.pdf"
  gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sColorConversionStrategy=LeaveColorUnchanged \
     -dFirstPage=1 -dLastPage=11 -sOutputFile="$T/short.pdf" "$BOOK"
  python3 "$V/make_test_proof.py" interior "$T/short.pdf" "$T/is.pdf" >/dev/null
  expect 1 "a proof with a missing page is rejected" python3 "$V/verify_proof.py" interior --proof "$T/is.pdf" --ours "$T/slice.pdf"
  if [ -n "${OLD_BOOK:-}" ]; then
    gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sColorConversionStrategy=LeaveColorUnchanged \
       -sOutputFile="$T/old.pdf" "$OLD_BOOK"
    python3 "$V/make_test_proof.py" interior "$T/old.pdf" "$T/io.pdf" >/dev/null
    expect 1 "a proof of an older build is rejected" python3 "$V/verify_proof.py" interior --proof "$T/io.pdf" --ours "$BOOK"
  fi

  echo "build-print-book"
  expect 0 "page report runs" python3 "$B/page_report.py" "$BOOK"
  gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile="$T/padded.pdf" "$T/slice.pdf" -c "showpage showpage" 2>/dev/null
  python3 "$B/page_report.py" "$T/padded.pdf" > "$T/out.txt"
  grep -q "2 blank page" "$T/out.txt" && ok "trailing blank padding is counted" || bad "trailing blank padding not counted"
  expect 0 "contact sheet renders" python3 "$B/contact_sheet.py" "$T/slice.pdf" "$T/sheet.png" --numbers
  python3 -c "import sys; sys.exit(open('$T/sheet.png','rb').read(4) != b'\x89PNG')" 2>/dev/null \
    && ok "contact sheet is a PNG" || bad "contact sheet missing or not a PNG"
fi

echo "art-show-kit"
gs -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile="$T/flyer.pdf" -sPAPERSIZE=letter \
   -c "/Helvetica findfont 14 scalefont setfont 72 700 moveto (Hardcover - 132 pages - \$65) show 72 680 moveto (All profits go to Search and Rescue) show showpage"
expect 0 "clean flyer passes" python3 "$HERE/art-show-kit/scripts/check_print_copy.py" "$T/flyer.pdf" --pages 132 --price 65 --expect "Search and Rescue"
expect 1 "stale page count is caught" python3 "$HERE/art-show-kit/scripts/check_print_copy.py" "$T/flyer.pdf" --pages 116
expect 1 "missing phrase is caught" python3 "$HERE/art-show-kit/scripts/check_print_copy.py" "$T/flyer.pdf" --expect "pre-order"

echo "chapter-edit"
cat > "$T/ch.mdx" <<'EOF'
## Day 1

We walked the the long way.

[[photo:Banner Peak]]

[[sparkle:nope]]

[[photo:Nowhere Lake]]

A long day — and then camp.
EOF
echo '[{"title":"Banner Peak and Thousand Island Lake","hash":"a"},{"title":"Garnet Lake","hash":"b"}]' > "$T/ch.photos.json"
expect 1 "chapter lint fails on seeded errors" python3 "$HERE/chapter-edit/scripts/check_chapter.py" "$T/ch.mdx"
for s in "em dash" "unknown marker" "matches no photo" "doubled word"; do
  grep -q "$s" "$T/out.txt" && ok "  ...reports: $s" || bad "  ...missed: $s"
done
printf '## Day 2\n\nA 3\xe2\x80\x934 day hike.\n\n[[photo:Garnet Lake]]\n' > "$T/ok.mdx"; cp "$T/ch.photos.json" "$T/ok.photos.json"
expect 0 "clean chapter passes (range en dash allowed)" python3 "$HERE/chapter-edit/scripts/check_chapter.py" "$T/ok.mdx"

echo "book-edition"
mkdir -p "$T/repo/src"; echo 'export const E = { sizeLabel: "11 x 8.5 in, 116 pages" };' > "$T/repo/src/book.ts"
python3 "$HERE/book-edition/scripts/find_edition_refs.py" "$T/repo" --pages 132 --old-pages 116 > "$T/out.txt"
grep -q "STALE" "$T/out.txt" && ok "stale page count is flagged" || bad "stale page count not flagged"
[ -n "${REPO:-}" ] && expect 0 "edition scan runs on the real repo" python3 "$HERE/book-edition/scripts/find_edition_refs.py" "$REPO"

echo "newsletter-sync"
if [ -n "${SUBSTACK:-}" ]; then
  expect 0 "audit runs with every cover host allowed" python3 "$HERE/newsletter-sync/scripts/newsletter_audit.py" substack "$SUBSTACK" --allowed-hosts "**.com" "**.amazonaws.com"
  expect 1 "an unlisted cover host is caught" python3 "$HERE/newsletter-sync/scripts/newsletter_audit.py" substack "$SUBSTACK" --allowed-hosts example.org
else
  echo "  skip  (set SUBSTACK=https://... to test against a live newsletter)"
fi

echo; echo "$pass passed, $fail failed"
[ "$fail" = 0 ]
