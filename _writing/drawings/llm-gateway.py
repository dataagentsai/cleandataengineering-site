"""Drawings for 'The LLM gateway: the switch between your agent and every model'. Globals kit, figure, E, ROOT are injected."""


def drawing_gw_switchboard():
    b, t = kit.box, kit.text
    apps = [("Support agent", "bx"), ("Claims agent", "bx"), ("Analyst notebook", "bxm")]
    models = [("Groq", "bx"), ("Azure OpenAI", "bx"), ("Bedrock", "bx")]
    d = t(500, 24, "every app plugs into one board; the board decides which line each call goes out on", "sm", "middle")
    jl = [(350, 105), (350, 175), (350, 245)]
    jr = [(650, 105), (650, 175), (650, 245)]
    for i, (n, k) in enumerate(apps):
        y = 70 + i * 70
        d += b(20, y, 200, 56, n, (), k)
        d += f'<line class="ln" x1="222" y1="{y + 28}" x2="{jl[i][0] - 12}" y2="{jl[i][1]}"/>'
    for i, (n, k) in enumerate(models):
        y = 70 + i * 70
        d += b(780, y, 200, 56, n, (), k)
        d += f'<line class="ln" x1="{jr[i][0] + 12}" y1="{jr[i][1]}" x2="778" y2="{y + 28}"/>'
    # the switchboard cabinet
    d += '<rect class="hz" x="330" y="60" width="340" height="215" rx="10"/>'
    d += '<rect class="pf pf-solid" x="345" y="285" width="310" height="22" rx="4"/><rect class="hz" x="340" y="280" width="320" height="22" rx="4"/>'
    for x, y in jl + jr:
        d += f'<circle class="hz" cx="{x}" cy="{y}" r="10"/><circle class="hk" cx="{x}" cy="{y}" r="4"/>'
    # patch cords
    d += '<path class="lnc" d="M350,105 Q500,150 650,175" fill="none"/>'
    d += '<path class="lnc" d="M350,175 Q500,215 650,105" fill="none"/>'
    d += '<path class="lnc" d="M350,245 Q500,290 650,245" fill="none"/>'
    d += t(500, 82, "THE GATEWAY", "lbl", "middle")
    # a little operator with a headset
    d += ('<circle class="bx" cx="500" cy="338" r="13"/><path class="ln" d="M486,334 Q500,312 514,334" fill="none"/>'
          '<circle class="hk" cx="486" cy="338" r="3"/><line class="lnc" x1="500" y1="351" x2="500" y2="372"/>'
          '<line class="lnc" x1="500" y1="358" x2="478" y2="345"/><line class="lnc" x1="500" y1="358" x2="522" y2="345"/>')
    d += t(120, 300, "your apps and agents", "sm", "middle") + t(880, 300, "the model providers", "sm", "middle")
    return figure(1000, 385, d, "An old telephone switchboard. On the left a support agent, a claims agent and an analyst notebook are plugged in. On the right are three providers: Groq, Azure OpenAI and Bedrock. Patch cords inside the board connect each app to a provider, and a small operator with a headset sits at the board.",
                  "The gateway as a switchboard. Apps never dial a provider directly; they plug into the board.")


def drawing_gw_one_call():
    b, a, t, n = kit.box, kit.arrow, kit.text, kit.num
    d = b(10, 60, 120, 80, "The app", "one call", "bxm")
    row1 = [("Key check", ["whose call is it?", "401 if unknown"]), ("Allow-list", ["approved model?", "403 if not"]),
            ("Rate limit", ["30 calls a minute", "429, wait, retry"]), ("Cache", ["asked before?", "answer, $0"])]
    row2 = [("Screen", ["jailbreak and harm", "on prompt and answer"]), ("Route", ["pick the provider,", "add its key"]),
            ("Log cost", ["who, which model,", "tokens, rupees"])]
    xs = [150, 360, 570, 780]
    d += a(132, 100, 148, 100)
    for i, (title, sub) in enumerate(row1):
        x = xs[i]
        d += b(x, 50, 190, 100, title, sub, "bxs" if i < 3 else "bx") + n(x + 6, 50, i + 1)
        if i < 3:
            d += a(x + 192, 100, x + 208, 100)
    d += a(875, 152, 875, 208)
    for i, (title, sub) in enumerate(row2):
        x = xs[3 - i]
        d += b(x, 210, 190, 100, title, sub, "bxs" if i == 0 else "bx") + n(x + 6, 210, i + 5)
        d += a(x - 2, 260, x - 18, 260)
    d += b(150, 220, 190, 80, "The provider", "runs the model", "solid")
    d += t(500, 25, "the numbered order is one example; steps 1 to 3 can stop the call before any money is spent", "sm", "middle")
    d += t(500, 345, "the answer comes back the same way, and is screened and logged before the app sees it", "sm", "middle")
    return figure(1000, 360, d, "One call through the gateway in seven numbered steps: 1 key check, 401 if unknown; 2 allow-list, 403 if not an approved model; 3 rate limit, 30 calls a minute, 429; 4 cache, answer for $0 if asked before; 5 screen for jailbreaks and harm; 6 route to a provider and add its key; 7 log who, which model, tokens and rupees. Then the provider runs the model.",
                  "One call, seven small jobs. The allow-list and the 30-a-minute limit are the real policies from our tutorial's gateway.")


def drawing_gw_fallback():
    b, a, t = kit.box, kit.arrow, kit.text
    d = b(10, 120, 150, 80, "The agent", "one call", "bxm")
    d += a(162, 160, 258, 160)
    d += b(260, 100, 220, 120, "The gateway", ["try A first;", "if it fails, try B"], "solid")
    d += b(720, 20, 200, 90, "Provider A", "down, or too slow", "bxm")
    d += b(720, 210, 200, 90, "Provider B", "the backup", "bx")
    d += a(482, 130, 716, 70, "1. try", lx=600, ly=88, kind="lnd")
    d += a(482, 190, 716, 250, "2. try next", lx=600, ly=246)
    # a big cross over provider A
    d += '<circle class="hz" cx="955" cy="65" r="22"/><line class="lnc" x1="943" y1="53" x2="967" y2="77"/><line class="lnc" x1="943" y1="77" x2="967" y2="53"/>'
    # a little unplugged plug
    d += ('<rect class="hz" x="640" y="128" width="34" height="22" rx="4"/>'
          '<line class="lnc" x1="674" y1="133" x2="686" y2="133"/><line class="lnc" x1="674" y1="145" x2="686" y2="145"/>'
          '<path class="ln" d="M640,139 Q615,146 610,162" fill="none"/>')
    d += t(657, 172, "unplugged", "sm", "middle")
    d += t(250, 280, ["the agent never knows A failed;", "the log says where it switched"], "sm", "middle")
    return figure(1000, 315, d, "An agent sends one call to the gateway. The gateway tries provider A, which is crossed out because it is down or too slow, then sends the call to provider B, the backup. The agent never knows A failed, and the log records the switch.",
                  "Fallback. One provider failing should be a line in the log, not an outage.")


def drawing_gw_two_boxes():
    b, t = kit.box, kit.text
    d = t(500, 22, "one question decides where a rule lives: does it need to know the business?", "sm", "middle")
    d += b(20, 45, 450, 300, "The gateway",
           ["sees every model call, from any app", "", "who is calling, and their key",
            "which models are approved", "rate limits and budgets per team", "the cache",
            "screening of prompt and answer", "routing and fallback", "tokens and cost in the log"], "bxs")
    d += b(530, 45, 450, 300, "The harness",
           ["knows the business, inside one agent", "", "did the customer ask for this?",
            "is the amount under ₹40,000?", "does it need a person's approval?",
            "may this user use this tool?", "is a tool result an attack?",
            "is the answer true to the tools?", "when to stop the turn"], "solid")
    # a small blind spot: the gateway's closed eye
    d += ('<path class="hz" d="M470,380 Q500,358 530,380 Q500,402 470,380 Z"/>'
          '<line class="lnc" x1="472" y1="380" x2="528" y2="380"/>')
    d += t(500, 420, "the gateway sees the model ask for a tool, never what the tool does", "sm", "middle")
    return figure(1000, 435, d, "Two boxes. The gateway sees every model call from any app: who is calling, approved models, rate limits and budgets per team, the cache, screening, routing and fallback, and tokens and cost. The harness knows the business inside one agent: whether the customer asked, whether the amount is under ₹40,000, whether a person must approve, tool permissions, attacks in tool results, whether the answer is true, and when to stop. A closed eye between them: the gateway never sees what a tool does.",
                  "Gateway and harness. Company-wide plumbing on the left; money, consent and truth on the right.")


DRAWINGS = {"gw-switchboard": drawing_gw_switchboard, "gw-one-call": drawing_gw_one_call,
            "gw-fallback": drawing_gw_fallback, "gw-two-boxes": drawing_gw_two_boxes}
