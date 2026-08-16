#!/bin/sh
set -eu

work=$(mktemp -d "$PWD/dist/pdf-editions.XXXXXX")
trap 'rm -rf "$work"' EXIT HUP INT TERM
mkdir -p "$work/full" "$work/short" "$work/passages"

normalize() {
  src=$1
  dst="$work/full/$(basename "$src")"
  if test "$(head -1 "$src")" = '---'; then
    title=$(grep '^title:' "$src" | head -1 | cut -d: -f2- | tr -d '"' | sed 's/^ *//')
    printf '# %s\n\n' "$title" > "$dst"
    awk 'NR==1 && $0=="---" { front=1; next } front && $0=="---" { front=0; next } !front { print }' "$src" >> "$dst"
  else
    cp "$src" "$dst"
  fi
  sed -i '' '/^<a id="[^"]*"><\/a>$/d' "$dst"
  perl -pi -e 's/\[([^]\n]+)\]\(#[^)]+\)/$1/g' "$dst"
}

for src in content/prefaces.md content/units/*.md content/divine-service.md content/divine-name.md; do normalize "$src"; done

for src in "$work/full"/*.md; do
  base=$(basename "$src")
  PASSAGE_INPUT="$src" PASSAGE_SHORT="$work/short/$base" PASSAGE_COMPANION="$work/passages/$base" go run ./cmd/passage-editions
  if test ! -s "$work/passages/$base"; then rm "$work/passages/$base"; fi
done

! grep -RqF 'Read this passage in the accompanying' "$work/short"

build_pdf() {
  out=$1; edition=$2; shift 2
  driver="dist/$out.typ"
  {
    printf '%s\n' '#import "../templates/book.typ": catechism-template'
    printf '#catechism-template((\n'
    for src in "$@"; do printf '  "../%s",\n' "${src#$PWD/}"; done
    printf '), edition: "%s")\n' "$edition"
  } > "$driver"
  typst compile --root . --font-path assets/fonts --ignore-system-fonts "$driver" "dist/$out.pdf"
}

complete() { out=$1; shift; build_pdf "$out" "Svebilius/Laine Edition · Complete Text" "$@"; }
short() { out=$1; shift; build_pdf "${out}-short" "Short Reading Edition · Passages over 50 words referenced" "$@"; }
passages() { out=$1; shift; build_pdf "${out}-passages" "Scripture Passages Companion · Full texts omitted from the short edition" "$@"; }

complete open-catechism "$work/full/prefaces.md" "$work/full"/[0-9][0-9]-*.md "$work/full/divine-service.md" "$work/full/divine-name.md"
short open-catechism "$work/short/prefaces.md" "$work/short"/[0-9][0-9]-*.md "$work/short/divine-service.md" "$work/short/divine-name.md"
passages open-catechism "$work/passages"/[0-9][0-9]-*.md "$work/full/divine-name.md"

complete 01-foundations-commandments "$work/full/prefaces.md" "$work/full"/0[1-9]-*.md "$work/full"/1[0-2]-*.md "$work/full/divine-name.md"
short 01-foundations-commandments "$work/short/prefaces.md" "$work/short"/0[1-9]-*.md "$work/short"/1[0-2]-*.md "$work/short/divine-name.md"
passages 01-foundations-commandments "$work/passages"/0[1-9]-*.md "$work/passages"/1[0-2]-*.md "$work/full/divine-name.md"

complete 02-creed "$work/full"/1[3-6]-*.md "$work/full/divine-name.md"
short 02-creed "$work/short"/1[3-6]-*.md "$work/short/divine-name.md"
passages 02-creed "$work/passages"/1[3-6]-*.md "$work/full/divine-name.md"

complete 03-lords-prayer "$work/full"/1[7-9]-*.md "$work/full"/2[0-6]-*.md "$work/full/divine-name.md"
short 03-lords-prayer "$work/short"/1[7-9]-*.md "$work/short"/2[0-6]-*.md "$work/short/divine-name.md"
passages 03-lords-prayer "$work/passages"/1[7-9]-*.md "$work/passages"/2[0-6]-*.md "$work/full/divine-name.md"

complete 04-means-of-grace "$work/full"/2[7-9]-*.md "$work/full"/3[0-3]-*.md "$work/full/divine-name.md"
short 04-means-of-grace "$work/short"/2[7-9]-*.md "$work/short"/3[0-3]-*.md "$work/short/divine-name.md"
passages 04-means-of-grace "$work/passages"/2[7-9]-*.md "$work/passages"/3[0-3]-*.md "$work/full/divine-name.md"

complete 05-daily-life-divine-service "$work/full"/3[4-5]-*.md "$work/full/divine-service.md" "$work/full/divine-name.md"
short 05-daily-life-divine-service "$work/short"/3[4-5]-*.md "$work/short/divine-service.md" "$work/short/divine-name.md"
passages 05-daily-life-divine-service "$work/passages"/3[4-5]-*.md "$work/full/divine-name.md"

test "$(find dist -maxdepth 1 -name '*-short.pdf' -type f | wc -l | tr -d ' ')" = 6
test "$(find dist -maxdepth 1 -name '*-passages.pdf' -type f | wc -l | tr -d ' ')" = 6
