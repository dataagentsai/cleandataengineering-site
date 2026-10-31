"""Drawings for 'OpenTelemetry is here to stay: instrument your agent once, send traces anywhere'.
kit, figure, E and ROOT are given as globals by build.py."""


def _plug(x, y):
    """A small two-pin plug whose body's top-left corner is at (x, y), pins pointing right."""
    return (f'<rect class="hz" x="{x}" y="{y}" width="46" height="40" rx="8"/>'
            f'<rect class="hk" x="{x + 46}" y="{y + 9}" width="16" height="6" rx="2"/>'
            f'<rect class="hk" x="{x + 46}" y="{y + 25}" width="16" height="6" rx="2"/>')


def _socket(cx, cy):
    """A round wall socket with two holes, centred at (cx, cy)."""
    return (f'<circle class="hz" cx="{cx}" cy="{cy}" r="20"/>'
            f'<rect class="hk" x="{cx - 9}" y="{cy - 9}" width="5" height="14" rx="2"/>'
            f'<rect class="hk" x="{cx + 4}" y="{cy - 9}" width="5" height="14" rx="2"/>')


def drawing_otel_plug():
    b, t, p = kit.box, kit.text, kit.path
    d = b(10, 110, 200, 100, "Your agent", ["spans written once"], "bx")
    # the cable and the one plug
    d += p("M210,160 Q260,160 296,160", "lnc", end=False)
    d += _plug(296, 140)
    # the adapter: one standard shape
    d += b(360, 100, 210, 120, "OpenTelemetry", ["one plug shape:", "OTLP, standard names"], "solid")
    vendors = ["Langfuse", "Arize Phoenix", "Datadog", "Azure Monitor", "Grafana"]
    for i, v in enumerate(vendors):
        y = 22 + i * 62
        d += p(f"M572,160 Q640,160 700,{y + 26}", "ln")
        d += _socket(730, y + 26)
        d += t(764, y + 32, v, "tx")
    d += t(110, 250, "no rewiring", "sm", "middle")
    d += t(465, 250, "the adapter you keep", "sm", "middle")
    d += t(830, 336, "sockets you can swap", "sm", "middle")
    return figure(1000, 345, d, "A cartoon: your agent has one cable ending in one plug. The plug goes into an OpenTelemetry adapter, which fans out to five wall sockets labelled Langfuse, Arize Phoenix, Datadog, Azure Monitor and Grafana.",
                  "One plug in your agent, many sockets. You change the socket, never the wiring.")


def drawing_otel_pipeline():
    b, a, t, n = kit.box, kit.arrow, kit.text, kit.num
    d = b(10, 70, 230, 120, "Agent code", ["+ the OpenTelemetry SDK", "opens spans, adds fields"], "bx") + n(24, 70, 1)
    d += a(242, 130, 318, 130, "OTLP", ly=118)
    d += t(280, 156, "the wire", "sm", "middle")
    d += b(320, 50, 260, 160, "The Collector", ["receives, batches,", "queues and retries,", "drops fields, fans out"], "solid") + n(334, 50, 2)
    d += a(582, 100, 688, 60)
    d += a(582, 160, 688, 200)
    d += b(690, 20, 290, 80, "Backend A", ["say, Langfuse"], "bxs")
    d += b(690, 160, 290, 80, "Backend B", ["say, Prometheus for numbers"], "bxs")
    d += t(500, 262, "the agent only knows the Collector's address; the Collector knows the rest", "sm", "middle")
    return figure(1000, 275, d, "A pipeline left to right: agent code with the OpenTelemetry SDK sends OTLP over the wire to the Collector, which receives, batches, queues, retries and drops fields, then sends to two backends at once, Langfuse and Prometheus.",
                  "The pipe. Your code talks OTLP to a Collector, and the Collector sends copies to as many backends as you like.")


def drawing_otel_settled():
    b, t = kit.box, kit.text
    d = '<path class="zg" d="M10,50 L480,50 L480,348 L10,348 Z"/>'
    d += '<path class="zy" d="M520,50 L990,50 L990,348 L520,348 Z"/>'
    d += t(245, 34, "SETTLED: BUILD ON IT", "lbl", "middle") + t(755, 34, "STILL MOVING: KEEP IT TIDY", "lbl", "middle")
    left = [("The SDK", "open a span, add fields"), ("OTLP", "the wire format"), ("The Collector", "the program in between"),
            ("Core names", "http.*, service.name")]
    right = [("gen_ai.* names", "status: development"), ("prompt_tokens", "renamed to input_tokens"),
             ("gen_ai.system", "renamed to provider.name"), ("Where they live", "moved to their own repo")]
    for i, ((lt, ls), (rt, rs)) in enumerate(zip(left, right)):
        y = 66 + i * 72
        d += b(40, y, 410, 56, lt, ls, "bx")
        d += b(550, y, 410, 56, rt, rs, "bxs")
    return figure(1000, 360, d, "Two columns. Settled, in green: the SDK, OTLP, the Collector, and core names such as http and service.name. Still moving, in yellow: the gen_ai names have development status, prompt_tokens was renamed to input_tokens, gen_ai.system was renamed to provider.name, and the GenAI conventions moved to their own repository.",
                  "The pipe is settled. The GenAI field names are still moving a little, so keep them in one file.")


def drawing_otel_switch():
    b, a, t = kit.box, kit.arrow, kit.text
    # the code, unchanged, in the middle
    d = b(370, 20, 260, 120, "Agent code", ["the same spans,", "the same names"], "solid")
    d += t(645, 86, "not touched", "sm")
    configs = [("config/local.yaml", "adapter: console", "spans stay in memory", 10),
               ("config/azure.yaml", "adapter: azure-monitor-otel", "Application Insights", 340),
               ("reference agent config", "adapter: otel-to-langfuse", "Collector, then Langfuse", 670)]
    for name, line, where, x in configs:
        cx = x + 160
        # a config file with a folded corner
        d += (f'<path class="hz" d="M{x},200 L{x + 296},200 L{x + 320},224 L{x + 320},300 L{x},300 Z"/>'
              f'<path class="ln" d="M{x + 296},200 L{x + 296},224 L{x + 320},224"/>')
        d += t(x + 16, 226, name, "sm")
        d += t(x + 16, 252, "telemetry:", "sm")
        d += f'<rect class="pf pf-bxs" x="{x + 12}" y="262" width="290" height="30" rx="6"/>'
        d += t(x + 30, 283, line, "bd")
        d += a(cx, 302, cx, 340)
        d += b(x + 20, 342, 280, 50, where, "", "bx")
    d += a(440, 142, 180, 196) + a(500, 142, 500, 196) + a(560, 142, 820, 196)
    return figure(1000, 405, d, "Agent code in the middle, unchanged. Below it, three config files: on a laptop the telemetry adapter is console and spans stay in memory; on Azure it is azure-monitor-otel and spans go to Application Insights; in the reference agent it is otel-to-langfuse and spans go through a Collector to Langfuse.",
                  "Switching backends: one line in a config file changes. The agent code stays the same.")


DRAWINGS = {"otel-plug": drawing_otel_plug, "otel-pipeline": drawing_otel_pipeline,
            "otel-settled": drawing_otel_settled, "otel-switch": drawing_otel_switch}
