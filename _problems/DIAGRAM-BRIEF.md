# Diagram brief: one picture per hard problem

The site cleandataengineering.ai has a section /problems/ with 79 hard unsolved problems, one page each.
Each page opens with a hand-drawn diagram **about the problem itself**: what goes wrong, and why it is hard.
You are drawing the diagrams for a set of problems (your task names them).

## What to read first

1. `_problems/data.json`: each problem's title, why it is still open, the 8-week experiment and the verdict. Your picture must match this text.
2. `_problems/build.py`: how pages are built and how diagrams are loaded.
3. Look at two existing drawing files for the style: `_writing/drawings/context-engineering.py` and `_writing/drawings/human-in-the-loop.py`. Also see `drawing_kitchen` in `_writing/build.py`.

## What each diagram must do

- **Show the problem, not the experiment.** Show the mechanism of what goes wrong, so a reader gets it in 5 seconds. Examples:
  - Hallucination: a question goes in, the model answers confidently and wrongly, and there is no "I'm guessing" light.
  - The memory wall: a fast chip waits at an empty plate while a slow memory conveyor brings data.
- **Simple, cartoon, hand-drawn.**
  - Use 3 to 7 boxes or objects, with short plain labels.
  - Draw one small cartoon object or stick person where it helps. Use `hz` shapes for objects, as `drawing_kitchen` does.
  - Avoid dense charts and paragraphs inside the picture.
- **Honest numbers only.** If you put a number in, it must come from the problem's text in data.json (for example "95% right per step is about 60% over 10 steps"), or be labelled "say," as an example.
- **A one-sentence caption** in plain words that states the problem's core.
- **No mention** of DataAgents, Octave, clients, or anyone's private plans.

## File format

Create exactly one file, `_problems/diagrams/<your-file>.py`, as named in your task. Do not import kit, figure, E or ROOT; they are injected as globals.

```python
def d_hallucination():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(...)  # build svg body
    return figure(1000, 260, d, "aria label describing the picture", "One-sentence caption.")

DRAWINGS = {"hallucination-the-model-doesn-t-know-what": d_hallucination, ...}
```

The keys must be the exact slugs from `_problems/SLUGS.txt`, and you must cover every slug in your task.

Kit API (from ~/agent-harness-tutorial/kit.py):
- `kit.box(x, y, w, h, title, sub, kind)` draws a wobbly box. `title` and `sub` are a str or a list of lines. `kind` is one of:
  - `bx`: blue
  - `bxs`: butter yellow, for warnings and highlights
  - `solid`: lavender, the star of the picture
  - `bxm`: dashed, for outside or missing things
- `kit.arrow(x1, y1, x2, y2, label=None, lx=None, ly=None, anchor="middle")`
- `kit.path("M.. Q..", "ln"|"lnd"|"lnc")` draws a curve with an arrowhead.
- `kit.text(x, y, str_or_lines, cls, anchor)`. `cls` is one of `tx`, `sm`, `bd` or `lbl`.
- `kit.num(x, y, n)` draws a numbered circle.
- Raw SVG is fine, using these classes:
  - `hz`: white shape with an ink outline, for objects
  - `hk`: ink fill
  - `ln`, `lnd` (dashed) and `lnc` (thick): lines
  - `zg`, `zy`, `zr`: green, yellow and red zones
  - `pf pf-bx`, `pf pf-bxs`, `pf pf-solid`: pastel fills

Box text at title size needs about 9 px per character, and sub text about 7 px per character. Keep at least 15 px between boxes. Width is 1000; height is usually 220 to 340.

## Check your work (required)

```
cd ~/cleandataengineering-site
python3 _problems/build.py          # preview into _writing/preview/problems/
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1100,900 --virtual-time-budget=4000 --screenshot=<your scratch png> \
  "file://$HOME/cleandataengineering-site/_writing/preview/problems/<slug>/index.html"
```

Screenshot EVERY page you drew and Read the PNG. Fix any of these, then screenshot again:
- overlapping text
- text outside boxes
- lines crossing boxes or labels
- unreadable labels

Other writers work at the same time. If a build fails on someone else's file, wait and retry. Keep your screenshots in your own scratchpad subfolder.

Do NOT edit build.py, data.json, other diagram files, or anything else. Do NOT commit.

When done, reply with:
- the slugs covered
- one line per diagram saying what it shows
- anything you were unsure about
