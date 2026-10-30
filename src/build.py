#!/usr/bin/env python3
"""Genera el sitio estático en dist/ a partir de src/.

Uso:   python3 src/build.py
Cada página se escribe una sola vez con textos ES/EN lado a lado (función t),
así las dos versiones no se desalinean. No hay dependencias externas.
"""
import hashlib
import html
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "dist"
SITE = "https://www.zirotti.com"
BRAND = "Zirotti Strategic Advisory"
EMAIL = "franco@zirotti.com"
PHONE = "+34 665 619 067"
PHONE_TEL = "+34665619067"
LINKEDIN = "https://linkedin.com/in/franco-giuseppe-zirotti"
WHATSAPP = "https://wa.me/34665619067"
ORG_ID = SITE + "/#organization"
PERSON_ID = SITE + "/#franco"

# clave -> (ruta ES, ruta EN)
PATHS = {
    "home": ("/", "/en/"),
    "forma": ("/formacion-ia-project-management/", "/en/ai-project-management-training/"),
    "asesora": ("/asesoria-estrategica-inversion/", "/en/strategic-investment-advisory/"),
    "dirige": ("/direccion-fractional-expansion/", "/en/fractional-expansion-director/"),
    "legal": ("/legal/", "/en/legal/"),
}
LINES = ["forma", "asesora", "dirige"]


def t(L, es, en):
    return es if L == "es" else en


def url(key, L):
    return PATHS[key][0 if L == "es" else 1]


def other(L):
    return "en" if L == "es" else "es"


def esc(s):
    return html.escape(s, quote=True)


def asset_ver(name):
    return hashlib.md5((SRC / "assets" / name).read_bytes()).hexdigest()[:8]


CSS_V = asset_ver("style.css")
JS_V = asset_ver("site.js")


# --------------------------------------------------------------------------
# Piezas comunes
# --------------------------------------------------------------------------
def line_names(L):
    return {
        "forma": ("FORMA", t(L, "Formación aplicada", "Applied training")),
        "asesora": ("ASESORA", t(L, "Asesoría estratégica", "Strategic advisory")),
        "dirige": ("DIRIGE", t(L, "Dirección fractional", "Fractional direction")),
    }


def sec_head(label, dark=False, tag="h2", cls=""):
    c = "sec-head" + (" sec-head--dark" if dark else "") + (" " + cls if cls else "")
    return f'<div class="{c}"><{tag} class="label">{label}</{tag}></div>'


def header(L, key):
    names = line_names(L)
    links = []
    for k in LINES:
        cur = ' aria-current="page"' if k == key else ""
        links.append(f'<a class="nav-link" href="{url(k, L)}"{cur}>{names[k][0]}</a>')
    links.append(f'<a class="nav-link" href="{url("home", L)}#sectores">{t(L, "Sectores", "Sectors")}</a>')
    links.append(f'<a class="nav-link" href="{url("home", L)}#contacto">{t(L, "Contacto", "Contact")}</a>')
    es_cur = ' aria-current="true"' if L == "es" else ""
    en_cur = ' aria-current="true"' if L == "en" else ""
    if L == "es":
        es_el = f'<span{es_cur}>ES</span>'
        en_el = f'<a href="{url(key, "en")}" hreflang="en" lang="en" title="English">EN</a>'
    else:
        es_el = f'<a href="{url(key, "es")}" hreflang="es" lang="es" title="Español">ES</a>'
        en_el = f'<span{en_cur}>EN</span>'
    return f"""<a class="skip" href="#main">{t(L, "Saltar al contenido", "Skip to content")}</a>
<header class="site-header" data-scrolled="0">
  <div class="wrap">
    <a class="brand" href="{url("home", L)}" aria-label="{BRAND} — {t(L, "inicio", "home")}">
      <img src="/assets/logo-dark.svg" alt="" width="34" height="34">
      <span class="brand-text"><span class="brand-name">Zirotti</span><span class="brand-sub">Strategic Advisory</span></span>
    </a>
    <nav class="nav" aria-label="{t(L, "Principal", "Main")}">
      {''.join(links)}
      <span class="lang" aria-label="{t(L, "Idioma", "Language")}">{es_el}<span aria-hidden="true">/</span>{en_el}</span>
    </nav>
  </div>
</header>"""


def footer(L):
    names = line_names(L)
    svc = "".join(f'<a href="{url(k, L)}">{names[k][0]}</a>' for k in LINES)
    legal = url("legal", L)
    return f"""<footer class="site-footer">
  <div class="wrap footer-main">
    <div class="footer-brand">
      <div class="row"><img src="/assets/logo-light.svg" alt="" width="30" height="30"><span class="brand-text"><span class="brand-name">Zirotti</span><span class="brand-sub">Strategic Advisory</span></span></div>
      <p>…{t(L, "libera todo tu potencial", "unlock your full potential")}</p>
    </div>
    <div class="footer-cols">
      <div class="footer-col"><h2>{t(L, "Servicios", "Services")}</h2>{svc}</div>
      <div class="footer-col"><h2>{t(L, "Contacto", "Contact")}</h2>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
        <a href="tel:{PHONE_TEL}">{PHONE}</a>
        <a href="{WHATSAPP}" target="_blank" rel="noopener">WhatsApp</a>
        <span>Madrid, {t(L, "España", "Spain")}</span>
      </div>
    </div>
  </div>
  <div class="footer-base"><div class="wrap">
    <span>© {date.today().year} {BRAND}</span>
    <nav aria-label="Legal"><a href="{legal}#aviso">{t(L, "Aviso legal", "Legal notice")}</a><a href="{legal}#privacidad">{t(L, "Privacidad", "Privacy")}</a><a href="{legal}#cookies">Cookies</a></nav>
    <span class="where">Madrid · {t(L, "España", "Spain")} · Santiago · Chile</span>
  </div></div>
</footer>"""


def head(L, key, title, desc, robots="index, follow", jsonld=None, alt=True):
    canon = SITE + url(key, L)
    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        f'<meta name="robots" content="{robots}">',
        f'<link rel="canonical" href="{canon}">',
    ]
    if alt:
        tags += [
            f'<link rel="alternate" hreflang="es" href="{SITE + url(key, "es")}">',
            f'<link rel="alternate" hreflang="en" href="{SITE + url(key, "en")}">',
            f'<link rel="alternate" hreflang="x-default" href="{SITE + url(key, "es")}">',
        ]
    tags += [
        '<meta name="theme-color" content="#FAFAF8">',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{BRAND}">',
        f'<meta property="og:locale" content="{t(L, "es_ES", "en_US")}">',
        f'<meta property="og:locale:alternate" content="{t(L, "en_US", "es_ES")}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{canon}">',
        f'<meta property="og:image" content="{SITE}/assets/og-image.png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{BRAND} — {t(L, "…libera todo tu potencial", "…unlock your full potential")}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(desc)}">',
        f'<meta name="twitter:image" content="{SITE}/assets/og-image.png">',
        '<link rel="preload" href="/assets/fonts/cormorant-garamond-latin.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="preload" href="/assets/fonts/roboto-latin.woff2" as="font" type="font/woff2" crossorigin>',
        f'<link rel="stylesheet" href="/assets/style.css?v={CSS_V}">',
    ]
    if jsonld:
        data = json.dumps({"@context": "https://schema.org", "@graph": jsonld}, ensure_ascii=False, separators=(",", ":"))
        tags.append(f'<script type="application/ld+json">{data}</script>')
    return "\n".join(tags)


def page(L, key, title, desc, body, robots="index, follow", jsonld=None, alt=True, with_js=False):
    js = f'<script src="/assets/site.js?v={JS_V}" defer></script>' if with_js else ""
    return f"""<!DOCTYPE html>
<html lang="{L}">
<head>
{head(L, key, title, desc, robots, jsonld, alt)}
</head>
<body>
{header(L, key)}
<main id="main">
{body}
</main>
{footer(L)}
{js}
</body>
</html>
"""


# --------------------------------------------------------------------------
# Datos estructurados
# --------------------------------------------------------------------------
def org_node(L):
    return {
        "@type": ["Organization", "ProfessionalService"],
        "@id": ORG_ID,
        "name": BRAND,
        "alternateName": "Zirotti",
        "url": SITE + "/",
        "logo": SITE + "/apple-touch-icon.png",
        "image": SITE + "/assets/og-image.png",
        "description": t(
            L,
            "Asesoría estratégica de inversión, formación aplicada en IA y Project Management y dirección fractional de expansión y obra.",
            "Strategic investment advisory, applied AI and Project Management training, and fractional direction of expansion and construction.",
        ),
        "email": EMAIL,
        "telephone": PHONE_TEL,
        "address": {"@type": "PostalAddress", "addressLocality": "Madrid", "addressCountry": "ES"},
        "areaServed": [{"@type": "Country", "name": "España"}, {"@type": "Country", "name": "Chile"}],
        "founder": {"@id": PERSON_ID},
        "knowsLanguage": ["es", "en"],
        "knowsAbout": [
            "Asesoría estratégica de inversión", "Dirección de expansión", "Dirección de obra",
            "Project Management", "IA aplicada a la gestión de proyectos", "Retail y QSR", "Hospitality",
        ],
        "makesOffer": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"FORMA — {t(L, 'Formación aplicada en IA y Project Management', 'Applied AI and Project Management training')}", "url": SITE + url("forma", L)}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"ASESORA — {t(L, 'Asesoría estratégica de inversión y proyecto', 'Strategic investment and project advisory')}", "url": SITE + url("asesora", L)}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"DIRIGE — {t(L, 'Dirección fractional de expansión y obra', 'Fractional direction of expansion and construction')}", "url": SITE + url("dirige", L)}},
        ],
    }


def person_node(L):
    return {
        "@type": "Person",
        "@id": PERSON_ID,
        "name": "Franco Giuseppe Zirotti",
        "jobTitle": t(L, "Director de Expansión y Proyecto (fractional)", "Fractional Expansion & Project Director"),
        "url": SITE + "/",
        "sameAs": [LINKEDIN],
        "worksFor": {"@id": ORG_ID},
        "address": {"@type": "PostalAddress", "addressLocality": "Madrid", "addressCountry": "ES"},
    }


def website_node(L):
    return {
        "@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": BRAND,
        "inLanguage": ["es", "en"], "publisher": {"@id": ORG_ID},
    }


def breadcrumb(L, key, label):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t(L, "Inicio", "Home"), "item": SITE + url("home", L)},
            {"@type": "ListItem", "position": 2, "name": label, "item": SITE + url(key, L)},
        ],
    }


def service_node(L, key, name, stype, desc):
    return {
        "@type": "Service",
        "@id": SITE + url(key, L) + "#service",
        "name": name,
        "serviceType": stype,
        "description": desc,
        "url": SITE + url(key, L),
        "inLanguage": L,
        "areaServed": [{"@type": "Country", "name": "España"}, {"@type": "Country", "name": "Chile"}],
        "provider": {"@type": "ProfessionalService", "@id": ORG_ID, "name": BRAND, "url": SITE + "/"},
    }


# --------------------------------------------------------------------------
# Bloques reutilizables
# --------------------------------------------------------------------------
def contact_form(L):
    opt = [
        "FORMA — Formación / Training",
        "ASESORA — Asesoría / Advisory",
        "DIRIGE — Dirección / Direction",
        "— Aún no lo sé / Not sure yet",
    ]
    options = "".join(f"<option>{o}</option>" for o in opt)
    privacy = f'{url("legal", L)}#privacidad'
    return f"""<form class="form" data-contact data-to="{EMAIL}" action="https://formsubmit.co/{EMAIL}" method="POST">
  <input type="hidden" name="_subject" value="{t(L, "Consulta web — Zirotti", "Website enquiry — Zirotti")}">
  <input type="hidden" name="_template" value="table">
  <input type="hidden" name="_captcha" value="false">
  <input class="honey" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
  <label><span>{t(L, "Nombre", "Name")}</span><input class="field" name="nombre" type="text" required autocomplete="name"></label>
  <label><span>{t(L, "Empresa", "Company")}</span><input class="field" name="empresa" type="text" autocomplete="organization"></label>
  <label><span>Email</span><input class="field" name="email" type="email" required autocomplete="email"></label>
  <label><span>{t(L, "Línea de interés", "Line of interest")}</span><select class="field" name="linea">{options}</select></label>
  <label><span>{t(L, "Cuéntanos el proyecto", "Tell us about the project")}</span><textarea class="field" name="mensaje" rows="3"></textarea></label>
  <p class="form-note">{t(L, f'Al enviar el formulario aceptas el tratamiento de tus datos para responder a tu consulta. Más información en la <a href="{privacy}">política de privacidad</a>.', f'By submitting the form you agree to the processing of your data to answer your enquiry. More in the <a href="{privacy}">privacy policy</a>.')}</p>
  <p class="form-error" data-error hidden></p>
  <button class="btn btn--accent" type="submit">{t(L, "Enviar y reservar consulta", "Send &amp; book a consultation")}</button>
</form>
<div class="thanks" data-thanks hidden tabindex="-1" role="status">
  <img src="/assets/logo-accent.svg" alt="" width="46" height="46">
  <h3>{t(L, "Gracias. Mensaje recibido.", "Thank you. Message received.")}</h3>
  <p>{t(L, f'Hemos recibido tu mensaje y se ha enviado directamente a Franco. Te responderá personalmente en menos de 48 horas. También puedes escribirle a <a href="mailto:{EMAIL}">{EMAIL}</a> o por WhatsApp.', f'We’ve received your message and sent it directly to Franco. He’ll reply personally within 48 hours. You can also reach him at <a href="mailto:{EMAIL}">{EMAIL}</a> or via WhatsApp.')}</p>
</div>"""


def contact_section(L):
    return f"""<section id="contacto" class="contact dark">
  <div class="wrap">
    <div>
      {sec_head("05 — " + t(L, "Contacto", "Contact"), dark=True, tag="p", cls="sec-head--bare")}
      <h2>{t(L, "Hablemos de tu próxima decisión.", "Let’s talk about your next decision.")}</h2>
      <p class="intro">{t(L, "Una primera conversación de 30 minutos, sin compromiso, para entender el proyecto y ver si encaja con alguna de las tres líneas.", "A first 30-minute conversation, no commitment, to understand the project and see if it fits one of the three lines.")}</p>
      <ul class="contact-list">
        <li><a href="mailto:{EMAIL}"><span class="k">Email</span><span class="v">{EMAIL}</span></a></li>
        <li><a href="tel:{PHONE_TEL}"><span class="k">{t(L, "Teléfono", "Phone")}</span><span class="v">{PHONE}</span></a></li>
        <li><a href="{WHATSAPP}" target="_blank" rel="noopener"><span class="k">WhatsApp</span><span class="v">{t(L, "Chat directo", "Direct chat")}</span></a></li>
        <li><a href="{LINKEDIN}" target="_blank" rel="noopener"><span class="k">LinkedIn</span><span class="v">franco-giuseppe-zirotti</span></a></li>
        <li><span class="k">{t(L, "Sede", "Based in")}</span><span class="v">Madrid, {t(L, "España", "Spain")}</span></li>
      </ul>
    </div>
    <div>
      {contact_form(L)}
    </div>
  </div>
</section>"""


def faq_block(L, title, items):
    rows = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
    return f"""<section class="block" id="faq"><div class="wrap">
  {sec_head(title)}
  <div class="faq">{rows}</div>
</div></section>"""


def cta_block(L, heading, text):
    return f"""<section class="cta dark"><div class="wrap">
  <div><h2>{heading}</h2><p>{text}</p></div>
  <div class="btn-row"><a class="btn btn--accent" href="{url("home", L)}#contacto">{t(L, "Reservar una consulta", "Book a consultation")}</a></div>
</div></section>"""


def others_block(L, current):
    names = line_names(L)
    desc = {
        "forma": t(L, "Formación práctica en IA aplicada y Project Management. Bonificable vía FUNDAE.", "Hands-on training in applied AI and Project Management. FUNDAE-eligible."),
        "asesora": t(L, "Criterio técnico-estratégico para decisiones de inversión, viabilidad y transformación de activos.", "Technical-strategic judgment for investment, feasibility and asset-transformation decisions."),
        "dirige": t(L, "Dirección senior de expansión y obra a tiempo parcial, sin el coste de un director fijo.", "Senior expansion and construction direction, part-time, without a full-time director’s cost."),
    }
    cards = "".join(
        f'<a href="{url(k, L)}"><strong>{names[k][0]}</strong><span class="label">{names[k][1]}</span><span class="d">{desc[k]}</span><span class="arrow" aria-hidden="true">→</span></a>'
        for k in LINES if k != current
    )
    return f"""<section class="block block--tint"><div class="wrap">
  {sec_head(t(L, "Otras líneas de servicio", "Other service lines"))}
  <div class="others">{cards}</div>
</div></section>"""


def crumbs(L, label):
    return f"""<div class="wrap crumbs"><nav aria-label="{t(L, "Migas de pan", "Breadcrumb")}"><ol>
  <li><a href="{url("home", L)}">{t(L, "Inicio", "Home")}</a></li>
  <li><a href="{url("home", L)}#servicios">{t(L, "Líneas de servicio", "Service lines")}</a></li>
  <li aria-current="page">{label}</li>
</ol></nav></div>"""


def page_hero(L, num, brandword, h1, lead, stats):
    st = "".join(f"<div><strong>{a}</strong><span>{b}</span></div>" for a, b in stats)
    return f"""<section class="page-hero"><div class="wrap">
  <div class="line-tag"><span class="num" aria-hidden="true">{num}</span><span class="label">{t(L, "Línea", "Line")} {num}</span></div>
  <h1><span class="brandword">{brandword}</span>{h1}</h1>
  <p class="lead">{lead}</p>
  <div class="stats">{st}</div>
</div></section>"""


def value_block(L, h2, paras):
    ps = "".join(f"<p>{p}</p>" for p in paras)
    return f"""<section class="block block--tint"><div class="wrap">
  {sec_head(t(L, "Propuesta de valor", "Value proposition"))}
  <div class="value"><h2>{h2}</h2><div class="prose">{ps}</div></div>
</div></section>"""


def card(tag, title, rows, foot=None, badge=None):
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    b = f'<span class="badge">{badge}</span>' if badge else ""
    f = f'<div class="card-foot"><strong>{foot[0]}</strong><span>{foot[1]}</span></div>' if foot else ""
    return f'<article class="card"><div class="card-head"><span class="tag">{tag}</span>{b}</div><h3>{title}</h3><dl>{dl}</dl>{f}</article>'


# --------------------------------------------------------------------------
# Páginas
# --------------------------------------------------------------------------
def build_home(L):
    names = line_names(L)
    title = t(L, "Asesoría estratégica de inversión y expansión | Zirotti", "Strategic Investment & Expansion Advisory | Zirotti")
    desc = t(
        L,
        "Asesoría estratégica de inversión, formación en IA y Project Management (FUNDAE) y dirección fractional de expansión y obra. Madrid, España y Chile.",
        "Strategic investment advisory, AI and Project Management training, and fractional direction of expansion and construction. Madrid, Spain and Chile.",
    )
    lines_nav = "".join(
        f'<a href="{url(k, L)}"><span class="num" aria-hidden="true">0{i}</span><strong>{names[k][0]}</strong><span class="sub"><span>{names[k][1]}</span><span class="arrow" aria-hidden="true">→</span></span></a>'
        for i, k in enumerate(LINES, 1)
    )
    svc_text = {
        "forma": t(L, "Formación práctica en IA aplicada y Project Management para equipos que necesitan herramientas reales, no teoría. Compatible con FUNDAE: coste efectivo 0 €.", "Hands-on training in applied AI and Project Management for teams that need real tools, not theory. FUNDAE-eligible: effective cost €0."),
        "asesora": t(L, "Criterio técnico-estratégico para decisiones de inversión, viabilidad y transformación de activos. Para inversores y directivos que necesitan más que un informe.", "Technical-strategic judgment for investment, feasibility and asset transformation. For investors and executives who need more than a report."),
        "dirige": t(L, "Dirección senior de expansión y obra para empresas que necesitan al mejor perfil en su proyecto, sin el coste de un director fijo a jornada completa.", "Senior expansion and construction direction for companies that need the best profile on their project, without the cost of a full-time director."),
    }
    rows = "".join(
        f"""<a class="svc-row" href="{url(k, L)}">
      <span class="num" aria-hidden="true">0{i}</span>
      <div class="svc-grid">
        <div><h3>{names[k][0]}</h3><p class="svc-kind">{names[k][1]}</p></div>
        <div class="svc-body"><p>{svc_text[k]}</p>
          <div class="svc-foot"><span class="quote">{t(L, "Presupuesto a medida", "Custom quote")}</span><span class="go">{t(L, "Ver línea", "View line")} <span class="arrow" aria-hidden="true">→</span></span></div>
        </div>
      </div></a>"""
        for i, k in enumerate(LINES, 1)
    )
    sectors = [
        (t(L, "Real estate operacional", "Operational real estate"), t(L, "Hoteles boutique, locales en prime, activos mixtos residencial-comercial.", "Boutique hotels, prime retail units, mixed residential-commercial assets.")),
        ("Retail &amp; QSR", t(L, "Expansión de cadenas, nueva ubicación, refit o cambio de operador.", "Chain expansion, new locations, refit or operator change.")),
        ("Hospitality", t(L, "Transformación de activos, refitting, cambio de marca o de modelo de negocio.", "Asset transformation, refitting, brand or business-model change.")),
        (t(L, "Industrial / uso mixto", "Industrial / mixed-use"), t(L, "Proyectos en desarrollo en España y Chile.", "Projects under development in Spain and Chile.")),
    ]
    cells = "".join(f'<div class="cell"><span class="num" aria-hidden="true">0{i}</span><h3>{h}</h3><p>{p}</p></div>' for i, (h, p) in enumerate(sectors, 1))
    principles = [
        (t(L, "Estratégico", "Strategic"), t(L, "Cada recomendación tiene una razón de negocio detrás. Sin atajos ni diagnósticos superficiales.", "Every recommendation has a business reason behind it. No shortcuts, no superficial diagnoses.")),
        (t(L, "Directo", "Direct"), t(L, "Sin ambigüedad. Lo que se dice resiste la pregunta difícil de un inversor exigente.", "No ambiguity. What we say withstands the hard question from a demanding investor.")),
        (t(L, "Ejecutable", "Executable"), t(L, "El equipo puede operar sin el asesor en la sala. La autonomía del receptor es parte de la calidad.", "The team can operate without the advisor in the room. The recipient’s autonomy is part of the quality.")),
        ("Premium", t(L, "Alto valor percibido en cada punto de contacto. Formato, tono, detalle, estructura: todo comunica.", "High perceived value at every touchpoint. Format, tone, detail, structure: everything communicates.")),
    ]
    pr = "".join(f"<li><h3>{h}</h3><p>{p}</p></li>" for h, p in principles)
    body = f"""<section class="hero"><div class="wrap">
  <div class="hero-mark" aria-hidden="true"><img src="/assets/logo-dark.svg" alt="" width="400" height="400"></div>
  <p class="eyebrow"><span>Strategic Advisory</span><i>·</i><span>Madrid · {t(L, "España", "Spain")}</span><i>·</i><span>Santiago · Chile</span></p>
  <p class="display" aria-hidden="true"><em>…</em>{t(L, "libera todo tu potencial.", "unlock your full potential.")}</p>
  <h1>{t(L, "Asesoría estratégica para decisiones de inversión, expansión y obra.", "Strategic advisory for investment, expansion and construction decisions.")}</h1>
  <div class="hero-cta">
    <p class="lead">{t(L, "No producimos informes estéticos — producimos criterio que resiste la pregunta difícil de un inversor o un comité.", "We don’t produce polished reports — we produce judgment that withstands the hard question from an investor or a board.")}</p>
    <div class="btn-row">
      <a class="btn btn--fill" href="#contacto">{t(L, "Reservar una consulta", "Book a consultation")}</a>
      <a class="btn btn--line" href="#servicios">{t(L, "Ver servicios", "See services")}</a>
    </div>
  </div>
  <nav class="lines" aria-label="{t(L, "Líneas de servicio", "Service lines")}">{lines_nav}</nav>
</div></section>

<section class="statement dark"><div class="wrap">
  {sec_head("01 — " + t(L, "Enfoque", "Approach"), dark=True, tag="p")}
  <h2>{t(L, "Tres formas de trabajar con Zirotti. Una sola exigencia: que lo que entregamos <em>funcione sin que estemos</em> en la sala.", "Three ways to work with Zirotti. One standard: what we deliver <em>works without us</em> in the room.")}</h2>
  <p>{t(L, "Las tres líneas operan como un embudo de confianza: formación, asesoría y dirección. Cada nivel alimenta al siguiente por orden de cercanía, ciclo de venta y profundidad del compromiso.", "The three lines operate as a funnel of trust: training, advisory and direction. Each level feeds the next by order of closeness, sales cycle and depth of commitment.")}</p>
</div></section>

<section id="servicios" class="services"><div class="wrap">
  {sec_head("02 — " + t(L, "Líneas de servicio", "Service lines"))}
  {rows}
  <div style="border-top:1px solid var(--ink)"></div>
</div></section>

<section id="sectores" class="sectors"><div class="wrap">
  {sec_head("03 — " + t(L, "Sectores y casos de uso", "Sectors &amp; use cases"))}
  <div class="cells">{cells}</div>
</div></section>

<section id="metodo" class="method"><div class="wrap">
  {sec_head("04 — " + t(L, "Cómo trabajamos", "How we work"))}
  <ul class="principles">{pr}</ul>
</div></section>

{contact_section(L)}"""
    jsonld = [org_node(L), person_node(L), website_node(L)]
    return page(L, "home", title, desc, body, jsonld=jsonld, with_js=True)


def build_forma(L):
    title = t(L, "Formación en IA y Project Management con FUNDAE | Zirotti", "AI & Project Management Training (FUNDAE) | Zirotti")
    desc = t(
        L,
        "Cursos de 8–16 h de IA aplicada, Project Management y metodologías ágiles para equipos. Bonificables vía FUNDAE (coste efectivo 0 €). Presupuesto a medida.",
        "Hands-on 8–16 h courses in applied AI, Project Management and agile for teams. FUNDAE-eligible (effective cost €0). Custom quote.",
    )
    label = "FORMA"
    hero = page_hero(
        L, "01", "FORMA",
        t(L, "Formación aplicada en <em>IA y Project Management</em>", "Applied training in <em>AI and Project Management</em>"),
        t(L, "Formación práctica para equipos que necesitan herramientas reales, no teoría. Cada sesión arranca con un caso real y termina con un entregable que el participante puede aplicar el lunes.", "Hands-on training for teams that need real tools, not theory. Every session starts with a real case and ends with a deliverable the participant can apply on Monday."),
        [(t(L, "8–16h", "8–16h"), t(L, "por curso", "per course")), ("≤12", t(L, "participantes", "participants")), ("0 €", t(L, "coste vía FUNDAE", "cost via FUNDAE"))],
    )
    value = value_block(
        L,
        t(L, "FORMA enseña lo que un PM senior usa en obra, en comité y en la sala con el cliente.", "FORMA teaches what a senior PM actually uses on site, in committee and in the room with the client."),
        [t(L, "La mayoría de la formación en IA y PM es teórica o genérica. Aquí no. La línea está diseñada para financiarse vía FUNDAE: el coste formativo se cubre con los créditos de formación de la empresa. Coste efectivo para el cliente: 0 €.", "Most AI and PM training is theoretical or generic. Not here. The line is designed to be funded via FUNDAE: the training cost is covered by the company’s training credits. Effective cost to the client: €0.")],
    )
    bon = t(L, "Bonificable vía FUNDAE", "FUNDAE-eligible")
    quote = t(L, "presupuesto a medida", "custom quote")
    K = {
        "dur": t(L, "Duración", "Duration"), "per": t(L, "Perfil", "Profile"),
        "con": t(L, "Contenido", "Content"), "ent": t(L, "Entregables", "Deliverables"),
    }
    cards = "".join([
        card(t(L, "Curso A", "Course A"), t(L, "IA aplicada a la gestión de proyectos y obra", "Applied AI for project &amp; construction management"), [
            (K["dur"], t(L, "16h · 2 jornadas de 8h o 4 módulos de 4h", "16h · 2 days of 8h or 4 modules of 4h")),
            (K["per"], t(L, "Project Managers, arquitectos, jefes de obra, técnicos de expansión, directores de operaciones", "Project Managers, architects, site managers, expansion technicians, operations directors")),
            (K["con"], t(L, "Prompting aplicado a PM · Automatización de reportes · IA para fichas técnicas y presupuestos · Flujos con n8n · Casos reales de retail y construcción", "Applied prompting for PM · Report automation · AI for spec sheets &amp; budgets · n8n workflows · Real retail &amp; construction cases")),
            (K["ent"], t(L, "Toolkit de prompts editables · Plantillas generadas con IA · Certificado FUNDAE", "Editable prompt toolkit · AI-generated templates · FUNDAE certificate")),
        ], (bon, quote)),
        card(t(L, "Curso B", "Course B"), t(L, "Project Management para equipos de expansión", "Project Management for expansion teams"), [
            (K["dur"], t(L, "16h · 2 jornadas de 8h o 4 módulos de 4h", "16h · 2 days of 8h or 4 modules of 4h")),
            (K["per"], t(L, "Equipos de expansión, franquiciados, operadores de cadenas QSR/retail, property managers", "Expansion teams, franchisees, QSR/retail chain operators, property managers")),
            (K["con"], t(L, "Fases de un proyecto de apertura · Control de CAPEX · Cronograma Gantt · Gestión de proveedores · Comité de inversión · Cierre y lecciones aprendidas", "Phases of an opening project · CAPEX control · Gantt scheduling · Supplier management · Investment committee · Closeout &amp; lessons learned")),
            (K["ent"], t(L, "Plantilla Gantt · Ficha de control de CAPEX · Check-list de apertura · Certificado FUNDAE", "Gantt template · CAPEX control sheet · Opening checklist · FUNDAE certificate")),
        ], (bon, quote)),
        card(t(L, "Curso C", "Course C"), t(L, "Metodologías ágiles para directivos", "Agile methodologies for executives"), [
            (K["dur"], t(L, "8h · 1 jornada o 2 módulos de 4h · máx. 8 personas", "8h · 1 day or 2 modules of 4h · max 8 people")),
            (K["per"], t(L, "Directivos, mandos intermedios y líderes de equipo sin formación previa en PM ágil", "Executives, middle managers and team leaders with no prior agile PM training")),
            (K["con"], t(L, "Scrum aplicado · Kanban para operaciones · OKR que funcionan · Toma de decisiones con datos · Retrospectivas ejecutivas", "Applied Scrum · Kanban for operations · OKRs that work · Data-driven decision making · Executive retrospectives")),
            (K["ent"], t(L, "Board Kanban del equipo configurado · OKR del trimestre diseñados en sesión · Certificado FUNDAE", "Team Kanban board configured · Quarter OKRs designed in session · FUNDAE certificate")),
        ], (bon, quote), badge=t(L, "Formato intensivo", "Intensive format")),
    ])
    catalog = f"""<section class="block"><div class="wrap">
  {sec_head(t(L, "Catálogo de cursos", "Course catalog"))}
  <div class="cards">{cards}</div>
</div></section>"""
    steps = [
        t(L, "Alta como entidad organizadora o acuerdo con una gestora acreditada.", "Registration as organizing entity or agreement with an accredited manager."),
        t(L, "Comunicación previa a FUNDAE con 7 días de antelación.", "Prior notice to FUNDAE 7 days in advance."),
        t(L, "Partes de asistencia y certificado. Zirotti gestiona el proceso completo o apoya en la gestión propia.", "Attendance records and certificate. Zirotti manages the full process or supports your own."),
    ]
    st = "".join(f'<li><span class="num" aria-hidden="true">0{i}</span><p>{s}</p></li>' for i, s in enumerate(steps, 1))
    fundae = f"""<section class="block block--tint"><div class="wrap">
  {sec_head(t(L, "Cómo funciona FUNDAE", "How FUNDAE works"))}
  <div class="fundae">
    <div class="big">0 €<small>{t(L, "coste efectivo", "effective cost")}</small></div>
    <div class="prose"><p>{t(L, "FUNDAE gestiona los créditos de formación continua de las empresas españolas. Cada empresa tiene un crédito anual proporcional a su masa salarial. La formación bonificada cubre el 100 % del coste para pequeñas empresas y entre el 75–100 % para medianas y grandes.", "FUNDAE manages the continuous-training credits of Spanish companies. Each company has an annual credit proportional to its payroll. Subsidized training covers 100% of the cost for small companies and 75–100% for medium and large ones.")}</p></div>
  </div>
  <ol class="steps" style="margin-top:clamp(32px,4vw,56px)">{st}</ol>
</div></section>"""
    faq = faq_block(L, t(L, "Preguntas frecuentes", "Frequently asked questions"), [
        (t(L, "¿Qué cursos de formación en IA y Project Management ofrece Zirotti?", "Which AI and Project Management courses does Zirotti offer?"),
         t(L, "Tres: IA aplicada a la gestión de proyectos y obra (16 h), Project Management para equipos de expansión (16 h) y Metodologías ágiles para directivos (8 h, formato intensivo). Todos parten de un caso real y terminan con un entregable aplicable.", "Three: Applied AI for project and construction management (16 h), Project Management for expansion teams (16 h) and Agile methodologies for executives (8 h, intensive format). All start from a real case and end with an applicable deliverable.")),
        (t(L, "¿Cuánto cuesta la formación si se bonifica con FUNDAE?", "How much does the training cost if funded through FUNDAE?"),
         t(L, "El coste efectivo para el cliente es 0 € cuando la formación se financia con los créditos de formación de la empresa. La formación bonificada cubre el 100 % del coste en pequeñas empresas y entre el 75 % y el 100 % en medianas y grandes. Se presupuesta a medida.", "The effective cost to the client is €0 when the training is funded with the company’s training credits. Subsidized training covers 100% of the cost for small companies and 75–100% for medium and large ones. Quotes are custom.")),
        (t(L, "¿Cuántas personas pueden participar y cuánto dura un curso?", "How many people can attend and how long is a course?"),
         t(L, "Los grupos son de hasta 12 participantes (8 en el curso intensivo para directivos). Cada curso dura entre 8 y 16 horas, en jornadas de 8 h o módulos de 4 h.", "Groups are up to 12 participants (8 in the intensive executive course). Each course lasts 8 to 16 hours, in 8 h days or 4 h modules.")),
        (t(L, "¿Quién gestiona los trámites con FUNDAE?", "Who handles the FUNDAE paperwork?"),
         t(L, "Zirotti gestiona el proceso completo o apoya en la gestión propia de la empresa: alta como entidad organizadora o acuerdo con una gestora acreditada, comunicación previa a FUNDAE con 7 días de antelación, partes de asistencia y certificado.", "Zirotti manages the full process or supports your own: registration as organizing entity or agreement with an accredited manager, prior notice to FUNDAE 7 days in advance, attendance records and certificate.")),
    ])
    cta = cta_block(
        L,
        t(L, "¿Formamos a tu equipo este trimestre?", "Shall we train your team this quarter?"),
        t(L, "Por sesión cerrada o pack trimestral (3–4 sesiones con 10 % de descuento). Ciclo habitual: 2–4 semanas.", "Per closed session or quarterly pack (3–4 sessions with 10% discount). Typical cycle: 2–4 weeks."),
    )
    body = crumbs(L, label) + hero + value + catalog + fundae + faq + cta + others_block(L, "forma")
    jsonld = [
        service_node(L, "forma", "FORMA — " + t(L, "Formación aplicada en IA y Project Management", "Applied training in AI and Project Management"),
                     t(L, "Formación empresarial", "Corporate training"), desc),
        breadcrumb(L, "forma", label),
    ]
    return page(L, "forma", title, desc, body, jsonld=jsonld)


def build_asesora(L):
    title = t(L, "Asesoría estratégica de inversión y proyecto | Zirotti", "Strategic Investment & Project Advisory | Zirotti")
    desc = t(
        L,
        "Criterio técnico-estratégico para decisiones de inversión: viabilidad, CAPEX, riesgos y business case. Para inversores, promotores y family offices.",
        "Technical-strategic judgment for investment decisions: feasibility, CAPEX, risk and business case. For investors, developers and family offices.",
    )
    label = "ASESORA"
    hero = page_hero(
        L, "02", "ASESORA",
        t(L, "Asesoría estratégica de <em>inversión y proyecto</em>", "Strategic <em>investment &amp; project</em> advisory"),
        t(L, "Criterio técnico-estratégico para decisiones de inversión, viabilidad y transformación de activos. Para inversores, promotores y directivos que necesitan más que un informe.", "Technical-strategic judgment for investment, feasibility and asset-transformation decisions. For investors, developers and executives who need more than a report."),
        [("0,5–15M€" if L == "es" else "€0.5–15M", t(L, "CAPEX por proyecto", "CAPEX per project")), ("2", t(L, "formatos de contratación", "engagement formats")), (t(L, "Criterio", "Judgment"), t(L, "no informes estéticos", "not polished reports"))],
    )
    value = value_block(
        L,
        t(L, "ASESORA no produce informes estéticos: produce <em>criterio</em>.", "ASESORA doesn’t produce polished reports: it produces <em>judgment</em>."),
        [
            t(L, "Cada entregable responde a una pregunta concreta que un inversor o directivo necesita resolver antes de comprometer capital o tiempo. El servicio combina análisis técnico de construcción y proyecto con visión de negocio y estructuración financiera básica.", "Each deliverable answers a concrete question an investor or executive needs to resolve before committing capital or time. The service combines technical construction and project analysis with business vision and basic financial structuring."),
            t(L, "El diferenciador frente a una consultora generalista: el asesor ha ejecutado proyectos de entre 0,5M€ y 15M€ de CAPEX, conoce la brecha entre el papel y la obra, y ha participado en comités de inversión reales.", "The differentiator versus a generalist consultancy: the advisor has executed projects between €0.5M and €15M in CAPEX, knows the gap between paper and site, and has sat on real investment committees."),
        ],
    )
    K = {k: t(L, a, b) for k, (a, b) in {
        "ded": ("Dedicación", "Dedication"), "min": ("Mínimo", "Minimum"), "inc": ("Incluye", "Includes"),
        "per": ("Perfil", "Profile"), "dur": ("Duración", "Duration"), "est": ("Estructura", "Structure"),
        "uso": ("Casos de uso", "Use cases"), "ent": ("Entregables", "Deliverables"),
    }.items()}
    foot = (t(L, "Presupuesto a medida", "Custom quote"), t(L, "Tras una primera consulta, sin compromiso.", "After an initial, no-commitment consultation."))
    cards = card(t(L, "Formato A", "Format A"), t(L, "Retainer mensual", "Monthly retainer"), [
        (K["ded"], t(L, "10–15 h/mes flexibles, ajustadas a la carga del período", "10–15 h/month, flexible to the period’s load")),
        (K["min"], t(L, "3 meses (renovable trimestralmente)", "3 months (renewable quarterly)")),
        (K["inc"], t(L, "Sesión mensual de seguimiento · Revisión de documentos y propuestas · Acceso directo para consultas · 1 entregable mensual", "Monthly review session · Document &amp; proposal review · Direct access for questions · 1 monthly deliverable")),
        (K["per"], t(L, "Holdings, family offices, promotores con cartera activa", "Holdings, family offices, developers with an active portfolio")),
    ], foot) + card(t(L, "Formato B", "Format B"), t(L, "Proyecto acotado", "Scoped project"), [
        (K["dur"], t(L, "2–8 semanas según alcance", "2–8 weeks depending on scope")),
        (K["est"], t(L, "Kick-off · Análisis · Entregable final · Sesión de presentación", "Kick-off · Analysis · Final deliverable · Presentation session")),
        (K["uso"], t(L, "Business case de nuevo activo · Viabilidad técnico-económica · Informe de riesgo · CAPEX y cronograma para comité · Estructuración de SPV", "New-asset business case · Techno-economic feasibility · Risk report · CAPEX &amp; schedule for committee · SPV structuring")),
        (K["ent"], t(L, "Documento estratégico · Modelización de escenarios · Matriz de riesgos · Presentación ejecutiva", "Strategic document · Scenario modeling · Risk matrix · Executive presentation")),
    ], foot)
    formats = f"""<section class="block"><div class="wrap">
  {sec_head(t(L, "Formatos de contratación", "Engagement formats"))}
  <div class="cards">{cards}</div>
</div></section>"""
    sectors = [
        (t(L, "Real estate operacional", "Operational real estate"), t(L, "Hoteles boutique, locales en prime, activos mixtos residencial-comercial.", "Boutique hotels, prime units, mixed residential-commercial assets.")),
        ("Retail &amp; QSR", t(L, "Expansión de cadenas, nueva ubicación, refit o cambio de operador.", "Chain expansion, new locations, refit or operator change.")),
        ("Hospitality", t(L, "Transformación de activos, refitting, cambio de marca o modelo.", "Asset transformation, refitting, brand or model change.")),
        (t(L, "Industrial / mixto", "Industrial / mixed-use"), t(L, "Proyectos en desarrollo en España y Chile.", "Projects under development in Spain and Chile.")),
    ]
    sl = "".join(f"<li><h3>{h}</h3><p>{p}</p></li>" for h, p in sectors)
    sect = f"""<section class="block block--tint"><div class="wrap">
  {sec_head(t(L, "Sectores prioritarios", "Priority sectors"))}
  <ul class="sector-list">{sl}</ul>
</div></section>"""
    faq = faq_block(L, t(L, "Preguntas frecuentes", "Frequently asked questions"), [
        (t(L, "¿En qué se diferencia ASESORA de una consultora generalista?", "How does ASESORA differ from a generalist consultancy?"),
         t(L, "El asesor ha ejecutado proyectos de entre 0,5 M€ y 15 M€ de CAPEX, conoce la brecha entre el papel y la obra y ha participado en comités de inversión reales. Cada entregable responde a una pregunta concreta que hay que resolver antes de comprometer capital o tiempo.", "The advisor has executed projects between €0.5M and €15M in CAPEX, knows the gap between paper and site, and has sat on real investment committees. Each deliverable answers a concrete question to resolve before committing capital or time.")),
        (t(L, "¿Qué formatos de contratación existen?", "What engagement formats are available?"),
         t(L, "Retainer mensual (10–15 h/mes, mínimo 3 meses renovable trimestralmente) o proyecto acotado de 2 a 8 semanas según alcance, con kick-off, análisis, entregable final y sesión de presentación.", "Monthly retainer (10–15 h/month, 3-month minimum renewable quarterly) or a scoped project of 2 to 8 weeks depending on scope, with kick-off, analysis, final deliverable and presentation session.")),
        (t(L, "¿Qué recibo en un proyecto de asesoría de inversión?", "What do I receive in an investment advisory project?"),
         t(L, "Un documento estratégico, modelización de escenarios, matriz de riesgos y una presentación ejecutiva. Casos habituales: business case de un nuevo activo, viabilidad técnico-económica, informe de riesgo, CAPEX y cronograma para comité y estructuración de SPV.", "A strategic document, scenario modeling, a risk matrix and an executive presentation. Typical cases: new-asset business case, techno-economic feasibility, risk report, CAPEX and schedule for committee, and SPV structuring.")),
        (t(L, "¿Cuánto cuesta y cuánto tarda?", "How much does it cost and how long does it take?"),
         t(L, "Se presupuesta a medida tras una primera consulta, sin compromiso. El contrato fija alcance y entregables antes del inicio. Ciclo habitual: 4–8 semanas.", "Quotes are custom, after an initial no-commitment consultation. The contract sets scope and deliverables before kick-off. Typical cycle: 4–8 weeks.")),
    ])
    cta = cta_block(
        L,
        t(L, "¿Tienes una decisión sobre la mesa?", "Have a decision on the table?"),
        t(L, "Contrato con alcance y entregables definidos antes del inicio. Ciclo habitual: 4–8 semanas.", "Contract with scope and deliverables defined before kick-off. Typical cycle: 4–8 weeks."),
    )
    body = crumbs(L, label) + hero + value + formats + sect + faq + cta + others_block(L, "asesora")
    jsonld = [
        service_node(L, "asesora", "ASESORA — " + t(L, "Asesoría estratégica de inversión y proyecto", "Strategic investment and project advisory"),
                     t(L, "Asesoría estratégica de inversión", "Strategic investment advisory"), desc),
        breadcrumb(L, "asesora", label),
    ]
    return page(L, "asesora", title, desc, body, jsonld=jsonld)


def build_dirige(L):
    title = t(L, "Director de expansión fractional (retail, QSR) | Zirotti", "Fractional Expansion Director (Retail, QSR) | Zirotti")
    desc = t(
        L,
        "Director de expansión y obra a tiempo parcial para cadenas de 10–60 unidades, grupos de restauración y operadores hoteleros. +75 M€ de CAPEX gestionado.",
        "Part-time senior expansion and construction director for 10–60-unit chains, restaurant groups and hotel operators. €75M+ CAPEX managed.",
    )
    label = "DIRIGE"
    hero = page_hero(
        L, "03", "DIRIGE",
        t(L, "Dirección fractional de <em>expansión y obra</em>", "Fractional direction of <em>expansion &amp; construction</em>"),
        t(L, "El mejor perfil en tu proyecto, sin el coste de un Director fijo a jornada completa. Acceso a 17 años de experiencia en apertura y remodelación de locales, hoteles y restaurantes.", "The best profile on your project, without the cost of a full-time Director. Access to 17 years of experience opening and remodeling retail units, hotels and restaurants."),
        [("+75M€" if L == "es" else "€75M+", t(L, "CAPEX gestionado", "CAPEX managed")), ("10–60", t(L, "unidades / cadena", "units / chain")), ("17", t(L, "años de experiencia", "years of experience"))],
    )
    value = value_block(
        L,
        t(L, "Un Director de Expansión <em>a tiempo parcial</em>, con la experiencia de uno a tiempo completo.", "An Expansion Director <em>part-time</em>, with the experience of a full-time one."),
        [t(L, "DIRIGE incorpora a Franco Giuseppe Zirotti como Director de Expansión o de Proyecto a tiempo parcial. El modelo fractional permite a cadenas de 10–60 unidades, promotores y grupos de restauración acceder a ese nivel de experiencia con la flexibilidad y el coste de un colaborador externo.", "DIRIGE brings in Franco Giuseppe Zirotti as a part-time Expansion or Project Director. The fractional model lets 10–60-unit chains, developers and restaurant groups access that level of experience with the flexibility and cost of an external collaborator.")],
    )
    K = {k: t(L, a, b) for k, (a, b) in {
        "ded": ("Dedicación", "Dedication"), "min": ("Mínimo", "Minimum"), "inc": ("Incluye", "Includes"),
        "per": ("Perfil", "Profile"), "alc": ("Alcance", "Scope"), "fas": ("Fases", "Phases"),
        "ent": ("Entregables", "Deliverables"), "base": ("Base", "Basis"),
    }.items()}
    foot = (t(L, "Presupuesto a medida", "Custom quote"), t(L, "Tras una primera consulta, sin compromiso.", "After an initial, no-commitment consultation."))
    cards = card(t(L, "Formato A", "Format A"), t(L, "Retainer mensual", "Monthly retainer"), [
        (K["ded"], t(L, "20–40 h/mes según fase del proyecto", "20–40 h/month depending on project phase")),
        (K["min"], t(L, "Trimestral (renovable)", "Quarterly (renewable)")),
        (K["inc"], t(L, "Coordinación de equipos técnicos · Seguimiento de obra y proveedores · Control de CAPEX y cronograma · Participación en comités · Reporting mensual · Gestión de incidencias", "Technical-team coordination · Site &amp; supplier follow-up · CAPEX &amp; schedule control · Committee participation · Monthly reporting · Issue management")),
        (K["per"], t(L, "Cadenas QSR o retail (10–60 unidades) · Grupos de restauración en expansión · Operadores hoteleros", "QSR or retail chains (10–60 units) · Expanding restaurant groups · Hotel operators")),
    ], foot, badge=t(L, "Director fractional", "Fractional director")) + card(t(L, "Formato B", "Format B"), t(L, "Dirección de proyecto", "Project direction"), [
        (K["base"], t(L, "Por proyecto", "Per-project basis")),
        (K["alc"], t(L, "De la decisión de inversión a la entrega de llaves y puesta en marcha", "From investment decision to handover and go-live")),
        (K["fas"], t(L, "Viabilidad técnica · Licencias y permisos · Proyecto de ejecución · Licitación · Construcción y supervisión · FF&amp;E y equipamiento · Apertura", "Technical feasibility · Licenses &amp; permits · Execution project · Tendering · Construction &amp; supervision · FF&amp;E &amp; equipment · Opening")),
        (K["ent"], t(L, "Plan de proyecto · Presupuesto y control de CAPEX · Cronograma Gantt · Actas de seguimiento · Informe de cierre", "Project plan · Budget &amp; CAPEX control · Gantt schedule · Follow-up minutes · Closeout report")),
        (K["per"], t(L, "Promotores con proyectos singulares · Operadores abriendo mercado nuevo · Inversores que transforman activos", "Developers with singular projects · Operators entering new markets · Investors transforming assets")),
    ], foot)
    formats = f"""<section class="block"><div class="wrap">
  {sec_head(t(L, "Formatos de contratación", "Engagement formats"))}
  <div class="cards">{cards}</div>
</div></section>"""
    scope = [
        t(L, "Análisis técnico del local o activo: planos, instalaciones, estado de conservación, adecuación normativa CTE.", "Technical analysis of the unit or asset: plans, installations, condition, CTE compliance."),
        t(L, "Coordinación con el arquitecto de proyecto y la dirección facultativa.", "Coordination with the project architect and works management."),
        t(L, "Licitación y selección de contratistas y proveedores.", "Tendering and selection of contractors and suppliers."),
        t(L, "Control de costes, certificaciones y gestión de cambios.", "Cost control, certifications and change management."),
        t(L, "Coordinación con operaciones, marketing y RRHH para la puesta en marcha.", "Coordination with operations, marketing and HR for go-live."),
        t(L, "Reporting a inversor o comité directivo con métricas de avance y desvío.", "Reporting to investor or board with progress and variance metrics."),
    ]
    st = "".join(f'<li><span class="num" aria-hidden="true">0{i}</span><p>{s}</p></li>' for i, s in enumerate(scope, 1))
    scope_sec = f"""<section class="block block--tint"><div class="wrap">
  {sec_head(t(L, "Alcance típico de un proyecto", "Typical project scope"))}
  <ol class="steps">{st}</ol>
</div></section>"""
    faq = faq_block(L, t(L, "Preguntas frecuentes", "Frequently asked questions"), [
        (t(L, "¿Qué es un director de expansión fractional?", "What is a fractional expansion director?"),
         t(L, "Es un Director de Expansión o de Proyecto a tiempo parcial, con la experiencia de uno a tiempo completo. El modelo fractional da acceso a ese nivel con la flexibilidad y el coste de un colaborador externo, sin la estructura de un director fijo a jornada completa.", "A part-time Expansion or Project Director with the experience of a full-time one. The fractional model gives access to that level with the flexibility and cost of an external collaborator, without the overhead of a full-time director.")),
        (t(L, "¿Para quién es DIRIGE?", "Who is DIRIGE for?"),
         t(L, "Para cadenas QSR o retail de 10–60 unidades, grupos de restauración en expansión, operadores hoteleros, promotores con proyectos singulares, operadores que abren mercado nuevo e inversores que transforman activos.", "For QSR or retail chains of 10–60 units, expanding restaurant groups, hotel operators, developers with singular projects, operators entering new markets and investors transforming assets.")),
        (t(L, "¿Qué dedicación y duración tiene?", "What are the time commitment and duration?"),
         t(L, "El retainer mensual es de 20–40 h/mes según la fase, con mínimo trimestral renovable. El ciclo habitual de un proyecto es de 6–12 semanas y se formaliza con un contrato mercantil de servicios con SLA, dedicación y entregables definidos.", "The monthly retainer is 20–40 h/month depending on phase, with a renewable quarterly minimum. A typical project cycle is 6–12 weeks, formalised through a commercial services contract with SLA, dedication and defined deliverables.")),
        (t(L, "¿Qué incluye la dirección de un proyecto de apertura u obra?", "What does directing an opening or construction project include?"),
         t(L, "Desde la decisión de inversión hasta la entrega de llaves y puesta en marcha: viabilidad técnica, licencias y permisos, proyecto de ejecución, licitación, construcción y supervisión, FF&amp;E y apertura, con control de CAPEX, cronograma y reporting a inversor o comité.", "From investment decision to handover and go-live: technical feasibility, licenses and permits, execution project, tendering, construction and supervision, FF&amp;E and opening, with CAPEX control, schedule and reporting to investor or board.")),
    ])
    cta = cta_block(
        L,
        t(L, "¿Diriges una expansión este año?", "Running an expansion this year?"),
        t(L, "Contrato mercantil de servicios con SLA, dedicación y entregables definidos. Ciclo habitual: 6–12 semanas.", "Commercial services contract with SLA, dedication and defined deliverables. Typical cycle: 6–12 weeks."),
    )
    body = crumbs(L, label) + hero + value + formats + scope_sec + faq + cta + others_block(L, "dirige")
    jsonld = [
        service_node(L, "dirige", "DIRIGE — " + t(L, "Dirección fractional de expansión y obra", "Fractional direction of expansion and construction"),
                     t(L, "Dirección de expansión y obra a tiempo parcial", "Fractional expansion and construction direction"), desc),
        breadcrumb(L, "dirige", label),
    ]
    return page(L, "dirige", title, desc, body, jsonld=jsonld)


def build_legal(L):
    title = t(L, "Aviso legal, privacidad y cookies | Zirotti", "Legal notice, privacy & cookies | Zirotti")
    desc = t(L, "Aviso legal, política de privacidad y política de cookies de Zirotti Strategic Advisory.", "Legal notice, privacy policy and cookie policy of Zirotti Strategic Advisory.")
    mail = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'
    browsers = (
        '<li><a href="https://support.google.com/chrome/answer/95647" target="_blank" rel="noopener">Google Chrome</a></li>'
        '<li><a href="https://support.mozilla.org/kb/cookies-informacion-que-los-sitios-web-guardan" target="_blank" rel="noopener">Mozilla Firefox</a></li>'
        '<li><a href="https://support.apple.com/es-es/guide/safari/sfri11471/mac" target="_blank" rel="noopener">Safari</a></li>'
        '<li><a href="https://support.microsoft.com/microsoft-edge" target="_blank" rel="noopener">Microsoft Edge</a></li>'
    )
    body = f"""<div class="wrap legal-head">
  <a class="nav-link" href="{url("home", L)}">← {t(L, "Inicio", "Home")}</a>
  <p class="label" style="margin-top:28px">{t(L, "Información legal", "Legal information")}</p>
  <h1>{t(L, "Aviso legal, privacidad y cookies", "Legal notice, privacy &amp; cookies")}</h1>
  <nav class="subtabs" aria-label="{t(L, "Secciones", "Sections")}"><a href="#aviso">{t(L, "Aviso legal", "Legal notice")}</a><a href="#privacidad">{t(L, "Privacidad", "Privacy")}</a><a href="#cookies">Cookies</a></nav>
</div>

<div class="wrap">
<section id="aviso" class="legal">
  <h2>1 · {t(L, "Aviso legal", "Legal notice")}</h2>
  <p>{t(L, "En cumplimiento del artículo 10 de la Ley 34/2002, de Servicios de la Sociedad de la Información y de Comercio Electrónico (LSSI-CE), se informa de los datos identificativos del titular de este sitio web:", "In compliance with Article 10 of Spanish Law 34/2002 on Information Society Services and E-Commerce (LSSI-CE), the identifying details of the owner of this website are provided:")}</p>
  <ul>
    <li>{t(L, "Titular:", "Owner:")} Franco Giuseppe Zirotti</li>
    <li>NIF / CIF: X8913104Y</li>
    <li>{t(L, "Domicilio:", "Address:")} Calle Costa Brava Nº20, 28034 - Madrid</li>
    <li>{t(L, "Correo electrónico:", "Email:")} {mail}</li>
    <li>{t(L, "Teléfono:", "Phone:")} {PHONE}</li>
    <li>{t(L, "Sitio web:", "Website:")} www.zirotti.com</li>
  </ul>
  <h3>{t(L, "Objeto", "Purpose")}</h3>
  <p>{t(L, "Este aviso regula el uso del sitio web, que el titular pone a disposición de los usuarios con carácter informativo sobre sus servicios de asesoría estratégica, formación y dirección de proyectos.", "This notice governs the use of the website, made available by the owner for informational purposes regarding its strategic advisory, training and project-direction services.")}</p>
  <h3>{t(L, "Propiedad intelectual e industrial", "Intellectual &amp; industrial property")}</h3>
  <p>{t(L, "Todos los contenidos del sitio (textos, marca «Zirotti», logotipo, diseño, estructura y código) son titularidad del titular o cuenta con licencia para su uso. Queda prohibida su reproducción, distribución o transformación sin autorización expresa.", "All site content (texts, the «Zirotti» brand, logo, design, structure and code) is owned by the owner or duly licensed. Its reproduction, distribution or transformation without express authorization is prohibited.")}</p>
  <h3>{t(L, "Responsabilidad", "Liability")}</h3>
  <p>{t(L, "El titular no se hace responsable del uso indebido de los contenidos, ni del contenido de sitios de terceros enlazados. Se reserva el derecho a modificar la información sin previo aviso.", "The owner is not liable for improper use of the content or for the content of linked third-party sites, and reserves the right to modify information without prior notice.")}</p>
  <h3>{t(L, "Legislación aplicable", "Applicable law")}</h3>
  <p>{t(L, "Estas condiciones se rigen por la legislación española. Para cualquier controversia, las partes se someten a los juzgados y tribunales de Madrid, salvo que la normativa de consumo disponga otro fuero.", "These terms are governed by Spanish law. For any dispute, the parties submit to the courts of Madrid, unless consumer regulations provide otherwise.")}</p>
</section>

<section id="privacidad" class="legal">
  <h2>2 · {t(L, "Política de privacidad", "Privacy policy")}</h2>
  <p>{t(L, "De acuerdo con el Reglamento (UE) 2016/679 (RGPD) y la Ley Orgánica 3/2018 (LOPDGDD), te informamos sobre el tratamiento de tus datos personales.", "In accordance with Regulation (EU) 2016/679 (GDPR) and Spanish Organic Law 3/2018 (LOPDGDD), we inform you about the processing of your personal data.")}</p>
  <h3>{t(L, "Responsable del tratamiento", "Data controller")}</h3>
  <p>Franco Giuseppe Zirotti — NIF X8913104Y, Costa Brava 20, 28034 - Madrid. {t(L, "Contacto:", "Contact:")} {mail}.</p>
  <h3>{t(L, "Datos que tratamos", "Data we process")}</h3>
  <p>{t(L, "Los que nos facilitas voluntariamente a través del formulario de contacto o por correo, teléfono o WhatsApp: nombre, empresa, correo electrónico, línea de servicio de interés y el contenido de tu mensaje.", "Those you voluntarily provide through the contact form or via email, phone or WhatsApp: name, company, email address, service line of interest and the content of your message.")}</p>
  <h3>{t(L, "Finalidad y base jurídica", "Purpose &amp; legal basis")}</h3>
  <ul>
    <li>{t(L, "Atender tu solicitud de información y gestionar una posible relación comercial — base: tu consentimiento (art. 6.1.a RGPD) y medidas precontractuales (art. 6.1.b).", "To respond to your enquiry and manage a possible commercial relationship — basis: your consent (Art. 6.1.a GDPR) and pre-contractual measures (Art. 6.1.b).")}</li>
    <li>{t(L, "No se realizan decisiones automatizadas ni elaboración de perfiles.", "No automated decision-making or profiling is carried out.")}</li>
  </ul>
  <h3>{t(L, "Conservación", "Retention")}</h3>
  <p>{t(L, "Conservamos tus datos mientras dure la relación y, después, durante los plazos legales aplicables. Cuando dejen de ser necesarios, se suprimen de forma segura.", "We keep your data for the duration of the relationship and thereafter for the applicable legal periods. Once no longer necessary, it is securely deleted.")}</p>
  <h3>{t(L, "Destinatarios y encargados", "Recipients &amp; processors")}</h3>
  <p>{t(L, "No cedemos tus datos a terceros salvo obligación legal. Pueden acceder a ellos, como encargados del tratamiento, nuestros proveedores tecnológicos de correo y alojamiento web, sujetos a contrato. El formulario de contacto se envía a través del servicio FormSubmit (formsubmit.co), que nos entrega el mensaje por correo electrónico.", "We do not share your data with third parties except by legal obligation. Our email and web-hosting technology providers may access it as data processors, under contract. The contact form is sent through the FormSubmit service (formsubmit.co), which delivers the message to us by email.")}</p>
  <h3>{t(L, "Transferencias internacionales", "International transfers")}</h3>
  <p>{t(L, "Este sitio no carga recursos de terceros: las tipografías se sirven desde el propio dominio. El proveedor del formulario (FormSubmit) puede tratar los datos que envíes fuera del Espacio Económico Europeo; consulta su política de privacidad en formsubmit.co.", "This site loads no third-party resources: fonts are served from our own domain. The form provider (FormSubmit) may process the data you submit outside the European Economic Area; see its privacy policy at formsubmit.co.")}</p>
  <h3>{t(L, "Tus derechos", "Your rights")}</h3>
  <p>{t(L, f'Puedes ejercer los derechos de acceso, rectificación, supresión, oposición, limitación del tratamiento y portabilidad escribiendo a {mail}, indicando el derecho que deseas ejercer. También puedes retirar tu consentimiento en cualquier momento y presentar una reclamación ante la Agencia Española de Protección de Datos (<a href="https://www.aepd.es" target="_blank" rel="noopener">www.aepd.es</a>).', f'You may exercise your rights of access, rectification, erasure, objection, restriction of processing and portability by writing to {mail}, stating the right you wish to exercise. You may also withdraw your consent at any time and lodge a complaint with the Spanish Data Protection Agency (<a href="https://www.aepd.es" target="_blank" rel="noopener">www.aepd.es</a>).')}</p>
</section>

<section id="cookies" class="legal">
  <h2>3 · {t(L, "Política de cookies", "Cookie policy")}</h2>
  <p>{t(L, "Una cookie o almacenamiento local es un pequeño fichero que se guarda en tu dispositivo al visitar el sitio. Este sitio <strong>no instala cookies ni utiliza almacenamiento local</strong>: no hay cookies técnicas, analíticas, publicitarias ni de redes sociales, por lo que no se muestra aviso de consentimiento.", "A cookie or local storage is a small file saved on your device when you visit the site. This site <strong>does not set cookies or use local storage</strong>: there are no technical, analytics, advertising or social-media cookies, so no consent notice is shown.")}</p>
  <h3>{t(L, "Servicios de terceros", "Third-party services")}</h3>
  <p>{t(L, "Las tipografías se alojan en este mismo sitio; no se cargan desde Google Fonts ni desde ningún otro servidor externo. Los enlaces a WhatsApp o LinkedIn te llevan a sitios de terceros con sus propias políticas.", "Fonts are hosted on this site itself; they are not loaded from Google Fonts or any other external server. Links to WhatsApp or LinkedIn take you to third-party sites with their own policies.")}</p>
  <h3>{t(L, "Cómo gestionarlas", "How to manage them")}</h3>
  <p>{t(L, "Aunque este sitio no almacena información en tu dispositivo, puedes eliminar o bloquear cookies y almacenamiento desde la configuración de tu navegador:", "Although this site stores nothing on your device, you can delete or block cookies and storage from your browser settings:")}</p>
  <ul>{browsers}</ul>
  <p>{t(L, "Última actualización: octubre de 2026.", "Last updated: October 2026.")}</p>
</section>
</div>"""
    return page(L, "legal", title, desc, body, robots="noindex, follow", jsonld=[breadcrumb(L, "legal", t(L, "Aviso legal", "Legal notice"))])


def build_404():
    L = "es"
    body = f"""<section class="notfound"><div class="wrap">
  <p class="label">404</p>
  <h1>{t(L, "Esta página no existe.", "This page doesn’t exist.")}</h1>
  <p class="lead" style="margin-bottom:32px">{t(L, "Puede que el enlace haya cambiado. Vuelve al inicio o elige una de las líneas de servicio.", "")}</p>
  <div class="btn-row"><a class="btn btn--fill" href="/">{t(L, "Ir al inicio", "")}</a><a class="btn btn--line" href="/en/">Go to the English site</a></div>
</div></section>"""
    out = page(L, "home", "404 | Zirotti Strategic Advisory", "", body, robots="noindex, follow", alt=False)
    # la 404 no necesita canonical ni metadatos sociales
    out = "\n".join(l for l in out.split("\n") if 'rel="canonical"' not in l and 'og:' not in l and 'twitter:' not in l and 'name="description"' not in l)
    return out


# --------------------------------------------------------------------------
# Salida
# --------------------------------------------------------------------------
def write(path, content):
    p = OUT / path.lstrip("/")
    if path.endswith("/"):
        p = p / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def sitemap():
    today = date.today().isoformat()
    rows = []
    for key in ("home", "forma", "asesora", "dirige"):
        for L in ("es", "en"):
            alts = "".join(
                f'<xhtml:link rel="alternate" hreflang="{l}" href="{SITE + url(key, l)}"/>' for l in ("es", "en")
            ) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE + url(key, "es")}"/>'
            prio = "1.0" if key == "home" and L == "es" else ("0.9" if key == "home" else "0.8")
            rows.append(f"<url><loc>{SITE + url(key, L)}</loc><lastmod>{today}</lastmod><priority>{prio}</priority>{alts}</url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(rows) + "\n</urlset>\n")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC / "assets", OUT / "assets", ignore=shutil.ignore_patterns("*.py", ".DS_Store"))
    # favicon + apple-touch-icon en la raíz
    for name in ("favicon.svg", "apple-touch-icon.png"):
        f = SRC / "root" / name
        if f.exists():
            shutil.copy(f, OUT / name)
    builders = {"home": build_home, "forma": build_forma, "asesora": build_asesora, "dirige": build_dirige, "legal": build_legal}
    for key, fn in builders.items():
        for L in ("es", "en"):
            write(url(key, L), fn(L))
    write("/404.html", build_404())
    (OUT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    pages = sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*.html"))
    print("OK —", len(pages), "páginas HTML en", OUT)
    for p in pages:
        print("  ", p)


if __name__ == "__main__":
    main()
