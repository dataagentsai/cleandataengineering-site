"""Claude API Simulator: change the request, watch the response. Writes /learn/llm-api-sim/.

    python3 _guides/llm_api_sim.py

A browser-only simulator of one call to the Claude Messages API (POST /v1/messages). The learner
edits the request (model, system prompt, message, max_tokens, effort, thinking display, temperature,
stop sequences, a tool, streaming) and sees, live: the Python SDK code, the TypeScript SDK code, the
cURL command and the JSON body; then the JSON response (or the server-sent events when streaming),
the HTTP status, token usage and cost. Tool use can be continued for a second turn.

Nothing calls the real API. Answers are canned for four example questions; token counts are
estimates (about 4 characters per token); error wording is illustrative. The shapes, field names,
model IDs, prices and per-model rules follow the Claude API reference as of 31 Oct 2026
(claude-api skill, cached 2026-10-06). Re-check them when models change.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("writing_build", ROOT / "_writing" / "build.py")
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)
E = wb.E
SITE = wb.SITE
URL = f"{SITE}/learn/llm-api-sim/"

MODELS = {
    "claude-opus-5-5": {"name": "Claude Opus 5.5", "in": 4.00, "out": 20.00, "temp": "removed", "effort": True, "effortDefault": "medium", "thinking": "adaptive"},
    "claude-sonnet-5-5": {"name": "Claude Sonnet 5.5", "in": 2.00, "out": 10.00, "temp": "default-only", "effort": True, "effortDefault": "high", "thinking": "adaptive"},
    "claude-haiku-5-5": {"name": "Claude Haiku 5.5", "in": 0.10, "out": 0.50, "temp": "default-only", "effort": True, "effortDefault": "medium", "thinking": "adaptive"},
    "claude-haiku-4-5": {"name": "Claude Haiku 4.5 (older)", "in": 1.00, "out": 5.00, "temp": "allowed", "effort": False, "effortDefault": None, "thinking": "budget"},
}

PRESETS = [
    {"id": "capital", "label": "Capital of France", "q": "What is the capital of France?",
     "a": "The capital of France is Paris.", "think": 0.3,
     "summary": "Simple factual question; answer directly."},
    {"id": "idem", "label": "Explain idempotency", "q": "Explain idempotency in one sentence, for a data engineer.",
     "a": "An operation is idempotent if running it once or many times leaves the data in the same state, so a retried job never double-counts a day.",
     "think": 1.0, "summary": "Define it plainly, then tie it to retries in pipelines."},
    {"id": "weather", "label": "Weather in Pune (tool)", "q": "What's the weather in Pune right now?",
     "a": "I can't check live weather without a weather tool, so I don't know the current conditions in Pune. A weather site or app will have them.",
     "think": 0.6, "summary": "Needs live data; use the weather tool if available.",
     "pre": "I'll check the current weather in Pune.", "toolInput": {"location": "Pune"}, "toolResult": "29°C, partly cloudy, humidity 62%",
     "final": "It's 29°C and partly cloudy in Pune right now, with humidity around 62%."},
    {"id": "haiku", "label": "Haiku (try a stop sequence)", "q": "Write a haiku about data pipelines.",
     "a": "Rows arrive at dawn\nquiet checks guard every gate\ndashboards wake in green", "think": 0.7,
     "summary": "Three lines, five-seven-five, one image per line."},
]

TOOL = {"name": "get_weather", "description": "Get the current weather for a city",
        "input_schema": {"type": "object", "properties": {"location": {"type": "string", "description": "City name"}}, "required": ["location"]}}

GLOSSARY_REQ = [
    ("model", "Which Claude model answers. It decides quality, speed and price per token."),
    ("max_tokens", "The most tokens the reply may use, thinking included. Hit it and the reply is cut off with stop_reason max_tokens."),
    ("system", "Instructions that frame the whole conversation: role, tone, rules. Sent once, applies to every turn."),
    ("messages", "The conversation so far, oldest first, alternating user and assistant. The API keeps no memory between calls: you send the history every time."),
    ("output_config.effort", "How hard the model works: low, medium, high, xhigh, max. Higher means more thinking, better answers on hard problems, more output tokens."),
    ("thinking", "Current models think before answering. display 'omitted' (the default) returns an empty thinking block; 'summarized' returns a readable summary. You pay for thinking either way."),
    ("temperature", "Randomness in word choice. Removed or fixed on the newest models (sending another value is an error); allowed on older ones."),
    ("stop_sequences", "Text that ends the reply early if the model writes it. The sequence itself is not included."),
    ("tools", "Functions the model may ask you to run: a name, a description and a JSON schema for the input. The model never runs them itself."),
    ("tool_choice", "auto lets the model decide; none forbids tools. Forcing a tool ('any' or a named tool) returns an error on Opus 5.5 and Sonnet 5.5."),
    ("stream", "Send the reply as a series of events while it is written, instead of one JSON at the end."),
]
GLOSSARY_RES = [
    ("id", "A unique id for this message. Quote it when reporting a problem."),
    ("content", "A list of blocks, not one string: thinking, text, tool_use. Always check each block's type."),
    ("thinking block", "The model's reasoning. Empty when display is omitted; the signature lets the API verify it when you send it back."),
    ("tool_use block", "The model asking you to run a tool: the tool's name, the input, and an id you must quote in your tool_result."),
    ("stop_reason", "Why it stopped: end_turn (finished), max_tokens (cut off), stop_sequence, tool_use (waiting for you), pause_turn, or refusal."),
    ("stop_sequence", "Which stop sequence ended the reply, or null."),
    ("usage.input_tokens", "Tokens you sent: system, tools and the whole conversation. Billed at the input price."),
    ("usage.output_tokens", "Tokens the model wrote, thinking included. Billed at the output price, usually 5 times input."),
    ("usage.cache_*", "Tokens written to or read from the prompt cache. Cache reads cost a fraction of normal input."),
]

CSS = """<style>
  .crumbs { font-size:13.5px; color:var(--faint); margin:28px 0 0; } .crumbs a { color:var(--muted); }
  .lede { font-size:19px; color:var(--ink-soft); }
  .note { font-size:13.5px; color:var(--faint); }
  .sim { display:grid; grid-template-columns: 330px 1fr; gap:16px; margin:18px 0; align-items:start; }
  .panel { border:var(--line); border-radius:14px; background:#fff; padding:12px 14px; min-width:0; }
  .sim > * { min-width:0; }
  .panel h3 { font-family:var(--hand); font-weight:400; font-size:23px; margin:0 0 6px; }
  .ctl { margin:0 0 10px; } .ctl label { display:block; font-size:12px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin-bottom:3px; }
  .ctl .hint { font-size:12.5px; color:var(--faint); margin-top:2px; }
  .ctl select, .ctl input[type=text], .ctl input[type=number], .ctl textarea { width:100%; font:inherit; font-size:14px; border:1.5px solid var(--ink); border-radius:9px; padding:5px 8px; background:#fff; color:var(--ink); }
  .ctl textarea { min-height:58px; resize:vertical; }
  .row2 { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
  .chk { display:flex; gap:8px; align-items:center; font-size:14.5px; margin:4px 0; }
  .presets { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px; }
  .presets button, .tabs button, .act { font:inherit; font-size:13px; border:1.5px solid var(--ink); border-radius:999px; padding:3px 10px; background:#fff; color:var(--ink); cursor:pointer; }
  .presets button.on, .tabs button.on { background:var(--butter-wash); font-weight:700; }
  .act { background:var(--ink); color:#fff; font-weight:700; padding:5px 14px; }
  .tabs { display:flex; flex-wrap:wrap; gap:6px; margin:0 0 8px; }
  pre.code { font-family:var(--mono); font-size:12.5px; line-height:1.5; background:#FBFAF7; border:1px solid var(--rule-firm); border-radius:10px; padding:10px 12px; overflow:auto; max-height:430px; margin:0; white-space:pre; }
  #res { white-space:pre-wrap; word-break:break-word; }
  pre.code .k { color:#3B4F8F; } pre.code .s { color:#2E7D4F; } pre.code .n { color:#A2541C; } pre.code .c { color:#8A8A8A; }
  .apistatus { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin:0 0 8px; font-size:14px; }
  .pill { display:inline-block; font-size:12px; font-weight:700; border:1.5px solid var(--ink); border-radius:999px; padding:1px 9px; }
  .pill.ok { background:var(--mint-wash,#E3F4EA); } .pill.err { background:var(--rose-wash); } .pill.warn { background:var(--butter-wash); }
  .meter { display:grid; grid-template-columns:repeat(4,1fr); gap:6px; margin:8px 0 0; }
  .meter div { border:1px dashed var(--rule-firm); border-radius:10px; padding:6px 8px; font-size:12.5px; color:var(--muted); }
  .meter b { display:block; font-size:16px; color:var(--ink); }
  .explain { margin:10px 0 0; padding:8px 12px; border-radius:10px; background:var(--peri-wash); font-size:14.5px; }
  .explain li { margin:3px 0; }
  .turn { font-size:13px; color:var(--muted); }
  table.gl { border-collapse:collapse; width:100%; font-size:14.5px; } table.gl td { padding:6px 8px; border-bottom:1px dashed var(--rule-firm); vertical-align:top; }
  table.gl td:first-child { font-family:var(--mono); font-size:13px; white-space:nowrap; color:var(--accent); }
  .cols { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
  @media (max-width:900px) { .sim, .cols { grid-template-columns:1fr; } .meter { grid-template-columns:1fr 1fr; } }
</style>"""

JS = r"""
(function(){
const M = __MODELS__, P = __PRESETS__, TOOL = __TOOL__;
const $ = id => document.getElementById(id);
let preset = P[0], codeTab = 'python', resTab = 'json', turn = 1;
const tok = s => Math.max(1, Math.ceil((s||'').length / 4));
const rid = (p, n) => p + Array.from({length:n}, (_, i) => 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz0123456789'[(i*37 + preset.id.length*11 + turn*7) % 58]).join('');
function state(){
  return { model:$('model').value, system:$('system').value.trim(), msg:$('msg').value, max:parseInt($('max').value||'0',10),
    effort:$('effort').value, display:$('display').value, temp:$('temp').value.trim(), stop:$('stop').value,
    tool:$('tool').checked, choice:$('choice').value, stream:$('stream').checked };
}
function body(s){
  const b = {model:s.model, max_tokens:s.max};
  if (s.system) b.system = s.system;
  if (s.effort !== 'default') b.output_config = {effort:s.effort};
  const md = M[s.model];
  if (md.thinking === 'adaptive' && s.display === 'summarized') b.thinking = {type:'adaptive', display:'summarized'};
  if (md.thinking === 'budget' && s.display === 'summarized') b.thinking = {type:'enabled', budget_tokens:1024};
  if (s.temp !== '') b.temperature = Number(s.temp);
  if (s.stop) b.stop_sequences = [s.stop];
  if (s.tool) { b.tools = [TOOL]; b.tool_choice = {type:s.choice}; }
  if (s.stream) b.stream = true;
  const msgs = [{role:'user', content:s.msg}];
  if (turn === 2) {
    msgs.push({role:'assistant', content:lastAssistant});
    msgs.push({role:'user', content:[{type:'tool_result', tool_use_id:lastToolId, content:preset.toolResult}]});
  }
  b.messages = msgs;
  return b;
}
let lastAssistant = null, lastToolId = null;
function check(s){
  const md = M[s.model], errs = [], warns = [];
  if (!s.msg.trim()) errs.push(['messages', 'messages: the user message must not be empty']);
  if (!(s.max >= 1)) errs.push(['max_tokens', 'max_tokens: must be at least 1']);
  if (s.temp !== '') {
    if (md.temp === 'removed') errs.push(['temperature', 'temperature: not supported on ' + s.model + '. Remove it; use effort to trade quality against cost.']);
    else if (md.temp === 'default-only' && Number(s.temp) !== 1) errs.push(['temperature', 'temperature: only the default value is accepted on ' + s.model + '.']);
    else if (isNaN(Number(s.temp)) || Number(s.temp) < 0 || Number(s.temp) > 1) errs.push(['temperature', 'temperature: must be between 0 and 1.']);
  }
  if (s.effort !== 'default' && !md.effort) errs.push(['effort', 'output_config.effort: not supported on ' + s.model + '.']);
  if (md.thinking === 'budget' && s.display === 'summarized' && s.max <= 1024) errs.push(['thinking', 'thinking.budget_tokens (1024) must be less than max_tokens.']);
  if (s.max > 16000 && !s.stream) warns.push('Large max_tokens without streaming: the SDKs ask you to stream long replies so the HTTP request does not time out.');
  return {errs, warns};
}
function thinkTokens(s){
  const md = M[s.model];
  if (md.thinking === 'budget') return s.display === 'summarized' ? Math.round(180 * preset.think + 40) : 0;
  const e = s.effort === 'default' ? md.effortDefault : s.effort;
  const base = {low:15, medium:60, high:140, xhigh:260, max:420}[e];
  return Math.round(base * preset.think + 8);
}
function response(s){
  const md = M[s.model], blocks = [];
  let out = 0, stop = 'end_turn', stopSeq = null, budget = s.max;
  const th = thinkTokens(s);
  if (th > 0) {
    const shown = s.display === 'summarized' ? preset.summary : '';
    blocks.push({type:'thinking', thinking:shown, signature:'EqQBCkgIBhABGAIiQ' + rid('', 18) + '…'});
    out += Math.min(th, budget); budget -= th;
    if (budget <= 0) return finish([{type:'thinking', thinking:shown, signature:blocks[0].signature}], s.max, 'max_tokens', null, s);
  }
  const useTool = s.tool && s.choice === 'auto' && preset.toolInput && turn === 1;
  let text = turn === 2 ? preset.final : (useTool ? preset.pre : (preset.a || '(simulated) A real model would answer here. This simulator has canned answers only for the four examples above.'));
  if (s.tool && s.choice === 'auto' && preset.toolInput === undefined && turn === 1) text = text;
  if (s.stop && text.includes(s.stop)) { text = text.slice(0, text.indexOf(s.stop)); stop = 'stop_sequence'; stopSeq = s.stop; }
  const tt = tok(text);
  if (tt > budget) { text = text.slice(0, Math.max(0, budget * 4)); out += budget; stop = 'max_tokens'; stopSeq = null;
    if (text) blocks.push({type:'text', text});
    return finish(blocks, out, stop, null, s); }
  if (text) blocks.push({type:'text', text}); out += tt; budget -= tt;
  if (useTool && stop === 'end_turn') {
    lastToolId = 'toolu_01' + rid('', 20);
    const tu = {type:'tool_use', id:lastToolId, name:'get_weather', input:preset.toolInput};
    blocks.push(tu); out += 22; stop = 'tool_use';
  }
  return finish(blocks, out, stop, stopSeq, s);
}
function finish(blocks, out, stop, stopSeq, s){
  const b = body(s);
  let inTok = tok(s.system) + tok(s.msg) + 7;
  if (s.tool) inTok += tok(JSON.stringify(TOOL)) + 290;
  if (turn === 2) inTok += 70;
  return {id:'msg_01' + rid('', 22), type:'message', role:'assistant', model:s.model, content:blocks,
          stop_reason:stop, stop_sequence:stopSeq, stop_details:null,
          usage:{input_tokens:inTok, cache_creation_input_tokens:0, cache_read_input_tokens:0, output_tokens:out}};
}
// ---------- rendering helpers
const esc = t => String(t).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
function hlJSON(str){
  return esc(str).replace(/("(?:[^"\\]|\\.)*")(\s*:)?|\b(true|false|null)\b|(-?\d+(?:\.\d+)?)/g, (m, s, colon, lit, num) =>
    s ? (colon ? '<span class="k">' + s + '</span>' + colon : '<span class="s">' + s + '</span>') : lit ? '<span class="n">' + lit + '</span>' : '<span class="n">' + num + '</span>');
}
function lit(v, ind, py){
  let j = JSON.stringify(v, null, py ? 4 : 2);
  j = j.replace(/("(?:[^"\\]|\\.)*")(\s*:)?|\b(true|false|null)\b/g, (m, str, colon, l) => {
    if (str) return (!py && colon && /^"[A-Za-z_]\w*"$/.test(str)) ? str.slice(1, -1) + colon : m;
    return py ? {true:'True', false:'False', null:'None'}[l] : l;
  });
  return j.split('\n').map((line, i) => i ? ' '.repeat(ind) + line : line).join('\n');
}
const pyLit = (v, ind) => lit(v, ind, true), tsLit = (v, ind) => lit(v, ind, false);
function codePy(b){
  const args = Object.entries(b).filter(([k]) => k !== 'stream').map(([k, v]) => '    ' + k + '=' + pyLit(v, 4) + ',').join('\n');
  const head = 'import anthropic\n\nclient = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY\n\n';
  if (b.stream) return head + 'with client.messages.stream(\n' + args + '\n) as stream:\n    for text in stream.text_stream:\n        print(text, end="", flush=True)\n    message = stream.get_final_message()\n\nprint(message.stop_reason, message.usage)';
  return head + 'response = client.messages.create(\n' + args + '\n)\n\nfor block in response.content:\n    if block.type == "text":\n        print(block.text)\nprint(response.stop_reason, response.usage)';
}
function codeTs(b){
  const args = Object.entries(b).filter(([k]) => k !== 'stream').map(([k, v]) => '  ' + k + ': ' + tsLit(v, 2) + ',').join('\n');
  const head = 'import Anthropic from "@anthropic-ai/sdk";\n\nconst client = new Anthropic(); // reads ANTHROPIC_API_KEY\n\n';
  if (b.stream) return head + 'const stream = client.messages.stream({\n' + args + '\n});\n\nfor await (const event of stream) {\n  if (event.type === "content_block_delta" && event.delta.type === "text_delta") {\n    process.stdout.write(event.delta.text);\n  }\n}\nconst message = await stream.finalMessage();\nconsole.log(message.stop_reason, message.usage);';
  return head + 'const response = await client.messages.create({\n' + args + '\n});\n\nfor (const block of response.content) {\n  if (block.type === "text") console.log(block.text);\n}\nconsole.log(response.stop_reason, response.usage);';
}
function codeCurl(b){
  const j = JSON.stringify(b, null, 2).replace(/'/g, "'\\''");
  return 'curl https://api.anthropic.com/v1/messages \\\n  -H "Content-Type: application/json" \\\n  -H "x-api-key: $ANTHROPIC_API_KEY" \\\n  -H "anthropic-version: 2023-06-01" \\\n  -d \'' + j + '\'';
}
function sse(r){
  const ev = (name, data) => 'event: ' + name + '\ndata: ' + JSON.stringify(data) + '\n';
  const start = Object.assign({}, r, {content:[], stop_reason:null, stop_sequence:null, usage:Object.assign({}, r.usage, {output_tokens:1})});
  let out = [ev('message_start', {type:'message_start', message:start})];
  r.content.forEach((b, i) => {
    if (b.type === 'thinking') {
      out.push(ev('content_block_start', {type:'content_block_start', index:i, content_block:{type:'thinking', thinking:'', signature:''}}));
      if (b.thinking) out.push(ev('content_block_delta', {type:'content_block_delta', index:i, delta:{type:'thinking_delta', thinking:b.thinking}}));
      out.push(ev('content_block_delta', {type:'content_block_delta', index:i, delta:{type:'signature_delta', signature:b.signature}}));
    } else if (b.type === 'text') {
      out.push(ev('content_block_start', {type:'content_block_start', index:i, content_block:{type:'text', text:''}}));
      const parts = b.text.match(/.{1,18}(\s|$)|.{1,18}/g) || [b.text];
      parts.forEach(p => out.push(ev('content_block_delta', {type:'content_block_delta', index:i, delta:{type:'text_delta', text:p}})));
    } else if (b.type === 'tool_use') {
      out.push(ev('content_block_start', {type:'content_block_start', index:i, content_block:{type:'tool_use', id:b.id, name:b.name, input:{}}}));
      const js = JSON.stringify(b.input);
      out.push(ev('content_block_delta', {type:'content_block_delta', index:i, delta:{type:'input_json_delta', partial_json:js.slice(0, 10)}}));
      out.push(ev('content_block_delta', {type:'content_block_delta', index:i, delta:{type:'input_json_delta', partial_json:js.slice(10)}}));
    }
    out.push(ev('content_block_stop', {type:'content_block_stop', index:i}));
  });
  out.push(ev('message_delta', {type:'message_delta', delta:{stop_reason:r.stop_reason, stop_sequence:r.stop_sequence}, usage:{output_tokens:r.usage.output_tokens}}));
  out.push(ev('message_stop', {type:'message_stop'}));
  return out.join('\n');
}
function explainRes(r, s){
  const li = [];
  const th = r.content.find(b => b.type === 'thinking');
  if (th) li.push(th.thinking ? 'The model thought first; display "summarized" returns a short summary of that thinking.' : 'There is a thinking block with empty text: the model thought, but display "omitted" (the default) hides it. Its tokens are still in output_tokens.');
  if (r.stop_reason === 'end_turn') li.push('stop_reason end_turn: the model finished on its own.');
  if (r.stop_reason === 'max_tokens') li.push('stop_reason max_tokens: the reply hit your max_tokens limit and was cut off. Raise max_tokens, or lower effort so less goes on thinking.');
  if (r.stop_reason === 'stop_sequence') li.push('stop_reason stop_sequence: the model wrote "' + r.stop_sequence + '", so the reply ended there. The sequence itself is not included.');
  if (r.stop_reason === 'tool_use') li.push('stop_reason tool_use: the model is waiting for you. Run get_weather with the input shown, then send the result back with the same tool_use id. Press "Run the tool and continue".');
  if (turn === 2) li.push('Turn 2: you sent the whole conversation again, including the assistant\'s earlier content unchanged (thinking block too) and a tool_result. The API keeps no memory between calls.');
  li.push('Cost of this call: input ' + r.usage.input_tokens + ' × $' + M[s.model].in + ' per million, output ' + r.usage.output_tokens + ' × $' + M[s.model].out + ' per million.');
  return '<ul>' + li.map(x => '<li>' + esc(x) + '</li>').join('') + '</ul>';
}
function render(){
  const s = state(), md = M[s.model];
  document.querySelectorAll('#presets button').forEach(b => b.classList.toggle('on', b.dataset.id === preset.id));
  document.querySelectorAll('#codetabs button').forEach(b => b.classList.toggle('on', b.dataset.t === codeTab));
  document.querySelectorAll('#restabs button').forEach(b => b.classList.toggle('on', b.dataset.t === resTab));
  $('effortHint').textContent = md.effort ? 'Default on this model: ' + md.effortDefault : 'Not supported on this model.';
  $('displayHint').textContent = md.thinking === 'budget' ? 'On Haiku 4.5, thinking is off unless you enable it (a token budget).' : 'Thinking is always on for this model; this only changes what you see.';
  $('tempHint').textContent = {removed:'Removed on this model: any value is an error.', 'default-only':'Only the default (1) is accepted on this model.', allowed:'Allowed on this model, 0 to 1.'}[md.temp];
  const b = body(s), {errs, warns} = check(s);
  const code = codeTab === 'python' ? codePy(b) : codeTab === 'ts' ? codeTs(b) : codeTab === 'curl' ? codeCurl(b) : null;
  $('code').innerHTML = code === null ? '<span class="c">POST https://api.anthropic.com/v1/messages\ncontent-type: application/json\nx-api-key: sk-ant-…  (your key, never in code)\nanthropic-version: 2023-06-01\n</span>\n' + hlJSON(JSON.stringify(b, null, 2)) : esc(code);
  $('turn').textContent = turn === 1 ? 'Turn 1: one user message' : 'Turn 2: history + tool result';
  let r = null;
  if (errs.length) {
    $('status').innerHTML = '<span class="pill err">HTTP 400 Bad Request</span><span class="note">the request was rejected before the model ran; nothing is billed</span>';
    $('res').innerHTML = hlJSON(JSON.stringify({type:'error', error:{type:'invalid_request_error', message:errs[0][1]}, request_id:'req_011' + rid('', 18)}, null, 2));
    $('explain').innerHTML = '<ul><li>' + esc('The API checks the request before running the model. ' + errs[0][1]) + '</li><li>Error wording here is illustrative; the shape (type, error.type, error.message, request_id) is what your code should handle.</li></ul>';
    $('meter').innerHTML = ''; $('cont').style.display = 'none';
  } else {
    r = response(s);
    $('status').innerHTML = '<span class="pill ok">HTTP 200 OK</span>' + (s.stream ? '<span class="pill">text/event-stream</span>' : '<span class="pill">application/json</span>') + '<span class="pill">stop_reason: ' + r.stop_reason + '</span>' + warns.map(w => '<span class="pill warn">' + esc(w) + '</span>').join('');
    $('res').innerHTML = resTab === 'json' && !s.stream ? hlJSON(JSON.stringify(r, null, 2)) : resTab === 'json' ? '<span class="c">// streamed: the same message arrives as server-sent events</span>\n' + esc(sse(r)) : hlJSON(JSON.stringify(r, null, 2));
    const cost = r.usage.input_tokens * md.in / 1e6 + r.usage.output_tokens * md.out / 1e6;
    $('meter').innerHTML = '<div>input tokens<b>' + r.usage.input_tokens + '</b></div><div>output tokens<b>' + r.usage.output_tokens + '</b></div><div>model<b>' + md.name.replace(' (older)', '') + '</b></div><div>cost of this call<b>$' + cost.toFixed(6) + '</b></div>';
    $('explain').innerHTML = explainRes(r, s);
    $('cont').style.display = r.stop_reason === 'tool_use' ? 'inline-block' : 'none';
    if (turn === 1) lastAssistant = r.content;
  }
  $('restabs').style.display = s.stream && !errs.length ? 'flex' : 'none';
}
// ---------- wiring
document.querySelectorAll('#presets button').forEach(b => b.onclick = () => { preset = P.find(p => p.id === b.dataset.id); turn = 1; $('msg').value = preset.q;
  if (preset.id === 'weather') $('tool').checked = true; if (preset.id === 'haiku') $('stop').value = ''; render(); });
document.querySelectorAll('#codetabs button').forEach(b => b.onclick = () => { codeTab = b.dataset.t; render(); });
document.querySelectorAll('#restabs button').forEach(b => b.onclick = () => { resTab = b.dataset.t; render(); });
['model','system','max','effort','display','temp','stop','tool','choice','stream'].forEach(id => { $(id).oninput = $(id).onchange = () => { if (['model','tool','choice','msg'].includes(id)) turn = 1; render(); }; });
$('msg').oninput = () => { turn = 1; preset = P.find(p => p.q === $('msg').value) || {id:'custom', q:$('msg').value, a:null, think:0.8, summary:'Work out what is being asked, then answer.'}; render(); };
$('cont').onclick = () => { if (lastToolId) { turn = 2; render(); } };
$('reset').onclick = () => { turn = 1; render(); };
$('msg').value = preset.q;
render();
})();
"""


def page():
    model_opts = "".join(f'<option value="{k}">{E(v["name"])} · ${v["in"]:g} / ${v["out"]:g}</option>' for k, v in MODELS.items())
    presets = "".join(f'<button data-id="{p["id"]}">{E(p["label"])}</button>' for p in PRESETS)
    gl = lambda rows: '<table class="gl">' + "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in rows) + "</table>"
    js = JS.replace("__MODELS__", json.dumps(MODELS)).replace("__PRESETS__", json.dumps(PRESETS, ensure_ascii=False)).replace("__TOOL__", json.dumps(TOOL))
    body = f"""<p class="crumbs"><a href="/">Home</a> › <a href="/simulators/">Simulators</a> › Claude API Simulator</p>
<p class="eyebrow" style="margin-top:22px">AI engineering · simulator · runs in your browser</p>
<h1>The Claude API, request and response</h1>
<p class="lede">Every app built on a language model makes the same call: send a request, get a response. Change the request on the left and watch everything update: the code in Python, TypeScript and cURL, the JSON that travels over the wire, the response that comes back, the tokens it used and what it cost.</p>
<p class="note">Nothing here calls the real API, and nothing is stored. Answers are canned for the four examples; token counts are estimates (about four characters per token); error wording is illustrative. The field names, response shapes, model IDs, prices and per-model rules follow the Claude API reference as of 31 October 2026.</p>

<div class="sim">
<div class="panel">
<h3>The request</h3>
<div class="presets" id="presets">{presets}</div>
<div class="ctl"><label for="model">model</label><select id="model">{model_opts}</select><div class="hint">Price per million tokens: input / output.</div></div>
<div class="ctl"><label for="system">system</label><textarea id="system">You are a concise assistant for data engineers.</textarea></div>
<div class="ctl"><label for="msg">messages: user</label><textarea id="msg"></textarea></div>
<div class="row2">
<div class="ctl"><label for="max">max_tokens</label><input id="max" type="number" value="1024" min="1"></div>
<div class="ctl"><label for="effort">effort</label><select id="effort"><option value="default">(model default)</option><option>low</option><option>medium</option><option>high</option><option>xhigh</option><option>max</option></select></div>
</div><div class="hint" id="effortHint" style="font-size:12.5px;color:var(--faint);margin:-6px 0 10px"></div>
<div class="ctl"><label for="display">thinking</label><select id="display"><option value="omitted">display omitted (default)</option><option value="summarized">display summarized</option></select><div class="hint" id="displayHint"></div></div>
<div class="row2">
<div class="ctl"><label for="temp">temperature</label><input id="temp" type="text" placeholder="not sent"></div>
<div class="ctl"><label for="stop">stop_sequences</label><input id="stop" type="text" placeholder="e.g. gate"></div>
</div><div class="hint" id="tempHint" style="font-size:12.5px;color:var(--faint);margin:-6px 0 10px"></div>
<label class="chk"><input type="checkbox" id="tool"> tools: get_weather</label>
<div class="ctl" style="margin-top:4px"><label for="choice">tool_choice</label><select id="choice"><option value="auto">auto: the model decides</option><option value="none">none: no tools this turn</option></select></div>
<label class="chk"><input type="checkbox" id="stream"> stream: true</label>
<p class="note" style="margin:8px 0 0">Try: raise effort and watch output tokens; set max_tokens to 20; type <code>gate</code> as a stop sequence on the haiku; set a temperature on Opus 5.5; switch on the tool and ask about the weather.</p>
</div>

<div>
<div class="panel" style="margin-bottom:14px">
<h3>What you send <span class="turn" id="turn"></span></h3>
<div class="tabs" id="codetabs"><button data-t="python">Python SDK</button><button data-t="ts">TypeScript SDK</button><button data-t="curl">cURL</button><button data-t="http">HTTP and JSON</button></div>
<pre class="code" id="code"></pre>
</div>
<div class="panel">
<h3>What comes back</h3>
<div class="apistatus" id="status"></div>
<div class="tabs" id="restabs"><button data-t="json">Events as they arrive</button><button data-t="final">The final message</button></div>
<pre class="code" id="res"></pre>
<div class="meter" id="meter"></div>
<div class="explain" id="explain"></div>
<p style="margin:10px 0 0"><button class="act" id="cont" style="display:none">Run the tool and continue →</button> <button class="act" id="reset" style="background:#fff;color:var(--ink)">Start again</button></p>
</div>
</div>
</div>

<section id="fields"><h2>Every field, in plain words</h2>
<div class="cols"><div><h3>In the request</h3>{gl(GLOSSARY_REQ)}</div><div><h3>In the response</h3>{gl(GLOSSARY_RES)}</div></div></section>

<section id="lessons"><h2>Five things the simulator shows</h2>
<ol>
<li><b>The API has no memory.</b> Every call carries the whole conversation. Turn 2 of the weather example sends the first question, the model's tool request and your tool result again.</li>
<li><b>The reply is a list of blocks, not a string.</b> Thinking, text and tool requests arrive as separate blocks. Code that reads <code>content[0].text</code> breaks the day a thinking block comes first.</li>
<li><b>You pay for thinking, even when you can't see it.</b> Raise effort and output tokens climb while the visible answer stays the same.</li>
<li><b>Always check stop_reason.</b> <code>max_tokens</code> means the answer was cut off; <code>tool_use</code> means the model is waiting for you; <code>refusal</code> means it declined. Treating every response as a finished answer is a classic bug.</li>
<li><b>The model never runs tools.</b> It asks; your code runs the tool and sends the result back. That loop is the core of every agent; the <a href="/learn/agent-harness-sim/">Agent Harness Simulator</a> shows it in a full agent.</li>
</ol>
<p>Next: <a href="/learn/agent-harness/">the Agent Harness course</a> builds a whole agent around this one call, and <a href="/writing/one-conversation-cost/">what one conversation costs</a> works through the token bill.</p></section>
<script>{js}</script>"""
    desc = "Interactive Claude API simulator: change the request (model, system prompt, max_tokens, effort, thinking, temperature, stop sequences, tools, streaming) and see the Python, TypeScript and cURL code, the JSON response or streamed events, tokens and cost."
    return wb.page("Claude API Simulator: request and response", desc, URL, body, CSS)


def main():
    out = ROOT / "learn" / "llm-api-sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page())
    print("LLM API simulator ->", out)


if __name__ == "__main__":
    main()
