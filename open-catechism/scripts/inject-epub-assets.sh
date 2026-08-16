#!/bin/sh
set -eu

book=$1
stage=$(mktemp -d "$PWD/dist/epub-images.XXXXXX")
trap 'rm -rf "$stage"' EXIT HUP INT TERM

unzip -q "$book" -d "$stage"
mkdir -p "$stage/OEBPS/assets"
cp -R assets/art "$stage/OEBPS/assets/"
sed -i '' 's|src="/assets/|src="assets/|g' "$stage/OEBPS/book.xhtml"

output="$stage/rebuilt.epub"
(
  cd "$stage"
  zip -q -X -0 "$output" mimetype
  zip -q -X -r "$output" META-INF OEBPS
)
mv -f "$output" "$book"
unzip -tq "$book"
