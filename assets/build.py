"""Generate the macOS desktop pieces used by the profile README.

Three components share one palette and one window chrome:

  hero-<theme>.svg    an animated zsh session, 900x556  (1 : 1.618)
  finder-<theme>.svg  the projects folder in list view, 900x344  (1 : 2.618)
  icon-<name>.svg     dock icons, 96pt squircles at Apple's 22.37% radius

Window metrics follow macOS: 12pt traffic lights on 20pt centres, 28pt
title bar on the terminal and a 52pt unified toolbar on Finder, 10pt corner
radius, 180pt sidebar.

Monospace families disagree on advance width (SF Mono 0.600em, Menlo
0.602em, Cascadia Mono 0.586em, Consolas 0.550em), so terminal lines are
pinned with textLength and lengthAdjust="spacingAndGlyphs". That keeps the
typing clip and the cursor aligned everywhere, and scales glyphs a couple of
percent rather than opening gaps between them.

    python3 assets/build.py
"""

import html

MARGIN, RADIUS = 24, 10
LIGHTS = [("#ed6a5f", "#e24b41"), ("#f6be50", "#e1a73e"), ("#61c555", "#2dac2f")]

LIGHT = dict(body="#ffffff", bar="#ececec", side="#f2f2f2", alt="#fafafa",
             edge="#c9c9c9", hair="#d4d4d4", title="#4a4a4a", text="#1d1d1f",
             dim="#86868b", key="#0071e3", sel="#0071e3", shadow=0.22, rim=0.5)
DARK = dict(body="#1e1e1e", bar="#333336", side="#252527", alt="#232325",
            edge="#ffffff", hair="#000000", title="#d8d8da", text="#f2f2f2",
            dim="#8a8a8f", key="#4aa8ff", sel="#0a84ff", shadow=0.55, rim=0.14)
THEMES = (("light", LIGHT), ("dark", DARK))

UI = ('font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, '
      '"Helvetica Neue", "Segoe UI", Arial, sans-serif;')
MONO = ('font-family: "SF Mono", SFMono-Regular, ui-monospace, Menlo, Monaco, '
        '"Cascadia Mono", "DejaVu Sans Mono", "Liberation Mono", "Courier New", monospace;')


def chrome(p, w, h, bar):
    """Shadowed rounded window, clipped so the bar and sidebar keep the corners."""
    ox = oy = MARGIN
    head = (f'<defs><clipPath id="win"><rect x="{ox}" y="{oy}" width="{w}" height="{h}" rx="{RADIUS}"/></clipPath>'
            f'<filter id="sh" x="-30%" y="-30%" width="160%" height="160%">'
            f'<feDropShadow dx="0" dy="9" stdDeviation="13" flood-color="#000000" flood-opacity="{p["shadow"]}"/>'
            f'</filter></defs>'
            f'<g filter="url(#sh)"><rect x="{ox}" y="{oy}" width="{w}" height="{h}" rx="{RADIUS}" fill="{p["body"]}"/></g>'
            f'<g clip-path="url(#win)"><rect x="{ox}" y="{oy}" width="{w}" height="{bar}" fill="{p["bar"]}"/>')
    dots = "".join(f'<circle cx="{ox + 20 + n * 20}" cy="{oy + 26 if bar > 40 else oy + bar / 2}" r="6" '
                   f'fill="{f}" stroke="{s}" stroke-width="0.5"/>' for n, (f, s) in enumerate(LIGHTS))
    tail = (f'</g><line x1="{ox}" y1="{oy + bar}" x2="{ox + w}" y2="{oy + bar}" stroke="{p["hair"]}" stroke-width="1"/>'
            f'{dots}<rect x="{ox + 0.5}" y="{oy + 0.5}" width="{w - 1}" height="{h - 1}" rx="{RADIUS}" '
            f'fill="none" stroke="{p["edge"]}" stroke-opacity="{p["rim"]}" stroke-width="1"/>')
    return head, tail


# --------------------------------------------------------------------------
# terminal
# --------------------------------------------------------------------------

TW, TH, TBAR = 900, 556, 28     # 900 / 556 = 1.6187
PAD_X, PAD_TOP = 38, 20
FS, LH, CW = 15, 24, 9.0        # 15 x 1.618 = 24 line height, 15 x 0.6 = 9 advance
CHAR_S, ENTER_S, OUT_S, BLANK_S = 0.075, 0.28, 0.26, 0.13
START_S, HOLD_S, BLINK_S = 0.6, 4.8, 0.53
PROMPT = "~ % "                 # zsh with PROMPT='%1~ %# '

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


def mono(x, y, text, fill):
    return (f'<text x="{x:.1f}" y="{y}" class="m" fill="{fill}" xml:space="preserve" '
            f'textLength="{len(text) * CW:.1f}" lengthAdjust="spacingAndGlyphs">'
            f'{html.escape(text)}</text>')


def terminal(p):
    lines, cycle, idle_at = schedule()
    head, tail = chrome(p, TW, TH, TBAR)
    top = MARGIN + TBAR + PAD_TOP
    x, pw = MARGIN + PAD_X, len(PROMPT) * CW
    out, still, clips = [], [], []
    cur_x, cur_xt = [x + pw], [0.0]
    cur_y, cur_yt = [top + 3], [0.0]
    cur_o, cur_ot = [0], [0.0]

    for i, (kind, text, t0, steps) in enumerate(lines):
        y = top + i * LH + 17
        if kind == "gap":
            continue
        if kind == "cmd":
            out.append(f'<g opacity="0">{mono(x, y, PROMPT, p["dim"])}'
                       f'{anim("opacity", [0, 1], [0, t0], cycle)}</g>')
            still.append(mono(x, y, PROMPT, p["dim"]))
            if text:
                clips.append(
                    f'<clipPath id="c{i}"><rect x="{x + pw:.1f}" y="{y - 17}" height="{LH}" width="0">'
                    f'{anim("width", [0] + [round((n + 1) * CW, 1) for n in range(len(text))], [0] + steps, cycle)}'
                    f'</rect></clipPath>')
                out.append(f'<g clip-path="url(#c{i})">{mono(x + pw, y, text, p["text"])}</g>')
                still.append(mono(x + pw, y, text, p["text"]))
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
            out.append(f'<g opacity="0">{mono(x, y, text, fill)}'
                       f'{anim("opacity", [0, 1], [0, t0], cycle)}</g>')
            still.append(mono(x, y, text, fill))

    t = idle_at
    while t < cycle:
        cur_o.append(len(cur_o) % 2)
        cur_ot.append(t)
        t += BLINK_S

    last_y = top + (len(lines) - 1) * LH + 17
    box = f'x="{x + pw:.1f}" y="{last_y - 14}" width="{CW}" height="18" rx="1" fill="{p["text"]}"'
    cursor = (f'<rect {box} opacity="0">{anim("x", cur_x, cur_xt, cycle)}'
              f'{anim("y", cur_y, cur_yt, cycle)}{anim("opacity", cur_o, cur_ot, cycle)}</rect>')
    still.append(f'<rect {box}/>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{TW + MARGIN * 2}" height="{TH + MARGIN * 2}" viewBox="0 0 {TW + MARGIN * 2} {TH + MARGIN * 2}" role="img" aria-labelledby="t d">
<title id="t">kevin, security researcher and builder</title>
<desc id="d">A macOS terminal window typing out a zsh session: whoami returns "kevin, security researcher and builder"; the principles are that files stay on your machine, with no upload, no telemetry and no build step, and that a report should be one a developer can act on rather than a severity number; the projects are convert.in, qr.in, snipsearch and stelegraphy; the security focus is authorization, SSRF and exposed configuration; the stack is typescript, node, powershell, python, burp, docker and k8s.</desc>
<style>
.m {{ {MONO} font-size: {FS}px; }}
.u {{ {UI} font-size: 13px; font-weight: 600; }}
.still {{ display: none; }}
@media (prefers-reduced-motion: reduce) {{
  .typed {{ display: none; }}
  .still {{ display: inline; }}
}}
</style>
<defs>{"".join(clips)}</defs>
{head}
<text class="u" x="{MARGIN + TW / 2}" y="{MARGIN + 19}" text-anchor="middle" fill="{p["title"]}">kevin · zsh · 90×20</text>
<g class="typed">
{chr(10).join(out)}
{cursor}
</g>
<g class="still">
{chr(10).join(still)}
</g>
{tail}
</svg>
'''


# --------------------------------------------------------------------------
# finder
# --------------------------------------------------------------------------

FW, FH, FBAR, SIDE = 900, 344, 52, 180      # 900 / 344 = 2.6163, golden ratio squared
ROW, HEADER, STATUS = 26, 25, 24

SIDEBAR = ["AirDrop", "Recents", "Applications", "Desktop", "Documents", "projects"]
FILES = [
    ("convert.in", "TypeScript", "#3178c6", "1.3 MB", "Sep 3, 2026 at 00:28"),
    ("qr.in", "HTML", "#e34c26", "229 KB", "Sep 4, 2026 at 07:49"),
    ("snipsearch", "PowerShell", "#5391fe", "29 KB", "Sep 4, 2026 at 00:08"),
    ("stelegraphy", "TypeScript", "#3178c6", "380 KB", "Sep 3, 2026 at 10:26"),
]


def folder(x, y, s=16, tint="#4d9dfb"):
    """A Finder folder glyph, drawn on a 16 unit grid and scaled."""
    k = s / 16
    return (f'<g transform="translate({x},{y}) scale({k:.3f})">'
            f'<path d="M0 3.5a2 2 0 0 1 2-2h4l1.6 1.6H14a2 2 0 0 1 2 2V13a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2Z" '
            f'fill="{tint}"/><path d="M0 6h16v7a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2Z" fill="{tint}" '
            f'fill-opacity="0.75"/></g>')


def side_glyph(name, x, y, tint):
    """Simplified SF Symbols for the sidebar, each on a 16 unit grid."""
    g = {
        "AirDrop": f'<circle cx="{x + 8}" cy="{y + 9}" r="6.5" fill="none" stroke="{tint}" stroke-width="1.5"/>'
                   f'<circle cx="{x + 8}" cy="{y + 9}" r="2.5" fill="{tint}"/>',
        "Recents": f'<circle cx="{x + 8}" cy="{y + 8}" r="7" fill="none" stroke="{tint}" stroke-width="1.5"/>'
                   f'<path d="M{x + 8} {y + 4}v4.5l3 2" fill="none" stroke="{tint}" stroke-width="1.5" stroke-linecap="round"/>',
        "Applications": f'<rect x="{x + 1}" y="{y + 1}" width="14" height="14" rx="4" fill="none" stroke="{tint}" stroke-width="1.5"/>'
                        f'<circle cx="{x + 8}" cy="{y + 8}" r="2.2" fill="{tint}"/>',
        "Desktop": f'<rect x="{x + 1}" y="{y + 2}" width="14" height="9.5" rx="1.6" fill="none" stroke="{tint}" stroke-width="1.5"/>'
                   f'<path d="M{x + 5} {y + 14}h6" stroke="{tint}" stroke-width="1.5" stroke-linecap="round"/>',
        "Documents": f'<path d="M{x + 3} {y + 1.5}h6l4 4v9a1.5 1.5 0 0 1-1.5 1.5h-8.5A1.5 1.5 0 0 1 {x + 1.5} {y + 14.5}v-11.5A1.5 1.5 0 0 1 {x + 3} {y + 1.5}Z" '
                     f'fill="none" stroke="{tint}" stroke-width="1.5"/>',
    }
    return g.get(name, folder(x, y + 1, 15, tint))


def toolbar_glyph(x, y, kind, tint):
    """View switcher segments: icon grid, list, columns, gallery."""
    if kind == "grid":
        return "".join(f'<rect x="{x + 3 + c * 5}" y="{y + 3 + r * 5}" width="3.4" height="3.4" rx="1" fill="{tint}"/>'
                       for r in range(2) for c in range(2))
    if kind == "list":
        return "".join(f'<path d="M{x + 3} {y + 4 + n * 4}h10" stroke="{tint}" stroke-width="1.6" stroke-linecap="round"/>'
                       for n in range(3))
    if kind == "columns":
        return "".join(f'<path d="M{x + 3 + n * 4.5} {y + 3}v10" stroke="{tint}" stroke-width="1.6" stroke-linecap="round"/>'
                       for n in range(3))
    return (f'<rect x="{x + 2.5}" y="{y + 3}" width="11" height="6.5" rx="1.4" fill="none" stroke="{tint}" stroke-width="1.5"/>'
            f'<path d="M{x + 5} {y + 12.5}h6" stroke="{tint}" stroke-width="1.5" stroke-linecap="round"/>')


def finder(p):
    head, tail = chrome(p, FW, FH, FBAR)
    ox = oy = MARGIN
    cx = ox + SIDE
    body = [head]

    # sidebar, drawn inside the window clip so it keeps the rounded corner
    body.append(f'<rect x="{ox}" y="{oy + FBAR}" width="{SIDE}" height="{FH - FBAR}" fill="{p["side"]}"/>')
    body.append(f'<text class="s" x="{ox + 18}" y="{oy + FBAR + 24}" fill="{p["dim"]}">Favorites</text>')
    for n, item in enumerate(SIDEBAR):
        y = oy + FBAR + 34 + n * 28
        on = item == "projects"
        if on:
            body.append(f'<rect x="{ox + 8}" y="{y}" width="{SIDE - 16}" height="24" rx="6" fill="{p["sel"]}"/>')
        tint = "#ffffff" if on else p["sel"]
        body.append(side_glyph(item, ox + 18, y + 4, tint))
        body.append(f'<text class="b" x="{ox + 42}" y="{y + 16}" fill="{"#ffffff" if on else p["text"]}">{item}</text>')

    # column headers
    hy = oy + FBAR
    body.append(f'<rect x="{cx}" y="{hy}" width="{FW - SIDE}" height="{HEADER}" fill="{p["body"]}"/>')
    for sx in (292, 432, 532):
        body.append(f'<path d="M{cx + sx} {hy + 5}v{HEADER - 10}" stroke="{p["hair"]}" stroke-width="1"/>')
    body.append(f'<text class="s" x="{cx + 14}" y="{hy + 17}" fill="{p["text"]}">Name</text>')
    body.append(f'<path d="M{cx + 55} {hy + 14}l3.5-4 3.5 4" fill="none" stroke="{p["dim"]}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(f'<text class="s" x="{cx + 302}" y="{hy + 17}" fill="{p["dim"]}">Tags</text>')
    body.append(f'<text class="s" x="{cx + 520}" y="{hy + 17}" text-anchor="end" fill="{p["dim"]}">Size</text>')
    body.append(f'<text class="s" x="{cx + 544}" y="{hy + 17}" fill="{p["dim"]}">Date Modified</text>')
    body.append(f'<path d="M{cx} {hy + HEADER}h{FW - SIDE}" stroke="{p["hair"]}" stroke-width="1"/>')

    # rows
    for n, (name, tag, colour, size, date) in enumerate(FILES):
        y = hy + HEADER + n * ROW
        if n % 2:
            body.append(f'<rect x="{cx}" y="{y}" width="{FW - SIDE}" height="{ROW}" fill="{p["alt"]}"/>')
        body.append(folder(cx + 14, y + 5))
        body.append(f'<text class="b" x="{cx + 38}" y="{y + 17}" fill="{p["text"]}">{name}</text>')
        body.append(f'<circle cx="{cx + 306}" cy="{y + 13}" r="4.5" fill="{colour}"/>')
        body.append(f'<text class="b" x="{cx + 318}" y="{y + 17}" fill="{p["dim"]}">{tag}</text>')
        body.append(f'<text class="b" x="{cx + 520}" y="{y + 17}" text-anchor="end" fill="{p["dim"]}">{size}</text>')
        body.append(f'<text class="b" x="{cx + 544}" y="{y + 17}" fill="{p["dim"]}">{date}</text>')

    # status bar
    sy = oy + FH - STATUS
    body.append(f'<rect x="{ox}" y="{sy}" width="{FW}" height="{STATUS}" fill="{p["bar"]}"/>')
    body.append(f'<path d="M{ox} {sy}h{FW}" stroke="{p["hair"]}" stroke-width="1"/>')
    body.append(f'<text class="s" x="{ox + FW / 2}" y="{sy + 16}" text-anchor="middle" fill="{p["dim"]}">4 items, 843.2 GB available</text>')
    body.append(f'<path d="M{cx} {oy + FBAR}v{FH - FBAR}" stroke="{p["hair"]}" stroke-width="1"/>')
    body.append(tail)

    # toolbar sits above the clip so its glyphs stay crisp
    tb = [f'<path d="M{ox + 96} {oy + 20}l-5 6 5 6" fill="none" stroke="{p["dim"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
          f'<path d="M{ox + 122} {oy + 20}l5 6-5 6" fill="none" stroke="{p["dim"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
          folder(ox + FW / 2 - 48, oy + 18, 15),
          f'<text class="t" x="{ox + FW / 2 - 26}" y="{oy + 31}" fill="{p["title"]}">projects</text>']
    vx = ox + FW - 232
    tb.append(f'<rect x="{vx}" y="{oy + 15}" width="88" height="23" rx="6" fill="{p["body"]}" fill-opacity="0.6" stroke="{p["hair"]}" stroke-width="1"/>')
    for n, kind in enumerate(("grid", "list", "columns", "gallery")):
        gx = vx + 3 + n * 21
        if kind == "list":
            tb.append(f'<rect x="{gx}" y="{oy + 17.5}" width="19" height="18" rx="5" fill="{p["hair"]}" fill-opacity="0.9"/>')
        tb.append(toolbar_glyph(gx + 2, oy + 19, kind, p["title"] if kind == "list" else p["dim"]))
    for n in range(3):  # group, share, more
        gx = ox + FW - 128 + n * 34
        tb.append(f'<circle cx="{gx}" cy="{oy + 26}" r="11" fill="{p["body"]}" fill-opacity="0.45"/>')
    tb.append(f'<path d="M{ox + FW - 133} {oy + 22}h10M{ox + FW - 133} {oy + 26}h10M{ox + FW - 133} {oy + 30}h6" stroke="{p["dim"]}" stroke-width="1.6" stroke-linecap="round"/>')
    tb.append(f'<path d="M{ox + FW - 94} {oy + 31}v-9m0-9 4 4m-4-4-4 4" fill="none" stroke="{p["dim"]}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" transform="translate(0,4)"/>')
    tb.append("".join(f'<circle cx="{ox + FW - 65 + n * 5}" cy="{oy + 26}" r="1.6" fill="{p["dim"]}"/>' for n in range(3)))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{FW + MARGIN * 2}" height="{FH + MARGIN * 2}" viewBox="0 0 {FW + MARGIN * 2} {FH + MARGIN * 2}" role="img" aria-labelledby="t d">
<title id="t">The projects folder in Finder</title>
<desc id="d">A macOS Finder window in list view showing four folders: convert.in, tagged TypeScript, 1.3 MB, modified Sep 3 2026; qr.in, tagged HTML, 229 KB, modified Sep 4 2026; snipsearch, tagged PowerShell, 29 KB, modified Sep 4 2026; and stelegraphy, tagged TypeScript, 380 KB, modified Sep 3 2026.</desc>
<style>
.t {{ {UI} font-size: 13px; font-weight: 600; }}
.b {{ {UI} font-size: 13px; }}
.s {{ {UI} font-size: 11px; font-weight: 500; }}
</style>
{"".join(body)}
{"".join(tb)}
</svg>
'''


# --------------------------------------------------------------------------
# dock icons
# --------------------------------------------------------------------------

ICON, PAD = 96, 12                          # 96 x 0.2237 = 21.5 corner radius, per Apple's squircle
W_ICON, H_ICON = ICON + PAD * 2, ICON + PAD * 2 + 18

GLYPHS = {
    "convert": ('#ff7a5a', '#e8452f',
                '<g fill="none" stroke="#fff" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round">'
                '<path d="M22 36h48m-13-13 13 13-13 13"/><path d="M74 62H26m13-13-13 13 13 13"/></g>'),
    "qr": ('#4a4a4e', '#1c1c1e',
           '<g fill="none" stroke="#fff" stroke-width="5">'
           '<rect x="20" y="20" width="24" height="24" rx="6"/><rect x="52" y="20" width="24" height="24" rx="6"/>'
           '<rect x="20" y="52" width="24" height="24" rx="6"/></g>'
           '<g fill="#fff"><rect x="28" y="28" width="8" height="8" rx="2"/><rect x="60" y="28" width="8" height="8" rx="2"/>'
           '<rect x="28" y="60" width="8" height="8" rx="2"/><rect x="52" y="52" width="9" height="9" rx="2"/>'
           '<rect x="67" y="52" width="9" height="9" rx="2"/><rect x="52" y="67" width="9" height="9" rx="2"/>'
           '<rect x="67" y="67" width="9" height="9" rx="2"/></g>'),
    "snipsearch": ('#b07bff', '#6e3bd8',
                   '<rect x="18" y="18" width="44" height="44" rx="8" fill="none" stroke="#fff" stroke-width="4.5" stroke-dasharray="9 7" stroke-linecap="round"/>'
                   '<circle cx="62" cy="62" r="13" fill="none" stroke="#fff" stroke-width="5.5"/>'
                   '<path d="M71.5 71.5 80 80" stroke="#fff" stroke-width="6.5" stroke-linecap="round"/>'),
    "stelegraphy": ('#4ade80', '#12a150',
                    '<g fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">'
                    '<path d="M32 18v60"/><path d="M32 20h16l8 12-8 12H32"/><path d="m46 44 18 34"/></g>'),
    "mail": ('#6fb6ff', '#1e70e0',
             '<rect x="18" y="28" width="60" height="42" rx="7" fill="#fff"/>'
             '<path d="m22 34 26 20 26-20" fill="none" stroke="#1e70e0" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'),
}


def icon(name, label):
    a, b, glyph = GLYPHS[name]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W_ICON}" height="{H_ICON}" viewBox="0 0 {W_ICON} {H_ICON}" role="img" aria-label="{label}">
<defs>
<linearGradient id="g" x1="0" y1="0" x2="0.35" y2="1">
<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/>
</linearGradient>
<filter id="sh" x="-30%" y="-30%" width="160%" height="160%">
<feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#000000" flood-opacity="0.28"/>
</filter>
</defs>
<style>.l {{ {UI} font-size: 12px; }}</style>
<g filter="url(#sh)"><rect x="{PAD}" y="{PAD}" width="{ICON}" height="{ICON}" rx="21.5" fill="url(#g)"/></g>
<g transform="translate({PAD},{PAD})">{glyph}</g>
<text class="l" x="{W_ICON / 2}" y="{ICON + PAD + 15}" text-anchor="middle" fill="#8a8a8f">{label}</text>
</svg>
'''


DOCK = [("convert", "convert.in"), ("qr", "qr.in"), ("snipsearch", "snipsearch"),
        ("stelegraphy", "stelegraphy"), ("mail", "email")]

if __name__ == "__main__":
    for name, palette in THEMES:
        for part, render in (("hero", terminal), ("finder", finder)):
            path = f"assets/{part}-{name}.svg"
            with open(path, "w") as f:
                f.write(render(palette))
            print(path)
    for name, label in DOCK:
        path = f"assets/icon-{name}.svg"
        with open(path, "w") as f:
            f.write(icon(name, label))
        print(path)
