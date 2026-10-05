#!/usr/bin/env python3
"""Draws the live profile cards (assets/profile/activity.svg, more.svg).

Called daily by generate_stats.py with fresh GitHub numbers. Hand-written
SVG so GitHub renders it without any third-party card service.
"""
import os
from xml.sax.saxutils import escape as esc

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "profile")

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"
GOLD, GOLD_HI, GOLD_LO = "#A78BFA", "#F472B6", "#7C3AED"
TEXT, SUB, MUTED = "#F1ECFF", "#C4B8E6", "#8B80A8"
PANEL = "#130C24"
GREEN, BLUE, AMBER = "#34D399", "#67E8F9", "#FBBF24"

ICONS = {
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    "repo": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"/>',
    "star": '<path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><path d="M16 3.128a4 4 0 0 1 0 7.744"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><circle cx="9" cy="7" r="4"/>',
    "trend": '<path d="M16 7h6v6"/><path d="m22 7-8.5 8.5-5-5L2 17"/>',
    "code": '<path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/>',
    "github": '<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>',
    "zap": '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
}

def icon(name, x, y, size=20, color=GOLD_HI, width=1.8):
    s = size / 24
    return (f'<g transform="translate({x} {y}) scale({s:.4f})" fill="none" stroke="{color}" '
            f'stroke-width="{width / s:.2f}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')

def t(x, y, s, size=16, fill=TEXT, weight=400, anchor="start", ls=0, family=SANS, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{s}</text>')

def tw(s, size, ls=0, k=0.56):
    """Rough text width for layout."""
    return len(s) * (size * k + ls)

def card(x, y, w, h, rx=14, glow=False):
    g = f' filter="url(#glow)"' if glow else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{PANEL}" fill-opacity=".85" '
            f'stroke="url(#goldLine)" stroke-opacity=".55"{g}/>')

def pill(x, y, label, color=GOLD_HI, size=11, h=24, anchor="start", fill_op=".1"):
    w = tw(label, size, 1.2, 0.62) + 24
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    return (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{color}" fill-opacity="{fill_op}" '
            f'stroke="{color}" stroke-opacity=".6"/>'
            + t(f"{x + w / 2:.1f}", y + h / 2 + size * 0.36, esc(label), size, color, 700, "middle", 1.2, MONO), w)

def icon_box(x, y, name, size=46):
    return (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="11" fill="{GOLD}" fill-opacity=".08" '
            f'stroke="{GOLD}" stroke-opacity=".5"/>' + icon(name, x + size / 2 - 11, y + size / 2 - 11, 22))


DEFS = f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0A0806"/><stop offset=".5" stop-color="#120E0A"/><stop offset="1" stop-color="#1C160E"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{GOLD_HI}"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_LO}"/></linearGradient>
<linearGradient id="goldLine" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD_HI}"/><stop offset=".5" stop-color="{GOLD_LO}" stop-opacity=".35"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{GOLD_HI}" stop-opacity="0"/><stop offset=".5" stop-color="#FFF8E7" stop-opacity=".10"/><stop offset="1" stop-color="{GOLD_HI}" stop-opacity="0"/></linearGradient>
<radialGradient id="halo"><stop offset="0" stop-color="{GOLD}" stop-opacity=".35"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{GOLD}" stroke-opacity=".05"/></pattern>
</defs>"""

DEFS = f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0B0716"/><stop offset=".55" stop-color="#110A20"/><stop offset="1" stop-color="#160E2A"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#A78BFA"/><stop offset=".5" stop-color="#C084FC"/><stop offset="1" stop-color="#F472B6"/></linearGradient>
<linearGradient id="goldLine" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#A78BFA"/><stop offset=".5" stop-color="#7C3AED" stop-opacity=".35"/><stop offset="1" stop-color="#F472B6"/></linearGradient>
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C084FC" stop-opacity="0"/><stop offset=".5" stop-color="#F5E8FF" stop-opacity=".09"/><stop offset="1" stop-color="#C084FC" stop-opacity="0"/></linearGradient>
<radialGradient id="halo"><stop offset="0" stop-color="#A78BFA" stop-opacity=".38"/><stop offset="1" stop-color="#F472B6" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#A78BFA" stroke-opacity=".06"/></pattern>
</defs>"""

def frame(w, h, body, title=None, subtitle=None, sweep=True):
    head = ""
    if title:
        head = (t(w / 2, 62, esc(title), 34, TEXT, 700, "middle")
                + f'<rect x="{w / 2 - 70}" y="78" width="140" height="3" rx="1.5" fill="url(#gold)"/>'
                + t(w / 2, 104, esc(subtitle.upper()), 12, MUTED, 600, "middle", 4, MONO))
    sw = ""
    if sweep:
        sw = (f'<rect x="-{w}" y="0" width="{w * 0.6:.0f}" height="{h}" fill="url(#sweep)">'
              f'<animate attributeName="x" from="-{w}" to="{w * 1.4:.0f}" dur="7s" repeatCount="indefinite"/></rect>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
{DEFS}
<clipPath id="clip"><rect width="{w}" height="{h}" rx="22"/></clipPath>
<g clip-path="url(#clip)"><rect width="{w}" height="{h}" fill="url(#bg)"/><rect width="{w}" height="{h}" fill="url(#grid)"/>{sw}</g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="21" fill="none" stroke="url(#goldLine)" stroke-opacity=".6" stroke-width="1.5"/>
{head}{body}
</svg>
"""


# ---------------------------------------------------------------- sections

def activity(stats):
    W, H = 690, 600
    b = []
    cards = [("flame", f'{stats["total_contributions"]:,}', "Contributions"), ("repo", str(stats["public_repos"]), "Public repos"),
             ("star", str(stats["total_stars"]), "Stars"), ("users", str(stats["followers"]), "Followers"),
             ("trend", f'{stats["longest_streak"]}d', "Longest streak"), ("zap", f'{stats["current_streak"]}d', "Current streak")]
    cw = (610 - 2 * 14) / 3
    for i, (ic, v, label) in enumerate(cards):
        x, y = 40 + (i % 3) * (cw + 14), 132 + (i // 3) * 86
        b += [card(x, y, cw, 72, 12), icon_box(x + 14, y + 14, ic, 44),
              t(x + 70, y + 38, v, 22, GOLD_HI, 800), t(x + 70, y + 57, label, 11.5, MUTED)]
    b.append(card(40, 316, 610, 248, 12))
    b.append(t(64, 350, "MOST USED LANGUAGES", 11.5, MUTED, 600, ls=3, family=MONO))
    colors = [GOLD_HI, GOLD, BLUE, GREEN]
    for i, (name, pct) in enumerate((l["name"], l["pct"]) for l in stats["languages"]):
        y = 386 + i * 46
        wv = 562 * pct / 100
        b += [t(64, y, name, 14.5, TEXT, 600), t(626, y, f"{pct}%", 14.5, colors[i], 700, "end"),
              f'<rect x="64" y="{y + 11}" width="562" height="6" rx="3" fill="#fff" fill-opacity=".06"/>',
              f'<rect x="64" y="{y + 11}" width="{wv:.1f}" height="6" rx="3" fill="{colors[i]}">'
              f'<animate attributeName="width" from="0" to="{wv:.1f}" dur="1.4s" begin="{i * .15}s" fill="freeze"/></rect>']
    return frame(W, H, "".join(b), "GitHub Activity", "Profile signal")

def more_strip(repos):
    W, H = 1400, 120
    b = [icon_box(40, 32, "github", 56),
         t(116, 58, "More on GitHub", 24, TEXT, 800),
         t(116, 86, "Frappe apps, client projects, experiments and this profile itself.", 15, SUB)]
    s, w = pill(1080, 46, f"{repos} PUBLIC REPOS", GOLD_HI, 11, 28, anchor="end")
    b.append(s)
    b += [f'<rect x="1110" y="38" width="250" height="44" rx="22" fill="url(#gold)"/>',
          t(1235, 66, "BROWSE REPOS ↗", 14, "#0B0716", 800, "middle", 2, MONO)]
    return frame(W, H, "".join(b))

def render_live_cards(stats):
    """Write activity.svg and more.svg from a generate_stats.py data dict."""
    os.makedirs(OUT_DIR, exist_ok=True)
    cards = {"activity": activity(stats), "more": more_strip(stats["public_repos"])}
    for name, svg in cards.items():
        with open(os.path.join(OUT_DIR, f"{name}.svg"), "w") as f:
            f.write(svg)
    return sorted(cards)
