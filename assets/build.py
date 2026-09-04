"""Generate the macOS desktop pieces used by the profile README.

Two components share one palette and one window chrome:

  hero-<theme>.svg    an animated zsh session, 900x556  (1 : 1.618)
  finder-<theme>.svg  one Finder window cycling projects, focus and toolbox,
                      900x344  (1 : 2.618)

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
from datetime import date, timedelta

MARGIN, RADIUS, FRADIUS = 34, 16, 26   # Tahoe rounds hard, and rounds windows with a toolbar harder
GAP = MARGIN * 2                       # the space between the two windows, 68, set here not in the README
LIGHTS = [("#ed6a5f", "#e24b41"), ("#f6be50", "#e1a73e"), ("#61c555", "#2dac2f")]

LIGHT = dict(body="#ffffff", bar="#ececec", side="#f2f2f2", alt="#fafafa",
             edge="#c9c9c9", hair="#dcdcde", title="#1d1d1f", text="#1d1d1f",
             dim="#6e6e73", key="#0071e3", sel="#0071e3", shadow=0.22, rim=0.5)
DARK = dict(body="#1e1e1e", bar="#333336", side="#252527", alt="#232325",
            edge="#ffffff", hair="#3a3a3d", title="#f5f5f7", text="#f2f2f2",
            dim="#98989d", key="#4aa8ff", sel="#0a84ff", shadow=0.55, rim=0.14)
THEMES = (("light", LIGHT), ("dark", DARK))

UI = ('font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, '
      '"Helvetica Neue", "Segoe UI", Arial, sans-serif;')
MONO = ('font-family: "SF Mono", SFMono-Regular, ui-monospace, Menlo, Monaco, '
        '"Cascadia Mono", "DejaVu Sans Mono", "Liberation Mono", "Courier New", monospace;')


def chrome(p, w, h, bar, radius=RADIUS, bar_x0=0):
    """Shadowed rounded window, clipped so the bar and sidebar keep the corners."""
    ox = oy = MARGIN
    head = (f'<defs><clipPath id="win"><rect x="{ox}" y="{oy}" width="{w}" height="{h}" rx="{radius}"/></clipPath>'
            f'<filter id="sh" x="-30%" y="-30%" width="160%" height="160%">'
            f'<feDropShadow dx="0" dy="9" stdDeviation="13" flood-color="#000000" flood-opacity="{p["shadow"]}"/>'
            f'</filter>'
            f'<linearGradient id="spec" x1="0" y1="{oy}" x2="0" y2="{oy + 40}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#ffffff" stop-opacity="0.16"/>'
            f'<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
            f'</linearGradient></defs>'
            f'<g filter="url(#sh)"><rect x="{ox}" y="{oy}" width="{w}" height="{h}" rx="{radius}" fill="{p["body"]}"/></g>'
            f'<g clip-path="url(#win)"><rect x="{ox + bar_x0}" y="{oy}" width="{w - bar_x0}" height="{bar}" fill="{p["bar"]}"/>')
    dots = "".join(f'<circle cx="{ox + 20 + n * 20}" cy="{oy + 26 if bar > 40 else oy + bar / 2}" r="6" '
                   f'fill="{f}" stroke="{s}" stroke-width="0.5"/>' for n, (f, s) in enumerate(LIGHTS))
    # the window rim, then the specular edge Liquid Glass carries, fading out of
    # the top corners rather than stopping dead at them
    tail = (f'</g>{dots}'
            f'<rect x="{ox + 0.5}" y="{oy + 0.5}" width="{w - 1}" height="{h - 1}" rx="{radius}" '
            f'fill="none" stroke="{p["edge"]}" stroke-opacity="{p["rim"]}" stroke-width="1"/>'
            f'<rect x="{ox + 0.5}" y="{oy + 0.5}" width="{w - 1}" height="{h - 1}" rx="{radius}" '
            f'fill="none" stroke="url(#spec)" stroke-width="1"/>')
    return head, tail


# --------------------------------------------------------------------------
# terminal
# --------------------------------------------------------------------------

TW, TH, TBAR = 900, 556, 28     # 900 / 556 = 1.6187
PAD_X, PAD_TOP = 34, 21
FS, LH, CW = 15, 24, 9.0        # 15 x 1.618 = 24 line height, 15 x 0.6 = 9 advance
CHAR_S, ENTER_S, OUT_S, BLANK_S = 0.075, 0.28, 0.26, 0.13
START_S, HOLD_S, BLINK_S = 0.6, 4.8, 0.53
PROMPT = "kevin@pradith ~ % "   # zsh with PROMPT='%n@%m %1~ %# '

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


def reveal(t0, cycle, fade=0.18):
    """A line arrives on a curve rather than snapping on, ready exactly at t0."""
    times = [0, max(t0 - fade, 0) / cycle, t0 / cycle, 1]
    return (f'<animate attributeName="opacity" calcMode="spline" values="0;0;1;1" '
            f'keyTimes="{";".join(f"{t:.5f}" for t in times)}" '
            f'keySplines="{FADE_EASE};{FADE_EASE};{FADE_EASE}" dur="{cycle}s" repeatCount="indefinite"/>')


def mono(x, y, text, fill):
    return (f'<text x="{x:.1f}" y="{y}" class="m" fill="{fill}" xml:space="preserve" '
            f'textLength="{len(text) * CW:.1f}" lengthAdjust="spacingAndGlyphs">'
            f'{html.escape(text)}</text>')


def terminal(p):
    lines, cycle, idle_at = schedule()
    head, tail = chrome(p, TW, TH, TBAR)
    bar_line = f'<line x1="{MARGIN}" y1="{MARGIN + TBAR}" x2="{MARGIN + TW}" y2="{MARGIN + TBAR}" stroke="{p["hair"]}" stroke-width="1"/>'
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
            out.append(f'<g opacity="0">{mono(x, y, PROMPT, p["dim"])}{reveal(t0, cycle)}</g>')
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
            out.append(f'<g opacity="0">{mono(x, y, text, fill)}{reveal(t0, cycle)}</g>')
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
{bar_line}
<text class="u" x="{MARGIN + TW / 2}" y="{MARGIN + 19}" text-anchor="middle" fill="{p["title"]}">kevin@pradith · zsh · 90×20</text>
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
# finder, drawn to match macOS 26 Tahoe
# --------------------------------------------------------------------------
#
# Tahoe replaced Sequoia's tight window corners with a much larger radius, and
# a window carrying a toolbar rounds harder still, so Finder uses FRADIUS while
# the terminal keeps the smaller radius Terminal.app kept. The sidebar and the
# toolbar are one Liquid Glass layer: the sidebar runs the full height of the
# window, up behind the traffic lights, and the toolbar sits on the same plane
# with no rule under it. Toolbar buttons now always show their grouped capsule
# rather than appearing on hover, and inner radii are concentric with the
# window, so the capsules and the selection pills stay in the same family.

FW, FH, FBAR, SIDE = 900, 344, 52, 170      # 900 / 344 = 2.6163, golden ratio squared
ROW, HEADER = 24, 24
SPAD, SRADIUS = 10, 16                      # Tahoe floats the sidebar as a nested window

SIDEBAR = ["AirDrop", "Recents", "Applications",
           "projects", "certifications", "awards"]

# projects keeps the columns Finder shows by default. The other folders swap
# Size for Comments, so nothing on screen is invented: every date, credential
# and placement below is the real one.
FOLDERS = {
    "projects": dict(
        icon="folder", disclosure=True,
        columns=[("Name", 50, "start"), ("Date Modified", 300, "start"),
                 ("Size", 550, "end"), ("Tags", 574, "start")],
        rules=[290, 460, 560],
        rows=[("convert.in", "Sep 3, 2026 at 00:28", "1.3 MB", ("TypeScript", "#3178c6")),
              ("qr.in", "Sep 4, 2026 at 07:49", "229 KB", ("HTML", "#e34c26")),
              ("snipsearch", "Sep 4, 2026 at 00:08", "29 KB", ("PowerShell", "#5391fe")),
              ("stelegraphy", "Sep 3, 2026 at 10:26", "380 KB", ("TypeScript", "#3178c6"))]),
    "certifications": dict(
        icon="doc", disclosure=False,
        columns=[("Name", 50, "start"), ("Kind", 330, "start"),
                 ("Date Modified", 460, "start"), ("Comments", 600, "start")],
        rules=[320, 450, 590],
        rows=[("aws-cloud-genai.pdf", "Dicoding", "Feb 2026", "2VX302O83XYQ"),
              ("azure-genai.pdf", "Dicoding", "Apr 2026", "0LZ0YR3LNX65"),
              ("backend-javascript.pdf", "Dicoding", "Feb 2026", "L4PQ93142PO1"),
              ("javascript-dasar.pdf", "Dicoding", "Feb 2026", "KEXLQ313WPG2"),
              ("microsoft-fabric.pdf", "Dicoding", "Mar 2026", "4EXG1NYVDPRL"),
              ("python-dasar.pdf", "Dicoding", "Apr 2026", "KEXLQ78KWPG2")]),
    "awards": dict(
        icon="doc", disclosure=False,
        columns=[("Name", 50, "start"), ("Kind", 300, "start"),
                 ("Date Modified", 430, "start"), ("Comments", 545, "start")],
        rules=[290, 420, 535],
        rows=[("technotainment-uiux.pdf", "1st place", "Jul 2026", "Trunojoyo Madura"),
              ("iofest-webdev.pdf", "1st place", "Jun 2026", "Tarumanagara"),
              ("lks-cybersecurity.pdf", "2nd place", "Jun 2026", "Disdik Jawa Barat"),
              ("ibfest-cyberlite.pdf", "2nd place", "May 2026", "Telkomsel"),
              ("samsung-ai.pdf", "Winner", "May 2026", "Samsung Indonesia"),
              ("ehax-ctf.pdf", "Top 88 of 887", "Mar 2026", "Delhi Technological University"),
              ("jhic-infra.pdf", "Semi-finalist", "Nov 2025", "Jagoan Hosting")]),
}

FINDER_LIGHT = dict(body="#ffffff", bar="#f0f0f2", panel="#f6f6f8", alt="#f7f7f8", btn="#e4e4e7",
                    edge="#c9c9cd", hair="#dcdcde", title="#1d1d1f", text="#1d1d1f",
                    dim="#6e6e73", head="#8a8a8e", glyph="#3c3c3f", sel="#0a63fe",
                    shadow=0.22, rim=0.5)
FINDER_DARK = dict(body="#1f1f21", bar="#2a2a2d", panel="#303033", alt="#252528", btn="#3a3a3e",
                   edge="#ffffff", hair="#3a3a3d", title="#f5f5f7", text="#f5f5f7",
                   dim="#98989d", head="#8e8e93", glyph="#d8d8dc", sel="#0a63fe",
                   shadow=0.55, rim=0.14)
FINDER_THEMES = (("light", FINDER_LIGHT), ("dark", FINDER_DARK))


def folder(x, y, s=16, tint="#4d9dfb"):
    """A Finder folder glyph, drawn on a 16 unit grid and scaled."""
    k = s / 16
    return (f'<g transform="translate({x},{y}) scale({k:.3f})">'
            f'<path d="M0 3.5a2 2 0 0 1 2-2h4l1.6 1.6H14a2 2 0 0 1 2 2V13a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2Z" '
            f'fill="{tint}"/><path d="M0 6h16v7a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2Z" fill="{tint}" '
            f'fill-opacity="0.75"/></g>')


def row_icon(kind, x, y, p):
    """Folder, text document or app icon, each on a 16 unit grid."""
    if kind == "folder":
        return folder(x, y)
    if kind == "doc":
        return (f'<path d="M{x + 2} {y + 1}h7l4 4v10a1 1 0 0 1-1 1H{x + 2}a1 1 0 0 1-1-1V{y + 2}a1 1 0 0 1 1-1Z" '
                f'fill="{p["body"]}" stroke="{p["dim"]}" stroke-width="1.1"/>'
                f'<path d="M{x + 9} {y + 1}v4h4" fill="none" stroke="{p["dim"]}" stroke-width="1.1"/>'
                + "".join(f'<path d="M{x + 4} {y + 7 + n * 2.6}h6.5" stroke="{p["dim"]}" stroke-width="1"/>'
                          for n in range(3)))
    return (f'<rect x="{x + 1}" y="{y + 1}" width="14" height="14" rx="4.4" fill="{p["sel"]}" fill-opacity="0.9"/>'
            f'<circle cx="{x + 8}" cy="{y + 8}" r="2.6" fill="#ffffff"/>')


def side_glyph(name, x, y, tint):
    """Simplified SF Symbols for the sidebar, each on a 16 unit grid."""
    g = {
        "AirDrop": f'<circle cx="{x + 8}" cy="{y + 9}" r="6.5" fill="none" stroke="{tint}" stroke-width="1.5"/>'
                   f'<circle cx="{x + 8}" cy="{y + 9}" r="2.5" fill="{tint}"/>',
        "Recents": f'<circle cx="{x + 8}" cy="{y + 8}" r="7" fill="none" stroke="{tint}" stroke-width="1.5"/>'
                   f'<path d="M{x + 8} {y + 4}v4.5l3 2" fill="none" stroke="{tint}" stroke-width="1.5" stroke-linecap="round"/>',
        "Applications": f'<path d="M{x + 2.5} {y + 13.5}l5.5-11 5.5 11" fill="none" stroke="{tint}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
                        f'<path d="M{x + 5.2} {y + 9.5}h5.6" stroke="{tint}" stroke-width="1.6" stroke-linecap="round"/>',
        "Desktop": f'<rect x="{x + 1}" y="{y + 2}" width="14" height="9.5" rx="1.6" fill="none" stroke="{tint}" stroke-width="1.5"/>'
                   f'<path d="M{x + 5} {y + 14}h6" stroke="{tint}" stroke-width="1.5" stroke-linecap="round"/>',
        "Documents": f'<path d="M{x + 3} {y + 1.5}h6l4 4v9a1.5 1.5 0 0 1-1.5 1.5h-8.5A1.5 1.5 0 0 1 {x + 1.5} {y + 14.5}v-11.5A1.5 1.5 0 0 1 {x + 3} {y + 1.5}Z" '
                     f'fill="none" stroke="{tint}" stroke-width="1.5"/>',
    }
    return g.get(name, folder(x, y + 1, 15, tint))


def capsule(p, x, y, w, h=28, r=None):
    """Tahoe shows toolbar button groups all the time, and rounds them fully."""
    r = h / 2 if r is None else r
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{p["btn"]}" fill-opacity="0.85"/>'


def tool_glyph(p, kind, x, y):
    """SF Symbols in the toolbar, each drawn around a 16 unit box at x, y."""
    c, sw = p["glyph"], 1.6
    if kind == "list":
        return "".join(f'<circle cx="{x + 2}" cy="{y + 3 + n * 5}" r="1.1" fill="{c}"/>'
                       f'<path d="M{x + 6} {y + 3 + n * 5}h9" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>'
                       for n in range(3))
    if kind == "sort":
        return (f'<path d="M{x + 4} {y + 5}l3-3.5 3 3.5" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
                f'<path d="M{x + 4} {y + 9}l3 3.5 3-3.5" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    if kind == "group":
        return ("".join(f'<rect x="{x + 1 + col * 5.5}" y="{y + 2 + row * 5.5}" width="4" height="4" rx="1.2" fill="{c}"/>'
                        for row in range(2) for col in range(3))
                + f'<path d="M{x + 19} {y + 6}l2.5 3 2.5-3" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    if kind == "share":
        return (f'<path d="M{x + 8} {y + 11}V{y + 1}m0 0-3.5 3.5M{x + 8} {y + 1}l3.5 3.5" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
                f'<path d="M{x + 3} {y + 7}H{x + 1.5}v7.5h13V{y + 7}H{x + 13}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    if kind == "tag":
        return (f'<path d="M{x + 1.5} {y + 2.5}h6.5l6.5 6.5-6.5 6-6.5-6.5Z" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linejoin="round"/>'
                f'<circle cx="{x + 5}" cy="{y + 6}" r="1.4" fill="{c}"/>')
    if kind == "more":
        return ("".join(f'<circle cx="{x + 2 + n * 5}" cy="{y + 8}" r="1.5" fill="{c}"/>' for n in range(3))
                + f'<circle cx="{x + 7} " cy="{y + 8}" r="8" fill="none" stroke="{c}" stroke-width="1.3" stroke-opacity="0.7"/>')
    return (f'<circle cx="{x + 7} " cy="{y + 7}" r="5.5" fill="none" stroke="{c}" stroke-width="{sw}"/>'
            f'<path d="M{x + 11} {y + 11}l4 4" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>')


DWELL = 4.0                      # seconds each folder stays selected
KEYS = list(FOLDERS)
CYCLE = DWELL * len(KEYS)


# SwiftUI's smooth spring settles without overshoot, so movement decelerates
# hard and stops, while a cross dissolve wants a symmetric curve. Neither list
# may end in a semicolon: Chrome drops the whole animation if it does.
EASE = "0 0 0.58 1"              # the plain ease-out, still used by the graph
FADE_EASE = "0.4 0 0.2 1"        # symmetric, for opacity
MOVE_EASE = "0.32 0.72 0 1"      # spring-like, for anything that travels
FADE, SLIDE, DRIFT = 0.36, 0.5, 6.0


def keyframes(attr, values, times, splines, dur, extra=""):
    v = ";".join(str(x) for x in values)
    k = ";".join(f"{t:.5f}" for t in times)
    s = ";".join(splines)
    return (f'<{"animateTransform" if attr == "translate" else "animate"} '
            f'attributeName="{"transform" if attr == "translate" else attr}"'
            f'{" type=\"translate\"" if attr == "translate" else ""} calcMode="spline" '
            f'values="{v}" keyTimes="{k}" keySplines="{s}" dur="{dur}s" '
            f'repeatCount="indefinite"{extra}/>')


def show(i):
    """Pane i holds its slot, then cross dissolves with the pane taking over."""
    if i == 0:
        values, times = [1, 1, 0, 0, 1], [0, (DWELL - FADE) / CYCLE, DWELL / CYCLE,
                                          (CYCLE - FADE) / CYCLE, 1]
    else:
        a, b = i * DWELL, (i + 1) * DWELL
        values, times = [0, 0, 1, 1, 0, 0], [0, (a - FADE) / CYCLE, a / CYCLE,
                                             (b - FADE) / CYCLE, b / CYCLE, 1]
    return keyframes("opacity", values, times, [FADE_EASE] * (len(values) - 1), CYCLE)


def settle(i):
    """The listing arrives from DRIFT below and settles as it fades in."""
    down, home = f"0 {DRIFT}", "0 0"
    if i == 0:
        values = [home, home, down, home]
        times = [0, DWELL / CYCLE, (CYCLE - FADE) / CYCLE, 1]
    else:
        a, b = i * DWELL, (i + 1) * DWELL
        values = [down, down, home, home, down]
        times = [0, (a - FADE) / CYCLE, a / CYCLE, b / CYCLE, 1]
    return keyframes("translate", values, times, [MOVE_EASE] * (len(values) - 1), CYCLE)


def pill_track(y_of):
    """One selection pill for the whole window, sliding row to row."""
    values, times, splines = [], [], []
    for i in range(len(KEYS)):
        y = y_of(KEYS[i])
        values += [y, y]
        times += [i * DWELL / CYCLE, ((i + 1) * DWELL - SLIDE) / CYCLE]
        splines += [MOVE_EASE, MOVE_EASE]
    values.append(y_of(KEYS[0]))
    times.append(1.0)
    return keyframes("y", values, times, splines[:len(values) - 1], CYCLE)


def cycled(parts, mover=None):
    """Wrap one fragment per folder so exactly one shows at a time."""
    out = ['<g class="cycle">']
    for i, part in enumerate(parts):
        extra = mover(i) if mover else ""
        out.append(f'<g opacity="{1 if i == 0 else 0}">{show(i)}<g>{extra}{part}</g></g>')
    out.append(f'</g><g class="still">{parts[0]}</g>')
    return "".join(out)


def pane(p, key):
    """The white sidebar label for one folder, then its column headers and rows."""
    spec = FOLDERS[key]
    ox = oy = MARGIN
    cx = ox + SIDE
    sy = oy + FBAR + 32 + SIDEBAR.index(key) * 28
    label = (side_glyph(key, ox + SPAD + 14, sy + 5, "#ffffff")
             + f'<text class="b" x="{ox + SPAD + 38}" y="{sy + 17}" fill="#ffffff">{key}</text>')

    out = []
    hy = oy + FBAR
    for sx in spec["rules"]:
        out.append(f'<path d="M{cx + sx} {hy + 6}v{HEADER - 12}" stroke="{p["hair"]}" stroke-width="1"/>')
    for lbl, lx, anchor in spec["columns"]:
        out.append(f'<text class="s" x="{cx + lx}" y="{hy + 17}" text-anchor="{anchor}" fill="{p["dim"]}">{lbl}</text>')
    out.append(f'<path d="M{cx + spec["rules"][0] - 18} {hy + 14}l3.5-4 3.5 4" fill="none" stroke="{p["dim"]}" '
               f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')

    for n, cells in enumerate(spec["rows"]):
        y = hy + HEADER + n * ROW
        if n % 2:
            out.append(f'<rect x="{cx}" y="{y}" width="{FW - SIDE}" height="{ROW}" fill="{p["alt"]}"/>')
        if spec["disclosure"]:
            out.append(f'<path d="M{cx + 14} {y + 8}l4 4-4 4" fill="none" stroke="{p["dim"]}" stroke-width="1.5" '
                       f'stroke-linecap="round" stroke-linejoin="round"/>')
        out.append(row_icon(spec["icon"], cx + 26, y + 4, p))
        out.append(f'<text class="b" x="{cx + 50}" y="{y + 16}" fill="{p["text"]}">{cells[0]}</text>')
        for (lbl, lx, anchor), value in zip(spec["columns"][1:], cells[1:]):
            if isinstance(value, tuple):      # a Finder tag: coloured dot plus name
                out.append(f'<circle cx="{cx + lx + 4}" cy="{y + 12}" r="4.5" fill="{value[1]}"/>')
                out.append(f'<text class="b" x="{cx + lx + 16}" y="{y + 16}" fill="{p["dim"]}">{value[0]}</text>')
            else:
                out.append(f'<text class="b" x="{cx + lx}" y="{y + 16}" text-anchor="{anchor}" '
                           f'fill="{p["dim"]}">{html.escape(value)}</text>')
    return label, "".join(out)


def finder(p):
    """One window whose selection walks the sidebar, a folder every DWELL seconds."""
    head, tail = chrome(p, FW, FH, FBAR, FRADIUS)   # the toolbar glass runs the full width
    ox = oy = MARGIN
    cx = ox + SIDE
    body = [head]

    # Tahoe floats the sidebar as a nested window inside the glass, so it is a
    # rounded panel inset from the edges rather than a column flush to them
    px, pw = ox + SPAD, SIDE - SPAD - 8
    py, ph = oy + FBAR, FH - FBAR - SPAD
    body.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="{SRADIUS}" fill="{p["panel"]}"/>')
    body.append(f'<rect x="{px + 0.5}" y="{py + 0.5}" width="{pw - 1}" height="{ph - 1}" rx="{SRADIUS}" '
                f'fill="none" stroke="{p["hair"]}" stroke-opacity="0.8" stroke-width="1"/>')
    body.append(f'<text class="s" x="{px + 14}" y="{py + 22}" fill="{p["head"]}">Favourites</text>')

    def row_y(item):
        return py + 32 + SIDEBAR.index(item) * 28

    for item in SIDEBAR:
        y = row_y(item)
        body.append(side_glyph(item, px + 14, y + 5, "#4d9dfb"))
        body.append(f'<text class="b" x="{px + 38}" y="{y + 17}" fill="{p["text"]}">{item}</text>')

    # the selection is one pill that travels, rather than three that blink
    body.append(f'<rect class="cycle" x="{px + 6}" y="{row_y(KEYS[0])}" width="{pw - 12}" height="26" '
                f'rx="13" fill="{p["sel"]}">{pill_track(row_y)}</rect>')
    body.append(f'<rect class="still" x="{px + 6}" y="{row_y(KEYS[0])}" width="{pw - 12}" height="26" '
                f'rx="13" fill="{p["sel"]}"/>')

    body.append(f'<path d="M{cx} {oy + FBAR + HEADER}h{FW - SIDE}" stroke="{p["hair"]}" stroke-width="1"/>')
    panes = [pane(p, key) for key in KEYS]
    body.append(cycled([label for label, _ in panes]))
    body.append(cycled([listing for _, listing in panes], settle))
    body.append(tail)

    # toolbar, above the clip so the glyphs stay crisp
    tb = [capsule(p, cx + 12, oy + 12, 66),
          f'<path d="M{cx + 32} {oy + 20}l-5 6 5 6" fill="none" stroke="{p["glyph"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
          f'<path d="M{cx + 58} {oy + 20}l5 6-5 6" fill="none" stroke="{p["glyph"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
          cycled([f'<text class="w" x="{cx + 96}" y="{oy + 32}" fill="{p["title"]}">{key}</text>' for key in KEYS])]
    groups = [("list", "sort"), ("group",), ("share",), ("tag",), ("more",), ("search",)]
    gx = ox + FW - 14
    for names in reversed(groups):
        w = 30 * len(names) + 14
        gx -= w
        tb.append(capsule(p, gx, oy + 12, w))
        for n, name in enumerate(names):
            tb.append(tool_glyph(p, name, gx + 7 + n * 30, oy + 18))
        gx -= 8

    listing = ". ".join(
        key + " holds " + ", ".join(row[0] for row in FOLDERS[key]["rows"]) for key in KEYS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{FW + MARGIN * 2}" height="{FH + MARGIN * 2}" viewBox="0 0 {FW + MARGIN * 2} {FH + MARGIN * 2}" role="img" aria-labelledby="t d">
<title id="t">A Finder window walking through {", ".join(KEYS[:-1])} and {KEYS[-1]}</title>
<desc id="d">A macOS Tahoe Finder window in list view. The sidebar selection slides from one folder to the next every {DWELL:.0f} seconds and the listing cross dissolves with it. {html.escape(listing)}.</desc>
<style>
.w {{ {UI} font-size: 13px; font-weight: 600; }}
.b {{ {UI} font-size: 13px; }}
.s {{ {UI} font-size: 11px; font-weight: 500; }}
.still {{ display: none; }}
@media (prefers-reduced-motion: reduce) {{
  .cycle {{ display: none; }}
  .still {{ display: inline; }}
}}
</style>
{"".join(body)}
{"".join(tb)}
</svg>
'''


# --------------------------------------------------------------------------
# contributions
# --------------------------------------------------------------------------
#
# GitHub draws its own calendar on the profile page and a README cannot restyle
# it, so this is the same data as a Tahoe panel: a glass title bar over the
# grid, cells carrying the concentric radius the windows use, and a specular
# sweep crossing once a cycle the way Liquid Glass catches light. The levels
# are real, read on 5 Sep 2026 and refreshed with
#
#   curl -s https://github.com/users/kevinpradith/contributions
#
# taking data-level off each ContributionCalendar-day cell. One string a week,
# Sunday first, "_" where the calendar carries no day.

GTOTAL, GSTART = 848, date(2025, 8, 31)
WEEKS = [
    "0000000", "0000000", "0000000", "0100000", "0000000", "0000001",
    "0000000", "0110100", "0000000", "0000000", "0100010", "0000000",
    "0000000", "0000000", "0000000", "0000000", "0000000", "0000000",
    "0000000", "0000000", "0000000", "0010100", "1122101", "1101100",
    "0111101", "0100000", "0001100", "0000000", "0000000", "1110111",
    "0011111", "1210010", "1011101", "1210100", "0233400", "0000000",
    "0011011", "1111101", "3111100", "0000000", "0001100", "0000000",
    "0000000", "0000000", "0000000", "0000000", "0000000", "0000010",
    "1100000", "0000000", "0000011", "0311100", "011123_",
]

GW, GH, GBAR = 900, 212, 28          # 900 / 212 = 4.25, near the golden ratio cubed
LABEL, GPAD = 34, 34                 # weekday gutter, then the terminal's own padding
GRID_W = GW - GPAD * 2 - LABEL
GAP = 3.2                            # 53 columns land exactly on the grid width
STEP = (GRID_W + GAP) / 53
CELL = STEP - GAP
REVEAL, GFADE = 0.03, 0.5            # a column every 30ms, each fading in over 500ms
SWEEP, SWEEP_IN = 7.0, 1.7           # then a specular pass every 7s, crossing in 1.7s

GRAPH_LIGHT = dict(empty="#ebedf0", scale=["#9be9a8", "#40c463", "#30a14e", "#216e39"])
GRAPH_DARK = dict(empty="#2b2b2e", scale=["#0e4429", "#006d32", "#26a641", "#39d353"])
GRAPHS = {"light": GRAPH_LIGHT, "dark": GRAPH_DARK}


def graph(p, g):
    head, tail = chrome(p, GW, GH, GBAR)
    ox = oy = MARGIN
    gx = ox + GPAD + LABEL
    gy = oy + GBAR + 26
    grid_h = 7 * STEP - GAP
    fill_in = round(0.4 + len(WEEKS) * REVEAL + GFADE, 2)   # the year draws once, then stays

    body = [head]
    body.append(f'<line x1="{ox}" y1="{oy + GBAR}" x2="{ox + GW}" y2="{oy + GBAR}" stroke="{p["hair"]}" stroke-width="1"/>')

    # a month label above the first column that opens a new month, as GitHub does
    seen = GSTART.month
    for i in range(len(WEEKS)):
        d = GSTART + timedelta(days=7 * i)
        if d.month != seen:
            seen = d.month
            body.append(f'<text class="g" x="{gx + i * STEP:.1f}" y="{gy - 9}" fill="{p["dim"]}">{d.strftime("%b")}</text>')
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        body.append(f'<text class="g" x="{ox + GPAD}" y="{gy + row * STEP + CELL - 2:.1f}" fill="{p["dim"]}">{name}</text>')

    cells, still, tiles = [], [], []
    for i, week in enumerate(WEEKS):
        col = []
        for row, lvl in enumerate(week):
            if lvl == "_":
                continue
            fill = g["empty"] if lvl == "0" else g["scale"][int(lvl) - 1]
            box = (f'x="{gx + i * STEP:.1f}" y="{gy + row * STEP:.1f}" '
                   f'width="{CELL:.2f}" height="{CELL:.2f}" rx="3.5"')
            col.append(f'<rect {box} fill="{fill}"/>')
            tiles.append(f'<rect {box}/>')
        still.extend(col)
        t = 0.4 + i * REVEAL
        cells.append(f'<g opacity="1">{"".join(col)}<animate attributeName="opacity" calcMode="spline" '
                     f'values="0;0;1;1" keyTimes="0;{t / fill_in:.5f};{(t + GFADE) / fill_in:.5f};1" '
                     f'keySplines="{FADE_EASE};{FADE_EASE};{FADE_EASE}" dur="{fill_in}s" '
                     f'repeatCount="1" fill="freeze"/></g>')
    body.append(f'<g class="cycle">{"".join(cells)}</g><g class="still">{"".join(still)}</g>')

    # the year holds, and the only thing that repeats is the specular pass, a
    # slow highlight crossing the finished grid the way light crosses glass
    body.append(f'<g class="cycle" clip-path="url(#tiles)"><rect y="{gy}" width="96" height="{grid_h:.1f}" fill="url(#sweep)" x="{gx - 220:.0f}" transform="skewX(-14)">'
                f'<animate attributeName="x" values="{gx - 220:.0f};{gx + GRID_W + 70:.0f};{gx + GRID_W + 70:.0f}" '
                f'keyTimes="0;{SWEEP_IN / SWEEP:.5f};1" calcMode="spline" keySplines="0.4 0 0.2 1;0 0 1 1" '
                f'begin="{fill_in}s" dur="{SWEEP}s" repeatCount="indefinite"/></rect></g>')

    ly = gy + grid_h + 24
    body.append(f'<text class="g" x="{gx}" y="{ly:.1f}" fill="{p["dim"]}">{GTOTAL} contributions in the last year</text>')
    lx = ox + GW - GPAD - 5 * STEP - 34
    body.append(f'<text class="g" x="{lx - 8:.1f}" y="{ly:.1f}" text-anchor="end" fill="{p["dim"]}">Less</text>')
    for n, fill in enumerate([g["empty"]] + g["scale"]):
        body.append(f'<rect x="{lx + n * STEP:.1f}" y="{ly - 10:.1f}" width="{CELL}" height="{CELL}" rx="3.5" fill="{fill}"/>')
    body.append(f'<text class="g" x="{lx + 5 * STEP + 6:.1f}" y="{ly:.1f}" fill="{p["dim"]}">More</text>')
    body.append(tail)

    end = (GSTART + timedelta(days=7 * len(WEEKS) - 1)).strftime("%d %B %Y")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{GW + MARGIN * 2}" height="{GH + MARGIN * 2}" viewBox="0 0 {GW + MARGIN * 2} {GH + MARGIN * 2}" role="img" aria-labelledby="t d">
<title id="t">{GTOTAL} contributions in the last year</title>
<desc id="d">The GitHub contribution calendar for the year ending {end}, {GTOTAL} contributions in all, drawn as a macOS panel. The weeks fill in from left to right.</desc>
<defs>
<clipPath id="tiles">{"".join(tiles)}</clipPath>
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>
<stop offset="0.5" stop-color="#ffffff" stop-opacity="0.18"/>
<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
</linearGradient>
</defs>
<style>
.u {{ {UI} font-size: 13px; font-weight: 600; }}
.g {{ {UI} font-size: 11px; }}
.still {{ display: none; }}
@media (prefers-reduced-motion: reduce) {{
  .cycle {{ display: none; }}
  .still {{ display: inline; }}
}}
</style>
{"".join(body)}
<text class="u" x="{MARGIN + GW / 2}" y="{MARGIN + 19}" text-anchor="middle" fill="{p["title"]}">contributions</text>
</svg>
'''


if __name__ == "__main__":
    for name, palette in THEMES:
        with open(f"assets/hero-{name}.svg", "w") as f:
            f.write(terminal(palette))
        print(f"assets/hero-{name}.svg")
    for name, palette in FINDER_THEMES:
        path = f"assets/finder-{name}.svg"
        with open(path, "w") as f:
            f.write(finder(palette))
        print(path)
    for name, palette in THEMES:
        path = f"assets/graph-{name}.svg"
        with open(path, "w") as f:
            f.write(graph(palette, GRAPHS[name]))
        print(path)
