"""Inline SVG visualizations for martinkawalski.com. No patient or personal data."""

AMB = "#F2B866"
INK = "#F3EADC"
SOFT = "#C9BBA7"
DIM = "#8E7F6C"
LINE = "#3A2C20"
FONT = "font-family=\"Nunito Sans, Helvetica, Arial, sans-serif\""

# Sardinia outline, rough coastline as (lon, lat)
SARD = [(8.21, 40.97), (8.32, 41.05), (8.55, 40.85), (8.75, 40.92), (8.95, 41.03), (9.10, 41.14),
        (9.23, 41.25), (9.40, 41.20), (9.55, 41.10), (9.62, 40.95), (9.75, 40.75), (9.73, 40.55),
        (9.65, 40.30), (9.70, 40.05), (9.65, 39.85), (9.57, 39.55), (9.55, 39.25), (9.55, 39.13),
        (9.20, 39.20), (9.00, 39.08), (8.85, 38.88), (8.62, 38.90), (8.45, 39.05), (8.40, 39.25),
        (8.45, 39.55), (8.50, 39.75), (8.40, 39.90), (8.47, 40.10), (8.48, 40.30), (8.38, 40.45),
        (8.30, 40.55), (8.15, 40.62), (8.20, 40.80)]


def _xy(lon, lat):
    return 60 + (lon - 8.0) * 300, 40 + (41.4 - lat) * 390


def sardinia():
    pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in (_xy(*p) for p in SARD))
    ax, ay = _xy(8.32, 40.56)
    bx, by = _xy(9.45, 40.02)
    return f"""<svg viewBox="0 0 640 1000" role="img" aria-label="Map of Sardinia with Alghero and the mountain villages of Ogliastra marked">
<defs><radialGradient id="bz"><stop offset="0" stop-color="{AMB}" stop-opacity=".55"/><stop offset="1" stop-color="{AMB}" stop-opacity="0"/></radialGradient></defs>
<polygon points="{pts}" fill="#2a1d14" stroke="{AMB}" stroke-opacity=".55" stroke-width="2" stroke-linejoin="round"/>
<circle cx="{bx:.0f}" cy="{by:.0f}" r="120" fill="url(#bz)"><animate attributeName="r" values="105;130;105" dur="6s" repeatCount="indefinite"/></circle>
<circle cx="{bx:.0f}" cy="{by:.0f}" r="7" fill="{AMB}"/>
<text x="{bx-150:.0f}" y="{by+120:.0f}" fill="{INK}" font-size="26" font-weight="800" {FONT}>Ogliastra</text>
<text x="{bx-150:.0f}" y="{by+150:.0f}" fill="{SOFT}" font-size="20" {FONT}>mountain villages where</text>
<text x="{bx-150:.0f}" y="{by+174:.0f}" fill="{SOFT}" font-size="20" {FONT}>centenarians cluster</text>
<circle cx="{ax:.0f}" cy="{ay:.0f}" r="9" fill="{INK}"/><circle cx="{ax:.0f}" cy="{ay:.0f}" r="18" fill="none" stroke="{INK}" stroke-opacity=".5"/>
<text x="{ax+26:.0f}" y="{ay-6:.0f}" fill="{INK}" font-size="26" font-weight="800" {FONT}>Alghero</text>
<text x="{ax+26:.0f}" y="{ay+20:.0f}" fill="{SOFT}" font-size="20" {FONT}>our hospital partner</text>
<text x="80" y="960" fill="{DIM}" font-size="18" {FONT}>Sardinia. Next: Okinawa, Japan.</text>
</svg>"""


def _box(x, y, w, h, title, sub, n=None):
    num = f'<text x="{x+20}" y="{y+34}" fill="{AMB}" font-size="17" font-weight="800" {FONT}>{n}</text>' if n else ""
    ty = y + (62 if n else 44)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#1C140E" stroke="{LINE}" stroke-width="2"/>{num}'
            f'<text x="{x+20}" y="{ty}" fill="{INK}" font-size="24" font-weight="800" {FONT}>{title}</text>'
            f'<text x="{x+20}" y="{ty+30}" fill="{SOFT}" font-size="18" {FONT}>{sub}</text>')


def _arrow(x1, y1, x2, y2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{AMB}" stroke-width="2.5" stroke-dasharray="6 8" class="flow"/>'
            f'<circle cx="{x2}" cy="{y2}" r="5" fill="{AMB}"/>')


def bluenotte_steps():
    s = [("Visit", "at home, in the village"), ("Sensors", "ring or watch, under-mattress"), ("Interview", "days, meals, naps, people"), ("Analysis", "at Stanford, across sites")]
    out = []
    for k, (a, b) in enumerate(s):
        y = 40 + k * 150
        out.append(_box(40, y, 520, 110, a, b, f"0{k+1}"))
        if k < 3:
            out.append(_arrow(300, y + 110, 300, y + 150))
    return f'<svg viewBox="0 0 600 640" role="img" aria-label="How BlueNotte measures sleep: visit, sensors, interview, analysis">{"".join(out)}</svg>'


def tenzo():
    ins = [("Calendar", "what's on today"), ("Mail", "who is waiting on me"), ("Wearables", "last night's sleep"), ("Notes and memos", "ideas, to-dos, REEL")]
    outs = [("Morning brief", "every day"), ("Chat", "ask it anything about my week"), ("Follow-ups", "what I promised people")]
    o = []
    for k, (a, b) in enumerate(ins):
        y = 30 + k * 130
        o.append(_box(20, y, 300, 100, a, b))
        o.append(_arrow(320, y + 50, 470, 290))
    o.append(f'<circle cx="600" cy="290" r="130" fill="#1C140E" stroke="{AMB}" stroke-opacity=".6" stroke-width="2"/>')
    o.append(f'<circle cx="600" cy="262" r="92" fill="#F6EFE4"/><image href="/img/work/tenzo/tenzo.png" x="515" y="177" width="170" height="170"/>')
    o.append(f'<text x="600" y="380" text-anchor="middle" fill="{INK}" font-size="26" font-weight="800" {FONT}>Tenzo</text>')
    o.append(f'<text x="600" y="406" text-anchor="middle" fill="{SOFT}" font-size="17" {FONT}>on a Mac mini at home</text>')
    for k, (a, b) in enumerate(outs):
        y = 80 + k * 150
        o.append(_arrow(730, 290, 870, y + 50))
        o.append(_box(880, y, 300, 100, a, b))
    return f'<svg viewBox="0 0 1200 580" role="img" aria-label="Tenzo reads calendar, mail, wearables and notes on a Mac mini at home, and returns a morning brief, chat answers and follow-ups">{"".join(o)}</svg>'


def tenzo_brief():
    lines = [("Slept 7 h 10 m, a little under your usual.", INK), ("Three meetings. The first is at 9:30.", INK),
             ("One email has waited on you since Tuesday.", INK), ("You said you'd send the slides by Friday.", INK)]
    t = "".join(f'<text x="60" y="{190+k*56}" fill="{c}" font-size="25" {FONT}>{s}</text>' for k, (s, c) in enumerate(lines))
    return f"""<svg viewBox="0 0 760 470" role="img" aria-label="A sample morning brief with made-up data">
<rect x="10" y="10" width="740" height="450" rx="22" fill="#F6EFE4"/>
<image href="/img/work/tenzo/tenzo.png" x="40" y="34" width="84" height="84"/>
<text x="140" y="74" fill="#1A120C" font-size="30" font-weight="800" {FONT}>Good morning.</text>
<text x="140" y="106" fill="#6b5b48" font-size="19" {FONT}>Tenzo, 7:00</text>
<rect x="40" y="140" width="680" height="250" rx="14" fill="#1A120C"/>{t}
<text x="40" y="430" fill="#6b5b48" font-size="18" {FONT}>Sample brief. The data is made up for this page.</text>
</svg>"""


def bridge():
    s = [("Old record system", "every chart, as it is"), ("Export", "API data and PDF documents"), ("Check", "validate before anything moves"),
         ("Map", "every field, in a visual mapper"), ("Load", "into the new system"), ("Verify", "what arrived matches what left")]
    o = []
    for k, (a, b) in enumerate(s):
        col, row = k % 3, k // 3
        x, y = 30 + col * 400, 40 + row * 210
        o.append(_box(x, y, 340, 120, a, b, f"0{k+1}"))
        if col < 2:
            o.append(_arrow(x + 340, y + 60, x + 400, y + 60))
    o.append(f'<path d="M1000 160 C1000 205 200 205 200 245" fill="none" stroke="{AMB}" stroke-width="2.5" stroke-dasharray="6 8" class="flow"/><circle cx="200" cy="248" r="5" fill="{AMB}"/>')
    o.append(f'<rect x="30" y="420" width="1140" height="70" rx="14" fill="none" stroke="{LINE}" stroke-width="2"/>')
    o.append(f'<text x="600" y="463" text-anchor="middle" fill="{SOFT}" font-size="20" {FONT}>Underneath every step: an audit log, encryption, a dry run and a rollback</text>')
    return f'<svg viewBox="0 0 1270 510" role="img" aria-label="Six steps a chart takes from the old record system to the new one">{"".join(o)}</svg>'


def lumos():
    parts = [("Ears", "turns to whoever speaks"), ("Eye", "knows the faces it lives with"), ("Memory", "remembers your life"),
             ("Mind at home", "its own model, in the house"), ("Body", "moves while it talks"), ("Night", "a whisper, no light")]
    import math
    o = [f'<circle cx="600" cy="330" r="120" fill="#1C140E" stroke="{AMB}" stroke-opacity=".6" stroke-width="2"/>',
         f'<circle cx="600" cy="330" r="34" fill="{AMB}"><animate attributeName="r" values="30;38;30" dur="4s" repeatCount="indefinite"/></circle>',
         f'<text x="600" y="420" text-anchor="middle" fill="{INK}" font-size="26" font-weight="800" {FONT}>Nuku</text>']
    for k, (a, b) in enumerate(parts):
        ang = -math.pi / 2 + k * math.pi / 3
        x, y = 600 + 400 * math.cos(ang), 330 + 250 * math.sin(ang)
        o.append(_arrow(round(600 + 130 * math.cos(ang)), round(330 + 130 * math.sin(ang)), round(x - 140 * math.cos(ang) * .2), round(y - 40 * math.sin(ang))))
        o.append(_box(round(x - 160), round(y - 45), 320, 96, a, b))
    return f'<svg viewBox="0 0 1200 660" role="img" aria-label="What Nuku is made of: ears, eye, memory, a mind at home, body and night mode">{"".join(o)}</svg>'


SVG = {"sardinia": sardinia, "bluenotte_steps": bluenotte_steps, "tenzo": tenzo, "tenzo_brief": tenzo_brief, "bridge": bridge, "nuku": lumos}
