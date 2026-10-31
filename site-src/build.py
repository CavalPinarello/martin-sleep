"""Builds public/index.html and public/work/<slug>/index.html from content.py.
Run from the repo root: python3 site-src/build.py"""
import html
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from content import HERO, THREAD, CATS, P, TALKS  # noqa: E402
from svgs import SVG  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..", "public")
E = html.escape
BY = {p["slug"]: p for p in P}
ORDER = [p["slug"] for c in CATS for p in P if p["cat"] == c[0]]

HEAD = """<!DOCTYPE html>
<html lang="en" class="{cls} no-js"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:image" content="https://martinkawalski.com/{og}">
<meta name="theme-color" content="#120C08">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='%23F2B866'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Domine:wght@500;700&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={v}">
<script>document.documentElement.classList.remove('no-js')</script>
</head><body>
<canvas id="fluid" aria-hidden="true"></canvas>
<nav class="top"><a class="me" href="/">Martin Kawalski</a><div class="links"><a href="/#hardware">Hardware</a><a href="/#software">Software</a><a href="/#research">Medicine<span class="wide"> and research</span></a><a href="/#contact">Contact</a></div></nav>
"""

FOOT = """<footer class="contact" id="contact"><div class="cat">Contact</div><h2>Write to me</h2>
<p><a href="mailto:martin@zoe-sleep.com">martin@zoe-sleep.com</a> &nbsp;·&nbsp; <a href="https://www.linkedin.com/in/martinkawalski">LinkedIn</a> &nbsp;·&nbsp; <a href="https://profiles.stanford.edu/martin-kawalski">Stanford profile</a></p></footer>
<script src="/assets/github.js?v={v}"></script><script src="/assets/site.js?v={v}" defer></script>
</body></html>"""

V = "9"


def media_html(p, big=True):
    kind = p["media"][0]
    if kind == "photo":
        _, src, pos = p["media"]
        cap = f'<span class="cap">{E(p.get("cap", ""))}</span>' if p.get("cap") else ""
        return f'<img class="bgimg" src="/{src}" alt="" style="object-position:{pos}" loading="lazy" decoding="async"><div class="shade"></div>{cap}'
    if kind == "screens":
        _, desk, phone = p["media"]
        ph = f'<img class="phone" src="/{phone}" alt="" loading="lazy" decoding="async">' if phone else ""
        return f'<div class="stage screens"><img class="desk" src="/{desk}" alt="" loading="lazy" decoding="async">{ph}</div>'
    _, key = p["media"]
    return f'<div class="stage art art-{key}">{SVG[key]()}</div>'


def fig(src, cap):
    if src.startswith("svg:"):
        body = f'<div class="art art-{src[4:]}">{SVG[src[4:]]()}</div>'
    else:
        body = f'<img src="/{src}" alt="{E(cap)}" loading="lazy" decoding="async">'
    return f'<figure class="rv">{body}<figcaption>{E(cap)}</figcaption></figure>'


def index():
    o = [HEAD.format(cls="reel", title="Martin Kawalski, MD, PhD · A doctor who builds things",
                     desc="Martin Kawalski, MD, PhD. A doctor who builds things: Lumos, Snowcookie, Slumber AI, FirstLight, and sleep research at Stanford.",
                     og="img/lumos_next.jpg", v=V)]
    o.append(f"""<section class="panel hero" id="top">
  <div class="hero-photo"><img src="/martin.jpeg" alt="Martin Kawalski"></div>
  <div class="copy rv"><div class="kick">{E(HERO['kick'])}</div><h1>{E(HERO['h1'])}</h1><p class="lead">{E(HERO['p'])}</p>
  <a class="scroll" href="#thread">See how it fits together</a></div>
</section>""")
    beats = []
    for k, (h, src, t) in enumerate(THREAD):
        vis = (f'<div class="art art-{src[4:]}">{SVG[src[4:]]()}</div>' if src.startswith("svg:")
               else f'<img src="/{src}" alt="" loading="lazy" decoding="async">' + ('<span class="cap">Illustration</span>' if 'bluenotte/' in src else ''))
        beats.append(f'<div class="beat rv" style="--d:{k*120}ms"><div class="bv">{vis}</div><div class="n">0{k+1}</div><h3>{E(h)}</h3><p>{E(t)}</p></div>')
    o.append(f'<section class="panel thread" id="thread"><div class="inner"><div class="cat rv">One thread</div><h2 class="rv">From a village clinic to the workbench</h2><div class="beats">{"".join(beats)}</div></div></section>')
    n = 0
    for key, name, blurb in CATS:
        items = [p for p in P if p["cat"] == key]
        o.append(f'<section class="panel intro" id="{key}"><div class="copy rv"><div class="cat">{len(items)} projects</div><h2 class="giant">{E(name)}</h2><p class="lead">{E(blurb)}</p></div></section>')
        for p in items:
            n += 1
            kind = p["media"][0]
            o.append(f"""<section class="panel proj k-{kind}" id="p-{p['slug']}">
  {media_html(p)}
  <div class="copy rv"><div class="n">{n:02d}</div><div class="cat">{E(p['kick'])}</div><h2>{E(p['title'])}</h2><p class="line">{E(p['line'])}</p>
  <a class="deeper" href="/work/{p['slug']}/">Go deeper<span aria-hidden="true"> &rarr;</span></a></div>
</section>""")
    talks = []
    for img, h, idea, where, links in TALKS:
        im = f'<img src="/{img}" alt="Martin on stage" loading="lazy">' if img else ""
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
    o = [HEAD.format(cls="work", title=f"{p['title']} · Martin Kawalski, MD, PhD", desc=p["line"], og=og, v=V)]
    link = f'<a class="go" href="{p["link"][0]}">{E(p["link"][1])}</a>' if p.get("link") else ""
    gh = f'<a class="go gh" data-gh="{p["slug"]}" hidden>Code on GitHub</a>'
    o.append(f"""<section class="panel proj wtop k-{p['media'][0]}">
  {media_html(p)}
  <div class="copy rv"><a class="back" href="/#{p['cat']}">&larr; {E(catname)}</a><div class="cat">{E(p['kick'])}</div><h1>{E(p['title'])}</h1><p class="line">{E(p['lead'])}</p><div class="golinks">{link}{gh}</div></div>
</section>""")
    o.append('<main class="deep">')
    o.append(f'<section class="block rv"><h2>{E(p.get("builth", "What I built"))}</h2><div class="txt">' + "".join(f"<p>{E(t)}</p>" for t in p["built"]) + "</div></section>")
    if p["how"]:
        steps = "".join(f'<li class="rv" style="--d:{k*80}ms"><span class="n">0{k+1}</span><b>{E(a)}</b><span>{E(b)}</span></li>' for k, (a, b) in enumerate(p["how"]))
        o.append(f'<section class="block"><h2 class="rv">How it works</h2><ol class="steps">{steps}</ol></section>')
    o.append('<section class="gallery">' + "".join(fig(s, c) for s, c in p["gallery"]) + "</section>")
    if p.get("next"):
        o.append(f'<section class="block rv"><h2>{E(p["nexth"])}</h2><div class="txt"><p>{E(p["next"])}</p></div></section>')
    o.append(f'<nav class="pn"><a href="/work/{prv["slug"]}/"><span>Previous</span><b>{E(prv["title"])}</b></a><a href="/work/{nxt["slug"]}/" class="r"><span>Next</span><b>{E(nxt["title"])}</b></a></nav>')
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
