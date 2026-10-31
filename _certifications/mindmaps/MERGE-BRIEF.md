# Merging the CCA-F mind maps (brief for writer agents)

## Why this exists
Every question in CCA-F Mocks 4 to 7 (240 questions) has a "mind map": a three-column decision table
for the concept family the question belongs to (for example "What you observe / Where the fault is /
Fix"). The site owner wants ONE page on cleandataengineering.ai that lists all of them, organised by
**what each mind map is for**, with similar maps merged so they don't read the same table four times.
A reader must be able to scan the page and instantly see "this is the mind map for X".

The owner prefers plain, simple English: full sentences, no cryptic shorthand, no arrow chains,
jargon defined on first use.

## Input
`_certifications/mindmaps/raw/<objective>.json`, one file per exam objective (1.1 to 5.6). Each is a
list of maps: `ref` (like `m7:s1-01`, meaning Mock 7, scenario 1, question 1), `mock`, `title` (the
question-to-ask-yourself line), `head` (three column names), `rows` (lists of three cells; cells may
contain `<b>`, `<i>`, `<code>`), `rule` (the one-line rule from that question).

## Output
Write `_certifications/mindmaps/merged/d<N>.json` for your domain N (objectives N.1 to N.x), in this shape:

```json
{"domain": 1,
 "objectives": [
  {"obj": "1.1",
   "maps": [
    {"for": "Why an agent loop stops at the wrong time",
     "ask": "Which signal is the loop reading to decide it is done?",
     "when": "The agent stops early, never stops, or drops a tool request.",
     "head": ["What you observe", "Where the fault is", "Fix"],
     "rows": [["…", "…", "…"]],
     "rule": "One or two sentences to remember.",
     "from": ["m7:s1-01", "m5:s1-01"]}
   ]}
 ]}
```

- `for`: a short noun phrase naming what this map decides. This is the heading the reader scans,
  so make it specific and distinct from the other maps (good: "Resume, fork or start fresh for old
  work"; bad: "Sessions").
- `ask`: the question you ask yourself, in plain words (adapt the best source `title`).
- `when`: one plain sentence naming the symptom or situation that tells you to reach for this map.
- `head`: one set of three column names for the merged map.
- `rows`: the merged rows.
- `rule`: one memorable rule for the merged map (adapt from the sources' `rule`, don't invent new claims).
- `from`: every source `ref` merged into this map.

## How to merge
1. Within an objective, merge maps that answer **the same decision** (for example four maps all
   titled "resume, fork, or start fresh"). Don't merge maps that only share a topic but decide
   different things; keep them as separate maps. Expect roughly 1 to 4 maps per objective, often 2 or 3.
2. Rows: take the union, drop duplicates and near-duplicates (keep the clearest wording), aim for
   5 to 10 rows. When source maps used different headers, pick one set and adjust cell wording
   minimally so each row fits the columns. Keep the facts from the sources; don't add facts that no
   source states. Keep the `<b>`/`<code>` markup where it helps, nothing else.
3. Every `ref` in your raw files must appear in exactly one map's `from`. No ref dropped, none twice.
   Stay inside your own objectives.
4. Order maps within an objective from most basic to most specialised.

## Check before you finish
Run this from the site repo root and fix anything it reports:

```
python3 -c "import json,glob;r={m['ref'] for f in glob.glob('_certifications/mindmaps/raw/N.*.json') for m in json.load(open(f))};d=json.load(open('_certifications/mindmaps/merged/dN.json'));s=[x for o in d['objectives'] for m in o['maps'] for x in m['from']];print('missing',r-set(s),'dupes',len(s)-len(set(s)),'extra',set(s)-r);print([len(r2) for o in d['objectives'] for m in o['maps'] for r2 in m['rows'] if len(r2)!=3])"
```
(replace N with your domain number). Expected output: `missing set() dupes 0 extra set()` and `[]`.

Only write your own `merged/d<N>.json`. Don't touch any other file, and don't commit.
Report back: per objective, the map `for` headings and how many sources each merged.
