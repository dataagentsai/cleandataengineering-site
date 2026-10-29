"""Mindset: train the dragon. For people who are scared or confused in the era of AI.

    python3 _mindset/build.py     # writes mindset/ (4 pages)
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)

CSS = """<style>
  .panel { display:grid; grid-template-columns:1fr 1fr; gap:30px; align-items:center; margin:30px 0; }
  .panel.flip > img { order:2; } .panel img { width:100%; height:auto; }
  .panel h3 { font-size:28px; margin:0 0 8px; } .panel p { font-size:17.5px; }
  .moral { background:var(--butter-wash); border:1.5px solid var(--ink); border-radius:var(--wob); padding:18px 24px; font-size:18px; margin:26px 0; }
  .cards4 { display:grid; grid-template-columns:repeat(auto-fit,minmax(185px,1fr)); gap:12px; margin:18px 0; }
  .cards4 > div, .cards4 > a { border:1.5px solid var(--ink); border-radius:var(--wob); padding:14px 18px; text-decoration:none; color:inherit; }
  .cards4 b { display:block; font-family:var(--hand); font-weight:400; font-size:24px; margin-bottom:4px; }
  .cards4 span { display:block; font-size:15px; color:var(--ink-soft); }
  .cards4 .wk { font-size:13px; color:var(--faint); margin-top:8px; }
  .c1 { background:var(--peri-wash); } .c2 { background:var(--mint-wash); } .c3 { background:var(--butter-wash); } .c4 { background:var(--rose-wash); }
  .tw { overflow-x:auto; } table.vs { border-collapse:collapse; width:100%; font-size:15.5px; margin:10px 0 20px; }
  table.vs th, table.vs td { text-align:left; padding:9px 12px; border-bottom:1.5px dashed var(--rule-firm); vertical-align:top; }
  table.vs th { font-family:var(--hand); font-weight:400; font-size:22px; } table.vs td:first-child { color:var(--faint); font-size:14px; width:22%; }
  .crumbs { font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  .next { display:flex; justify-content:space-between; gap:12px; margin-top:36px; border-top:1.5px dashed var(--rule-firm); padding-top:16px; font-size:16px; }
  @media (max-width:760px) { .panel { grid-template-columns:1fr; } .panel.flip > img { order:0; } }
</style>"""

IMG = lambda n: f'<img src="/assets/illustrations/{n}.svg" alt="" width="520" height="320">'  # noqa: E731
PAGES = [("", "Train the dragon"), ("builder", "From surviving to building"), ("first-30-days", "Your first 30 days"), ("start-something", "Start something")]


def nav(i):
    prev = f'<a href="/mindset/{PAGES[i - 1][0]}">← {PAGES[i - 1][1]}</a>'.replace("/mindset//", "/mindset/") if i > 0 else "<span></span>"
    nxt = f'<a href="/mindset/{PAGES[i + 1][0]}/">{PAGES[i + 1][1]} →</a>' if i < len(PAGES) - 1 else '<a href="/learn/ai-universe/">Draw the map: the AI Universe →</a>'
    return f'<div class="next">{prev}{nxt}</div>'


def crumbs(title):
    return f'<p class="crumbs"><a href="/mindset/">Mindset</a> · {title}</p>'


def story():
    return f"""<div class="hero hub-hero"><div><p class="eyebrow">Mindset · for anyone scared or confused about AI</p><h1>Train the dragon</h1>
<p class="thesis">If you are in college, just graduated, have lost your job, or lie awake worried you might: this is for you. It starts with a story.</p></div>
{IMG('dragon-ride')}</div>

<div class="panel">{IMG('dragon-attack')}<div><h3>The dragon</h3>
<p>News spread through the valley. A dragon had come, huge, with fire pouring from its mouth. Wherever it flew, villages burned. Fields, houses, everything in front of it.</p>
<p>Village after village heard the news and was afraid. Some hid. Some built higher walls. Some packed up and waited for the worst.</p></div></div>

<div class="panel flip">{IMG('village-decides')}<div><h3>The village that decided</h3>
<p>But one village made a different decision. They didn't ask, "how do we hide from it?" They asked, "what if we learned how this creature works?"</p>
<p>They watched it. They studied what it ate, where it rested, what made it angry and what made it calm. They practised, failed, and practised again.</p></div></div>

<div class="panel">{IMG('dragon-ride')}<div><h3>And then they flew</h3>
<p>One day the dragon came again, and this time it didn't burn the village. The villagers had learned to ride it.</p>
<p>The same fire that destroyed the other villages now cleared their land, carried their goods over mountains, and let them see further than anyone in the valley had ever seen. The dragon didn't change. <strong>They did.</strong></p></div></div>

<div class="moral"><strong>AI is the dragon.</strong> It is real, and it is powerful. It will change many jobs, and some people will be hurt; pretending otherwise would be dishonest. But all around you, people are learning it in a particular way: building things, creating things, solving problems, and letting AI help them fly. The difference between the villages was never the dragon. It was the decision.</div>

<div class="panel flip">{IMG('lion')}<div><h3 id="the-lion">The lion mindset</h3>
<p>The dragon, the surfer and the lion all teach the same thing. <strong>The best way to survive is not to try to survive.</strong> A lion doesn't spend the day hiding from the jungle; it moves first.</p>
<p>Be the driver, the builder, the innovator. Use AI to fly, and to build something that didn't exist before.</p></div></div>
<div class="cards4">
<div class="c1"><b>Front foot, not back foot</b><span>Don't defend the old work. Go after new problems, and let AI do what used to need a team.</span></div>
<div class="c2"><b>Be a giver</b><span>Teach, help and mentor. Reach out to graduates who can't find a first job and to people losing theirs. Lift them with you.</span></div>
<div class="c3"><b>Choose who you build for</b><span>Say no to organisations that want AI only to cut jobs. Say yes to the ones using it to build something new.</span></div>
<div class="c4"><b>Ride, don't hide</b><span>Learn how the dragon works, paddle towards the wave, and fly.</span></div>
</div>

<h2>Four pages, in order</h2>
<div class="cards4">
<a class="c1" href="/mindset/"><b>1 · Train the dragon</b><span>The story, and the decision it asks of you.</span></a>
<a class="c2" href="/mindset/builder/"><b>2 · From surviving to building</b><span>The four mindsets that change how you learn: builder, innovator, problem solver, entrepreneur.</span></a>
<a class="c3" href="/mindset/first-30-days/"><b>3 · Your first 30 days</b><span>Concrete steps for students, graduates, people who lost a job, and people who fear losing one.</span></a>
<a class="c4" href="/mindset/start-something/"><b>4 · Start something</b><span>Solve a customer's problem, or a problem many people share, with AI as your wings.</span></a>
</div>
{nav(0)}"""


def builder():
    return f"""{crumbs('From surviving to building')}
<div class="hero hub-hero"><div><h1>From surviving to building</h1>
<p class="thesis">When you are scared, the natural goal is to survive: keep my job, get any job. That is a fine first step. But it is a small goal, and small goals make you learn in a small way.</p></div>{IMG('projects')}</div>

<p>Bigger goals change how you learn and how you prepare. Someone trying to keep their job learns the one tool their manager mentioned. Someone trying to build something learns how the whole thing works, because they have to make it work.</p>

<div class="tw"><table class="vs">
<tr><th></th><th>Surviving</th><th>Building</th></tr>
<tr><td>The question you ask</td><td>"Will AI take my job?"</td><td>"What can I now build that I couldn't before?"</td></tr>
<tr><td>How you learn</td><td>a course, a certificate, a tool name for the CV</td><td>the concepts first, then by making something real</td></tr>
<tr><td>How you use AI</td><td>to do my old work a bit faster</td><td>to do work that was impossible for one person last year</td></tr>
<tr><td>What you show people</td><td>a list of skills</td><td>things you built, problems you solved, people you helped</td></tr>
<tr><td>What success looks like</td><td>still employed next year</td><td>more options every year: a better job, clients, or your own company</td></tr>
</table></div>

<h2>Four mindsets that change everything</h2>
<div class="cards4">
<div class="c1"><b>The builder</b><span>You learn by making. Every concept ends in something that runs: a small agent, a script, a page.</span><span class="wk">This week: build one tiny thing with AI and show it to someone.</span></div>
<div class="c2"><b>The innovator</b><span>You ask "what if?" You combine two ideas nobody combined, or bring AI to a place that hasn't seen it.</span><span class="wk">This week: list five tasks in your field that repeat every day.</span></div>
<div class="c3"><b>The problem solver</b><span>You start from the problem, not the tool. AI is one of many tools, and often the plain-code answer wins.</span><span class="wk">This week: pick one of those five and solve it end to end.</span></div>
<div class="c4"><b>The entrepreneur</b><span>You look for problems people would pay to make go away, and you take responsibility for the whole solution.</span><span class="wk">This week: talk to three people who have that problem.</span></div>
</div>

<h2 id="the-surfer">The surfer</h2>
<div class="panel flip">{IMG('surfer')}<div>
<p>When a high tide comes, it comes for everyone on the beach. Some people are knocked over. Some swim away from it. And a prepared surfer paddles <em>towards</em> the wave, stands up at exactly the right moment, and rides on top of it.</p>
<p>The wave is the same for all of them. What decides who ends up on top is preparation and mindset, built long before the wave arrived.</p></div></div>
<div class="tw"><table class="vs">
<tr><th></th><th>What the surfer prepares</th><th>What you prepare</th></tr>
<tr><td>Balance</td><td>core strength</td><td>fundamentals: software engineering, data, clear thinking, writing</td></tr>
<tr><td>Reading the water</td><td>knowing how waves form</td><td>knowing the map: <a href="/learn/ai-universe/">the AI Universe</a>, concepts before products</td></tr>
<tr><td>Paddling early</td><td>moving before the wave arrives</td><td>starting now, while the ground is still changing</td></tr>
<tr><td>Falling and getting up</td><td>hundreds of falls</td><td>small projects that fail fast and teach you a lot</td></tr>
</table></div>
{nav(1)}"""


def first30():
    who = [("c1", "Still in college", "You have the most time and the least to lose. Build in public now; by graduation, your projects speak louder than your marks."),
           ("c2", "Just graduated", "Don't wait for the perfect job to teach you. Join a real project, ship something, and you will interview with evidence instead of hope."),
           ("c3", "Lost your job", "First, breathe: it is not a verdict on you. Your domain experience is gold. Pair it with AI and you can solve problems in your field that a fresh graduate can't even see."),
           ("c4", "Scared of losing it", "Your job is your laboratory. Find the work that repeats in your team, solve it with AI, and become the person who brings the dragon home.")]
    weeks = [("Week 1 · Draw the map", "Read the <a href='/learn/ai-universe/'>AI Universe</a>. Pick the one family closest to your work. Learn its concepts, not product names."),
             ("Week 2 · Build something tiny", "Make one small thing that works: a script, a chatbot over your notes, an agent that does one job. It doesn't have to be good. It has to run."),
             ("Week 3 · Join something real", "Pick a <a href='/projects/'>project</a> that is under way and take a good first task. Real code, real reviews, real people."),
             ("Week 4 · Share and ask", "Write what you learned in five minutes of reading. Then talk to five people about a problem they have every week. That conversation is your next project.")]
    cards = "".join(f'<div class="{c}"><b>{t}</b><span>{s}</span></div>' for c, t, s in who)
    wk = "".join(f'<div class="c{i + 1}"><b>{t}</b><span>{s}</span></div>' for i, (t, s) in enumerate(weeks))
    return f"""{crumbs('Your first 30 days')}
<div class="hero hub-hero"><div><h1>Your first 30 days</h1>
<p class="thesis">Fear shrinks when you start moving. Here is a month that turns "I'm worried about AI" into "I built something with AI, and I know what to learn next".</p></div>{IMG('learn')}</div>
<h2>Where are you starting from?</h2>
<div class="cards4">{cards}</div>
<h2>Four weeks, one step each</h2>
<div class="cards4">{wk}</div>
<div class="moral">One rule for the whole month: <strong>learn the concept, then build it once.</strong> A product name on a CV fades in a year. Understanding why a system works, and having built one, lasts a career.</div>
{nav(2)}"""


def start():
    steps = [("c1", "Find a real problem", "Start from a person and their pain, not from AI. What do they do every week that is slow, error-prone or expensive?"),
             ("c2", "Prefer shared problems", "A customer's problem pays your rent. A horizontal problem, one that many companies share, can become a product."),
             ("c3", "Build the tiniest version", "The core that solves it, then a way to measure it, then a way to charge for it. Most of it is ordinary software; AI is the small, powerful part."),
             ("c4", "Let AI be your wings", "One person with AI can now do what took a team. Use it to build faster, test faster, and reach people you couldn't reach alone.")]
    cards = "".join(f'<div class="{c}"><b>{t}</b><span>{s}</span></div>' for c, t, s in steps)
    return f"""{crumbs('Start something')}
<div class="hero hub-hero"><div><h1>Start something</h1>
<p class="thesis">The villagers who learned to ride the dragon didn't just keep their village. They built a better one. In the age of AI, more people than ever can open a company, because one person with AI can build what used to need a team.</p></div>{IMG('about')}</div>
<div class="cards4">{cards}</div>
<h2>Two kinds of problem worth solving</h2>
<div class="tw"><table class="vs">
<tr><th></th><th>A customer's problem</th><th>A horizontal problem</th></tr>
<tr><td>What it is</td><td>one company's specific pain</td><td>the same pain in many companies</td></tr>
<tr><td>Example</td><td>"our claims team re-types every form"</td><td>"every company wastes money on idle cloud clusters"</td></tr>
<tr><td>How you earn</td><td>a project, a contract, a retainer</td><td>a product many customers pay for</td></tr>
<tr><td>Where to start</td><td>talk to people in your old industry</td><td>notice which customer problems keep repeating</td></tr>
</table></div>
<h2>Start with what we are building together</h2>
<p>Every <a href="/projects/">project on this site</a> has a page saying why it matters and what needs doing next. Some need a lead. The <a href="/projects/pain-registry-helpers/">pain registry</a> collects the real problems of people hit by AI-era job loss, so the next things built can actually help them. Join one, or bring your own problem and start the next one.</p>
<div class="moral">Surviving is a fine first step. But the people who will shape this era are the ones who decided to learn the dragon, build with it, and fly. <strong>You can be one of them, starting this week.</strong></div>
{nav(3)}"""


def main():
    out = ROOT / "mindset"
    bodies = {"": story(), "builder": builder(), "first-30-days": first30(), "start-something": start()}
    meta = {"": ("Train the dragon", "For anyone scared or confused about AI: the dragon story, the lion mindset, and the decision it asks of you."),
            "builder": ("From surviving to building", "The builder, innovator, problem-solver and entrepreneur mindsets, and the surfer."),
            "first-30-days": ("Your first 30 days", "A month that turns worry about AI into something built and a clear next step."),
            "start-something": ("Start something", "Solve a customer's problem, or one many share, with AI as your wings.")}
    for rel, body in bodies.items():
        d = out / rel if rel else out
        d.mkdir(parents=True, exist_ok=True)
        title, desc = meta[rel]
        (d / "index.html").write_text(wb.page(title, desc, f"{wb.SITE}/mindset/{rel + '/' if rel else ''}", body, CSS))
    print(f"{len(bodies)} pages -> {out}")


if __name__ == "__main__":
    main()
