"""Generate the animated terminal hero SVGs for the profile README.

Geometry follows macOS window metrics (12pt traffic lights on 20pt centres,
28pt title bar, 10pt corner radius) and a golden-ratio type scale:
window 900x556 (1.618), 15px text on a 24px line, 38px gutter (24 x 1.618).

    python3 assets/hero.py
"""

import html

W, H = 900, 556                 # 900 / 556 = 1.6187
MARGIN = 24                     # room for the window shadow
TITLEBAR, RADIUS = 28, 10
PAD_X, PAD_TOP = 38, 20
FS, LH, CW = 15, 24, 9.0        # 15 x 1.618 = 24 line height
CHAR_S, ENTER_S, OUT_S, BLANK_S = 0.075, 0.28, 0.26, 0.13
START_S, HOLD_S, BLINK_S = 0.6, 4.8, 0.53

PROMPT = "kevin@MacBook-Pro ~ % "

# (kind, text) - cmd is typed out, the rest appear a line at a time.
SCRIPT = [
    ("dim", "Last login: Fri Sep  4 09:41:12 on ttys001"),
    ("gap", ""),
    ("cmd", "whoami"),
    ("out", "kevin, security researcher and builder"),
    ("gap", ""),
    ("cmd", "cat .principles"),
    ("out", "files stay on your machine."),
    ("out", "no upload, no telemetry, no build step."),
    ("out", "a report a developer can act on, not a severity number."),
    ("gap", ""),
    ("cmd", "ls ~/projects"),
    ("key", "convert.in    qr.in    snipsearch    stelegraphy"),
    ("gap", ""),
    ("cmd", "security --focus"),
    ("out", "authorization, SSRF, exposed configuration."),
    ("gap", ""),
    ("cmd", "cat .stack"),
    ("out", "typescript  node  powershell  python  burp  docker  k8s"),
    ("gap", ""),
    ("cmd", ""),
]

LIGHT = dict(body="#ffffff", bar="#ececec", edge="#c9c9c9", hair="#d4d4d4",
             title="#4a4a4a", text="#1d1d1f", dim="#86868b", key="#0071e3",
             shadow=0.22, rim=0.5)
DARK = dict(body="#1e1e1e", bar="#333336", edge="#ffffff", hair="#000000",
            title="#d8d8da", text="#f2f2f2", dim="#8a8a8f", key="#4aa8ff",
            shadow=0.55, rim=0.14)

LIGHTS = [("#ed6a5f", "#e24b41"), ("#f6be50", "#e1a73e"), ("#61c555", "#2dac2f")]


def schedule():
    """Walk the script once, returning per-line reveal times and the cycle length."""
    t, lines = START_S, []
    for kind, text in SCRIPT:
        if kind == "gap":
            lines.append((kind, text, t, []))
            t += BLANK_S
        elif kind == "cmd":
            steps = [t + (i + 1) * CHAR_S for i in range(len(text))]
            lines.append((kind, text, t, steps))
            t = (steps[-1] if steps else t) + ENTER_S
        else:
            lines.append((kind, text, t, []))
            t += OUT_S
    return lines, t + HOLD_S, t


def anim(attr, values, times, cycle):
    v = ";".join(str(round(x, 2)) if isinstance(x, float) else str(x) for x in values)
    k = ";".join(f"{min(x / cycle, 1):.5f}" for x in times)
    return (f'<animate attributeName="{attr}" calcMode="discrete" values="{v}" '
            f'keyTimes="{k}" dur="{cycle}s" repeatCount="indefinite"/>')


def build(p):
    lines, cycle, idle_at = schedule()
    ox, oy = MARGIN, MARGIN
    top = oy + TITLEBAR + PAD_TOP
    out, clips = [], []
    x0 = ox + PAD_X + len(PROMPT) * CW
    cur_x, cur_xt = [x0], [0.0]
    cur_y, cur_yt = [top + 3], [0.0]
    cur_o, cur_ot = [0], [0.0]

    for i, (kind, text, t0, steps) in enumerate(lines):
        y = top + i * LH + 17
        x = ox + PAD_X
        if kind == "gap":
            continue
        if kind == "cmd":
            pw = len(PROMPT) * CW
            out.append(f'<g opacity="0"><text x="{x}" y="{y}" class="m" fill="{p["dim"]}" xml:space="preserve" '
                       f'textLength="{pw:.1f}" lengthAdjust="spacing">{html.escape(PROMPT)}</text>'
                       f'{anim("opacity", [0, 1], [0, t0], cycle)}</g>')
            if text:
                cw_ = len(text) * CW
                clips.append(f'<clipPath id="c{i}"><rect x="{x + pw:.1f}" y="{y - 17}" '
                             f'height="{LH}" width="0">'
                             f'{anim("width", [0] + [round((n + 1) * CW, 1) for n in range(len(text))], [0] + steps, cycle)}'
                             f'</rect></clipPath>')
                out.append(f'<g clip-path="url(#c{i})"><text x="{x + pw:.1f}" y="{y}" class="m" '
                           f'fill="{p["text"]}" textLength="{cw_:.1f}" lengthAdjust="spacing">'
                           f'{html.escape(text)}</text></g>')
            # cursor rides the prompt, then each typed character
            cur_o.append(1)
            cur_ot.append(t0)
            cur_y.append(y - 14)
            cur_yt.append(t0)
            cur_x.append(x + pw)
            cur_xt.append(t0)
            for n, st in enumerate(steps):
                cur_x.append(x + pw + (n + 1) * CW)
                cur_xt.append(st)
            if text:  # the final bare prompt keeps its cursor and blinks instead
                cur_o.append(0)
                cur_ot.append(steps[-1] + ENTER_S * 0.6)
        else:
            fill = p["dim"] if kind == "dim" else (p["key"] if kind == "key" else p["text"])
            out.append(f'<g opacity="0"><text x="{x}" y="{y}" class="m" fill="{fill}" '
                       f'textLength="{len(text) * CW:.1f}" lengthAdjust="spacing">'
                       f'{html.escape(text)}</text>{anim("opacity", [0, 1], [0, t0], cycle)}</g>')

    # blink on the final idle prompt
    t = idle_at
    while t < cycle:
        cur_o.append(len(cur_o) % 2)
        cur_ot.append(t)
        t += BLINK_S

    last_y = top + (len(lines) - 1) * LH + 17
    cursor = (f'<rect x="{ox + PAD_X + len(PROMPT) * CW:.1f}" y="{last_y - 14}" width="{CW}" '
              f'height="18" rx="1" fill="{p["text"]}" opacity="0">'
              f'{anim("x", cur_x, cur_xt, cycle)}{anim("y", cur_y, cur_yt, cycle)}'
              f'{anim("opacity", cur_o, cur_ot, cycle)}</rect>')

    dots = "".join(
        f'<circle cx="{ox + 20 + n * 20}" cy="{oy + TITLEBAR / 2}" r="6" fill="{f}" stroke="{s}" stroke-width="0.5"/>'
        for n, (f, s) in enumerate(LIGHTS))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W + MARGIN * 2}" height="{H + MARGIN * 2}" viewBox="0 0 {W + MARGIN * 2} {H + MARGIN * 2}" role="img" aria-label="Terminal window typing out: kevin, security researcher and builder. Projects: convert.in, qr.in, snipsearch, stelegraphy.">
<style>
.m {{ font-family: "SF Mono", SFMono-Regular, ui-monospace, Menlo, Monaco, Consolas, "DejaVu Sans Mono", monospace; font-size: {FS}px; }}
.u {{ font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, "Helvetica Neue", "Segoe UI", Arial, sans-serif; font-size: 13px; font-weight: 600; }}
</style>
<defs>
<filter id="sh" x="-30%" y="-30%" width="160%" height="160%">
<feDropShadow dx="0" dy="9" stdDeviation="13" flood-color="#000000" flood-opacity="{p["shadow"]}"/>
</filter>
{"".join(clips)}
</defs>
<g filter="url(#sh)">
<rect x="{ox}" y="{oy}" width="{W}" height="{H}" rx="{RADIUS}" fill="{p["body"]}"/>
</g>
<path d="M{ox} {oy + RADIUS}A{RADIUS} {RADIUS} 0 0 1 {ox + RADIUS} {oy}H{ox + W - RADIUS}A{RADIUS} {RADIUS} 0 0 1 {ox + W} {oy + RADIUS}V{oy + TITLEBAR}H{ox}Z" fill="{p["bar"]}"/>
<line x1="{ox}" y1="{oy + TITLEBAR}" x2="{ox + W}" y2="{oy + TITLEBAR}" stroke="{p["hair"]}" stroke-width="1"/>
{dots}
<text class="u" x="{ox + W / 2}" y="{oy + 19}" text-anchor="middle" fill="{p["title"]}">kevin · zsh · 90×20</text>
{chr(10).join(out)}
{cursor}
<rect x="{ox + 0.5}" y="{oy + 0.5}" width="{W - 1}" height="{H - 1}" rx="{RADIUS}" fill="none" stroke="{p["edge"]}" stroke-opacity="{p['rim']}" stroke-width="1"/>
</svg>
'''


if __name__ == "__main__":
    for name, palette in (("light", LIGHT), ("dark", DARK)):
        with open(f"assets/hero-{name}.svg", "w") as f:
            f.write(build(palette))
        print(f"assets/hero-{name}.svg")
