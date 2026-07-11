# resources

Supplementary Bible-reference material for the **Open Catechism** project. The
goal (future) is to combine these curated scripture references — plus the
references embedded in the Svebilius catechism itself — into a multilingual
catechism whose texts are parsed in the same vein as `~/matt/bible` (canonical
book codes, verse-addressable, parallel languages).

## Layout

    resources/
      en/
        references.json   structured data (machine-readable)
        references.md      human-readable index
      _source/
        chatgpt-transcript.md   full recovered source conversation (provenance)
        tools/                  the pipeline that produced en/ (reproducible)

Language dirs (`en/`, later `fi/`, `la/`, …) mirror the `~/matt/bible` edition
pattern: same reference IDs, parallel per language.

## What `en/` covers

Bible-verse groupings for a Lutheran catechism (Svebilius), curated in a ChatGPT
conversation and titled by topic. Coverage runs the arc **What is Christianity →
the Ten Commandments → the Creed's First Article** (complete through the First
Article's stewardship/thanksgiving conclusion).

- **61** source pages (one per image submitted)
- **254** topical verse-groups
- **816** scripture references

## `references.json` schema

```jsonc
{
  "source": "...", "note": "...",
  "pages": [
    {
      "page": 2,
      "section_hint": "Ten Commandments",   // best-effort label, may be null
      "intro": "…assistant's first line…",
      "groups": [
        {
          "topic": "The Holy Trinity",
          "references_raw": "John 17:3; Matthew 28:19; Matthew 3:13–17",
          "references": [
            { "book": "JOH", "book_name": "John", "citation": "17:3" },
            { "book": "MAT", "book_name": "Matthew", "citation": "3:13-17" }
          ],
          "explanation": "…",
          "alt_titles": ["The Triune God", "…"]
        }
      ]
    }
  ]
}
```

- `book` — canonical uppercase code from `~/matt/bible/data/books.json`; resolves
  to `bible/<testament>/<CODE>/<NNN>.json`.
- `citation` — normalized `chapter:verse` (ranges `-`, verse lists `,`,
  chapter-only where the source gave no verse). All 53 book codes used are
  present in the bible repo.

## Provenance

The source is a shared ChatGPT conversation (`chatgpt.com/share/6a518709-…`).
Share pages are a JS SPA behind Cloudflare, so the text was recovered by loading
the page in a headless browser and extracting the embedded conversation JSON
(`_source/tools/fetch_html.py`), then parsed (`parse.py`) and rendered
(`gen_md.py`). The full transcript is preserved in `_source/`.

## Known caveats

- Topic titles are the assistant's suggestions (a preferred title plus
  `alt_titles`); they are editorial, not from Svebilius.
- One source oddity: `Jude 2:11–12` (Jude is a single-chapter book — likely a
  slip for `Jude 11–12`). Left faithful to source. Single-chapter books (Jude,
  Obadiah, Philemon, 2–3 John) cite by verse only, e.g. `Jude 6` = verse 6.
- 5 groups carry no scripture (a liturgical outline, an "Atheism · Agnosticism ·
  Deism · Pantheism" apologetics note, and two "implied conclusion" markers);
  they are kept with `references: []`.
