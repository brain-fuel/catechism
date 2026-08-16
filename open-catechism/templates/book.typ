#import "../vendor/typst/cmarker/lib.typ" as cmarker

#let catechism-template = (xs, edition: "Svebilius/Laine Edition") => {
  let title = "Open Catechism"
  set document(title: title, author: "Open Catechism")
  set page(
    paper: "us-letter",
    margin: (inside: 0.82in, outside: 0.7in, top: 0.72in, bottom: 0.76in),
    numbering: "1",
    number-align: bottom + right,
  )
  set text(font: "Atkinson Hyperlegible", size: 10pt, lang: "en")
  set par(justify: true, leading: 0.68em)
  set heading(numbering: none)
  show heading: it => {
    set text(font: "Overpass", weight: "bold")
    if it.level == 1 { set text(size: 23pt) }
    if it.level == 2 { set text(size: 16pt) }
    if it.level >= 3 { set text(size: 12pt) }
    block(above: if it.level == 1 { 0pt } else { 1.2em }, below: 0.55em, it)
  }
  show strong: set text(weight: "bold")
  show emph: set text(style: "italic")
  show raw: set text(font: "Atkinson Hyperlegible")
  show quote.where(block: true): it => block(
    width: 100%,
    inset: (left: 0.9em, right: 0.35em, y: 0.5em),
    stroke: (left: 1.5pt + rgb("72551b")),
    fill: rgb("f7f1e5"),
    radius: (right: 3pt),
    above: 0.7em,
    below: 0.7em,
    it.body,
  )

  align(center + horizon)[
    #text(font: "Overpass", size: 28pt, weight: "bold")[#title]
    #v(0.45in)
    #text(size: 13pt)[#edition]
    #v(0.3in)
    #text(size: 10pt)[Open Catechism]
  ]
  pagebreak()

  for (index, path) in xs.enumerate() {
    columns(2, gutter: 0.28in)[
      #cmarker.render(
        read(path),
        smart-punctuation: false,
        raw-typst: false,
        scope: (image: (source, ..args) => image(source, ..args)),
      )
    ]
    if index < xs.len() - 1 { pagebreak() }
  }
}
