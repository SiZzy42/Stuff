"""Generate the Doletin Mechanical poster HTML files from info.json.

Run:  python3 build.py && node render.js
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).parent
INFO = json.loads((HERE / "info.json").read_text())

# Trim size 18 x 24 in + 0.125 in bleed on every side.
W_IN, H_IN = 18.25, 24.25

FONTS = """
@font-face { font-family: Anton; src: url(fonts/Anton.ttf); }
@font-face { font-family: Oswald; font-weight: 400; src: url(fonts/Oswald-400.ttf); }
@font-face { font-family: Oswald; font-weight: 600; src: url(fonts/Oswald-600.ttf); }
@font-face { font-family: Oswald; font-weight: 700; src: url(fonts/Oswald-700.ttf); }
@font-face { font-family: Barlow; font-weight: 500; src: url(fonts/Barlow-500.ttf); }
@font-face { font-family: Barlow; font-weight: 700; src: url(fonts/Barlow-700.ttf); }
@font-face { font-family: Barlow; font-weight: 800; src: url(fonts/Barlow-800.ttf); }
@font-face { font-family: Archivo; src: url(fonts/ArchivoBlack.ttf); }
"""

BASE_CSS = f"""
@page {{ size: {W_IN}in {H_IN}in; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: {W_IN}in; height: {H_IN}in; overflow: hidden; }}
.poster {{ position: relative; width: {W_IN}in; height: {H_IN}in; overflow: hidden; }}
"""


# ---------------------------------------------------------------- icons ----
# All icons use a 64x64 viewBox and draw in currentColor.
S = 'fill="none" stroke="currentColor" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"'


def wrench_shape(uid):
    """Filled open-end wrench pointing up, centred on (32,32), length ~60."""
    return f"""
    <mask id="wm{uid}"><rect x="-10" y="-10" width="84" height="84" fill="#fff"/>
      <rect x="27.5" y="-2" width="9" height="15" rx="1.5" fill="#000"/>
      <circle cx="32" cy="55" r="3.2" fill="#000"/></mask>
    <g mask="url(#wm{uid})" fill="currentColor">
      <circle cx="32" cy="12" r="11"/>
      <rect x="27" y="14" width="10" height="44" rx="5"/>
      <circle cx="32" cy="55" r="7"/>
    </g>"""


ICONS = {
    "brakes": f"""<g {S}><circle cx="32" cy="32" r="24"/><circle cx="32" cy="32" r="8"/>
        <circle cx="32" cy="17" r="1.5"/><circle cx="47" cy="32" r="1.5"/><circle cx="32" cy="47" r="1.5"/><circle cx="17" cy="32" r="1.5"/></g>
        <path d="M44 9 A26 26 0 0 1 58 26" fill="none" stroke="currentColor" stroke-width="9" stroke-linecap="round"/>""",
    "oil": f"""<g {S}><path d="M32 6 C26 16 14 28 14 40 a18 18 0 0 0 36 0 C50 28 38 16 32 6z"/>
        <path d="M24 42 a8 8 0 0 0 8 8"/></g>""",
    "diagnostics": f"""<g {S}><path d="M8 44 A24 24 0 1 1 56 44"/><path d="M32 40 L44 24"/>
        <circle cx="32" cy="40" r="3" fill="currentColor"/><path d="M14 30 l4 2 M32 18 v4 M50 30 l-4 2"/><path d="M20 54 h24"/></g>""",
    "tires": f"""<g {S}><circle cx="32" cy="32" r="25" stroke-width="8"/><circle cx="32" cy="32" r="9"/>
        <path d="M32 23 V14 M40.5 35 l8 3 M23.5 35 l-8 3 M37 39.5 l5 7 M27 39.5 l-5 7"/></g>""",
    "battery": f"""<g {S}><rect x="6" y="18" width="52" height="36" rx="4"/><path d="M14 18 v-6 h8 v6 M42 18 v-6 h8 v6"/>
        <path d="M14 36 h10 M19 31 v10 M40 36 h10"/></g>""",
    "suspension": f"""<g {S}><path d="M14 8 h36 M14 56 h36"/>
        <path d="M32 8 v4 L46 16 L18 22 L46 28 L18 34 L46 40 L18 46 L32 50 v6"/></g>""",
    "snowflake": f"""<g {S}><path d="M32 4 V60 M7.8 18 L56.2 46 M7.8 46 L56.2 18"/>
        <path d="M24 8 l8 7 8-7 M24 56 l8-7 8 7 M8 28 l10 1 -4 -9 M56 36 l-10 -1 4 9 M8 36 l10 -1 -4 9 M56 28 l-10 1 4 -9"/></g>""",
    "thermo": f"""<g {S}><path d="M26 38 V12 a6 6 0 0 1 12 0 V38 a11 11 0 1 1 -12 0z"/>
        <path d="M32 24 V44" stroke-width="6"/><path d="M44 14 h8 M44 22 h6 M44 30 h8"/></g>""",
    "wiper": f"""<g {S}><path d="M6 50 A28 28 0 0 1 58 50"/><path d="M32 52 L14 22" stroke-width="5.5"/>
        <circle cx="32" cy="52" r="4" fill="currentColor"/></g>""",
    "lights": f"""<g {S}><path d="M30 14 C14 14 10 24 10 32 s4 18 20 18 z"/>
        <path d="M38 18 H58 M38 28 H58 M38 38 H58 M38 48 H58"/></g>""",
    "heater": f"""<g {S}><path d="M18 52 c-6-8 6-14 0-22 s6-14 0-22 M32 52 c-6-8 6-14 0-22 s6-14 0-22 M46 52 c-6-8 6-14 0-22 s6-14 0-22"/></g>""",
    "check": f"""<path d="M14 34 l12 12 L52 18" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>""",
}


def icon(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 64 64">{ICONS[name]}</svg>'


def gear_path(cx, cy, r_out, r_in, teeth, hole):
    """Gear outline (outer teeth + centre hole), evenodd."""
    pts = []
    for i in range(teeth):
        a0 = 2 * math.pi * i / teeth
        step = 2 * math.pi / teeth
        for frac, r in ((0.0, r_in), (0.12, r_out), (0.42, r_out), (0.54, r_in)):
            a = a0 + step * frac
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"
    d += f" M{cx + hole} {cy} A{hole} {hole} 0 1 0 {cx - hole} {cy} A{hole} {hole} 0 1 0 {cx + hole} {cy} Z"
    return d


def emblem(color_gear, color_wrench, bg):
    """Gear with two crossed wrenches. viewBox 0 0 200 200."""
    gear = gear_path(100, 100, 92, 76, 14, 46)
    return f"""<svg class="emblem" viewBox="0 0 200 200">
      <path d="{gear}" fill="{color_gear}" fill-rule="evenodd"/>
      <circle cx="100" cy="100" r="62" fill="none" stroke="{color_gear}" stroke-width="5"/>
      <g color="{bg}" transform="translate(100 100) rotate(45) translate(-62 -62) scale(1.94)">
        <g transform="translate(0 0)" stroke="{bg}" stroke-width="6">{wrench_shape('a')}</g></g>
      <g color="{bg}" transform="translate(100 100) rotate(-45) translate(-62 -62) scale(1.94)">
        <g stroke="{bg}" stroke-width="6">{wrench_shape('b')}</g></g>
      <g color="{color_wrench}" transform="translate(100 100) rotate(45) translate(-62 -62) scale(1.94)">{wrench_shape('c')}</g>
      <g color="{color_wrench}" transform="translate(100 100) rotate(-45) translate(-62 -62) scale(1.94)">{wrench_shape('d')}</g>
    </svg>"""


def page(title, css, body):
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>
<style>{FONTS}{BASE_CSS}{css}</style></head><body>{body}</body></html>"""


SERVICES = [
    ("brakes", "Brakes"),
    ("oil", "Oil Changes"),
    ("diagnostics", "Engine Diagnostics"),
    ("tires", "Tires & Alignment"),
    ("battery", "Batteries & Electrical"),
    ("suspension", "Suspension & Steering"),
]

# ------------------------------------------------------- poster 1: shop ----
P1_CSS = """
:root { --ink:#16181b; --orange:#ff6b12; --steel:#c9ced6; --white:#f7f7f5; }
.poster { background:
    radial-gradient(ellipse at 50% 28%, #2b2f35 0%, #16181b 62%),
    var(--ink); color: var(--white); }
.poster::before { content:""; position:absolute; inset:0;
  background: repeating-linear-gradient(135deg, rgba(255,255,255,.018) 0 2px, transparent 2px 14px); }
.hazard { position:absolute; left:0; right:0; height:0.95in;
  background: repeating-linear-gradient(-45deg, var(--orange) 0 0.55in, #0d0e10 0.55in 1.1in); }
.hazard.top { top:0; } .hazard.bot { bottom:0; }
.inner { position:absolute; top:1.35in; bottom:1.35in; left:0.9in; right:0.9in;
  display:flex; flex-direction:column; align-items:center; }
.emblem { width:3.9in; height:3.9in; margin-top:0.05in; filter: drop-shadow(0 0.08in 0.12in rgba(0,0,0,.5)); }
.name { font-family:Anton; font-size:300pt; line-height:0.86; letter-spacing:0.01em;
  margin-top:0.25in; color:var(--white); text-shadow: 0 0.06in 0 #000; }
.mech { font-family:Oswald; font-weight:600; font-size:96pt; letter-spacing:0.36em;
  margin-right:-0.36em; line-height:1; color:var(--orange); margin-top:0.12in; }
.tag { margin-top:0.4in; width:100%; background:var(--orange); color:#111;
  font-family:Barlow; font-weight:800; font-size:58pt; text-align:center; letter-spacing:0.08em;
  padding:0.12in 0 0.16in; transform: skewX(-8deg); }
.tag span { display:inline-block; transform: skewX(8deg); }
.services { margin-top:0.5in; width:100%; display:grid; grid-template-columns:repeat(3,1fr);
  row-gap:0.36in; column-gap:0.3in; }
.svc { display:flex; flex-direction:column; align-items:center; text-align:center; }
.svc .icon { width:1.2in; height:1.2in; color:var(--orange); }
.svc div { font-family:Barlow; font-weight:700; font-size:40pt; line-height:1.05; margin-top:0.12in;
  text-transform:uppercase; letter-spacing:0.03em; }
.cta { margin-top:auto; width:100%; text-align:center; }
.cta .call { font-family:Oswald; font-weight:600; font-size:44pt; letter-spacing:0.3em; color:var(--steel); }
.cta .phone { font-family:Anton; font-size:150pt; line-height:1; color:var(--orange); margin-top:0.04in; }
.cta .meta { font-family:Barlow; font-weight:500; font-size:36pt; color:var(--steel); margin-top:0.18in; letter-spacing:0.02em; }
"""


def poster1():
    svcs = "".join(f'<div class="svc">{icon(k)}<div>{v}</div></div>' for k, v in SERVICES)
    body = f"""<div class="poster">
  <div class="hazard top"></div><div class="hazard bot"></div>
  <div class="inner">
    {emblem('#ff6b12', '#f7f7f5', '#16181b')}
    <div class="name">DOLETIN</div>
    <div class="mech">MECHANICAL</div>
    <div class="tag"><span>HONEST REPAIRS · FAIR PRICES</span></div>
    <div class="services">{svcs}</div>
    <div class="cta">
      <div class="call">CALL TODAY</div>
      <div class="phone">{INFO['phone']}</div>
      <div class="meta">{INFO['address']}<br>{INFO['hours']}</div>
    </div>
  </div>
</div>"""
    return page("Doletin Mechanical – Shop", P1_CSS, body)


# ----------------------------------------------------- poster 2: winter ----
P2_CSS = """
:root { --navy:#0b1f33; --ice:#bfe6ff; --frost:#e9f6ff; --orange:#ff6b12; }
.poster { background: linear-gradient(180deg, #0f2a45 0%, #0b1f33 55%, #08172a 100%); color:var(--frost); }
.flakes { position:absolute; inset:0; }
.flakes svg { position:absolute; color:#ffffff; opacity:.07; }
.inner { position:absolute; top:1.1in; bottom:0.95in; left:1in; right:1in;
  display:flex; flex-direction:column; align-items:center; text-align:center; }
.brand { font-family:Oswald; font-weight:600; font-size:46pt; letter-spacing:0.32em; margin-right:-0.32em; color:var(--ice); }
.brand b { color:var(--orange); font-weight:700; }
.rule { width:3in; height:0.06in; background:var(--orange); margin:0.3in 0 0.3in; }
.q1 { font-family:Oswald; font-weight:600; font-size:120pt; line-height:1; letter-spacing:0.04em; color:#fff; }
.q2 { font-family:Anton; font-size:236pt; line-height:0.9; color:var(--ice); margin-top:0.08in;
  text-shadow: 0 0.07in 0 #05101c; }
.sub { font-family:Barlow; font-weight:500; font-size:42pt; margin-top:0.3in; color:var(--frost); line-height:1.25; }
.list { margin-top:0.5in; width:100%; display:grid; grid-template-columns:1fr 1fr; column-gap:0.45in; row-gap:0.28in; text-align:left; }
.item { display:flex; align-items:center; gap:0.28in; background:rgba(191,230,255,.07);
  border:0.03in solid rgba(191,230,255,.22); border-radius:0.18in; padding:0.18in 0.3in; }
.item .icon { width:0.95in; height:0.95in; color:var(--ice); flex:none; }
.item div { font-family:Barlow; font-weight:700; font-size:40pt; line-height:1.05; text-transform:uppercase; color:#fff; }
.cta { margin-top:auto; width:100%; background:var(--orange); color:#140a02; border-radius:0.25in;
  padding:0.3in 0.4in 0.35in; }
.cta .t { font-family:Oswald; font-weight:700; font-size:66pt; letter-spacing:0.06em; line-height:1.05; }
.cta .phone { font-family:Anton; font-size:150pt; line-height:1; margin-top:0.05in; color:#fff;
  text-shadow: 0 0.05in 0 rgba(0,0,0,.18); }
.meta { font-family:Barlow; font-weight:500; font-size:36pt; margin-top:0.3in; color:var(--ice); line-height:1.3; }
"""

WINTER = [
    ("battery", "Battery Test"),
    ("tires", "Tires & Tread"),
    ("thermo", "Coolant & Antifreeze"),
    ("brakes", "Brake Inspection"),
    ("wiper", "Wipers & Washer Fluid"),
    ("heater", "Heater & Defrost"),
]


def poster2():
    flakes = "".join(
        f'<svg viewBox="0 0 64 64" style="left:{x}in;top:{y}in;width:{s}in;height:{s}in;transform:rotate({r}deg)">{ICONS["snowflake"]}</svg>'
        for x, y, s, r in [(-1.2, 1.5, 5.5, 10), (13.6, -0.8, 6, 25), (14.8, 9.5, 3.2, 5), (-0.6, 11.5, 2.6, 30),
                           (5.2, 3.2, 1.5, 15), (1.5, 6.6, 1.4, 40), (15.6, 6.0, 1.5, 0), (3.6, 0.2, 1.1, 20)])
    items = "".join(f'<div class="item">{icon(k)}<div>{v}</div></div>' for k, v in WINTER)
    body = f"""<div class="poster">
  <div class="flakes">{flakes}</div>
  <div class="inner">
    <div class="brand"><b>DOLETIN</b> MECHANICAL</div>
    <div class="rule"></div>
    <div class="q1">IS YOUR RIDE</div>
    <div class="q2">WINTER READY?</div>
    <div class="sub">Don’t get left out in the cold.<br>Get your car checked before the first freeze.</div>
    <div class="list">{items}</div>
    <div class="cta">
      <div class="t">BOOK YOUR WINTER CHECK-UP</div>
      <div class="phone">{INFO['phone']}</div>
    </div>
    <div class="meta">{INFO['address']}<br>{INFO['hours']}</div>
  </div>
</div>"""
    return page("Doletin Mechanical – Winter", P2_CSS, body)


# ------------------------------------------------------ poster 3: retro ----
P3_CSS = """
:root { --cream:#f3ead6; --red:#c4161c; --ink:#1d2430; --tan:#d9c9a6; }
.poster { background: var(--cream); color: var(--ink); }
.poster::before { content:""; position:absolute; inset:0;
  background: radial-gradient(ellipse at center, transparent 55%, rgba(120,90,40,.12) 100%); }
.frame { position:absolute; inset:0.6in; border:0.09in solid var(--ink); }
.frame::after { content:""; position:absolute; inset:0.16in; border:0.03in solid var(--ink); }
.inner { position:absolute; top:1.15in; bottom:1.05in; left:1.2in; right:1.2in;
  display:flex; flex-direction:column; align-items:center; text-align:center; }
.badge { width:6.1in; height:6.1in; flex:none; }
.head { font-family:Archivo; font-size:136pt; line-height:0.95; color:var(--red); margin-top:0.2in; letter-spacing:-0.01em; }
.head small { display:block; font-size:62pt; color:var(--ink); letter-spacing:0.02em; margin-top:0.12in; }
.stars { display:flex; gap:0.45in; color:var(--red); margin:0.28in 0 0.22in; }
.stars svg { width:0.42in; height:0.42in; }
.svcs { width:100%; display:grid; grid-template-columns:1fr 1fr; column-gap:0.6in; row-gap:0.12in; }
.svcs div { font-family:Oswald; font-weight:600; font-size:44pt; text-transform:uppercase; letter-spacing:0.04em;
  border-bottom:0.03in dashed rgba(29,36,48,.35); padding:0.06in 0; display:flex; align-items:center; gap:0.2in; }
.svcs div::before { content:""; width:0.2in; height:0.2in; background:var(--red); transform:rotate(45deg); flex:none; }
.banner { margin-top:auto; flex:none; width:calc(100% + 0.6in); background:var(--red); color:var(--cream);
  padding:0.25in 0 0.32in; position:relative; }
.banner .t { font-family:Oswald; font-weight:600; font-size:42pt; letter-spacing:0.3em; margin-right:-0.3em; }
.banner .phone { font-family:Archivo; font-size:118pt; line-height:1.05; }
.meta { font-family:Oswald; font-weight:400; font-size:36pt; margin-top:0.3in; letter-spacing:0.04em; line-height:1.3; }
"""


def badge():
    gear = gear_path(200, 200, 196, 182, 36, 0.01)
    return f"""<svg class="badge" viewBox="0 0 400 400">
  <defs>
    <path id="arcTop" d="M 70 200 A 130 130 0 0 1 330 200"/>
    <path id="arcBot" d="M 43 200 A 157 157 0 0 0 357 200"/>
  </defs>
  <path d="{gear}" fill="#1d2430"/>
  <circle cx="200" cy="200" r="176" fill="#c4161c"/>
  <circle cx="200" cy="200" r="168" fill="none" stroke="#f3ead6" stroke-width="3"/>
  <circle cx="200" cy="200" r="104" fill="#f3ead6"/>
  <circle cx="200" cy="200" r="96" fill="none" stroke="#1d2430" stroke-width="3"/>
  <text font-family="Archivo" font-size="46" fill="#f3ead6" letter-spacing="4" text-anchor="middle">
    <textPath href="#arcTop" startOffset="50%">DOLETIN</textPath></text>
  <text font-family="Oswald" font-weight="600" font-size="30" fill="#f3ead6" letter-spacing="8" text-anchor="middle">
    <textPath href="#arcBot" startOffset="50%">MECHANICAL</textPath></text>
  <polygon points="{star_points(58, 201, 13)}" fill="#f3ead6"/>
  <polygon points="{star_points(342, 201, 13)}" fill="#f3ead6"/>
  <g color="#1d2430" transform="translate(200 200) rotate(45) translate(-73.6 -73.6) scale(2.3)">{wrench_shape('e')}</g>
  <g color="#c4161c" transform="translate(200 200) rotate(-45) translate(-73.6 -73.6) scale(2.3)">
    <g stroke="#f3ead6" stroke-width="5">{wrench_shape('f')}</g></g>
  <g color="#c4161c" transform="translate(200 200) rotate(-45) translate(-73.6 -73.6) scale(2.3)">{wrench_shape('g')}</g>
</svg>"""


def star_points(cx, cy, r):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return " ".join(pts)


STAR_SVG = f'<svg viewBox="0 0 20 20"><polygon points="{star_points(10, 10.6, 10)}" fill="currentColor"/></svg>'


RETRO_SVCS = ["Brakes", "Oil Changes", "Diagnostics", "Tires", "Batteries", "Tune-Ups", "Suspension", "A/C & Heat"]


def poster3():
    svcs = "".join(f"<div>{s}</div>" for s in RETRO_SVCS)
    body = f"""<div class="poster">
  <div class="frame"></div>
  <div class="inner">
    {badge()}
    <div class="head">WE FIX IT<br>RIGHT.<small>Auto repair you can trust</small></div>
    <div class="stars">{STAR_SVG * 3}</div>
    <div class="svcs">{svcs}</div>
    <div class="banner">
      <div class="t">CALL OR STOP BY</div>
      <div class="phone">{INFO['phone']}</div>
    </div>
    <div class="meta">{INFO['address']}<br>{INFO['hours']}</div>
  </div>
</div>"""
    return page("Doletin Mechanical – Retro", P3_CSS, body)


if __name__ == "__main__":
    for name, fn in [("1-shop", poster1), ("2-winter", poster2), ("3-retro", poster3)]:
        (HERE / f"poster-{name}.html").write_text(fn())
        print("wrote", f"poster-{name}.html")
