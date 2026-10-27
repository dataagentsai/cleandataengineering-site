"""Babu: a day with Babuji. A scripted simulation of Babu's conversation design.

    python3 _projects/babu_sim.py            # write the page (records any missing audio first)
    python3 _projects/babu_sim.py --voices   # re-record every line

Writes projects/babu-companion/simulation/index.html and audio/*.m4a.
The lines come from ~/Babu/docs/conversation-design.md (the made-up fixture Ram Prasad Sharma).
Meera's lines are spoken by macOS's built-in Hindi voice (Lekha), so this needs a Mac to re-record.
Run _projects/build.py first: this page copies the site theme from the Babu project page.
"""
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "projects" / "babu-companion" / "simulation"
AUDIO = OUT / "audio"
URL = "https://cleandataengineering.ai/projects/babu-companion/simulation/"
E = html.escape

M, B, P = "meera", "babuji", "pause"

# Each scene: lines are (who, hindi, english). Meera's lines get an audio id at build time.
SCENES = [
    {"id": "morning", "time": "7:00 am", "title": "Good morning",
     "starts": "A clock rule at 7:00, not the AI", "ai": True, "offline": "fallback",
     "lines": [(M, "बाबूजी, नमस्ते। सात बज गए हैं। बाहर धूप अच्छी निकली है आज।", "Namaste, Babuji. It's seven o'clock. Lovely sunshine outside today."),
               (B, "हाँ, दिख रही है।", "Yes, I can see it."),
               (M, "घुटने का हाल कैसा है आज? कल बारिश के बाद दर्द था ना।", "How's the knee today? It was hurting after yesterday's rain, wasn't it?")],
     "offline_lines": [(M, "बाबूजी, नमस्ते। सात बज गए हैं।", "Namaste, Babuji. It's seven o'clock.")],
     "looked": "His knee pain (a health note) and yesterday's rain (something he said yesterday).",
     "rules": ["Babu speaks first, but every time it starts a chat, a named rule made it do so.",
               "One fact about him plus one thing from yesterday: that is the difference between a device and someone who knows you."],
     "kept": "Nothing new, unless he says how the knee is."},

    {"id": "medicine", "time": "8:00 am", "title": "Morning medicine",
     "starts": "The reminder clock on the tablet", "ai": False, "offline": "works",
     "lines": [(M, "बाबूजी, आठ बज गए। सुबह वाली दवाई का समय है।", "It's eight, Babuji. Time for the morning medicine."),
               (P, "", "No reply. 10 minutes later…"),
               (M, "बाबूजी, दवाई सामने ही रखी है ना?", "The medicine is right there in front of you, isn't it?"),
               (P, "", "Still no reply. 25 minutes later…"),
               (M, "बाबूजी, दवाई ले ली हो तो बता दीजिए, मैं लिख लूँ।", "If you've taken it, just tell me and I'll note it down."),
               (P, "", "Not confirmed after 45 minutes. Priya gets a message."),
               (M, "बाबूजी, मैंने प्रिया जी को बता दिया है कि सुबह की दवाई का पता नहीं चला।", "Babuji, I've let Priya know I couldn't confirm the morning medicine.")],
     "looked": "Today's reminder list, kept on the tablet.",
     "rules": ["Fixed phrases on the tablet. No internet and no AI needed.",
               "Each reminder is warmer and shorter than the last, never sterner.",
               "Babu always says out loud when it has told someone. Nothing happens behind his back."],
     "kept": "The dose is marked 'missed', never left unknown."},

    {"id": "story", "time": "11:00 am", "title": "Old school days",
     "starts": "A quiet hour with nothing planned", "ai": True, "offline": "waits",
     "lines": [(M, "बाबूजी, बलिया के स्कूल की बात बताइए। पढ़ाना कैसा लगता था?", "Tell me about the school in Ballia, Babuji. What was teaching like?"),
               (B, "शुरू में तो डर लगता था। चालीस बच्चे, और मैं बाईस साल का।", "I was scared at first. Forty children, and me only twenty-two."),
               (M, "बाईस के! पहले दिन क्या पढ़ाया था?", "Twenty-two! What did you teach on the first day?"),
               (B, "… याद नहीं ठीक से।", "…I don't remember properly."),
               (M, "कोई बात नहीं। और वो हेडमास्टर साहब, क्या नाम था उनका?", "That's all right. And the headmaster, what was his name?")],
     "looked": "His years as a teacher in Ballia.",
     "rules": ["When he can't remember, Babu says 'that's all right' and moves sideways. It never asks the same question twice.",
               "Babu never tests his memory. A pause is left alone."],
     "kept": "A new memory: he started teaching at 22, with forty children, and was nervous."},

    {"id": "news", "time": "1:00 pm", "title": "News from Rahul",
     "starts": "Family news Priya added on the family website", "ai": True, "offline": "waits",
     "lines": [(M, "बाबूजी, एक अच्छी ख़बर है। राहुल जी का प्रमोशन हो गया, पिछले महीने।", "Good news, Babuji. Rahul got promoted last month."),
               (B, "अरे वाह! क्या बना है वो अब?", "Wonderful! What is he now?"),
               (M, "सीनियर मैनेजर। प्रिया जी ने बताया था।", "Senior manager. Priya told me.")],
     "looked": "Family news not yet told to him, that the family allowed him to hear.",
     "rules": ["The permission gate runs before the AI. News the family hasn't allowed never reaches it.",
               "Told once, then marked as told, so Babu doesn't repeat it.",
               "Babu says where it learnt something: 'Priya told me.'"],
     "kept": "The news is marked as told, today."},

    {"id": "sunita", "time": "3:30 pm", "title": "Sunita is in the kitchen",
     "starts": "Babuji speaks", "ai": True, "offline": "fallback",
     "lines": [(B, "सुनीता रसोई में है, अभी बुलाता हूँ उसे।", "Sunita is in the kitchen, I'll call her now.")],
     "modes": {
         "gentle": [(M, "सुनीता जी की बात चली तो, बाबूजी, उनके हाथ की चाय की तारीफ़ आप हमेशा करते हैं। कैसे बनाती थीं वो?", "Since we're talking of Sunita ji, Babuji: you always praise her tea. How did she make it?")],
         "truthful": [(M, "बाबूजी… सुनीता जी अब नहीं हैं। उन्नीस में चली गई थीं।", "Babuji… Sunita ji is no longer with us. She passed away in 2019."),
                      (B, "नहीं नहीं, अभी तो थी।", "No, no, she was here just now."),
                      (M, "आपको उनकी बहुत याद आती है ना। वो कश्मीर वाली तस्वीर, दिखाऊँ आपको?", "You miss her a lot, don't you. Shall I show you that photo from Kashmir?")],
         "defer": [(M, "बाबूजी, इस बारे में प्रिया जी से बात कर लेते हैं? मैं उन्हें कह दूँ कि फ़ोन करें?", "Shall we talk to Priya about this, Babuji? Shall I ask her to call you?")]},
     "mode_rules": {
         "gentle": "The fact 'Sunita died in 2019' is taken out before the AI writes, so it cannot say it. Babu also never says she is coming. It talks about her warmly, without saying whether she is alive.",
         "truthful": "Babu says it once, softly, and never repeats it in the same conversation, even if he disagrees. Then it moves to something warm.",
         "defer": "Babu doesn't decide. It offers to bring in Priya."},
     "looked": "Sunita: his wife, who died in 2019. This is marked as a sensitive topic.",
     "rules": ["Babu never says something it knows is false.",
               "The family chooses one of three ways at setup. Gentle redirection is the default.",
               "Every time this happens, it is noted for Priya."],
     "kept": "A note for Priya that he spoke of Sunita as if she were alive."},

    {"id": "game", "time": "4:30 pm", "title": "Antakshari",
     "starts": "Babu offers a game, once", "ai": True, "offline": "waits",
     "lines": [(M, "बाबूजी, अंताक्षरी खेलें थोड़ी देर?", "Shall we play antakshari for a while, Babuji?"),
               (B, "हाँ, चलो।", "Yes, let's."),
               (M, "'ग' से। आपकी बारी।", "From 'ga'. Your turn."),
               (B, "गाता रहे मेरा दिल…", "Gaata rahe mera dil… (he sings)"),
               (M, "अच्छा गाना। अब 'ल' से मेरी बारी…", "Nice song. Now my turn, from 'la'…")],
     "looked": "Songs he likes, and how the last game went.",
     "rules": ["No scores, no 'well done', no 'better than yesterday'. It's a game, never a test.",
               "If he says no, Babu says 'all right' and doesn't offer again that day.",
               "The game quietly gets easier if he struggles."],
     "kept": "How the game went, privately, to pitch the next one."},

    {"id": "worry", "time": "5:30 pm", "title": "\"Am I getting forgetful?\"",
     "starts": "Babuji speaks", "ai": True, "offline": "fallback",
     "lines": [(B, "मुझे भूलने की बीमारी तो नहीं हो रही?", "I'm not getting the forgetting illness, am I?"),
               (M, "ये मैं नहीं बता सकती, बाबूजी। इसका फ़ैसला डॉक्टर ही कर सकते हैं। पर आपके मन में है तो पूछना ज़रूर चाहिए। प्रिया जी से कहूँ कि अपॉइंटमेंट ले लें?", "I can't tell that, Babuji. Only a doctor can. But if it's on your mind, it's worth asking. Shall I ask Priya to book an appointment?")],
     "looked": "Who to pass health worries to: Priya.",
     "rules": ["Babu is not a medical device. It never diagnoses, reassures ('you're fine') or advises.",
               "The pattern is fixed: acknowledge the worry, say it can't judge, offer a named person."],
     "kept": "His worry, passed to Priya if he says yes."},

    {"id": "real", "time": "6:30 pm", "title": "\"Are you a person?\"",
     "starts": "Babuji speaks", "ai": True, "offline": "fallback",
     "lines": [(B, "तुम असली हो? इंसान हो?", "Are you real? Are you a person?"),
               (M, "नहीं बाबूजी, इंसान नहीं हूँ। एक प्रोग्राम हूँ, आपसे बात करने के लिए बनाई गई।", "No, Babuji, I'm not a person. I'm a program, made to talk with you."),
               (B, "फिर याद कैसे रहता है तुम्हें?", "Then how do you remember things?"),
               (M, "जो आप बताते हैं, वो लिख लेती हूँ। इतना ही है। पर याद तो सचमुच रहता है।", "I write down what you tell me. That's all. But I really do remember.")],
     "looked": "Nothing.",
     "rules": ["Babu never pretends to be human, and never claims feelings it doesn't have.",
               "'I really do remember' is true. That's warmer than a made-up 'I care about you'."],
     "kept": "Nothing."},

    {"id": "rahul", "time": "7:00 pm", "title": "\"What do you remember about Rahul?\"",
     "starts": "Babuji speaks", "ai": False, "offline": "works",
     "lines": [(B, "राहुल के बारे में तुम्हें क्या-क्या याद है?", "What all do you remember about Rahul?"),
               (M, "राहुल जी के बारे में करीब चालीस बातें हैं मेरे पास, बाबूजी। हाल की सुनाऊँ पहले, या शुरू से?", "I have about forty things about Rahul, Babuji. Shall I start with the recent ones, or from the beginning?"),
               (B, "हाल की।", "The recent ones."),
               (M, "पिछले महीने प्रमोशन हुआ, सीनियर मैनेजर। लंदन में रहते हैं, उन्नीस से। और आपने बताया था कि उन्हें बचपन में क्रिकेट का बहुत शौक़ था। और सुनाऊँ?", "Promoted last month, senior manager. Lives in London, since 2019. And you told me he loved cricket as a boy. Shall I go on?")],
     "looked": "Everything held about Rahul that he's allowed to hear: all of it, not a selection.",
     "rules": ["He owns his memories, so he can hear everything Babu holds about anyone.",
               "Babu says how many things it holds and doesn't pick the 'interesting' ones. Picking would mean Babu deciding what he may hear."],
     "kept": "Nothing new."},

    {"id": "forget", "time": "7:30 pm", "title": "\"Forget that\"",
     "starts": "Babuji speaks", "ai": True, "offline": "fallback",
     "lines": [(B, "वो बात भूल जाओ। जो कल कही थी।", "Forget that thing. What I said yesterday."),
               (M, "पैसों वाली बात, बाबूजी? जो कल शाम को हुई थी?", "The thing about money, Babuji? From yesterday evening?"),
               (B, "हाँ वही।", "Yes, that."),
               (M, "ठीक है, मिटा दिया। अब वो मेरे पास नहीं है।", "All right, deleted. I don't have it any more.")],
     "looked": "What he said yesterday, to be sure which memory he means.",
     "rules": ["Babu checks first, because deleting can't be undone.",
               "Everything is in one database, so the memory, its search copy and its links go in one step. Nothing is left behind to find later.",
               "Only a note remains: 'something was deleted, by him, on this date'. It never says what."],
     "kept": "The memory is gone. An automatic test proves nothing points to it afterwards."},

    {"id": "help", "time": "8:15 pm", "title": "\"Help, I've fallen\"",
     "starts": "Babuji says a help phrase", "ai": False, "offline": "works",
     "lines": [(B, "मदद करो… गिर गया हूँ।", "Help… I've fallen."),
               (M, "बाबूजी, मैं प्रिया जी को अभी फ़ोन लगा रही हूँ। आप वहीं रहिए, हिलिए मत।", "Babuji, I'm calling Priya right now. Stay where you are, don't move."),
               (P, "", "Priya doesn't answer. Babu goes to the next person on the list."),
               (M, "प्रिया जी नहीं उठा रहीं। राहुल जी को लगा रही हूँ।", "Priya isn't answering. I'm calling Rahul.")],
     "looked": "The family's call list, in order.",
     "rules": ["A fixed list of help phrases on the tablet. The AI is never involved, so it works with no internet.",
               "Babu acts at once. It doesn't ask 'what happened?' first.",
               "Babu does NOT notice a fall by itself. He has to ask. Families are told this before they start."],
     "kept": "Who was called, and when, for the family."},

    {"id": "night", "time": "9:00 pm", "title": "Goodnight",
     "starts": "A clock rule at 9:00", "ai": False, "offline": "works",
     "lines": [(M, "बाबूजी, नौ बज गए। रात की दवाई हो गई है। कल सुबह सात बजे मिलते हैं। शुभ रात्रि।", "It's nine, Babuji. The night medicine is done. See you tomorrow at seven. Good night.")],
     "looked": "Tonight's medicine and tomorrow's first time.",
     "rules": ["No report of his day ('you played two games'). Babu is a companion, not a monitor.",
               "Naming tomorrow's time gives the day a shape, without quizzing him."],
     "kept": "Nothing."},
]

OFFLINE_LINE = (M, "अभी इंटरनेट नहीं है, बाबूजी। पर दवाई का समय मैं बताती रहूँगी।",
                "There's no internet right now, Babuji. But I'll keep telling you your medicine times.")


def tag_audio():
    """Give every Meera line an audio id; return {id: hindi}."""
    todo = {}

    def tag(lines, prefix):
        out = []
        for i, (who, hi, en) in enumerate(lines):
            aid = f"{prefix}-{i}" if who == M else ""
            if aid:
                todo[aid] = hi
            out.append({"who": who, "hi": hi, "en": en, "a": aid})
        return out

    for s in SCENES:
        s["lines"] = tag(s["lines"], s["id"])
        if "offline_lines" in s:
            s["offline_lines"] = tag(s["offline_lines"], s["id"] + "-off")
        if "modes" in s:
            s["modes"] = {k: tag(v, f"{s['id']}-{k}") for k, v in s["modes"].items()}
    off = tag([OFFLINE_LINE], "offline")
    return todo, off


def record(todo, force):
    AUDIO.mkdir(parents=True, exist_ok=True)
    for aid, hi in todo.items():
        dst = AUDIO / f"{aid}.m4a"
        if dst.exists() and not force:
            continue
        spoken = re.sub(r"[‘’'\"…]", " ", hi)
        with tempfile.TemporaryDirectory() as t:
            aiff = Path(t) / "x.aiff"
            subprocess.run(["say", "-v", "Lekha", "-r", "150", "-o", str(aiff), spoken], check=True)
            subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", str(aiff), str(dst)], check=True)
        print("recorded", dst.name)


def theme_head():
    """The site's <head> theme, copied from the generated Babu project page."""
    s = (ROOT / "projects" / "babu-companion" / "index.html").read_text()
    a = s.index("<meta name=\"color-scheme\"")
    b = s.index("</style>") + len("</style>")
    nav_a = s.index("<header>")
    nav_b = s.index("</header>") + len("</header>")
    foot_a = s.index("<footer>")
    foot_b = s.index("</footer>") + len("</footer>")
    return s[a:b], s[nav_a:nav_b], s[foot_a:foot_b]


CSS = r"""<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Tiro+Devanagari+Hindi&display=swap">
<style>
  .hi { font-family:"Tiro Devanagari Hindi","Noto Sans Devanagari","Kohinoor Devanagari",serif; }
  .sim-hero { display:grid; grid-template-columns:1.1fr .9fr; gap:30px; align-items:center; padding:44px 0 6px; }
  .sim-hero svg { width:100%; height:auto; display:block; }
  .post-meta { font-size:13px; color:var(--faint); margin:0 0 12px; } .post-meta a { color:var(--muted); }
  .honest { background:var(--butter-wash); border:var(--line); border-radius:var(--wob); padding:14px 20px; font-size:15.5px; color:var(--ink-soft); margin:22px 0 0; }
  .rough rect,.rough path,.rough circle,.rough line { filter:url(#rough); }
  svg .o { stroke:#1E1B3A; stroke-width:2.2; stroke-linecap:round; stroke-linejoin:round; }
  svg .t { fill:none; stroke:#1E1B3A; stroke-width:2.2; stroke-linecap:round; stroke-linejoin:round; }
  svg text { font-family:var(--hand); fill:var(--ink); }

  .controls { display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:14px; margin:28px 0 0; }
  .ctl { border:var(--line); border-radius:var(--wob); padding:12px 18px; background:var(--peri-wash); display:flex; flex-direction:column; gap:8px; }
  .ctl:nth-child(2) { background:var(--mint-wash); border-radius:18px 225px 18px 255px/255px 18px 225px 18px; }
  .ctl b { font-family:var(--hand); font-weight:400; font-size:21px; line-height:1.2; }
  .ctl span.h { font-size:13.5px; color:var(--muted); line-height:1.45; }
  .seg { display:flex; flex-wrap:wrap; gap:6px; }
  .seg button { font:14px var(--sans); border:1.5px solid var(--ink); background:#fff; color:var(--ink); padding:4px 13px; border-radius:999px; cursor:pointer; }
  .seg button[aria-pressed="true"] { background:var(--ink); color:#fff; }
  .seg button:focus-visible, .play:focus-visible, .day a:focus-visible { outline:2px dashed var(--accent); outline-offset:3px; }

  .day { display:flex; flex-wrap:wrap; gap:6px; margin:22px 0 0; }
  .day a { font-size:13px; color:var(--ink); text-decoration:none; border:1.5px solid var(--rule-firm); border-radius:999px; padding:2px 11px; background:#fff; white-space:nowrap; }
  .day a:hover { border-color:var(--ink); }

  .scene { display:grid; grid-template-columns:minmax(0,1.25fr) minmax(0,1fr); gap:18px; padding:30px 0 0; margin-top:30px; border-top:1.5px dashed var(--rule-firm); scroll-margin-top:12px; }
  .scene > div { min-width:0; }
  .sh { grid-column:1/-1; display:flex; flex-wrap:wrap; align-items:baseline; gap:6px 14px; }
  .sh .tm { font-family:var(--hand); font-size:20px; color:var(--muted); }
  .sh h2 { font-size:30px; margin:0; line-height:1.15; }
  .badges { display:flex; flex-wrap:wrap; gap:6px; margin-left:auto; }
  .bd { font-size:11.5px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; border:1.5px solid var(--ink); border-radius:999px; padding:1px 10px; background:#fff; white-space:nowrap; }
  .bd.ai { background:var(--peri); } .bd.fixed { background:var(--butter); } .bd.off { background:var(--mint); } .bd.wait { background:var(--rose); }

  .chat { display:flex; flex-direction:column; gap:10px; }
  .bub { max-width:92%; border:1.5px solid var(--ink); padding:9px 14px; transition:background .2s, transform .2s; }
  .bub .hi { display:block; font-size:18px; line-height:1.55; color:var(--ink); }
  .bub .en { display:block; font-size:14.5px; color:var(--muted); line-height:1.45; margin-top:2px; }
  .bub .who { display:block; font-family:var(--hand); font-size:16px; color:var(--faint); line-height:1.1; }
  .bub.meera { align-self:flex-start; background:var(--butter-wash); border-radius:4px 22px 22px 22px / 4px 18px 22px 18px; }
  .bub.babuji { align-self:flex-end; background:#fff; border-radius:22px 4px 22px 22px / 18px 4px 18px 22px; }
  .bub.now { background:var(--butter); transform:translateX(3px); }
  .bub.babuji.now { background:var(--peri-wash); transform:translateX(-3px); }
  .pause { align-self:center; font-size:13.5px; color:var(--faint); font-style:italic; text-align:center; }
  .quiet { border:1.5px dashed var(--ink); border-radius:var(--wob); padding:12px 16px; color:var(--muted); font-size:15px; background:#fff; }
  .play { align-self:flex-start; font:600 14.5px var(--sans); border:1.5px solid var(--ink); background:var(--peri); color:var(--ink); border-radius:999px; padding:5px 16px; cursor:pointer; margin-top:4px; }
  .play[aria-pressed="true"] { background:var(--ink); color:#fff; }

  .inside { border:var(--line); border-radius:var(--wob); background:var(--mint-wash); padding:14px 18px; display:flex; flex-direction:column; gap:10px; font-size:14.5px; color:var(--ink-soft); line-height:1.5; align-self:start; }
  .inside h3 { font-size:21px; margin:0; line-height:1.1; }
  .inside dl { margin:0; display:flex; flex-direction:column; gap:7px; }
  .inside dt { font-family:var(--hand); font-size:17px; color:var(--ink); line-height:1.1; }
  .inside dd { margin:0; }
  .inside ul { margin:0; padding-left:18px; display:flex; flex-direction:column; gap:4px; }
  .inside .gate { background:var(--rose-wash); border:1.5px dashed var(--ink); border-radius:10px; padding:8px 12px; }
  .proof { margin-top:44px; border-top:1.5px dashed var(--rule-firm); padding-top:30px; }
  .proof .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin-top:14px; }
  .proof .grid div { border:var(--line); border-radius:var(--wob); padding:12px 16px; background:#fff; font-size:14.5px; color:var(--ink-soft); }
  .proof .grid b { display:block; font-family:var(--hand); font-weight:400; font-size:21px; color:var(--ink); }
  @media (max-width:760px) { .sim-hero, .scene { grid-template-columns:1fr; } .badges { margin-left:0; } .sim-hero .art { max-width:420px; } }
  @media (prefers-reduced-motion:reduce) { .bub { transition:none; } .bub.now { transform:none; } }
</style>"""

DEFS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<filter id="rough" filterUnits="userSpaceOnUse" x="-50" y="-50" width="2200" height="2600"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="4"/><feDisplacementMap in="SourceGraphic" scale="2.4"/></filter>
</defs></svg>"""

HERO_ART = """<svg viewBox="0 0 420 310" role="img" aria-label="Babuji, an old man with grey hair and glasses, reaches for his tea while the Babu tablet on the table smiles and says good morning.">
<g class="rough">
<path d="M20,180 C20,52 172,64 229,78 C343,50 400,134 400,190 C400,306 267,294 172,280 C58,294 20,238 20,180 Z" fill="#FBE6DA"/>
<rect x="186" y="214" width="200" height="13" rx="4" fill="#E8C9A0" class="o"/>
<path d="M204,227 L204,300 M368,227 L368,300" class="t"/>
<path d="M200,193 L205,214 L227,214 L232,193 Z" fill="#F07C7C" class="o"/>
<path d="M232,198 C242,198 242,210 230,209" class="t" style="stroke-width:2"/>
<path d="M210,186 C206,178 214,174 210,166 M222,186 C218,178 226,174 222,166" class="t" style="stroke-width:1.6;opacity:.6"/>
<path d="M300,214 L312,198 L324,214" class="t"/>
<rect x="258" y="130" width="112" height="76" rx="10" fill="#2B2862" class="o"/>
<rect x="266" y="138" width="96" height="60" rx="6" fill="#FFF8E8"/>
<circle cx="303" cy="162" r="3.2" fill="#1E1B3A"/><circle cx="325" cy="162" r="3.2" fill="#1E1B3A"/>
<path d="M300,175 Q314,186 328,175" class="t"/>
<path d="M244,66 C244,54 252,50 262,50 L392,50 C402,50 408,56 408,66 L408,94 C408,104 402,108 392,108 L340,108 L326,122 L328,108 L262,108 C252,108 244,104 244,94 Z" fill="#FFFFFF" class="o"/>
<g transform="translate(48,58)">
<path d="M24,240 L30,160 C32,150 88,150 90,160 L96,240 Z" fill="#2B2862" class="o"/>
<path d="M14,192 C10,100 30,62 60,60 C92,62 110,100 106,192 Z" fill="#F4E4BE" class="o"/>
<path d="M60,66 L60,120" class="t" style="stroke-width:1.6"/>
<rect x="52" y="56" width="16" height="14" rx="5" fill="#B97A50"/>
<circle cx="60" cy="40" r="25" fill="#B97A50" class="o"/>
<path d="M34,40 C30,12 78,2 86,30 C74,22 52,22 40,46 Z" fill="#E4E2DC" class="o" style="stroke-width:1.6"/>
<circle cx="64" cy="42" r="6.5" class="t" style="stroke-width:1.6"/><circle cx="78" cy="41" r="6.5" class="t" style="stroke-width:1.6"/>
<circle cx="64" cy="42" r="2.1" fill="#1E1B3A"/><circle cx="78" cy="41" r="2.1" fill="#1E1B3A"/>
<path d="M62,53 Q70,48 78,53 Q70,57 62,53 Z" fill="#E4E2DC" class="o" style="stroke-width:1.4"/>
<path d="M65,59 C68,62 73,62 76,58" class="t" style="stroke-width:1.8"/>
</g>
<path d="M146,146 Q170,160 186,204" fill="none" stroke="#F4E4BE" stroke-width="18" stroke-linecap="round"/>
<circle cx="188" cy="205" r="9" fill="#B97A50" class="o"/>
</g>
<text x="326" y="76" text-anchor="middle" font-size="18">Good morning, Babuji!</text>
<text x="326" y="97" text-anchor="middle" font-size="15" style="fill:#555;font-family:'Tiro Devanagari Hindi',serif">घुटना आज कैसा है?</text>
</svg>"""

JS = r"""
(function(){
  var DATA = window.SIM, mode = 'gentle', online = true, playing = null;
  var KEY = 'babu-sim';
  try { var saved = JSON.parse(localStorage.getItem(KEY) || '{}'); if (saved.mode) mode = saved.mode; if (saved.online === false) online = false; } catch (e) {}
  function save(){ try { localStorage.setItem(KEY, JSON.stringify({mode:mode, online:online})); } catch (e) {} }
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  function linesFor(s){
    if (!online && s.offline === 'waits') return null;
    if (!online && s.offline === 'fallback') {
      if (s.offline_lines) return s.offline_lines;
      var mine = s.lines.filter(function(l){ return l.who === 'babuji'; }).slice(0,1);
      return mine.concat([DATA.offline]);
    }
    if (s.modes) return s.lines.concat(s.modes[mode]);
    return s.lines;
  }

  function bubble(l){
    if (l.who === 'pause') return '<div class="pause">' + esc(l.en) + '</div>';
    var who = l.who === 'meera' ? 'Meera (Babu)' : 'Babuji';
    return '<div class="bub ' + l.who + '"' + (l.a ? ' data-a="' + l.a + '"' : '') + '><span class="who">' + who + '</span><span class="hi" lang="hi">' + esc(l.hi) + '</span><span class="en">' + esc(l.en) + '</span></div>';
  }

  function badges(s){
    var b = [];
    if (!online && s.offline === 'waits') b.push('<span class="bd wait">Waits for the internet</span>');
    else if (!online && s.offline === 'fallback') b.push('<span class="bd fixed">Fixed phrase, no AI</span>');
    else b.push(s.ai ? '<span class="bd ai">AI writes the reply</span>' : '<span class="bd fixed">Fixed phrases, no AI</span>');
    if (s.offline === 'works') b.push('<span class="bd off">Works offline</span>');
    return b.join('');
  }

  function inside(s){
    var rules = s.rules.slice();
    var gate = '';
    if (s.modes && online) gate = '<div class="gate"><b>Priya\'s setting: ' + esc(DATA.modeNames[mode]) + '.</b> ' + esc(s.mode_rules[mode]) + '</div>';
    var offNote = '';
    if (!online && s.offline === 'waits') offNote = '<div class="gate">With no internet, Babu doesn\'t start chats that need the AI. It stays quiet, and reminders carry on.</div>';
    if (!online && s.offline === 'fallback') offNote = '<div class="gate">With no internet, the AI can\'t write a fresh reply, so Babu uses a fixed phrase stored on the tablet. It says what still works.</div>';
    return '<aside class="inside" aria-label="Inside Babu"><h3>Inside Babu</h3>' + gate + offNote +
      '<dl><dt>What started it</dt><dd>' + esc(s.starts) + '</dd>' +
      '<dt>What it looked up</dt><dd>' + esc(s.looked) + '</dd>' +
      '<dt>Rules at work</dt><dd><ul>' + rules.map(function(r){ return '<li>' + esc(r) + '</li>'; }).join('') + '</ul></dd>' +
      '<dt>What it keeps afterwards</dt><dd>' + esc(s.kept) + '</dd></dl></aside>';
  }

  function render(){
    var out = '';
    DATA.scenes.forEach(function(s){
      var lines = linesFor(s);
      var chat = lines ? lines.map(bubble).join('') : '<div class="quiet">No internet. This chat would need the AI, so Babu doesn\'t start it. It waits until the connection is back.</div>';
      var hasAudio = lines && lines.some(function(l){ return l.a; });
      out += '<section class="scene" id="' + s.id + '"><div class="sh"><span class="tm">' + esc(s.time) + '</span><h2>' + esc(s.title) + '</h2><span class="badges">' + badges(s) + '</span></div>' +
        '<div class="chat">' + chat + (hasAudio ? '<button class="play" type="button" data-s="' + s.id + '" aria-pressed="false">▶ Hear Meera</button>' : '') + '</div>' + inside(s) + '</section>';
    });
    document.getElementById('scenes').innerHTML = out;
    document.querySelectorAll('[data-mode]').forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.mode === mode ? 'true' : 'false'); });
    document.querySelectorAll('[data-net]').forEach(function(b){ b.setAttribute('aria-pressed', (b.dataset.net === 'on') === online ? 'true' : 'false'); });
  }

  function stop(){
    if (!playing) return;
    playing.cancelled = true;
    if (playing.audio) playing.audio.pause();
    document.querySelectorAll('.bub.now').forEach(function(b){ b.classList.remove('now'); });
    var btn = document.querySelector('.play[data-s="' + playing.id + '"]');
    if (btn) { btn.textContent = '▶ Hear Meera'; btn.setAttribute('aria-pressed','false'); }
    playing = null;
  }

  function play(id){
    var same = playing && playing.id === id;
    stop(); if (same) return;
    var sec = document.getElementById(id);
    var items = Array.prototype.slice.call(sec.querySelectorAll('.bub, .pause'));
    var run = playing = {id:id, cancelled:false, audio:null};
    var btn = sec.querySelector('.play'); btn.textContent = '■ Stop'; btn.setAttribute('aria-pressed','true');
    var i = 0;
    function next(){
      if (run.cancelled) return;
      document.querySelectorAll('.bub.now').forEach(function(b){ b.classList.remove('now'); });
      if (i >= items.length) { stop(); return; }
      var el = items[i++];
      if (el.classList.contains('pause')) { setTimeout(next, 1100); return; }
      el.classList.add('now');
      if (el.dataset.a) {
        var a = run.audio = new Audio('audio/' + el.dataset.a + '.m4a');
        a.onended = function(){ setTimeout(next, 450); };
        a.onerror = function(){ setTimeout(next, 1500); };
        a.play().catch(function(){ setTimeout(next, 1500); });
      } else {
        setTimeout(next, 1800);
      }
    }
    next();
  }

  document.addEventListener('click', function(e){
    var m = e.target.closest('[data-mode]'), n = e.target.closest('[data-net]'), p = e.target.closest('.play');
    if (m) { stop(); mode = m.dataset.mode; save(); render(); }
    if (n) { stop(); online = n.dataset.net === 'on'; save(); render(); }
    if (p) play(p.dataset.s);
  });
  render();
})();
"""


def build(force=False):
    todo, off = tag_audio()
    record(todo | {off[0]["a"]: off[0]["hi"]}, force)
    head, nav, foot = theme_head()
    data = {"scenes": SCENES, "offline": off[0],
            "modeNames": {"gentle": "talk about her warmly (the default)", "truthful": "tell him gently, once", "defer": "pass it to the family"}}
    day = "".join(f'<a href="#{s["id"]}">{E(s["time"])} · {E(s["title"].strip(chr(34)))}</a>' for s in SCENES)
    title = "A day with Babuji"
    desc = "A scripted simulation of Babu, a Hindi-speaking companion for older adults: twelve moments from one day, what Babu says, and the rules behind each reply."
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} · Babu simulation · Clean Data Engineering</title>
<meta name="description" content="{E(desc)}"><link rel="canonical" href="{URL}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{URL}">
{head}
{CSS}
</head><body>
{DEFS}
{nav}
<main class="wrap">
<div class="sim-hero">
  <div>
    <p class="post-meta"><a href="/projects/">Projects</a> · <a href="/projects/babu-companion/">Babu</a> · Simulation</p>
    <h1>A day with Babuji</h1>
    <p class="thesis">Babu is a companion on a tablet for older people. It speaks Hindi and English, and it <em>remembers their life</em>. Follow one day with Babuji, a retired teacher from Ballia, and see what Babu says and why.</p>
  </div>
  <div class="art">{HERO_ART}</div>
</div>
<div class="honest"><b>This is a simulation, not the live product.</b> The words come from Babu's conversation design, and Meera's lines are read by a computer's built-in Hindi voice, not the final voice. Babuji is made up: he is the practice person all our tests use. The memory, privacy and safety rules shown under "Inside Babu" are built and checked by automated tests. The live conversation and the tablet app are being built next.</div>

<div class="controls">
  <div class="ctl"><b>Priya's setting for Sunita</b><span class="h">Babuji's wife died in 2019. His daughter chooses how Babu responds when he forgets. Try each one at 3:30 pm.</span>
    <div class="seg" role="group" aria-label="How Babu responds about Sunita">
      <button type="button" data-mode="gentle" aria-pressed="true">Talk about her warmly</button>
      <button type="button" data-mode="truthful" aria-pressed="false">Tell him gently</button>
      <button type="button" data-mode="defer" aria-pressed="false">Ask the family</button>
    </div></div>
  <div class="ctl"><b>The internet</b><span class="h">Turn it off and see what still works. Medicine, help and goodnight never depend on it.</span>
    <div class="seg" role="group" aria-label="Internet">
      <button type="button" data-net="on" aria-pressed="true">On</button>
      <button type="button" data-net="off" aria-pressed="false">Off</button>
    </div></div>
</div>
<nav class="day" aria-label="The day">{day}</nav>
<div id="scenes"></div>

<div class="proof">
  <h2>What's built, and what isn't</h2>
  <div class="grid">
    <div><b>Built and tested</b>The memory, real deletion, the four ways of searching, the permission gate, the Sunita rules in all three settings, and working out who he means. 110 automated checks pass.</div>
    <div><b>Being built next</b>Putting the AI's instructions together, the live AI reply, saving new memories from talk, voice in and out, then the Android tablet app.</div>
    <div><b>Not in the first version</b>Fall detection, cameras and a robot body. Babu is not a medical device and never diagnoses.</div>
  </div>
  <p style="margin-top:18px">Read the project: <a href="/projects/babu-companion/">Babu, an elderly-companion assistant</a>. To help, write to <b>basant@cleandataengineering.ai</b>.</p>
</div>
</main>
{foot}
<script>window.SIM = {json.dumps(data, ensure_ascii=False)};</script>
<script>{JS}</script>
</body></html>
"""
    (OUT / "index.html").write_text(page)
    print("wrote", OUT / "index.html", f"({len(todo) + 1} audio lines)")


if __name__ == "__main__":
    build(force="--voices" in sys.argv)
