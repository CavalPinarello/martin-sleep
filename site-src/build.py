"""Builds public/index.html and public/work/<slug>/index.html from content.py.
Run from the repo root: python3 site-src/build.py"""
import html
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from content import HERO, THREAD, CATS, P, TALKS, TEDX_URL  # noqa: E402
from svgs import SVG  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "public")
E = html.escape
BY = {p["slug"]: p for p in P}
ORDER = [p["slug"] for c in CATS for p in P if p["cat"] == c[0]]
V = "10"

# small inline icons for the side rail and the phone tab bar
IC = {
    "home": '<svg viewBox="0 0 24 24"><path d="M4 11l8-7 8 7v9h-5v-6H9v6H4z"/></svg>',
    "hardware": '<svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/></svg>',
    "software": '<svg viewBox="0 0 24 24"><path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/></svg>',
    "research": '<svg viewBox="0 0 24 24"><path d="M12 4v16M4 12h16"/><circle cx="12" cy="12" r="9"/></svg>',
    "contact": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
}

HEAD = """<!DOCTYPE html>
<html lang="en" class="{cls} no-js"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:image" content="https://martinkawalski.com/{og}">
<meta name="theme-color" content="#110D0A">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='%23F2B866'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Domine:wght@500;700&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={v}">
<script>document.documentElement.classList.remove('no-js')</script>
</head><body>
<canvas id="fluid" aria-hidden="true"></canvas>
<a class="me" href="/">Martin Kawalski</a>
<nav class="bar" aria-label="Sections">{links}</nav>
"""

FOOT = """<footer class="contact" id="contact"><div class="cat">Contact</div><h2>Write to me</h2>
<p><a href="mailto:martin@zoe-sleep.com">martin@zoe-sleep.com</a></p><p><a href="https://www.linkedin.com/in/martinkawalski">LinkedIn</a> &nbsp;·&nbsp; <a href="https://profiles.stanford.edu/martin-kawalski">Stanford profile</a></p></footer>
<script src="/assets/github.js?v={v}"></script><script src="/assets/site.js?v={v}" defer></script>
</body></html>"""


def nav_links():
    items = [("/#top", "home", "Home"), ("/#hardware", "hardware", "Hardware"), ("/#software", "software", "Software"),
             ("/#research", "research", "Medicine"), ("/#contact", "contact", "Contact")]
    return "".join(f'<a href="{u}" class="nv-{k}">{IC[k]}<span>{t}</span></a>' for u, k, t in items)


def head(**kw):
    return HEAD.format(links=nav_links(), v=V, **kw)


# responsive images: x.jpg gets x-800.jpg and x-1400.jpg next to it
def variants(src):
    path = os.path.join(ROOT, src)
    stem, ext = os.path.splitext(path)
    if ext.lower() not in (".jpg", ".jpeg"):
        return None
    im = None
    out = []
    for w in (800, 1400):
        vp = f"{stem}-{w}{ext}"
        if not os.path.exists(vp):
            im = im or Image.open(path).convert("RGB")
            if im.width <= w:
                continue
            c = im.copy()
            c.thumbnail((w, 10000))
            c.save(vp, quality=78, optimize=True, progressive=True)
        if os.path.exists(vp):
            out.append((w, "/" + os.path.relpath(vp, ROOT)))
    full = Image.open(path).width
    out.append((full, "/" + src))
    return ", ".join(f"{u} {w}w" for w, u in out)


def img(src, sizes, alt="", cls="", style="", eager=False):
    ss = variants(src)
    a = f' srcset="{ss}" sizes="{sizes}"' if ss else ""
    c = f' class="{cls}"' if cls else ""
    st = f' style="{style}"' if style else ""
    ld = "eager" if eager else "lazy"
    return f'<img src="/{src}"{a}{c}{st} alt="{E(alt)}" loading="{ld}" decoding="async">'


PANEL_SIZES = "(max-width: 820px) 100vw, 96vw"


def media_html(p, eager=False):
    kind = p["media"][0]
    if kind == "photo":
        _, src, pos = p["media"]
        cap = f'<span class="cap">{E(p.get("cap", ""))}</span>' if p.get("cap") else ""
        return f'<div class="media photo">{img(src, PANEL_SIZES, "", "bgimg", "object-position:" + pos, eager)}{cap}</div>'
    if kind == "screens":
        _, desk, phone = p["media"]
        ph = img(phone, "(max-width: 820px) 24vw, 14vw", "", "phone") if phone else ""
        return f'<div class="media screens"><div class="sc">{img(desk, "(max-width: 820px) 94vw, 70vw", "", "desk", eager=eager)}{ph}</div></div>'
    _, key = p["media"]
    return f'<div class="media art art-{key}">{SVG[key]()}</div>'


def fig(src, cap, k, n):
    if src.startswith("svg:"):
        body = f'<div class="art art-{src[4:]}">{SVG[src[4:]]()}</div>'
    else:
        body = img(src, "(max-width: 820px) 92vw, 86vw", cap)
    return f'<figure class="slide" aria-label="{k+1} of {n}">{body}<figcaption>{E(cap)}</figcaption></figure>'


def index():
    o = [head(cls="reel", title="Martin Kawalski, MD, PhD · A doctor who builds things",
              desc="Martin Kawalski, MD, PhD. A doctor who builds things: Lumos, Snowcookie, Slumber AI, FirstLight, and sleep research at Stanford.",
              og="img/lumos_next.jpg")]
    o.append(f"""<section class="panel hero" id="top">
  <div class="hero-photo">{img("martin.jpeg", "(max-width: 820px) 100vw, 50vw", "Martin Kawalski", eager=True)}</div>
  <div class="copy rv"><div class="kick">{E(HERO['kick'])}</div><h1>{E(HERO['h1'])}</h1><p class="lead">{E(HERO['p'])}</p>
  <a class="pill" href="#thread">See how it fits together</a></div>
</section>""")
    beats = []
    for k, (h, src, t) in enumerate(THREAD):
        if src.startswith("svg:"):
            vis = f'<div class="art art-{src[4:]}">{SVG[src[4:]]()}</div>'
        else:
            vis = img(src, "(max-width: 820px) 92vw, 46vw") + ('<span class="cap">Illustration</span>' if "bluenotte/" in src else "")
        beats.append(f'<div class="beat rv" style="--d:{k*120}ms"><div class="bv">{vis}</div><h3>{E(h)}</h3><p>{E(t)}</p></div>')
    o.append(f'<section class="panel thread" id="thread"><div class="inner"><div class="cat rv">One thread</div><h2 class="rv">Where the work comes from</h2><div class="beats">{"".join(beats)}</div></div></section>')
    for key, name, blurb in CATS:
        items = [p for p in P if p["cat"] == key]
        o.append(f'<section class="panel intro" id="{key}"><div class="copy rv"><div class="cat">{len(items)} projects</div><h2 class="giant">{E(name)}</h2><p class="lead">{E(blurb)}</p></div></section>')
        for p in items:
            o.append(f"""<section class="panel proj k-{p['media'][0]}" id="p-{p['slug']}">
  <div class="frame">{media_html(p)}
  <div class="copy rv"><div class="cat">{E(p['kick'])}</div><h2>{E(p['title'])}</h2><p class="line">{E(p['line'])}</p>
  <a class="pill" href="/work/{p['slug']}/">Go deeper<span aria-hidden="true"> &rarr;</span></a></div></div>
</section>""")
    talks = []
    for im_, h, idea, where, links in TALKS:
        im = img(im_, "(max-width: 820px) 92vw, 40vw", "Martin on stage") if im_ else ""
        ls = "".join(f'<a href="{u}">{E(t)}</a>' for t, u in links)
        talks.append(f'<div class="talk rv">{im}<h3>{E(h)}</h3><p class="idea">{E(idea)}</p><p class="where">{E(where)}</p><div class="gos">{ls}</div></div>')
    o.append(f'<section class="panel talks-p" id="talks"><div class="inner"><div class="cat rv">From my talks</div><h2 class="rv">On sleep</h2><div class="talks">{"".join(talks)}</div></div></section>')
    o.append(FOOT.format(v=V))
    return "\n".join(o)


def work(p):
    i = ORDER.index(p["slug"])
    prv, nxt = BY[ORDER[i - 1]], BY[ORDER[(i + 1) % len(ORDER)]]
    catname = dict((c[0], c[1]) for c in CATS)[p["cat"]]
    og = p["media"][1] if p["media"][0] in ("photo", "screens") else "img/lumos_next.jpg"
    o = [head(cls="work", title=f"{p['title']} · Martin Kawalski, MD, PhD", desc=p["line"], og=og)]
    links = []
    if p.get("link"):
        links.append(f'<a class="pill" href="{p["link"][0]}">{E(p["link"][1])}</a>')
    if p["slug"] == "nepal" and TEDX_URL:
        links.append(f'<a class="pill" href="{TEDX_URL}">Watch the TEDx talk</a>')
    links.append(f'<a class="pill gh" data-gh="{p["slug"]}" hidden>Code on GitHub</a>')
    o.append(f"""<section class="panel proj wtop k-{p['media'][0]}">
  <div class="frame">{media_html(p, eager=True)}
  <div class="copy rv"><a class="back" href="/#{p['cat']}">&larr; {E(catname)}</a><div class="cat">{E(p['kick'])}</div><h1>{E(p['title'])}</h1><p class="line">{E(p['lead'])}</p><div class="golinks">{"".join(links)}</div></div></div>
</section>""")
    o.append('<main class="deep">')
    n = len(p["gallery"])
    o.append(f"""<section class="gallery" aria-label="Pictures">
  <div class="track" tabindex="0">{"".join(fig(s, c, k, n) for k, (s, c) in enumerate(p["gallery"]))}</div>
  <div class="gnav"{' hidden' if n < 2 else ''}><button class="gp" aria-label="Previous picture">&larr;</button><span class="gc">1 / {n}</span><button class="gn" aria-label="Next picture">&rarr;</button></div>
</section>""")
    o.append(f'<section class="block rv"><h2>{E(p.get("builth", "What I built"))}</h2><div class="txt">' + "".join(f"<p>{E(t)}</p>" for t in p["built"]) + "</div></section>")
    if p["how"]:
        steps = "".join(f'<li class="rv" style="--d:{k*80}ms"><b>{E(a)}</b><span>{E(b)}</span></li>' for k, (a, b) in enumerate(p["how"]))
        o.append(f'<section class="block"><h2 class="rv">How it works</h2><ul class="steps">{steps}</ul></section>')
    if p.get("next"):
        o.append(f'<section class="block rv"><h2>{E(p["nexth"])}</h2><div class="txt"><p>{E(p["next"])}</p></div></section>')
    o.append(f'<nav class="pn" aria-label="More work"><a href="/work/{prv["slug"]}/"><span>Previous</span><b>{E(prv["title"])}</b></a><a href="/work/{nxt["slug"]}/" class="r"><span>Next</span><b>{E(nxt["title"])}</b></a></nav>')
    o.append("</main>")
    o.append(FOOT.format(v=V))
    return "\n".join(o)


def write(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(s)


if __name__ == "__main__":
    write(os.path.join(ROOT, "index.html"), index())
    for p in P:
        write(os.path.join(ROOT, "work", p["slug"], "index.html"), work(p))
    if not os.path.exists(os.path.join(ROOT, "assets", "github.js")):
        write(os.path.join(ROOT, "assets", "github.js"),
              "/* Paste a repository URL to show a 'Code on GitHub' link on that project's page. Empty = hidden. */\n"
              "window.GITHUB = {" + ", ".join(f'"{p["slug"]}": ""' for p in P) + "};\n")
    print("built", len(P), "project pages")
