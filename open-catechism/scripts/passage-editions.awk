function emit(block,   clean,n,parts,words,lines,first,cite,i) {
  if (block == "") return
  clean = block
  gsub(/<[^>]*>/, " ", clean)
  gsub(/\*\*[^*]+\*\*/, " ", clean)
  gsub(/[^[:alnum:]'-]+/, " ", clean)
  n = split(clean, parts, /[[:space:]]+/)
  words = 0
  for (i = 1; i <= n; i++) if (parts[i] != "") words++
  split(block, lines, /\n/)
  first = lines[1]
  if (words > 50 && first ~ /^> \*\*[^*]+\*\*$/) {
    cite = first
    sub(/^> \*\*/, "", cite)
    sub(/\*\*$/, "", cite)
    printf "> **%s**\n>\n> Read this passage in the accompanying *Scripture Passages* volume.\n", cite >> short
    if (omitted == 0) printf "# %s: Longer Scripture Passages\n\n", title >> companion
    printf "## %s\n\n%s\n\n", cite, block >> companion
    omitted++
  } else {
    printf "%s\n", block >> short
  }
}

BEGIN {
  short = ENVIRON["PASSAGE_SHORT"]
  companion = ENVIRON["PASSAGE_COMPANION"]
  printf "" > short
  printf "" > companion
  block = ""
  title = "Open Catechism"
  omitted = 0
}

/^# / && title == "Open Catechism" {
  title = $0
  sub(/^# /, "", title)
}

/^>/ {
  if (block == "") block = $0
  else block = block "\n" $0
  next
}

{
  emit(block)
  block = ""
  print $0 >> short
}

END {
  emit(block)
  printf "%s: %d passages moved\n", title, omitted
}
