#!/usr/bin/env python3
"""Comprobaciones SEO básicas sobre dist/. Uso: python3 src/check.py (tras build.py)."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITE = "https://www.zirotti.com"


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""; self._t = False
        self.meta = {}; self.links = []; self.h = []; self._h = None
        self.hrefs = []; self.imgs = []; self.ld = []; self._ld = False; self.ids = set()
        self.lang = None

    def handle_starttag(self, tag, a):
        a = dict(a)
        if a.get("id"): self.ids.add(a["id"])
        if tag == "html": self.lang = a.get("lang")
        if tag == "title": self._t = True
        if tag == "meta":
            self.meta[a.get("name") or a.get("property")] = a.get("content")
        if tag == "link": self.links.append(a)
        if tag in ("h1", "h2", "h3"): self._h = [tag, ""]
        if tag == "a" and a.get("href"): self.hrefs.append(a["href"])
        if tag == "img": self.imgs.append(a)
        if tag == "script" and a.get("type") == "application/ld+json": self._ld = True

    def handle_endtag(self, tag):
        if tag == "title": self._t = False
        if self._h and tag == self._h[0]:
            self.h.append(tuple(self._h)); self._h = None
        if tag == "script": self._ld = False

    def handle_data(self, d):
        if self._t: self.title += d
        if self._h is not None: self._h[1] += d
        if self._ld: self.ld.append(d)


def route(f):
    r = "/" + str(f.relative_to(DIST)).replace("index.html", "")
    return r


errors, warns = [], []
pages = {}
for f in sorted(DIST.rglob("*.html")):
    p = P(); p.feed(f.read_text(encoding="utf-8")); pages[route(f)] = (f, p)

for r, (f, p) in pages.items():
    if r == "/404.html":
        continue
    e = lambda m: errors.append(f"{r}: {m}")
    w = lambda m: warns.append(f"{r}: {m}")
    if not p.lang: e("falta lang")
    if not 20 <= len(p.title.strip()) <= 65: w(f"title de {len(p.title.strip())} caracteres: {p.title.strip()!r}")
    d = p.meta.get("description") or ""
    if not 70 <= len(d) <= 170: w(f"description de {len(d)} caracteres")
    h1 = [x for x in p.h if x[0] == "h1"]
    if len(h1) != 1: e(f"{len(h1)} H1")
    canon = [l for l in p.links if l.get("rel") == "canonical"]
    if len(canon) != 1 or canon[0]["href"] != SITE + r: e(f"canonical incorrecto: {canon}")
    alts = {l["hreflang"]: l["href"] for l in p.links if l.get("rel") == "alternate"}
    if "legal" not in r or True:
        for lang in ("es", "en", "x-default"):
            if lang not in alts: e(f"falta hreflang {lang}")
        # reciprocidad: la alterna debe apuntar de vuelta a esta página
        for lang in ("es", "en"):
            tr = urlparse(alts.get(lang, "")).path
            if tr in pages:
                back = {l["hreflang"]: l["href"] for l in pages[tr][1].links if l.get("rel") == "alternate"}
                if back.get(p.lang) != SITE + r: e(f"hreflang no recíproco con {tr}")
            else:
                e(f"hreflang {lang} apunta a página inexistente {tr}")
    for k in ("og:title", "og:description", "og:image", "og:url", "twitter:card"):
        if not p.meta.get(k): e(f"falta {k}")
    for im in p.imgs:
        if "alt" not in im: e(f"img sin alt: {im.get('src')}")
    for raw in p.ld:
        try:
            json.loads(raw)
        except Exception as ex:
            e(f"JSON-LD inválido: {ex}")
    for href in p.hrefs:
        if href.startswith(("mailto:", "tel:", "http")):
            continue
        path, _, frag = href.partition("#")
        target = path or r
        t = pages.get(target)
        if t is None and not (DIST / target.lstrip("/")).exists():
            e(f"enlace roto: {href}")
        elif frag and t is not None and frag not in t[1].ids:
            e(f"ancla inexistente: {href}")
    if "{{" in f.read_text(encoding="utf-8"):
        e("quedan marcadores {{ }} sin resolver")

# sitemap / robots
sm = (DIST / "sitemap.xml").read_text(encoding="utf-8")
for loc in re.findall(r"<loc>(.*?)</loc>", sm):
    if urlparse(loc).path not in pages: errors.append(f"sitemap apunta a página inexistente: {loc}")
if "Sitemap:" not in (DIST / "robots.txt").read_text(encoding="utf-8"): errors.append("robots.txt sin Sitemap")

print(f"{len(pages)} páginas revisadas")
for m in warns: print("AVISO ", m)
for m in errors: print("ERROR ", m)
print("RESULTADO:", "OK" if not errors else f"{len(errors)} errores")
sys.exit(1 if errors else 0)
