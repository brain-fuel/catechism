#!/usr/bin/env python3
import json, os
SC = "/tmp/claude-1000/-home-brainfuel-matt-catechism/508c015f-c287-4e7d-ada6-9a3956709daf/scratchpad"
d = json.load(open(f"{SC}/references.json", encoding="utf-8"))

BOOK_EN = {  # code -> readable label for citations
 'GEN':'Genesis','EXO':'Exodus','LEV':'Leviticus','NUM':'Numbers','DEU':'Deuteronomy',
 'JOS':'Joshua','JDG':'Judges','RUT':'Ruth','1SA':'1 Samuel','2SA':'2 Samuel','1KI':'1 Kings',
 '2KI':'2 Kings','1CH':'1 Chronicles','2CH':'2 Chronicles','EZR':'Ezra','NEH':'Nehemiah',
 'EST':'Esther','JOB':'Job','PSA':'Psalm','PRO':'Proverbs','ECC':'Ecclesiastes','SOS':'Song of Solomon',
 'ISA':'Isaiah','JER':'Jeremiah','LAM':'Lamentations','EZE':'Ezekiel','DAN':'Daniel','HOS':'Hosea',
 'JOE':'Joel','AMO':'Amos','OBA':'Obadiah','JON':'Jonah','MIC':'Micah','NAH':'Nahum','HAB':'Habakkuk',
 'ZEP':'Zephaniah','HAG':'Haggai','ZEC':'Zechariah','MAL':'Malachi','MAT':'Matthew','MAR':'Mark',
 'LUK':'Luke','JOH':'John','ACT':'Acts','ROM':'Romans','1CO':'1 Corinthians','2CO':'2 Corinthians',
 'GAL':'Galatians','EPH':'Ephesians','PHP':'Philippians','COL':'Colossians','1TH':'1 Thessalonians',
 '2TH':'2 Thessalonians','1TI':'1 Timothy','2TI':'2 Timothy','TIT':'Titus','PHM':'Philemon','HEB':'Hebrews',
 'JAM':'James','1PE':'1 Peter','2PE':'2 Peter','1JO':'1 John','2JO':'2 John','3JO':'3 John','JDE':'Jude','REV':'Revelation',
}

def cite(r):
    return f"{BOOK_EN.get(r['book'], r['book'])} {r['citation']}"

out = []
out.append("# Catechism Bible-Reference Index (English)\n")
out.append(d['note'] + "\n")
out.append(f"**Source:** {d['source']}\n")
out.append(f"**Coverage:** {len(d['pages'])} source pages, "
           f"{sum(len(p['groups']) for p in d['pages'])} topical verse-groups, "
           f"{sum(len(g['references']) for p in d['pages'] for g in p['groups'])} scripture references. "
           "Runs from *What is Christianity* → the Ten Commandments → the Creed's First Article.\n")
out.append("Book codes in `references.json` are canonical and resolve against `~/matt/bible/"
           "bible/<testament>/<CODE>/<NNN>.json`.\n")
out.append("\n---\n")

last_hint = object()
for p in d['pages']:
    if p['section_hint'] != last_hint:
        out.append(f"\n## {p['section_hint'] or 'Introduction / Scripture'}\n")
        last_hint = p['section_hint']
    out.append(f"\n### Page {p['page']}\n")
    for g in p['groups']:
        topic = g['topic'] or '(untitled)'
        refs = "; ".join(cite(r) for r in g['references']) or (g['references_raw'] or '—')
        out.append(f"- **{topic}** — {refs}")
        if g['explanation']:
            expl = g['explanation']
            if len(expl) > 300:
                expl = expl[:297].rstrip() + "…"
            out.append(f"  <br>*{expl}*")
open(f"{SC}/references.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote references.md", len(out), "lines")
