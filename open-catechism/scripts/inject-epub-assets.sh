#!/bin/sh
set -eu

book=$1
stage=$(mktemp -d "$PWD/dist/epub-images.XXXXXX")
trap 'rm -rf "$stage"' EXIT HUP INT TERM

unzip -q "$book" -d "$stage"
mkdir -p "$stage/OEBPS/assets"
cp -R assets/art "$stage/OEBPS/assets/"
sed -i '' 's|src="/assets/|src="assets/|g' "$stage/OEBPS/book.xhtml"

image_items=
for image in assets/art/unit-*.jpg; do
  base=$(basename "$image")
  id=$(basename "$image" .jpg | tr '-' '_')
  image_items="${image_items}<item id=\"${id}\" href=\"assets/art/${base}\" media-type=\"image/jpeg\"/>"
done
awk -v items="$image_items" '{ sub(/<\/manifest>/, items "</manifest>"); print }' "$stage/OEBPS/content.opf" > "$stage/OEBPS/content.opf.new"
mv -f "$stage/OEBPS/content.opf.new" "$stage/OEBPS/content.opf"
xmllint --noout "$stage/OEBPS/content.opf"

output="$stage/rebuilt.epub"
(
  cd "$stage"
  zip -q -X -0 "$output" mimetype
  zip -q -X -r "$output" META-INF OEBPS
)
mv -f "$output" "$book"
unzip -tq "$book"
