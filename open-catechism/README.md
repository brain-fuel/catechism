# Open Catechism: Svebilius/Laine Edition

A canonical, offline-buildable English edition in 35 units. The historic
Svebilius/Luther substrate is preserved; clearly labelled Laine additions map
every inherited reference group and supply teaching, narratives, illustrations,
memory work, prayer, discussion, and provenance.

From this directory, run:

```sh
make generate
make serve
go run ./cmd/open-catechism sources sync
go run ./cmd/open-catechism validate
go run ./cmd/open-catechism coverage
go run ./cmd/open-catechism build --format web
go run ./cmd/open-catechism build --format epub
go run ./cmd/open-catechism build --format pdf
go run ./cmd/open-catechism build --format all
```

The ready-to-serve site is committed in `public/`. Publication binaries are
built into ignored `dist/`. EPUB output is semantic EPUB 3 XHTML with embedded
Overpass and Atkinson Hyperlegible fonts. PDF output renders CommonMark through
the vendored cmarker Typst package and uses the same font families. The build
source is GoML and lowers through `brain-fuel/goplus` v0.145.1 to ordinary Go;
Typst is needed for PDF output. All textual datasets are local after
synchronization.

Each printable is built as a three-file family:

- the standard PDF contains every Scripture passage in place;
- the `-short.pdf` edition keeps passages of 50 words or fewer, or passages
  of no more than two verses, in place; only passages exceeding both limits
  are replaced with their citations;
- the matching `-passages.pdf` companion contains those longer passages in full,
  grouped by unit and citation.

This applies to the complete book and all five split printables, producing six
standard PDFs, six shortened PDFs, and six Scripture-passages companions.

The website is rendered from the canonical Markdown by Hugo v0.164.0 using the
project-local `open-catechism` theme. Unit numbers indicate sequence; doctrinal
titles—not generic unit labels—name links, pages, and browser titles.
Scripture cited by a teaching section is printed there as an inline blockquote,
not deferred to a reference section.

Use `make serve` for local preview. It runs the pinned Hugo v0.164.0 with full
rebuilds and one render worker, avoiding the v0.165.0 live-render buffer crash
affecting long Markdown pages.

## Editorial policy

Scripture is labelled “KJV-based reading text with Divine Name and terminology
concordance.” Untouched KJV records remain in `vendor/datasets`. Old Testament
small-cap Divine Name forms are rendered Yahweh, with JAH rendered Yah. New
Testament restorations require and appear in the approved registry. “Holy Ghost”
is used for the Third Person; distinct titles and other senses of spirit remain.

The principal credit is “Open Catechism.” Contributors are credited by role in
the generated provenance. New content is CC BY-SA 4.0; independent build code is
MIT; third-party licenses are preserved under `vendor/`.
