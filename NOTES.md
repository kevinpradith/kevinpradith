# Notes to self

This repo is my GitHub profile README. It is public because a profile repo has
to be, but it is not a project looking for contributors. These notes are here
so that six months from now I do not have to rediscover any of it.

## What is actually here

`README.md` is three centred `<picture>` blocks and a footer. Everything you
see on the profile is six self hosted animated SVG files, drawn to match real
macOS 26 Tahoe. No third party badge service, no shields.io, no
github-readme-stats. Nothing calls out to anyone.

`assets/build.py` is the only generator. It writes all six files:

```
hero-{light,dark}.svg     an animated zsh session, 900x556
finder-{light,dark}.svg   a Finder window cycling three folders, 900x344
graph-{light,dark}.svg    a year of contributions, 900x212
```

Window sizes are a deliberate chain, and `MARGIN` is 34, so stacked windows sit
68 apart and the README needs no `<br>` between them.

## Rebuilding

The GitHub API allows 60 calls an hour unauthenticated and this machine hits
that, so pass a token. Read it from the Windows credential manager and keep it
in a shell variable for one command. Never write it to a file.

```sh
TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' | GCM_INTERACTIVE=never \
  git -c credential.helper='!"/mnt/c/Program Files/Git/mingw64/bin/git-credential-manager.exe"' \
  credential fill 2>/dev/null | sed -n 's/^password=//p')
GITHUB_TOKEN="$TOKEN" python3 assets/build.py
```

**Bump `?v=` in README.md on every asset change.** GitHub caches the raw URLs
hard, and without a new query string the old drawing keeps showing.

## Editing the content

Project rows and the contribution numbers are read live at build time, so they
never go stale. The two folders with no API behind them, certifications and
awards, are typed by hand and live in `assets/data.json`. Edit that file, then
rebuild. Column positions and rules stay in `build.py`, because moving those is
a drawing decision and not data entry.

## The traps, all of them found the hard way

**A spline animation whose `keyTimes` do not end at exactly 1 is invalid, and
the renderer silently drops the whole thing.** `keyTimes` must start at 0, end
at 1 and match the `values` count, and `keySplines` must hold exactly one fewer
entry than `values`. Chrome also drops the animation if `keySplines` ends in a
semicolon. Run this after every change:

```sh
python3 - <<'PY'
import re
bad = 0
for f in ("hero-dark", "finder-dark", "graph-dark", "hero-light", "finder-light", "graph-light"):
    s = open(f'assets/{f}.svg').read()
    for m in re.finditer(r'<animate\w*[^>]*calcMode="spline"[^>]*>', s):
        t = m.group(0)
        kt = re.search(r'keyTimes="([^"]+)"', t).group(1).split(';')
        v = re.search(r'values="([^"]+)"', t).group(1).split(';')
        k = re.search(r'keySplines="([^"]+)"', t).group(1).split(';')
        if float(kt[0]) or abs(float(kt[-1]) - 1) > 1e-9 or len(kt) != len(v) or len(k) != len(v) - 1:
            print("INVALID", f, t[:130]); bad += 1
print("animations:", "OK" if not bad else bad)
PY
```

**If the artwork looks frozen, check the operating system before the code.**
Every animated group has a `.still` twin that takes over under
`@media (prefers-reduced-motion: reduce)`. Windows reports that whenever
Settings, Accessibility, Visual effects, Animation effects is off, and Chrome
passes it straight through, so the profile renders the static fallback and
nothing is wrong with the SVG at all. Confirm which one you are looking at:

```sh
powershell.exe -NoProfile -Command "Add-Type -Namespace W -Name U -MemberDefinition '[DllImport(\"user32.dll\")] public static extern bool SystemParametersInfo(uint a, uint b, ref bool c, uint d);'; \$v=\$false; [W.U]::SystemParametersInfo(0x1042,0,[ref]\$v,0) | Out-Null; \"ClientAreaAnimation=\$v\""
```

`False` means reduced motion, and the fallback is correct behaviour. Headless
Chrome reports reduced motion too, so a screenshot taken for review is always
the still frame unless the media query is stripped first.

**Animate transforms, never geometry.** The caret, the sidebar selection pill
and the contribution sweep all animate `animateTransform type="translate"`.
Animating `x`, `y` or `width` makes the renderer lay the element out again on
every frame.

**Monospace advance widths differ per family**, so terminal lines are pinned
with `textLength` plus `lengthAdjust="spacingAndGlyphs"`. Never switch to
`lengthAdjust="spacing"`, it opens gaps on Windows. Consolas is deliberately
out of the font stack.

**GitHub strips `<script>`, `<style>`, `class`, `id` and inline `style` from
README HTML**, but the SVGs are served straight from `raw.githubusercontent.com`
with no camo proxy in between, so their internal stylesheet and SMIL animation
both survive. Anything requiring a click inside the artwork does not: GitHub
renders the SVG as an `<img>`, so links, `:hover` and pointer events are dead
in there. The auto cycling Finder exists because of exactly that.

## Previewing

There is no browser in WSL, so drive the Windows one:

```sh
cp assets/*.svg /mnt/c/Users/Kevin/AppData/Local/Temp/heroshot/
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" --headless --disable-gpu \
  --hide-scrollbars --run-all-compositor-stages-before-draw --virtual-time-budget=1500 \
  --window-size=1010,460 \
  --screenshot="C:\Users\Kevin\AppData\Local\Temp\heroshot\out.png" \
  "file:///C:/Users/Kevin/AppData/Local/Temp/heroshot/finder-dark.svg"
```

`--run-all-compositor-stages-before-draw` is what makes SMIL frames land where
the budget says. Without it Chrome keeps screenshotting the frame at zero.
`--virtual-time-budget` must be an integer. Add `--force-device-scale-factor=4`
when checking a single glyph.

## The daily refresh

`.github/workflows/refresh.yml` runs the build at 05:17 UTC and commits only
when the drawing actually changed. It commits as me, so every refresh counts as
a contribution and the calendar will never show an empty day again. That was a
deliberate choice. The alternative, if it ever stops being worth it, is `on:
push` instead of the cron, which refreshes only on days I actually write code.

## Ruled out, do not try again

- Clicking anything inside the artwork. See the `<img>` note above.
- `<details>` and `<summary>` sections. They work, but the page jumps on every
  open and close.
- Restyling GitHub's own contribution calendar on the profile page. Not
  reachable from a README.
- Em dashes in the terminal title bar. Terminal really does use them, but five
  in one line reads as a row of rules.
