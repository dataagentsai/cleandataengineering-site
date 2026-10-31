# Writer brief: posts for cleandataengineering.ai/writing/

You are writing ONE blog post for cleandataengineering.ai, a free community learning site for data and AI engineers.
Three posts are already published; read them first to copy the voice, length and drawing style exactly:

- `_writing/posts/model-is-ten-percent.md` (AI, explainer)
- `_writing/posts/medallion-done-right.md` (data, explainer)
- `_writing/posts/guardrails-sorted.md` (AI, explainer with a table)

Their drawings are in `_writing/build.py` (search `def drawing_`). Study `drawing_agent_loop`, `drawing_kitchen` and `drawing_build_order`.

## Hard rules

1. **Simple, pictorial, hand-drawn.** 3 to 5 drawings per post. Each drawing has few boxes (usually 3 to 8), short plain labels, and one idea. Cartoon touches are welcome, for example small objects drawn with `hz` shapes as in `drawing_kitchen`, or a stick person as in `drawing_build_order`. No dense diagrams.
2. **10-minute read at most.** Aim for 900 to 1,500 words. The build prints a warning if a post runs over 10 minutes.
3. **Plain language.** Use full sentences. No arrow chains like "A → B → C" in text. Define any jargon the first time it appears. No unexplained abbreviations. Prefer short paragraphs, numbered steps, and one small table at most.
4. **Shape:**
   - a hook of 2 or 3 short paragraphs
   - sections with `##` headings, each built around a picture
   - a "mistakes" or "what goes wrong" section where it fits
   - "N questions to check your own X" near the end
   - one closing line
5. **Honesty.** Don't invent statistics, customers or benchmarks. Numbers must come from the source material named in your task, or be clearly framed as an example ("say, a refund of ₹40,000"). Prefer Indian examples (₹, Indian names) as the existing posts do. Product names are fine; never claim a product feature you are not sure of. When unsure, describe the job instead of the product.
6. **Never mention** Octave, JKH, any client name, or DataAgents. Links to github.com/dataagentsai are fine.
7. **Light pages only.** No colours outside the kit classes.

## Files you create (and only these)

1. `_writing/posts/<slug>.md`. The front matter must have these fields:

```
---
title: <EXACTLY the title given in your task — it must match _writing/planned.py character for character>
date: 2026-10-31
subject: <ai | data | analytics | llm | cost | career>
audience: builders
kind: <explainer | decision | field-note>
draft: true
summary: <2–3 sentences, plain, the whole point of the post>
linkedin: <2–3 sentence hook for LinkedIn>
deeper: <a site path that goes deeper, if one exists, else omit the field>
deeper_label: <link text>
---
```

   Insert each drawing on its own line as `{{drawing: <name>}}`. Body markdown supports:
   - `##` and `###` headings
   - paragraphs
   - `-` lists and `1.` lists
   - `|` tables
   - `>` quotes
   - fenced code
   - `**bold**`, `*italic*`, `` `code` `` and `[links](url)`

   Nothing else is supported. A list item can't span lines unless the continuation is indented by 3 spaces.

2. `_writing/drawings/<slug>.py`. It defines drawing functions and a `DRAWINGS = {"name": func}` dict. Drawing names must be unique across the site, so prefix them with a short tag for your post, such as `genie-...`. The module receives `kit`, `figure`, `E` and `ROOT` as globals; do NOT import them. Each function returns `figure(width, height, svg_body, aria_label, caption)`. Width is normally 1000.

   Kit API (from ~/agent-harness-tutorial/kit.py):
   - `kit.box(x, y, w, h, title, sub, kind)` draws a wobbly box. `title` and `sub` are a str or a list of lines. `kind` is one of:
     - `bx`: blue
     - `bxs`: butter yellow, for checks and highlights
     - `solid`: lavender, the star of the picture
     - `bxm`: dashed white, for outside or optional things
   - `kit.arrow(x1, y1, x2, y2, label=None, lx=None, ly=None, anchor="middle")`
   - `kit.path("M.. Q..", kind="ln"|"lnd"|"lnc")` draws a curve with an arrowhead.
   - `kit.text(x, y, str_or_lines, cls, anchor)`. `cls` is one of:
     - `tx`: normal
     - `sm`: small grey
     - `bd`: bold-ish
     - `lbl`: caps label
   - `kit.num(x, y, n)` draws a numbered circle.
   - Raw SVG is fine too, using these classes:
     - `hz`: white shape with an ink outline, for cartoon objects
     - `hk`: ink fill
     - `ln`, `lnd` (dashed) and `lnc` (thick): lines
     - `zg`, `zy`, `zr`: green, yellow and red zones
     - `pf pf-bx`, `pf pf-bxs`, `pf pf-solid`: pastel fills

   Box text at title size fits about 9 px per character and sub text about 7 px per character, so size boxes accordingly. Keep at least 15 px between boxes.

## Linking

Link to other posts only if they are **published**, which means a folder exists at `~/cleandataengineering-site/writing/<slug>/`. Never link to a draft. Do link related published posts where they help: one or two links, not a list. Site guide pages under `learn/`, `concepts/` and `paths/` are fine to link if the file exists.

## Check your work (required)

```
cd ~/cleandataengineering-site
python3 _writing/build.py --drafts
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1100,<tall enough> --virtual-time-budget=4000 --screenshot=<your scratch png> \
  "file://$HOME/cleandataengineering-site/_writing/preview/<slug>/index.html"
```

Then Read the PNG and look at every drawing. Fix any of these and screenshot again until it is clean:
- overlapping text
- text spilling out of a box
- lines crossing boxes
- unreadable labels

Also confirm that the read time in the page header is 10 minutes or less.

Do NOT edit build.py, planned.py, other posts or other drawing files. Do NOT commit, push or publish. When done, reply with:
- the slug
- the word count
- the drawing names
- one line per drawing saying what it shows
- anything you were unsure about
