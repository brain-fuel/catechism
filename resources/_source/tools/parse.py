#!/usr/bin/env python3
"""Parse the ChatGPT catechism-reference conversation into structured JSON.

Source: the shared conversation's embedded reactRouterContext JSON (recovered
via headless browser). We walk assistant turns in order; each turn corresponds
to one page/image of grouped Bible verses. For each delineated group we capture
the topic, the raw scripture citation, a normalized reference list (canonical
book codes resolvable against ~/matt/bible), the explanation, and alt titles.
"""
import json, re, os

SC = "/tmp/claude-1000/-home-brainfuel-matt-catechism/508c015f-c287-4e7d-ada6-9a3956709daf/scratchpad"
d = json.load(open(f"{SC}/data_reactRouterContext.json", encoding="utf-8"))

# ---- locate conversation --------------------------------------------------
found = {}
def find(o):
    if isinstance(o, dict):
        if 'linear_conversation' in o:
            found['c'] = o
        for v in o.values():
            find(v)
    elif isinstance(o, list):
        for v in o:
            find(v)
find(d)
lin = found['c']['linear_conversation']

turns = []
for node in lin:
    m = node.get('message')
    if not m:
        continue
    role = m.get('author', {}).get('role')
    if role != 'assistant':
        continue
    c = m.get('content', {}) or {}
    parts = [p for p in (c.get('parts') or []) if isinstance(p, str) and p.strip()]
    txt = "\n".join(parts).strip()
    if txt:
        turns.append(txt)
print("assistant text turns:", len(turns))

# ---- book-name -> canonical code -----------------------------------------
NAMES = {
 'Genesis':'GEN','Exodus':'EXO','Leviticus':'LEV','Numbers':'NUM','Deuteronomy':'DEU',
 'Joshua':'JOS','Judges':'JDG','Ruth':'RUT','1 Samuel':'1SA','2 Samuel':'2SA',
 '1 Kings':'1KI','2 Kings':'2KI','1 Chronicles':'1CH','2 Chronicles':'2CH','Ezra':'EZR',
 'Nehemiah':'NEH','Esther':'EST','Job':'JOB','Psalms':'PSA','Psalm':'PSA','Proverbs':'PRO',
 'Ecclesiastes':'ECC','Song of Solomon':'SOS','Song of Songs':'SOS','Isaiah':'ISA',
 'Jeremiah':'JER','Lamentations':'LAM','Ezekiel':'EZE','Daniel':'DAN','Hosea':'HOS',
 'Joel':'JOE','Amos':'AMO','Obadiah':'OBA','Jonah':'JON','Micah':'MIC','Nahum':'NAH',
 'Habakkuk':'HAB','Zephaniah':'ZEP','Haggai':'HAG','Zechariah':'ZEC','Malachi':'MAL',
 'Matthew':'MAT','Mark':'MAR','Luke':'LUK','John':'JOH','Acts':'ACT','Romans':'ROM',
 '1 Corinthians':'1CO','2 Corinthians':'2CO','Galatians':'GAL','Ephesians':'EPH',
 'Philippians':'PHP','Colossians':'COL','1 Thessalonians':'1TH','2 Thessalonians':'2TH',
 '1 Timothy':'1TI','2 Timothy':'2TI','Titus':'TIT','Philemon':'PHM','Hebrews':'HEB',
 'James':'JAM','1 Peter':'1PE','2 Peter':'2PE','1 John':'1JO','2 John':'2JO','3 John':'3JO',
 'Jude':'JDE','Revelation':'REV',
}
NAMES_SORTED = sorted(NAMES, key=len, reverse=True)  # match "1 John" before "John"

def norm_dash(s):
    return s.replace('–','-').replace('—','-').replace('−','-')

unresolved = set()

def parse_refs(raw):
    """Return list of {book, book_name, citation} from a citation string."""
    raw = norm_dash(raw)
    raw = re.sub(r'\([^)]*\)', '', raw)      # drop parentheticals
    raw = raw.replace('*', '').strip().rstrip('.')
    out = []
    cur_name = cur_code = None
    for tok in raw.split(';'):
        tok = tok.strip()
        if not tok:
            continue
        # does this token start with a book name?
        m = None
        for nm in NAMES_SORTED:
            if tok == nm or tok.startswith(nm + ' ') or tok.startswith(nm + ' '):
                m = nm
                break
        if m:
            cur_name, cur_code = m, NAMES[m]
            rest = tok[len(m):].strip()
        else:
            # continuation of previous book (e.g. "; 19:4" after "Matthew ...")
            rest = tok
            # if the token itself looks like a bare book name we couldn't map
            if not re.match(r'^[0-9]', rest) and cur_code is None:
                unresolved.add(tok)
                continue
        if cur_code is None:
            unresolved.add(tok)
            continue
        cite = re.sub(r'\s+', '', rest)      # e.g. "10:9,13"
        out.append({'book': cur_code, 'book_name': cur_name, 'citation': cite})
    return out

# ---- extract groups from one assistant turn -------------------------------
ALT_HDR = re.compile(r'^(Other options|Other possibilities|Other fitting titles|'
                     r'Alternative titles|Other titles):\s*$')
TOPIC_INLINE = re.compile(r'\*\*Topic:\*\*\s*\*\*(.+?)\*\*')
TOPIC_HDR = re.compile(r'^###\s*Topic:\s*\*\*(.+?)\*\*\s*$')
NUM_HDR = re.compile(r'^###\s*\d+\.\s*(.+?)\s*$')
BOLD_ONLY = re.compile(r'^\*\*(.+?)\*\*\s*$')

def looks_like_refs(s):
    s2 = norm_dash(s)
    return bool(re.search(r'\d+:\d+', s2)) or bool(
        re.match(r'^(' + '|'.join(re.escape(n) for n in NAMES_SORTED) + r')\b', s2))

def parse_turn(txt):
    lines = txt.split('\n')
    groups = []
    last_bold_refs = None
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].rstrip()
        mnum = NUM_HDR.match(line)
        mtop = TOPIC_HDR.match(line)
        mbold = BOLD_ONLY.match(line)
        if mbold and looks_like_refs(mbold.group(1)):
            last_bold_refs = mbold.group(1)
        if mnum or mtop:
            refs_raw = None
            topic = None
            if mnum:
                refs_raw = mnum.group(1)
            else:  # "### Topic: **X**" -> refs came from preceding bold line
                topic = mtop.group(1)
                refs_raw = last_bold_refs
            # gather body until next ### header
            j = i + 1
            body = []
            while j < n and not lines[j].startswith('### '):
                body.append(lines[j])
                j += 1
            btxt = "\n".join(body)
            if topic is None:
                mt = TOPIC_INLINE.search(btxt)
                topic = mt.group(1) if mt else None
            # explanation = prose before the alt-title list / --- rule
            expl_lines, alts, in_alts = [], [], False
            for bl in body:
                s = bl.strip()
                if ALT_HDR.match(s):
                    in_alts = True
                    continue
                if in_alts:
                    mb = re.match(r'^-\s+(.+?)\s*$', s)   # dash+space, not '---'
                    if mb:
                        alts.append(mb.group(1).replace('*', '').strip())
                        continue
                    in_alts = False   # list ended
                if s.startswith('**Topic:**') or s == '---' or not s:
                    continue
                expl_lines.append(s)
            explanation = " ".join(expl_lines).strip()
            refs = parse_refs(refs_raw) if refs_raw and looks_like_refs(refs_raw) else []
            groups.append({
                'topic': (topic or '').replace('*', '').strip() or None,
                'references_raw': (refs_raw or '').replace('*', '').strip() or None,
                'references': refs,
                'explanation': explanation or None,
                'alt_titles': alts,
            })
            i = j
            continue
        i += 1
    return groups

# ---- section hints --------------------------------------------------------
def section_hint(txt):
    for pat, lab in [
        (r'First Commandment','1st Commandment'),(r'Second Commandment','2nd Commandment'),
        (r'Third Commandment','3rd Commandment'),(r'Fourth Commandment','4th Commandment'),
        (r'Fifth Commandment','5th Commandment'),(r'Sixth Commandment','6th Commandment'),
        (r'Seventh Commandment','7th Commandment'),(r'Eighth Commandment','8th Commandment'),
        (r'Ninth and Tenth Commandments|Tenth Commandment','9th & 10th Commandments'),
        (r'First Article','Creed: First Article'),
        (r'Second Article','Creed: Second Article'),
        (r'Ten Commandments','Ten Commandments'),
        (r'\bCreed\b','Creed'),
    ]:
        if re.search(pat, txt):
            return lab
    return None

def fallback_turn(txt):
    """Turns that don't use '### N.' headers: 'The Way' (bullet refs) and the
    'For **1 Corinthians 11:28**:' single-verse turn."""
    lines = txt.split('\n')
    refs_raw_parts, topic = [], None
    for ln in lines:
        s = ln.strip()
        mb = BOLD_ONLY.match(s)
        # bold-only title that is NOT a citation -> topic
        if mb and not looks_like_refs(mb.group(1)) and topic is None and mb.group(1) != 'Topic:':
            topic = mb.group(1)
        # collect bold citations from bullets or inline
        for bold in re.findall(r'\*\*([^*]+?)\*\*', s):
            if looks_like_refs(bold):
                refs_raw_parts.append(bold.strip())
    if not refs_raw_parts:
        return []
    # topic fallback: first bulleted bold phrase
    if topic is None:
        for ln in lines:
            mbl = re.match(r'^-\s*\*\*(.+?)\*\*', ln.strip())
            if mbl:
                topic = mbl.group(1)
                break
    refs_raw = "; ".join(refs_raw_parts)
    refs = parse_refs(refs_raw)
    return [{
        'topic': (topic or '').replace('*', '').strip() or None,
        'references_raw': refs_raw,
        'references': refs,
        'explanation': txt.split('\n', 1)[0].strip() or None,
        'alt_titles': [],
    }]

pages = []
for idx, txt in enumerate(turns):
    g = parse_turn(txt)
    if not g:
        g = fallback_turn(txt)
    if not g:
        continue
    pages.append({'page': len(pages) + 1, 'section_hint': section_hint(txt),
                  'intro': txt.split('\n', 1)[0].strip(), 'groups': g})

ngroups = sum(len(p['groups']) for p in pages)
nrefs = sum(len(g['references']) for p in pages for g in p['groups'])
print("pages:", len(pages), "groups:", ngroups, "parsed refs:", nrefs)
print("groups w/o refs:", sum(1 for p in pages for g in p['groups'] if not g['references']))
print("unresolved tokens:", sorted(unresolved))

json.dump({'source': 'ChatGPT shared conversation 6a518709 — Bible-verse groupings '
           'for a Lutheran catechism (Svebilius), through the Creed\'s First Article',
           'note': 'Each page = one image the user submitted; each group = one '
                   'verse-cluster the assistant titled. references[] carry canonical '
                   'book codes resolvable against ~/matt/bible.',
           'pages': pages},
          open(f"{SC}/references.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("wrote references.json")
