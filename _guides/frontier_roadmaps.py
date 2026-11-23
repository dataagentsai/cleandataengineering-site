"""Four roadmaps for frontier AI work: /learn/frontier-ai-roadmaps/ and one page per role.

    python3 _guides/frontier_roadmaps.py      (then python3 _site/nav.py and python3 _site/seo.py)

Roles: LLM engineer, inference engineer, AI safety and security, AI researcher. Each page has the job in plain words,
eight small steps (each with what to do, how you know you are done, and a tick box kept in the visitor's browser),
five small projects that each end in a number you can publish, what to leave for later, and a short FAQ.
The hub shows the shared base and how to pick. Every internal link is checked against the built site.
Time spans, prices and difficulty are rules of thumb and are stated as such. The tools named were checked against
a sample of 2026 job postings and engineering guides in November 2026; tools change, so recheck each quarter.
"""
import json
import sys
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / "_paths"))
import components as C  # noqa: E402

wb = C.wb
SITE = wb.SITE
BASE = "/learn/frontier-ai-roadmaps/"
DATE = "2026-11-23"
AUTHOR = {"@type": "Person", "name": "Basant Choudhary", "url": f"{SITE}/#about"}


def L(path):
    base = path.split("#")[0]
    if base.startswith(BASE):  # our own pages, written by this script
        return path
    if base and base != "/" and not base.startswith("http"):
        assert (ROOT / base.strip("/") / "index.html").exists() or (ROOT / base.strip("/")).is_file(), f"missing page: {path}"
    return path


# =================================================================== the content
# Each role: id, name, wash colour, one-line job, plain picture of the job, who it suits, steps, projects, skip, faq, links.
# step = (title, do this, you are done when, link-or-None)
# project = (id, name, time, what you build, what you learn, the number you publish, link-or-None)

BASE_STEPS = [
    ("Python you can read", "Write ten small programs: read a file, count words, call a web API, sort a list of records. Use plain Python, no framework.", "You can write a loop, a function and a dictionary without looking anything up."),
    ("Git and GitHub", "Put every small program in one repository. Commit each change with a one-line message.", "A stranger can open your repository and run something from the README."),
    ("Tensors and PyTorch basics", "Make a tensor, multiply two of them, take a gradient of one number. Do the first official PyTorch tutorial.", "You can explain in two sentences what a gradient is for."),
    ("Run a model on your own machine", "Install a local runner (Ollama or llama.cpp) and ask a small open model ten questions.", "You know the model's size on disk and how many answers per minute it gives."),
    ("Keep a measurement notebook", "One file where every experiment gets: the question, the setup, the number, and what surprised you.", "Your last three experiments are written down so someone else could repeat them."),
]

ROLES = [
    {
        "id": "llm-engineer", "name": "LLM engineer", "wash": "var(--mint-wash)", "fill": "#eaf6ef",
        "job": "You build products on top of language models and adapt them to a task: prompts, tools, retrieval, evaluation, fine-tuning.",
        "picture": "Think of a model as a very well-read new colleague. The LLM engineer decides what to tell them, what files to hand them, what tools they may use, and how to check their work. When prompts are not enough, the engineer teaches the colleague on examples (fine-tuning).",
        "suits": "You like building, testing and fixing. You enjoy turning a vague wish into something that works 95 times out of 100, and knowing which five fail.",
        "start": "Open the Claude API simulator, change the temperature and max tokens, and write down what changed in the answer.",
        "steps": [
            ("Call a model and read the answer", "Send one request to a model API and print the reply. Change temperature and max tokens, and note what changes.", "You can explain what temperature does, and what happens when max tokens is too small.", "/learn/llm-api-sim/"),
            ("Count tokens", "Take five sentences in English and the same five in Hindi or Tamil. Count tokens for each with a tokenizer. Make a small table.", "You know why the same sentence costs more in some languages.", None),
            ("Ask for structured output and call a tool", "Make the model return JSON that matches a schema. Then let it call one function you wrote, such as a weather lookup.", "Your code receives valid JSON 30 times out of 30, or you know exactly why not.", None),
            ("Write a test set before you tune the prompt", "Write 30 questions with the answers you expect. Run them, record the pass rate, change the prompt, run again.", "You can show a before and after pass rate, and list the cases that still fail.", "/learn/eval-harness/"),
            ("Add retrieval", "Split ten documents into chunks, turn each into a vector, fetch the best five for a question, and answer with a quote from them.", "On 20 questions you can say how often the right chunk was in the top five.", None),
            ("Fine-tune a small open model", "Use LoRA (training a small add-on instead of the whole model) on a narrow task with a few hundred examples.", "You have a held-out set where the tuned model beats the base model, or you can say why it did not.", None),
            ("Learn what preference tuning does", "Read a plain explanation of DPO (training on pairs of better and worse answers). Build ten pairs for your task and train once.", "You can say when preference tuning helps and when better data would help more.", None),
            ("Ship it with a cost per answer", "Put your system behind a small web API. Log tokens, time and price for every call, and add a cache.", "You can state the cost of 1,000 answers and what makes it go up.", "/learn/which-model/"),
        ],
        "projects": [
            ("L1", "Token tax table", "one weekend", "A table of tokens per sentence for 5 languages across 3 tokenizers.", "How tokenizers split text, and why some languages cost more.", "Tokens per sentence, by language and tokenizer.", None),
            ("L2", "A 30-case test for one prompt", "one weekend", "A small test set and a script that scores a prompt and prints a pass rate.", "Testing before tuning; how prompts change results.", "Pass rate before and after your best prompt.", "/learn/eval-harness/"),
            ("L3", "Ask my notes", "two weeks", "A question-answering tool over your own notes or a public document set, with quoted sources.", "Chunking, embeddings, retrieval, and where answers go wrong.", "Share of questions where the right chunk was retrieved.", None),
            ("L4", "A small tuned model", "two to three weeks", "A LoRA fine-tune of a small open model on one narrow task.", "Data preparation, training, and honest before and after testing.", "Held-out score, base model versus tuned model.", None),
            ("L5", "Cost per answer dashboard", "one week", "A log of tokens and price for every call, with a weekly summary.", "What really drives LLM cost; caching and model choice.", "Cost per 1,000 answers before and after one change.", "/learn/which-model/"),
        ],
        "skip": [("Learning every agent framework", "Drop", "Learn the loop once: model, tool, result, repeat. Frameworks are wrappers around it."),
                 ("Fine-tuning first", "Delay", "Most problems are fixed by better prompts, retrieval and test cases. Fine-tune when a test shows the need."),
                 ("Training a model from scratch", "Delay", "It teaches a lot but is not needed to build useful products. The researcher roadmap covers a tiny version."),
                 ("Chasing the newest model each week", "Drop", "Keep one fixed test set. Swap the model, rerun the test, and decide by the number.")],
        "faq": [("What is the difference between an LLM engineer and an AI engineer?", "On this site, the AI engineer builds whole agent systems: harness, guardrails, evaluation and governance. The LLM engineer goes deeper on the model side: tokens, retrieval, tuning and cost. The skills overlap a lot, and the first six steps are shared."),
                ("Do I need a GPU?", "Not for steps 1 to 5. For fine-tuning a small model you can use a free notebook GPU or rent one by the hour. Free options have limits and change often, so check current terms."),
                ("How long does it take?", "As a rule of thumb, two to four months at about eight hours a week to finish the eight steps. Your pace will differ.")],
        "links": [("Learning path: LLM engineering", "/paths/llm-engineering/"), ("Claude API simulator", "/learn/llm-api-sim/"), ("Which AI model for which job", "/learn/which-model/"), ("Eval Harness", "/learn/eval-harness/")],
    },
    {
        "id": "inference-engineer", "name": "Inference engineer", "wash": "var(--butter-wash)", "fill": "#fff4d6",
        "job": "You make trained models answer faster and cheaper: memory, speed, batching, quantization and the GPU code underneath.",
        "picture": "If training is writing the cookbook, inference is the restaurant kitchen at dinner rush. The inference engineer decides how many orders to cook at once, how to keep the ingredients close at hand, and how to serve the same dish with less cost and less waiting.",
        "suits": "You like measuring, tuning and finding out why something is slow. You are comfortable with low-level detail and with being proved wrong by a stopwatch.",
        "start": "Run a small model with Ollama or llama.cpp and write down the time to the first word and the words per second.",
        "steps": [
            ("Learn the two phases of an answer", "Read a plain explanation of prefill (reading your prompt) and decode (writing the answer one token at a time), and of the KV cache that stores earlier work.", "You can draw both phases and say which one is limited by memory speed.", None),
            ("Measure before you guess", "Run one small model locally. Record time to first token and tokens per second for a short and a long prompt.", "You have a table of three measurements with the machine and settings written beside it.", None),
            ("Do the memory sum", "A model with 7 billion parameters at 16 bits needs about 14 GB for weights alone. Work out 8-bit and 4-bit, then add room for the KV cache.", "You can predict whether a model fits on a given card without trying.", None),
            ("Quantize and compare", "Run the same model at three precisions. Measure speed and answer quality on 100 questions.", "You can say what you gave up for each saving.", None),
            ("Serve with a real engine", "Rent a GPU by the hour and serve a model with vLLM. Send 1, 8 and 32 requests at once and record throughput and delay.", "You have a curve of throughput against delay and can explain its shape.", None),
            ("Write one GPU kernel", "In Triton (a Python language for GPU code), write vector add and softmax. Time them against PyTorch.", "Your kernel gives the same answers, and you know why it is faster or slower.", None),
            ("Reproduce one speed-up idea", "Pick one of continuous batching, prefix caching or speculative decoding (a small model drafts, a big one checks). Reproduce the gain at small scale.", "You have a before and after number and a plain sentence on why it works.", None),
            ("Turn speed into money", "Work out the cost per million tokens for your setup, including idle time. Change one thing and recompute.", "You can say which one change saved the most.", "/learn/which-model/"),
        ],
        "projects": [
            ("I1", "Will it fit? A memory calculator", "one weekend", "A small tool that takes parameters, precision and context length, and says how much memory is needed.", "Weights, KV cache and overhead.", "Predicted against real memory use on three models.", None),
            ("I2", "Laptop speed table", "one weekend", "Speed of one model at three precisions on your own machine.", "Where time goes on ordinary hardware.", "Tokens per second and first-token time, per precision.", None),
            ("I3", "Quality versus bits", "two weeks", "100 questions run through the same model at 8, 4 and 3 bits, scored the same way.", "What compression costs in quality.", "Score drop per bit-width, with a note on sample size.", None),
            ("I4", "The batching curve", "two weeks", "Throughput and delay of vLLM at several levels of load on a rented GPU.", "Why batching raises throughput and hurts delay.", "A chart of throughput against delay. Cost: a few dollars to tens of dollars; check current prices.", None),
            ("I5", "Two small GPU kernels", "two weeks", "Vector add and softmax in Triton, timed against PyTorch.", "How GPUs move memory, and where kernels win.", "Milliseconds per call at three sizes.", None),
        ],
        "skip": [("Writing CUDA from day one", "Delay", "Start with measurement and Triton. CUDA matters for kernel roles, but the first gains come from knowing where time goes."),
                 ("Reading every inference paper", "Drop", "Reproduce one idea in full. A reproduced result teaches more than ten summaries."),
                 ("Buying a GPU", "Drop", "Rent by the hour until you know what you need. Prices change, so check current rates."),
                 ("Training large models", "Delay", "Training infrastructure is a different job. Learn serving first; the memory sums carry over.")],
        "faq": [("Is this harder to enter than LLM engineering?", "Usually, yes. Postings often ask for GPU programming and systems skill, which take longer to build. The steps above are a way to build that evidence in small pieces."),
                ("Do I need C++ or Rust?", "Not at the start. Python and Triton cover the first eight steps. Postings often list C++ or CUDA for kernel and engine work, so add them once you know that is your direction."),
                ("What does it cost?", "Steps 1 to 4 are free on a laptop. Steps 5 to 7 need a rented GPU for a few hours; as a rule of thumb, a few dollars to tens of dollars in total. Check current prices.")],
        "links": [("Which AI model for which job", "/learn/which-model/"), ("Hard problems: faster and cheaper answers", "/problems/"), ("Learning path: LLM engineering", "/paths/llm-engineering/")],
    },
    {
        "id": "ai-safety", "name": "AI safety and security", "wash": "var(--rose-wash)", "fill": "#fbeef3",
        "job": "You find how AI systems can fail or be attacked, measure it honestly, add controls, and show the evidence that the controls work.",
        "picture": "A safety engineer is a careful inspector. They try to break the system the way a real person or attacker would, count how often it breaks, fit a guard, and then test again. At the end they leave a page that a regulator or a customer can read and check.",
        "suits": "You like asking what could go wrong, and you can be patient and fair. You write clearly, and you are happy to prove your own fix does not work.",
        "start": "Open any chatbot you built, write ten tricky inputs, and note which ones it handles badly. Practise on systems you own only.",
        "steps": [
            ("Learn six ways AI fails", "Write one example each for: wrong but confident answers, jailbreaks, prompt injection, leaking private data, unsafe tool use, and unfair answers.", "You can show each failure on a toy system in one screen.", "/learn/agent-guardrails/"),
            ("Read the two key lists", "Read the OWASP Top 10 for LLM Applications and skim MITRE ATLAS (a catalogue of attack methods on AI systems).", "You can say which three items matter most for the system you have built.", None),
            ("Attack your own toy chatbot", "Write ten prompt-injection attempts against a chatbot you built. Log what each did.", "You have a table of attempt, result and why.", None),
            ("Build a tiny test with a pass or fail", "Turn your attempts into a script that runs them all and prints the attack success rate.", "Anyone can rerun the script and get the same number.", "/learn/eval-harness/"),
            ("Add one defence and test again", "Add an input filter, an output check or a limit on which tools the agent may use. Rerun the test.", "You can show the rate before and after, and the attacks that still get through.", "/learn/agent-guardrails/"),
            ("Threat-model one agent", "List what it protects, how things get in, and how each could be abused. Add a test for each threat.", "You have one page: threats found, and how many your controls stop.", "/learn/agenttwin/"),
            ("Map your controls to a standard", "Pick NIST AI RMF or ISO/IEC 42001. Match each of your controls to a clause and link the evidence.", "A reader can follow each claim to a test result.", "/learn/ai-governance/"),
            ("Write a short incident review", "Invent or find a small failure. Write what happened, the cause, the fix and what you now check.", "It reads in under two pages and has no blame in it.", None),
        ],
        "projects": [
            ("S1", "A 50-attack test set", "one weekend", "Fifty prompt-injection and jailbreak attempts for a toy assistant, in a file.", "How attacks are phrased, and how to log them.", "Attack success rate on one model.", None),
            ("S2", "Defences compared", "two weeks", "Three or four defences run against the same attack set.", "What each defence blocks, and what it breaks.", "Attack success rate with and without each defence.", "/learn/agent-guardrails/"),
            ("S3", "A permission sandbox", "two to three weeks", "An agent with least-privilege tools and a script that tries to break out.", "Tool scoping, secrets and isolation.", "Escapes blocked out of attempts made.", None),
            ("S4", "A threat model with tests", "two weeks", "One real agent, its threats listed against OWASP and MITRE ATLAS, each with a test.", "Threat modelling for AI systems.", "Threats found, and how many your controls stop.", "/learn/agenttwin/"),
            ("S5", "An evidence one-pager", "one week", "A report that turns your test results into controls mapped to a standard.", "How audit evidence is built.", "Controls covered, with a link to a result for each.", "/learn/ai-governance/"),
        ],
        "skip": [("Attacking systems you do not own", "Drop", "Practise only on your own systems or ones with published permission. Follow each programme's rules."),
                 ("Collecting framework names", "Drop", "Use two frameworks properly instead of listing ten."),
                 ("Alignment theory first", "Delay", "It is deep research. Start with measuring and defending real systems; theory is easier once you have seen failures."),
                 ("Reporting one lucky number", "Drop", "Use enough examples, show the cases that fail, and publish your data and script.")],
        "faq": [("Is this a research job or an engineering job?", "Both exist. Evaluation, red-teaming and applied security are mostly careful engineering and writing. Alignment and interpretability research usually asks for a research record."),
                ("What tools do postings name?", "In a sample of 2026 postings, garak, PyRIT, promptfoo and Giskard appear for red-teaming, alongside OWASP, MITRE ATLAS and NIST AI RMF. Inspect, from the UK AI Security Institute, is widely used for evaluations. It is a sample, not a survey."),
                ("Do I need a security background?", "It helps a lot. Many postings ask for offensive-security grounding, with certifications such as OSCP preferred rather than required. If you do not have it, steps 3 and 4 are where to build it.")],
        "links": [("Agent guardrails", "/learn/agent-guardrails/"), ("Running AI you can trust", "/learn/ai-governance/"), ("Eval Harness", "/learn/eval-harness/"), ("AgentTwin, explained", "/learn/agenttwin/")],
    },
    {
        "id": "ai-researcher", "name": "AI researcher", "wash": "var(--peri-wash)", "fill": "#eef3fb",
        "job": "You ask a question nobody has settled, design a fair test, run it, and publish what you found so others can check it.",
        "picture": "A researcher is a scientist whose lab is a computer. They write the guess down first, build the experiment, run it many times, and report honestly, even when the answer is no. The finished product is a short paper, code and data that others can rerun.",
        "suits": "You are patient with hard ideas and happy with slow progress. You like reading carefully, and you care more about being right than about being quick.",
        "start": "Pick one short paper, write down its claim, its evidence, and what result would have proved it wrong.",
        "steps": [
            ("Get the maths minimum", "One hour a day on vectors, matrices, derivatives and basic probability. Work problems, not videos.", "You can compute a derivative by hand and multiply two small matrices.", None),
            ("Build a neural net from scratch", "In plain NumPy, train a tiny network on a toy task such as separating two clusters.", "You can explain each line of the training loop, including the gradient step.", None),
            ("Build a tiny transformer", "In PyTorch, train a character-level transformer on a small text file. A public tutorial is fine as a guide.", "It writes text that looks like the training text, and you can describe attention in your own words.", None),
            ("Read one paper a week", "Use a fixed template: the claim, the evidence, what would prove it wrong, and what you do not trust.", "You have four filled templates, one per week.", None),
            ("Reproduce one small result", "Pick a small, well-known result and rerun it. Record every place your numbers differ from the paper.", "You can say whether it held up and what the paper left unclear.", None),
            ("Ask your own narrow question", "Write the guess and the measurement before running anything. Keep the question small enough to finish.", "Someone else can tell from your note what would count as a yes and what as a no.", "/problems/"),
            ("Run it with controls and several seeds", "Repeat each experiment with at least five random seeds and report the range, not the best run.", "Your result includes a spread, and you say if the spread is bigger than the effect.", None),
            ("Write it up and ask for feedback", "A two to four page note, with code and data public. Send it to one person who works on the topic.", "A stranger could rerun your code from the page.", None),
        ],
        "projects": [
            ("R1", "A neural net in NumPy", "one to two weeks", "A tiny network, written without a framework.", "What a framework hides: gradients and updates.", "Accuracy on a toy task, and the loss curve.", None),
            ("R2", "A character-level transformer", "two weeks", "A small transformer trained on a text file.", "Attention, training loops and sampling.", "Loss curve and a sample of the text it writes.", None),
            ("R3", "Reproduce a small result", "two to three weeks", "A rerun of one short, well-known paper result.", "What reproducibility really takes.", "Your numbers beside the paper's, with the differences explained.", None),
            ("R4", "How much do seeds matter?", "one week", "The same experiment run with ten random seeds.", "Why one run proves little.", "The spread of the result across seeds.", None),
            ("R5", "A small measurement of your own", "two to four weeks", "One narrow question, such as how a tokenizer treats a language, measured fairly.", "Framing a question, controls, and honest reporting.", "One headline number with its spread, and the data released.", "/problems/"),
        ],
        "skip": [("Reading every new paper", "Drop", "One paper a week, filled in fully, beats thirty skimmed."),
                 ("Starting with a huge question", "Drop", "Pick a question you can finish in weeks. Small and finished beats large and abandoned."),
                 ("Chasing a PhD before any output", "Delay", "Many research roles ask for a PhD or an equivalent public record. Small replications and measurements are how you build that record, whether or not you later enrol."),
                 ("Using a framework to hide the maths", "Delay", "Write the first network by hand once. After that, use the tools.")],
        "faq": [("Do I need a PhD?", "For many research-scientist roles, yes, or an equivalent public record of original work. Some research-engineer roles value strong engineering plus replications and measurements. Check each posting; this is a pattern, not a rule."),
                ("Can I do research without a lab?", "Yes, at small scale. Careful replications and measurements, such as the 'small measurement of your own' project, need a laptop and patience, and labs rarely have time for them."),
                ("How is this different from LLM engineering?", "An LLM engineer makes a system work for a purpose. A researcher answers a question and publishes the answer. The first four steps overlap.")],
        "links": [("Hard unsolved problems, with 8-week experiments", "/problems/"), ("Hard problems by layer, and how to solve them", "/learn/hard-problems/"), ("Learning path: LLM engineering", "/paths/llm-engineering/")],
    },
]
BY_ID = {r["id"]: r for r in ROLES}

HUB_TABLE = [
    ("LLM engineer", "Builds products on models: prompts, tools, retrieval, tests, tuning, cost.", "Moderate. Reachable with projects and published tests.", "L2: a 30-case test for one prompt", "llm-engineer"),
    ("Inference engineer", "Makes models answer faster and cheaper: memory, batching, quantization, GPU code.", "Hard. Postings often ask for GPU and systems skill.", "I2: laptop speed table", "inference-engineer"),
    ("AI safety and security", "Finds failures and attacks, measures them, adds controls, writes the evidence.", "Moderate to hard. Measurement and security grounding matter most.", "S1: a 50-attack test set", "ai-safety"),
    ("AI researcher", "Asks an open question, runs a fair test, publishes the result.", "Hardest. Many roles expect a PhD or an equivalent record.", "R4: how much do seeds matter?", "ai-researcher"),
]

OVERLAP = [
    ("Measure honestly", "All four", "A fair test, enough examples, a number with its spread. This is the habit that gets work noticed."),
    ("Publish code and data", "All four", "A stranger must be able to rerun it. Hiring teams read repositories, not claims."),
    ("Tokens and how models read text", "LLM, inference, safety", "Tokens set cost, speed and some attacks."),
    ("Evaluation sets", "LLM, safety, research", "A fixed test set lets you change one thing and see what happened."),
    ("GPU and memory sums", "Inference, research", "Needed whenever you train or serve something bigger than a laptop model."),
    ("Threat thinking", "Safety, LLM", "Asking how a system could be abused makes products stronger, not only safer."),
]

PICK = [
    ("I like making things that work for users", "LLM engineer"),
    ("I like finding out why something is slow", "Inference engineer"),
    ("I like asking what could go wrong", "AI safety and security"),
    ("I like questions more than products", "AI researcher"),
]

JOB_NOTE = ("Time spans, prices and difficulty on these pages are rules of thumb. The tools named were checked in November 2026 against a sample of job postings and engineering guides, "
            "which is a sample and not a survey. Tools change fast, so recheck each quarter.")


# =================================================================== drawings
def _t(x, y, s, size=16, anchor="middle", fill="#1F1F1F", bold=False):
    w = ' font-weight="700"' if bold else ""
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}"{w}>{E(s)}</text>'


def _r(x, y, w, h, fill, rx=12, sw=1.6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="#1F1F1F" stroke-width="{sw}"/>'


def _svg(w, h, body, label):
    defs = ('<defs><marker id="fa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            '<path d="M0,0 L10,5 L0,10 z" fill="#1F1F1F"/></marker></defs>')
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}">{defs}{body}</svg>'


def draw_hub():
    b = _r(10, 12, 920, 74, "#fffaf0") + _t(470, 42, "Shared base: Python, Git, PyTorch, a local model, a measurement notebook", 19, bold=True)
    b += _t(470, 68, "about four weeks, the same for everyone", 15, fill="#555")
    xs = [10, 244, 478, 712]
    for i, r in enumerate(ROLES):
        x = xs[i]
        b += f'<line x1="{x + 109}" y1="88" x2="{x + 109}" y2="122" stroke="#1F1F1F" stroke-width="1.6" marker-end="url(#fa)"/>'
        b += f'<a href="{BASE}{r["id"]}/">' + _r(x, 124, 218, 92, r["fill"]) + _t(x + 109, 160, r["name"], 20, bold=True) + _t(x + 109, 188, "8 steps, 5 projects", 15, fill="#555") + "</a>"
    b += _r(10, 232, 920, 54, "#f4f1ea") + _t(470, 256, "Every roadmap ends the same way: a number you measured, with the code and data public", 17)
    b += _t(470, 276, "Share it with people who work on the topic.", 15, fill="#555")
    return _svg(940, 298, b, "A shared four-week base leads to four roles: LLM engineer, inference engineer, AI safety and security, and AI researcher. Each has eight steps and five projects.")


def draw_ladder(role):
    steps = role["steps"]
    b = ""
    w, h, gx, gy = 218, 78, 14, 20
    for i, st in enumerate(steps):
        col, row = i % 4, i // 4
        x, y = 10 + col * (w + gx), 14 + row * (h + gy)
        b += _r(x, y, w, h, role["fill"]) + _t(x + 16, y + 28, str(i + 1), 20, "middle", bold=True)
        words = st[0]
        # wrap the title over two lines
        parts, line = [], ""
        for wd in words.split():
            if len(line) + len(wd) > 24:
                parts.append(line)
                line = wd
            else:
                line = (line + " " + wd).strip()
        parts.append(line)
        for k, ln in enumerate(parts[:3]):
            b += _t(x + 34, y + 28 + k * 20, ln, 15, "start")
        if col < 3:
            b += f'<line x1="{x + w + 1}" y1="{y + h / 2}" x2="{x + w + gx - 1}" y2="{y + h / 2}" stroke="#1F1F1F" stroke-width="1.4" marker-end="url(#fa)"/>'
    return _svg(940, 14 + 2 * (h + gy), b, f"The eight steps of the {role['name']} roadmap in order.")


# =================================================================== pages
CSS = """<style>
  .fr .chip { display:inline-block; border:1.5px solid #1F1F1F; border-radius:999px; padding:2px 12px; margin:3px 4px 3px 0; font-size:14px; text-decoration:none; color:#1F1F1F; background:#fff; }
  .fr .chip:hover { background:#fff4d6; }
  .fr .fig { margin:12px 0 16px; } .fr .fig svg { width:100%; height:auto; background:#fff; border:var(--line); border-radius:var(--wob); font-family:var(--hand), sans-serif; }
  .fr .fig p { font-size:13.5px; color:#555; margin:4px 2px 0; }
  .fr .box { border:var(--line); border-radius:var(--wob); padding:12px 18px; margin:12px 0; background:#fff; }
  .fr .box.start { background:#fff4d6; } .fr .box.pic { background:#f4f8ff; }
  .fr .step { display:grid; grid-template-columns:34px 1fr; gap:4px 12px; border:var(--line); border-radius:var(--wob); padding:12px 16px; margin:10px 0; background:#fff; }
  .fr .step input { width:20px; height:20px; margin-top:4px; accent-color:#3B4F8F; }
  .fr .step h3 { font-size:22px; margin:0 0 2px; } .fr .step p { margin:2px 0; font-size:15.5px; } .fr .step .done { font-size:14.5px; background:#f0f8f3; border-radius:8px; padding:5px 10px; margin-top:6px; }
  .fr .step.checked { opacity:.62; } .fr .progress { font-size:15px; margin:8px 0 2px; }
  .fr .proj { border:var(--line); border-radius:var(--wob); padding:12px 16px; margin:10px 0; background:#fff; } .fr .proj h3 { font-size:22px; margin:0 0 2px; } .fr .proj .meta { color:#555; font-size:14px; margin:0 0 6px; }
  .fr .proj dl { display:grid; grid-template-columns:130px 1fr; gap:3px 12px; margin:6px 0; font-size:15px; } .fr .proj dt { font-family:var(--hand); font-size:18px; } .fr .proj dd { margin:0; }
  @media (max-width:640px) { .fr .proj dl { grid-template-columns:1fr; } }
</style>"""


def ld(title, desc, url, crumbs, faq=None):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]
    out = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": title, "description": desc, "url": url, "inLanguage": "en",
            "isAccessibleForFree": True, "dateModified": DATE, "author": AUTHOR,
            "publisher": {"@type": "Organization", "name": "Clean Data Engineering", "url": SITE}},
           {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]
    if faq:
        out.append({"@context": "https://schema.org", "@type": "FAQPage",
                    "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    return "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in out)


def chips(links):
    return "".join(f'<a class="chip" href="{L(u)}">{E(n)}</a>' for n, u in links)


TICKS_JS = """<script>
(function(){
  var KEY='frontier-roadmap-%s', boxes=document.querySelectorAll('.fr .step input'), out=document.getElementById('progress'), saved={};
  try { saved=JSON.parse(localStorage.getItem(KEY)||'{}'); } catch(e) {}
  function show(){
    var n=0; boxes.forEach(function(b){ var s=b.closest('.step'); if(b.checked){ n++; s.classList.add('checked'); } else { s.classList.remove('checked'); } });
    out.textContent=n+' of '+boxes.length+' steps ticked. Your ticks stay in this browser only.';
  }
  boxes.forEach(function(b){ if(saved[b.dataset.i]) b.checked=true;
    b.addEventListener('change', function(){ var v={}; boxes.forEach(function(x){ if(x.checked) v[x.dataset.i]=1; }); try { localStorage.setItem(KEY, JSON.stringify(v)); } catch(e) {} show(); }); });
  show();
})();
</script>"""


def role_page(r):
    url = f"{SITE}{BASE}{r['id']}/"
    title = f"{r['name']} roadmap: eight small steps and five small projects"
    desc = (f"A plain roadmap to become a {r['name'].lower()}: what the job is, eight small steps with how to know you are done, "
            f"five small projects that each end in a number you can publish, and what to leave for later.")
    steps = "".join(
        f'<div class="step"><input type="checkbox" data-i="{i}" id="s{i}" aria-label="Done: {E(s[0])}"><div><h3>{i + 1}. {E(s[0])}</h3><p>{E(s[1])}</p>'
        f'<p class="done"><b>You are done when:</b> {E(s[2])}</p>' + (f'<p><a href="{L(s[3])}">Open the matching guide on this site</a></p>' if s[3] else "") + "</div></div>"
        for i, s in enumerate(r["steps"]))
    projects = "".join(
        f'<div class="proj"><h3>{E(p[0])}. {E(p[1])}</h3><p class="meta">About {E(p[2])}</p><dl><dt>You build</dt><dd>{E(p[3])}</dd><dt>You learn</dt><dd>{E(p[4])}</dd>'
        f'<dt>Number you publish</dt><dd>{E(p[5])}</dd></dl>' + (f'<p><a href="{L(p[6])}">Related guide</a></p>' if p[6] else "") + "</div>"
        for p in r["projects"])
    base = C.table(["Step", "What to do", "You are done when"], [(f"{i + 1}. {s[0]}", s[1], s[2]) for i, s in enumerate(BASE_STEPS)])
    skip = C.table(["Temptation", "Verdict", "Why"], r["skip"])
    others = chips([(o["name"], f"{BASE}{o['id']}/") for o in ROLES if o["id"] != r["id"]])
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="{BASE}">Frontier AI roadmaps</a> › {E(r['name'])}</p>
<p class="eyebrow" style="margin-top:22px">Frontier AI roadmaps · {E(r['name'])}</p>
<h1>{E(r['name'])}: the roadmap</h1>
<p class="lede">{E(r['job'])} This page gives you eight small steps, each with a clear finish line, and five small projects. Each project ends in one number you can publish.</p>
<div class="fr">
<div class="box pic"><b>The job, in a picture you can hold in your head.</b> {E(r['picture'])}</div>
<div class="box"><b>This may suit you if:</b> {E(r['suits'])}</div>
<div class="box start"><b>Start in 30 minutes:</b> {E(r['start'])}</div>

<section id="base"><p class="eyebrow">Week 0 to 4</p><h2>First, the base every role shares</h2>
<p>Do these five things first. They are the same for all four roles, so nothing you do here is wasted if you change your mind.</p>{base}</section>

<section id="steps"><p class="eyebrow">The roadmap</p><h2>Eight small steps</h2>
<div class="fig">{draw_ladder(r)}<p>The eight steps in order. Do one at a time; each one is small enough for a weekend or two.</p></div>
<p class="progress" id="progress"></p>{steps}</section>

<section id="projects"><p class="eyebrow">Small projects</p><h2>Five projects, each ending in a number</h2>
<p>Keep each project small. Put the code and data in a public repository and write a one-page note on what you found. Where a project has code that can be tested, write the tests as one table of inputs and expected results, with one loop that runs every row. That keeps tests short and easy to extend.</p>{projects}</section>

<section id="skip"><p class="eyebrow">What to leave for later</p><h2>Temptations, with a verdict</h2>{skip}</section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(r['faq'])}</section>

<section id="next"><p class="eyebrow">Keep going</p><h2>Related</h2>
<p>{chips(r['links'])}</p><p>Other roadmaps: {others} <a class="chip" href="{BASE}">Compare all four</a></p>
<p style="font-size:14px;color:#555">{E(JOB_NOTE)}</p></section>
</div>{TICKS_JS % r['id']}"""
    crumbs = [("Frontier AI roadmaps", f"{SITE}{BASE}"), (r["name"], url)]
    return wb.page(title, desc, url, body, CSS + ld(title, desc, url, crumbs, r["faq"]))


def hub_page():
    url = f"{SITE}{BASE}"
    title = "Frontier AI roadmaps: LLM engineer, inference engineer, AI safety, AI researcher"
    desc = ("Four plain roadmaps for working on frontier AI: LLM engineer, inference engineer, AI safety and security, and AI researcher. "
            "A shared base, eight small steps each, five small projects each, and how to choose.")
    rows = "".join(f'<tr><td><a href="{BASE}{rid}/"><b>{E(n)}</b></a></td><td>{E(what)}</td><td>{E(hard)}</td><td>{E(first)}</td></tr>' for n, what, hard, first, rid in HUB_TABLE)
    table = f'<div class="tw"><table class="t"><tr><th>Role</th><th>What you do</th><th>How hard to enter</th><th>A first project</th></tr>{rows}</table></div>'
    overlap = C.table(["What you learn", "Which roles", "Why it matters"], OVERLAP)
    pick = C.table(["If you say this", "Look at"], PICK)
    base = C.table(["Step", "What to do", "You are done when"], [(f"{i + 1}. {s[0]}", s[1], s[2]) for i, s in enumerate(BASE_STEPS)])
    faq = [("Do I have to pick one role?", "No. The four roles share a base and many skills. Start with the base, then follow the role that matches your answers in the table below. You can switch later without losing the work."),
           ("Which role is easiest to enter?", "LLM engineering and AI safety and security are usually the most reachable with public projects. Inference engineering and research ask for more depth. Check postings in your market, because this is a general pattern."),
           ("How do I get noticed?", "Publish a measured number with code and data, and send it to people who work on the topic. A clear, checkable result opens more doors than a certificate."),
           ("Where do the tools on these pages come from?", "They were checked in November 2026 against a sample of job postings and engineering guides. It is a sample, not a survey, and tools change fast.")]
    body = f"""<p class="crumbs"><a href="/">Home</a> › Frontier AI roadmaps</p>
<p class="eyebrow" style="margin-top:22px">Learn · frontier AI work</p>
<h1>Four roadmaps for working on frontier AI</h1>
<p class="lede">LLM engineer, inference engineer, AI safety and security, AI researcher. Each roadmap is eight small steps and five small projects, written so you can start this week. All four share the same first four weeks.</p>
<div class="fr">
<div class="fig">{draw_hub()}<p>One shared base, then four roles. Click a role box to open its roadmap.</p></div>

<section id="roles"><p class="eyebrow">The four roles</p><h2>What each one does, and where to start</h2>{table}</section>

<section id="pick"><p class="eyebrow">Choosing</p><h2>Which one fits you</h2>
<p>Answer with your gut, not with what pays most. People do their best work in the role they would enjoy on a bad day.</p>{pick}</section>

<section id="base"><p class="eyebrow">Week 0 to 4</p><h2>The base every role shares</h2>
<p>Do these first. Whatever role you choose later, none of this is wasted.</p>{base}</section>

<section id="overlap"><p class="eyebrow">How they connect</p><h2>What the four roles share</h2>
<p>Because so much is shared, choosing is not a one-way door.</p>{overlap}</section>

<section id="how"><p class="eyebrow">How each roadmap works</p><h2>Eight steps, five projects, one number</h2>
<p>Each step has a finish line written as "you are done when". Each project ends in one number you measured, such as a pass rate, a speed or an attack success rate. Publish the number with the code and data, so a stranger can rerun it.</p>
<p>The same shape of work appears across roles. A fair test, a clear number and open code are what people remember.</p></section>

<section id="faq"><p class="eyebrow">FAQ</p><h2>Questions people ask</h2>{C.faq(faq)}</section>

<section id="next"><p class="eyebrow">Related</p><h2>Keep going</h2>
<p>{chips([("Learning path: LLM engineering", "/paths/llm-engineering/"), ("Learning path: AI engineering", "/paths/ai-engineering/"), ("Hard unsolved problems", "/problems/"),
          ("Running AI you can trust", "/learn/ai-governance/"), ("Eval Harness", "/learn/eval-harness/"), ("Which AI model for which job", "/learn/which-model/")])}</p>
<p style="font-size:14px;color:#555">{E(JOB_NOTE)}</p></section>
</div>"""
    crumbs = [("Frontier AI roadmaps", url)]
    return wb.page(title, desc, url, body, CSS + ld(title, desc, url, crumbs, faq))


def main():
    out = ROOT / "learn" / "frontier-ai-roadmaps"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(hub_page())
    for r in ROLES:
        d = out / r["id"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(role_page(r))
    print("frontier roadmaps ->", out, "(hub + 4 roles)")


if __name__ == "__main__":
    main()
