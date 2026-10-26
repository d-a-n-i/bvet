# -*- coding: utf-8 -*-
"""HTML components, page layout and JSON-LD for the site generator."""
import json
import html as H
from clinic import *  # noqa: F401,F403
from clinic import href as h, url as absurl
import content as C

IMG = {}  # filled by build.py from the image manifest

# ---------------------------------------------------------------------------
# Icons (24x24, stroke-based, inherit currentColor)
# ---------------------------------------------------------------------------
_S = 'fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"'
ICONS = {
    "phone": f'<path {_S} d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.4-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    "whatsapp": '<path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 1.8a8.2 8.2 0 0 1 0 16.4 8.1 8.1 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 0 1 12 3.8zm-3.3 4.4c-.2 0-.5 0-.7.3-.3.3-1 1-1 2.4s1 2.8 1.2 3c.1.2 2 3.2 5 4.4 2.5 1 3 .8 3.5.7.5 0 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.3l-2-1c-.3-.1-.5-.1-.7.2l-.9 1.1c-.2.2-.3.2-.6.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.4.1-.2 0-.4 0-.5l-.9-2.1c-.2-.6-.5-.5-.7-.5h-.6z"/>',
    "waze": f'<path {_S} d="M12 3a8 8 0 0 0-8 8c0 1.5.3 2.6.9 3.6L3 19l4.4-.4A8.3 8.3 0 0 0 12 20a8.5 8.5 0 0 0 8-8.5A8 8 0 0 0 12 3z"/><circle cx="9.5" cy="10.5" r="1" fill="currentColor"/><circle cx="14.5" cy="10.5" r="1" fill="currentColor"/><path {_S} d="M9 14c1.5 1.3 4.5 1.3 6 0"/>',
    "pin": f'<path {_S} d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 0 1 18 0z"/><circle {_S} cx="12" cy="10" r="3"/>',
    "clock": f'<circle {_S} cx="12" cy="12" r="9"/><path {_S} d="M12 7v5l3 2"/>',
    "mail": f'<rect {_S} x="3" y="5" width="18" height="14" rx="2"/><path {_S} d="m3 7 9 6 9-6"/>',
    "check": f'<path {_S} d="M20 6 9 17l-5-5"/>',
    "arrow": f'<path {_S} d="M19 12H5M12 19l-7-7 7-7"/>',
    "chev": f'<path {_S} d="m6 9 6 6 6-6"/>',
    "menu": f'<path {_S} d="M3 6h18M3 12h18M3 18h18"/>',
    "close": f'<path {_S} d="M18 6 6 18M6 6l12 12"/>',
    "star": '<path fill="currentColor" d="M12 2l3 6.2 6.8 1-4.9 4.8 1.2 6.8L12 17.6 5.9 20.8l1.2-6.8L2.2 9.2 9 8.2z"/>',
    "heart": '<path fill="currentColor" d="M12 21s-7-4.4-9.5-8.5C.5 9 2.3 5 6 5c2.1 0 3.4 1.2 4 2.3C10.6 6.2 11.9 5 14 5c3.7 0 5.5 4 3.5 7.5C19 16.6 12 21 12 21z"/>',
    "paw": '<path fill="currentColor" d="M8 8.5c1.2 0 2-1.3 2-3s-.8-3-2-3-2 1.3-2 3 .8 3 2 3zm8 0c1.2 0 2-1.3 2-3s-.8-3-2-3-2 1.3-2 3 .8 3 2 3zM4 13c1.1 0 1.8-1.1 1.8-2.6S5.1 7.8 4 7.8s-1.8 1.1-1.8 2.6S2.9 13 4 13zm16 0c1.1 0 1.8-1.1 1.8-2.6S21.1 7.8 20 7.8s-1.8 1.1-1.8 2.6S18.9 13 20 13zm-8-2c-3 0-6.5 3.3-6.5 6.2 0 1.6 1.1 2.8 2.7 2.8 1.3 0 2.3-.9 3.8-.9s2.5.9 3.8.9c1.6 0 2.7-1.2 2.7-2.8C18.5 14.3 15 11 12 11z"/>',
    "scalpel": f'<path {_S} d="M3 21 14.5 9.5M14.5 9.5l5.3-5.3a2 2 0 0 1 2.8 2.8L17.3 12.3M14.5 9.5 17.3 12.3M3 21h4l10-10"/>',
    "syringe": f'<path {_S} d="m18 2 4 4M20 4l-9 9M9 13l-2 2M14 8l2 2M11 11l2 2M4 20l3-3M7.5 10.5l6 6a2 2 0 0 1 0 2.8l-1.2 1.2a2 2 0 0 1-2.8 0l-6-6a2 2 0 0 1 0-2.8l1.2-1.2a2 2 0 0 1 2.8 0z"/>',
    "flask": f'<path {_S} d="M9 3h6M10 3v6.5L4.5 19a1.5 1.5 0 0 0 1.3 2.2h12.4a1.5 1.5 0 0 0 1.3-2.2L14 9.5V3M7 15h10"/>',
    "xray": f'<rect {_S} x="3" y="3" width="18" height="18" rx="3"/><path {_S} d="M12 6v12M8 9h8M8.5 12h7M9 15h6"/>',
    "tooth": f'<path {_S} d="M7.5 3C5 3 3.5 5 3.5 7.5c0 2 1 3 1.5 5s.5 8 2.5 8 2-5 4.5-5 2.5 5 4.5 5 2-6 2.5-8 1.5-3 1.5-5C20.5 5 19 3 16.5 3c-1.8 0-3 1-4.5 1s-2.7-1-4.5-1z"/>',
    "heartpulse": f'<path {_S} d="M19.5 12.6 12 20l-7.5-7.4A5 5 0 0 1 12 6a5 5 0 0 1 7.5 6.6z"/><path {_S} d="M3.5 12h4l1.5-3 2.5 6 2-4h7"/>',
    "bowl": f'<path {_S} d="M3 11h18a9 9 0 0 1-18 0z"/><path {_S} d="M12 11V5M9 7.5 12 5l3 2.5M6 20h12"/>',
    "siren": f'<path {_S} d="M6 18v-5a6 6 0 0 1 12 0v5M4 18h16v2H4zM12 3v2M4.9 6.1l1.4 1.4M19.1 6.1l-1.4 1.4"/>',
    "lab": f'<circle {_S} cx="12" cy="12" r="9"/><path {_S} d="M8 12h8M12 8v8"/>',
    "shield": f'<path {_S} d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path {_S} d="m9 12 2 2 4-4"/>',
    "users": f'<circle {_S} cx="9" cy="8" r="3.5"/><path {_S} d="M2.5 20a6.5 6.5 0 0 1 13 0M16 4.5a3.5 3.5 0 0 1 0 7M21.5 20a6.5 6.5 0 0 0-4.5-6.2"/>',
    "book": f'<path {_S} d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v16H6.5A2.5 2.5 0 0 0 4 20.5z"/><path {_S} d="M4 20.5A2.5 2.5 0 0 1 6.5 18H20M8 6h8M8 9.5h6"/>',
    "home": f'<path {_S} d="m3 11 9-8 9 8v10a1 1 0 0 1-1 1h-5v-7h-6v7H4a1 1 0 0 1-1-1z"/>',
    "car": f'<path {_S} d="M5 16 6.3 9.5A2 2 0 0 1 8.3 8h7.4a2 2 0 0 1 2 1.5L19 16M3 16h18v3H3z"/><circle {_S} cx="7.5" cy="19" r="1.5"/><circle {_S} cx="16.5" cy="19" r="1.5"/>',
    "walk": f'<circle {_S} cx="13" cy="4" r="1.8"/><path {_S} d="m7 21 3-7-2-1.5V9l4-2 2 3 3 1M11 14l3 2 1 5"/>',
    "cal": f'<rect {_S} x="3" y="5" width="18" height="16" rx="2"/><path {_S} d="M3 10h18M8 3v4M16 3v4"/>',
    "info": f'<circle {_S} cx="12" cy="12" r="9"/><path {_S} d="M12 11v5M12 8h.01"/>',
    "globe": f'<circle {_S} cx="12" cy="12" r="9"/><path {_S} d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "fb": '<path fill="currentColor" d="M13.5 22v-8h2.7l.4-3.2h-3.1V8.8c0-.9.3-1.6 1.6-1.6h1.7V4.3c-.3 0-1.3-.1-2.5-.1-2.5 0-4.1 1.5-4.1 4.2v2.4H7.4V14h2.8v8z"/>',
    "quote": '<path fill="currentColor" d="M7.2 6C4.5 6.8 3 9 3 12.3V18h6v-6H6.4c0-1.8.9-3 2.8-3.6zm10 0C14.5 6.8 13 9 13 12.3V18h6v-6h-2.6c0-1.8.9-3 2.8-3.6z"/>',
}


def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


def esc(s):
    return H.escape(s, quote=True)


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------
def img_url(name, w=None, ext="webp"):
    m = IMG[name]
    if w is None:
        return h(f"assets/img/{m['fallback']}")
    return h(f"assets/img/{name}-{w}.{ext}")


def picture(name, alt, sizes="(max-width: 720px) 100vw, 50vw", cls="", priority=False, img_cls=""):
    m = IMG[name]
    srcset = ", ".join(f"{h('assets/img/' + name + '-' + str(w) + '.webp')} {w}w" for w in m["widths"])
    loading = 'fetchpriority="high"' if priority else 'loading="lazy"'
    return (
        f'<picture class="{cls}">'
        f'<source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
        f'<img src="{h("assets/img/" + m["fallback"])}" width="{m["w"]}" height="{m["h"]}" alt="{esc(alt)}" '
        f'{loading} decoding="async" class="{img_cls}">'
        f'</picture>'
    )


# ---------------------------------------------------------------------------
# Buttons & small parts
# ---------------------------------------------------------------------------
def btn_call(label=None, cls="btn btn--accent", number=PHONE_TEL, display=PHONE_DISPLAY, track="call"):
    label = label or f"חייגו {display}"
    return f'<a class="{cls}" href="tel:{number}" data-track="{track}">{icon("phone")}<span>{label}</span></a>'


def btn_wa(label="שלחו וואטסאפ", cls="btn btn--wa", link=None, track="whatsapp"):
    link = link or WA_DEFAULT
    return f'<a class="{cls}" href="{link}" target="_blank" rel="noopener" data-track="{track}">{icon("whatsapp")}<span>{label}</span></a>'


def btn_waze(label="נווטו ב-Waze", cls="btn btn--ghost"):
    return f'<a class="{cls}" href="{WAZE}" target="_blank" rel="noopener" data-track="waze">{icon("waze")}<span>{label}</span></a>'


def link_arrow(text, path, cls="link-arrow"):
    return f'<a class="{cls}" href="{h(path)}">{esc(text)} {icon("arrow", "ic ic--sm")}</a>'


def status_pill():
    # Filled by JS from the hours table; server-rendered fallback shows the hours.
    return (f'<span class="status" id="open-status" data-hours=\'{json.dumps(HOURS)}\'>'
            f'<span class="status__dot" aria-hidden="true"></span>'
            f'<span class="status__text">{HOURS_SHORT}</span></span>')


# ---------------------------------------------------------------------------
# Header / footer / chrome
# ---------------------------------------------------------------------------
NAV = [
    ("שירותים", "services/"),
    ("חירום", "emergency/"),
    ("הצוות", "team/"),
    ("סיפורים", "stories/"),
    ("מדריכים", "guides/"),
    ("שאלות", "faq/"),
    ("צור קשר", "contact/"),
]


def header(page):
    cur = page["slug"]
    links = ""
    for t, p in NAV:
        current = ' aria-current="page"' if cur.startswith(p) else ""
        links += f'<li><a href="{h(p)}"{current}>{esc(t)}</a></li>'
    logo = picture("logo", "הלוגו של מרפאת בן ארי", sizes="56px", cls="brand__logo", priority=True)
    return f'''
<a class="skip" href="#main">דילוג לתוכן</a>
<div class="topbar">
  <div class="wrap topbar__in">
    {status_pill()}
    <div class="topbar__links">
      <a href="tel:{PHONE_TEL}" data-track="call">{icon("phone", "ic ic--sm")} {PHONE_DISPLAY}</a>
      <a href="{WA_DEFAULT}" target="_blank" rel="noopener" data-track="whatsapp">{icon("whatsapp", "ic ic--sm")} וואטסאפ</a>
      <a href="{WAZE}" target="_blank" rel="noopener" data-track="waze">{icon("pin", "ic ic--sm")} {STREET}, רמת אביב</a>
    </div>
  </div>
</div>
<header class="site-header" id="site-header">
  <div class="wrap header__in">
    <a class="brand" href="{h("")}" aria-label="{NAME} — דף הבית">
      {logo}
      <span class="brand__text"><span class="brand__name">{NAME}</span><span class="brand__sub">וטרינרים ברמת אביב · מאז {FOUNDED}</span></span>
    </a>
    <nav class="nav" id="nav" aria-label="ניווט ראשי">
      <ul>{links}</ul>
      <div class="nav__cta">
        {btn_wa("קביעת תור בוואטסאפ", "btn btn--wa btn--sm")}
        {btn_call(PHONE_DISPLAY, "btn btn--accent btn--sm")}
      </div>
    </nav>
    <button class="burger" id="burger" aria-label="פתיחת תפריט" aria-expanded="false" aria-controls="nav">{icon("menu")}{icon("close")}</button>
  </div>
</header>'''


def mobile_bar():
    return f'''
<div class="mbar" role="region" aria-label="יצירת קשר מהירה">
  <a href="tel:{PHONE_TEL}" data-track="call">{icon("phone")}<span>חיוג</span></a>
  <a href="{WA_DEFAULT}" target="_blank" rel="noopener" data-track="whatsapp" class="mbar__wa">{icon("whatsapp")}<span>וואטסאפ</span></a>
  <a href="{WAZE}" target="_blank" rel="noopener" data-track="waze">{icon("waze")}<span>ניווט</span></a>
</div>'''


def footer():
    svc = "".join(f'<li><a href="{h(s["slug"])}">{esc(s["name"])}</a></li>' for s in C.SERVICES)
    info = "".join(f'<li><a href="{h(p)}">{esc(t)}</a></li>' for t, p in [
        ("אודות המרפאה", "about/"), ("הצוות", "team/"), ("סיפורים מהמרפאה", "stories/"),
        ("המלצות", "reviews/"), ("מדריכים", "guides/"), ("שאלות ותשובות", "faq/"),
        ("וטרינר חירום", "emergency/"), ("אזורי שירות", "areas/"), ("הצהרת נגישות ופרטיות", "accessibility/"),
        ("English", "en/"),
    ])
    hours = "".join(f'<tr><th scope="row">{d}</th><td>{a}{(" · " + b) if b else ""}</td></tr>' for d, a, b in HOURS_ROWS)
    return f'''
<footer class="site-footer">
  <div class="wrap foot__grid">
    <div class="foot__brand">
      {picture("logo", "מרפאת בן ארי", sizes="72px", cls="foot__logo")}
      <p class="foot__name">{NAME}</p>
      <p class="foot__tag">מרפאה וטרינרית לכלבים ולחתולים ברמת אביב, תל אביב. {DR_MOSHE} ו{DR_TOMER} — מאז {FOUNDED}.</p>
      <address class="foot__addr">
        <a href="{GMAPS}" target="_blank" rel="noopener">{icon("pin", "ic ic--sm")} {STREET}, {NEIGHBORHOOD}, {CITY_SHORT} — {LANDMARK}</a>
        <a href="tel:{PHONE_TEL}" data-track="call">{icon("phone", "ic ic--sm")} {PHONE_DISPLAY}</a>
        <a href="tel:{MOBILE_TEL}" data-track="call-mobile">{icon("phone", "ic ic--sm")} {MOBILE_DISPLAY} (נייד)</a>
        <a href="{WA_DEFAULT}" target="_blank" rel="noopener" data-track="whatsapp">{icon("whatsapp", "ic ic--sm")} וואטסאפ</a>
        <a href="mailto:{EMAIL}">{icon("mail", "ic ic--sm")} {EMAIL}</a>
        <a href="{FACEBOOK}" target="_blank" rel="noopener">{icon("fb", "ic ic--sm")} פייסבוק</a>
      </address>
    </div>
    <div>
      <h2 class="foot__h">שעות פעילות</h2>
      <table class="hours hours--foot"><tbody>{hours}</tbody></table>
      <p class="foot__note">בערבי חג ובחגים — התקשרו לוודא. חירום מחוץ לשעות הפעילות: {MOBILE_DISPLAY}.</p>
    </div>
    <div>
      <h2 class="foot__h">שירותים</h2>
      <ul class="foot__list">{svc}</ul>
    </div>
    <div>
      <h2 class="foot__h">מידע</h2>
      <ul class="foot__list">{info}</ul>
    </div>
  </div>
  <div class="wrap foot__bottom">
    <span>© {TODAY.year} {NAME} · {STREET}, {CITY_SHORT}</span>
    <span>וטרינר ברמת אביב · וטרינר בצפון תל אביב · מרפאה וטרינרית בתל אביב</span>
  </div>
</footer>'''


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------
def breadcrumbs(trail):
    """trail: list of (name, path). Home is added automatically."""
    items = [("בית", "")] + list(trail)
    lis = []
    for i, (n, p) in enumerate(items):
        last = i == len(items) - 1
        if last:
            lis.append(f'<li aria-current="page">{esc(n)}</li>')
        else:
            lis.append(f'<li><a href="{h(p)}">{esc(n)}</a></li>')
    return f'<nav class="crumbs" aria-label="פירורי לחם"><ol>{"".join(lis)}</ol></nav>'


def page_hero(page, image=None, image_alt="", extra=""):
    media = ""
    if image:
        media = f'<div class="phero__media">{picture(image, image_alt, sizes="(max-width: 900px) 100vw, 42vw", cls="phero__pic", priority=True)}</div>'
    eyebrow = page.get("eyebrow", "")
    return f'''
<section class="phero{" phero--media" if image else ""}">
  <div class="wrap phero__grid">
    <div class="phero__copy">
      {breadcrumbs(page.get("crumbs", []))}
      {f'<p class="eyebrow">{esc(eyebrow)}</p>' if eyebrow else ""}
      <h1>{page["h1"]}</h1>
      <p class="lead">{page["lead"]}</p>
      <div class="cta-row">{btn_call()}{btn_wa()}</div>
      {extra}
    </div>
    {media}
  </div>
</section>'''


def summary_box(items, title="בקצרה"):
    rows = "".join(f'<div class="sum__row"><dt>{esc(k)}</dt><dd>{v}</dd></div>' for k, v in items)
    return f'<section class="sum" aria-label="{esc(title)}"><div class="wrap"><div class="sum__box"><p class="sum__title">{icon("info")} {esc(title)}</p><dl>{rows}</dl></div></div></section>'


def clinic_summary():
    return summary_box([
        ("איפה", f'<a href="{GMAPS}" target="_blank" rel="noopener">{STREET}, {NEIGHBORHOOD}, {CITY_SHORT}</a> — {LANDMARK}'),
        ("מתי", f"{HOURS_SHORT}. שבת סגור."),
        ("טלפון", f'<a href="tel:{PHONE_TEL}" data-track="call">{PHONE_DISPLAY}</a> · נייד וחירום: <a href="tel:{MOBILE_TEL}" data-track="call-mobile">{MOBILE_DISPLAY}</a> · <a href="{WA_DEFAULT}" target="_blank" rel="noopener" data-track="whatsapp">וואטסאפ</a>'),
        ("חניה", "ברחוב ברודצקי ובחניון קניון רמת אביב הסמוך."),
        ("תור", "מומלץ לתאם מראש. במקרה חירום בשעות הפעילות — הגיעו ישירות והתקשרו בדרך."),
        ("מטפלים ב", "כלבים וחתולים, מגור ועד הגיל השלישי."),
    ])


def section_head(title, text="", eyebrow="", center=False):
    eb = f'<p class="eyebrow">{esc(eyebrow)}</p>' if eyebrow else ""
    tx = f"<p>{text}</p>" if text else ""
    cls = " sec-head--c" if center else ""
    return f'<div class="sec-head{cls}">{eb}<h2>{title}</h2>{tx}</div>'


def service_card(s, big=False):
    if big:
        return f'''<a class="scard scard--big" href="{h(s["slug"])}">
      {picture(s["image"], s["image_alt"], sizes="(max-width: 700px) 100vw, 33vw", cls="scard__pic")}
      <div class="scard__body"><span class="scard__ic">{icon(s["icon"])}</span><h3>{esc(s["name"])}</h3><p>{esc(s["short"])}</p><span class="link-arrow">לפרטים {icon("arrow", "ic ic--sm")}</span></div></a>'''
    return f'''<a class="scard" href="{h(s["slug"])}">
      <span class="scard__ic">{icon(s["icon"])}</span>
      <h3>{esc(s["name"])}</h3><p>{esc(s["short"])}</p>
      <span class="link-arrow">לפרטים {icon("arrow", "ic ic--sm")}</span></a>'''


def services_grid(big=False, limit=None):
    items = C.SERVICES[:limit] if limit else C.SERVICES
    return f'<div class="sgrid{" sgrid--big" if big else ""}">{"".join(service_card(s, big) for s in items)}</div>'


def services_section():
    return f'''
<section class="band" id="services">
  <div class="wrap">
    {section_head("טיפול וטרינרי מקיף — במקום אחד", "מרפואה מונעת ועד ניתוחים: מעבדה, רנטגן דיגיטלי, אולטרסאונד וחדר ניתוח במרפאה, כדי שהאבחנה והטיפול יקרו באותו ביקור.", "השירותים שלנו")}
    {services_grid()}
    <p class="band__more">{link_arrow("לכל השירותים", "services/")}</p>
  </div>
</section>'''


WHY = [
    ("cal", "מאז 1985, באותה כתובת", "המרפאה הווטרינרית הוותיקה בתל אביב — ליד קניון רמת אביב כבר שני דורות של בעלי חיים."),
    ("users", "אבא ובן, שני בתי ספר", "ד״ר משה (אוניברסיטת בולוניה) וד״ר תומר (האוניברסיטה העברית, שנתיים במרפאת חירום). תמיד תפגשו אחד מהם."),
    ("flask", "מעבדה עם תוצאות תוך דקות", "ספירת דם וביוכימיה בזמן הביקור — החלטות באותו יום, לא בעוד יומיים."),
    ("xray", "רנטגן דיגיטלי ואולטרסאונד", "אבחון מיידי במקום, בלי לשלוח אתכם למכון."),
    ("scalpel", "חדר ניתוח עם הרדמה מנוטרת", "אלפי ניתוחים: עיקור, גידולים, גופים זרים, שברים."),
    ("book", "הסמכות שכתבה את הספר", "ד״ר משה בן ארי — העורך המדעי של „ספר הכלב“ ו„ספר החתול“ (הוצאת כתר)."),
]


def why_section():
    items = "".join(f'<li><span class="why__ic">{icon(i)}</span><div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></li>' for i, t, d in WHY)
    return f'''
<section class="band band--cream" id="why">
  <div class="wrap why__grid">
    <div>
      {section_head("למה רמת אביב בוחרת בבן ארי כבר 40 שנה", "", "למה אנחנו")}
      <ul class="why">{items}</ul>
      <p class="cta-row">{link_arrow("הכירו את הרופאים", "team/")}</p>
    </div>
    <div class="why__media">
      <figure class="photo-stack">
        {picture("sos-adoption-day", "ד״ר משה וד״ר תומר בן ארי בודקים כלב ביום אימוץ של עמותת SOS לחיות", sizes="(max-width: 900px) 100vw, 40vw", cls="photo-stack__a")}
        {picture("family-visit", "משפחה עם כלב בביקור במרפאת בן ארי, עם שני הרופאים", sizes="(max-width: 900px) 60vw, 24vw", cls="photo-stack__b")}
        <figcaption>יום אימוץ עם עמותת SOS לחיות — ומטופלים בבית, במרפאה.</figcaption>
      </figure>
      <div class="books">
        {picture("book-dog", "כריכת ספר הכלב — עורך מדעי ד״ר משה בן ארי", sizes="110px")}
        {picture("book-cat", "כריכת ספר החתול — עורך מדעי ד״ר משה בן ארי", sizes="110px")}
        <p>„ספר הכלב“ ו„ספר החתול“, הוצאת כתר — עורך מדעי: ד״ר משה בן ארי.</p>
      </div>
    </div>
  </div>
</section>'''


def team_cards():
    cards = []
    for m in C.TEAM:
        facts = "".join(f"<li>{esc(f)}</li>" for f in m["facts"][:2])
        cards.append(f'''<article class="tcard">
          {picture(m["image"], m["image_alt"], sizes="180px", cls="tcard__pic")}
          <h3>{esc(m["name"])}</h3><p class="tcard__role">{esc(m["role"])}</p>
          <ul class="tcard__facts">{facts}</ul>
          {link_arrow("לפרופיל המלא", "team/")}
        </article>''')
    return "".join(cards)


def team_section():
    return f'''
<section class="band" id="team">
  <div class="wrap">
    {section_head("שני רופאים. משפחה אחת. אותם פנים בכל ביקור.", "אתם תמיד תפגשו את ד״ר משה או את ד״ר תומר — רופאים שמכירים את ההיסטוריה של החיה שלכם, לא צוות מתחלף.", "הצוות", center=True)}
    <div class="tgrid">{team_cards()}</div>
  </div>
</section>'''


def story_card(s):
    title, img, alt, text = s
    return f'''<article class="story">
      {picture(img, alt, sizes="(max-width: 700px) 100vw, 33vw", cls="story__pic")}
      <div class="story__body"><h3>{esc(title)}</h3><p>{esc(text)}</p></div></article>'''


def stories_section():
    picks = [C.STORIES[1], C.STORIES[4], C.STORIES[0]]
    return f'''
<section class="band band--teal" id="stories">
  <div class="wrap">
    {section_head("סיפורים מהמרפאה", "ביז׳ו שבלע מטבע, באלו שחגג יום הולדת עם קילו שוקולד, ודולי שנולדה אצלנו בניתוח קיסרי. מטופלים אמיתיים, סיפורים אמיתיים.", "40 שנה של מטופלים")}
    <div class="stgrid">{"".join(story_card(s) for s in picks)}</div>
    <p class="band__more">{link_arrow("לכל הסיפורים", "stories/")}</p>
  </div>
</section>'''


def rating_badges():
    return f'''<div class="badges">
      <a class="badge" href="{GOOGLE_REVIEW}" target="_blank" rel="noopener"><span class="badge__num">{GOOGLE_RATING}</span><span class="badge__stars" aria-hidden="true">{icon("star")}{icon("star")}{icon("star")}{icon("star")}{icon("star")}</span><span class="badge__lbl">{GOOGLE_REVIEWS} ביקורות בגוגל</span></a>
      <a class="badge" href="{FACEBOOK}" target="_blank" rel="noopener"><span class="badge__num">{FB_RECOMMEND}</span><span class="badge__lbl">ממליצים בפייסבוק ({FB_REVIEWS} ביקורות)</span></a>
      <span class="badge"><span class="badge__num">{FOUNDED}</span><span class="badge__lbl">שנת ההקמה · {YEARS} שנים ברמת אביב</span></span>
    </div>'''


def review_card(r):
    name, year, title, text = r
    return f'''<figure class="rev">
      <span class="rev__q">{icon("quote")}</span>
      <blockquote><p class="rev__title">{esc(title)}</p><p>{esc(text)}</p></blockquote>
      <figcaption><span class="rev__av">{esc(name[0])}</span><b>{esc(name)}</b><span>{year}</span></figcaption></figure>'''


def reviews_section(n=3):
    return f'''
<section class="band" id="reviews">
  <div class="wrap">
    {section_head("מה הלקוחות מספרים", "", "המלצות", center=True)}
    {rating_badges()}
    <div class="rgrid">{"".join(review_card(r) for r in C.REVIEWS[:n])}</div>
    <p class="band__more">{link_arrow("לכל ההמלצות", "reviews/")} <a class="link-arrow" href="{GOOGLE_REVIEW}" target="_blank" rel="noopener">כתבו לנו ביקורת בגוגל {icon("arrow", "ic ic--sm")}</a></p>
  </div>
</section>'''


def emergency_band():
    return f'''
<section class="emerg" id="emergency">
  <div class="wrap emerg__in">
    <div class="emerg__copy">
      <p class="eyebrow eyebrow--light">{icon("siren", "ic ic--sm")} מקרה חירום?</p>
      <h2>אל תחכו. התקשרו — ובואו.</h2>
      <p>קשיי נשימה, חתול שלא משתין, בליעת רעל או גוף זר, פציעה, פרכוס, בטן נפוחה — בשעות הפעילות הגיעו ישירות והתקשרו בדרך. מחוץ לשעות הפעילות חייגו לנייד.</p>
      <p class="emerg__links">{link_arrow("מה עושים עד שמגיעים — מדריך החירום", "emergency/")}</p>
    </div>
    <div class="emerg__btns">
      {btn_call(f"מרפאה {PHONE_DISPLAY}", "btn btn--accent btn--lg")}
      {btn_call(f"נייד / אחרי שעות {MOBILE_DISPLAY}", "btn btn--light btn--lg", MOBILE_TEL, MOBILE_DISPLAY, "call-mobile")}
    </div>
  </div>
</section>'''


def hours_table(cls="hours"):
    rows = "".join(f'<tr data-days="{i}"><th scope="row">{d}</th><td>{a}</td><td>{b}</td></tr>' for i, (d, a, b) in enumerate(HOURS_ROWS))
    return f'<table class="{cls}"><caption class="sr-only">שעות פעילות</caption><tbody>{rows}</tbody></table>'


def location_section(with_map=True):
    mp = ""
    if with_map:
        mp = f'''<div class="map">
          <iframe src="{GMAPS_EMBED}" title="מפה: מרפאת בן ארי, ברודצקי 43, תל אביב" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
        </div>'''
    return f'''
<section class="band band--cream" id="location">
  <div class="wrap loc__grid">
    <div class="loc__info">
      {section_head("ליד קניון רמת אביב. קל להגיע, קל לחנות.", "", "שעות ומיקום")}
      <address class="loc__addr">
        <p><strong>{STREET}, {NEIGHBORHOOD}, {CITY_SHORT}</strong><br>{LANDMARK}.</p>
        <p>חניה ברחוב ברודצקי ובחניון הקניון. קווי אוטובוס רבים לקניון רמת אביב ולאוניברסיטת תל אביב; תחנת הרכבת „אוניברסיטה“ במרחק רכיבה קצרה.</p>
      </address>
      {hours_table()}
      <p class="loc__note">{status_pill()}</p>
      <div class="cta-row">{btn_waze()}<a class="btn btn--ghost" href="{GMAPS}" target="_blank" rel="noopener">{icon("pin")}<span>Google Maps</span></a>{btn_call(PHONE_DISPLAY)}</div>
      <p class="loc__areas">מגיעים אלינו מ{C.AREA_LIST_OTHERS}. {link_arrow("הוראות הגעה לפי שכונה", "areas/")}</p>
    </div>
    {mp}
  </div>
</section>'''


def faq_block(items, title="שאלות ותשובות", intro="", open_first=True):
    det = []
    for i, (q, a) in enumerate(items):
        det.append(f'<details class="faq__item"{" open" if open_first and i == 0 else ""}><summary><span>{esc(q)}</span>{icon("chev")}</summary><div class="faq__a"><p>{a}</p></div></details>')
    return f'''
<section class="band band--faq">
  <div class="wrap faq__grid">
    <div>{section_head(title, intro, "")}</div>
    <div class="faq">{"".join(det)}</div>
  </div>
</section>'''


def contact_section(compact=False):
    thanks = absurl("thanks/")
    return f'''
<section class="band" id="contact">
  <div class="wrap con__grid">
    <div>
      {section_head("קבעו תור או שאלו אותנו", f"הדרך המהירה ביותר: טלפון או וואטסאפ. אפשר גם להשאיר פרטים ונחזור אליכם בשעות הפעילות.", "צור קשר")}
      <div class="cta-row cta-row--stack">{btn_call()}{btn_wa()}</div>
      <ul class="con__list">
        <li>{icon("phone", "ic ic--sm")} מרפאה: <a href="tel:{PHONE_TEL}" data-track="call">{PHONE_DISPLAY}</a></li>
        <li>{icon("phone", "ic ic--sm")} נייד / חירום: <a href="tel:{MOBILE_TEL}" data-track="call-mobile">{MOBILE_DISPLAY}</a></li>
        <li>{icon("mail", "ic ic--sm")} <a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li>{icon("pin", "ic ic--sm")} <a href="{GMAPS}" target="_blank" rel="noopener">{STREET}, {NEIGHBORHOOD}, {CITY_SHORT}</a></li>
        <li>{icon("clock", "ic ic--sm")} {HOURS_SHORT}</li>
      </ul>
    </div>
    <form class="form" id="contact-form" action="{FORM_ACTION}" method="POST" data-track="form">
      <input type="hidden" name="_subject" value="פנייה חדשה מאתר מרפאת בן ארי">
      <input type="hidden" name="_next" value="{thanks}">
      <input type="hidden" name="_template" value="table">
      <input type="hidden" name="_captcha" value="false">
      <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="form__row">
        <label>שם<input type="text" name="שם" required autocomplete="name"></label>
        <label>טלפון<input type="tel" name="טלפון" required autocomplete="tel" inputmode="tel" pattern="[0-9+\\-\\s]{{8,15}}"></label>
      </div>
      <div class="form__row">
        <label>בעל החיים<select name="בעל חיים"><option>כלב</option><option>חתול</option><option>אחר</option></select></label>
        <label>הסיבה לפנייה<select name="סיבה"><option>קביעת תור</option><option>חיסונים / ביקור שגרה</option><option>החיה לא מרגישה טוב</option><option>ניתוח / ייעוץ</option><option>שאלה כללית</option></select></label>
      </div>
      <label>מה נוכל לעזור?<textarea name="הודעה" rows="4" placeholder="שם החיה, גיל, ומה קורה"></textarea></label>
      <div class="form__actions">
        <button class="btn btn--accent" type="submit">{icon("mail")}<span>שלחו ונחזור אליכם</span></button>
        <button class="btn btn--wa" type="button" id="form-wa" data-wa="{WHATSAPP_NUMBER}">{icon("whatsapp")}<span>או שלחו בוואטסאפ</span></button>
      </div>
      <p class="form__note">נחזור אליכם בשעות הפעילות. במקרה דחוף — התקשרו.</p>
    </form>
  </div>
</section>'''


def cta_band(title="מוכנים לקבוע תור?", text=None):
    text = text or f"התקשרו או שלחו וואטסאפ — נמצא לכם שעה שנוחה לכם. {STREET}, ליד קניון רמת אביב."
    return f'''
<section class="ctab">
  <div class="wrap ctab__in">
    <div><h2>{esc(title)}</h2><p>{esc(text)}</p></div>
    <div class="cta-row">{btn_call()}{btn_wa()}</div>
  </div>
</section>'''


def related_links(slugs, title="קשור"):
    items = []
    for s in slugs:
        svc = C.SERVICE_BY_SLUG.get(s)
        if svc:
            items.append((svc["name"], s))
        elif s == "emergency/":
            items.append(("וטרינר חירום ברמת אביב", s))
        elif s == "team/":
            items.append(("הצוות", s))
        else:
            g = next((g for g in C.GUIDES if g["slug"] == s), None)
            if g:
                items.append((g["name"], s))
    lis = "".join(f'<li><a href="{h(p)}">{esc(n)} {icon("arrow", "ic ic--sm")}</a></li>' for n, p in items)
    return f'<section class="band band--tight"><div class="wrap"><h2 class="rel__h">{esc(title)}</h2><ul class="rel">{lis}</ul></div></section>'


def marquee():
    pets = [
        ("kiwi-smile", "קיווי מחייך על שולחן הבדיקה"), ("three-cavaliers", "שלושה קבליירים על שולחן הבדיקה"),
        ("maine-coon-face", "חתול מיין קון"), ("puggle-puppy", "גור כלבים בעיניים גדולות"),
        ("vizsla-bana", "באנה הוויזלה"), ("girl-kitten-carrier", "ילדה וגורת חתולים"),
        ("shihtzu-face", "שיצו"), ("jul-and-mawi", "ג׳ול ומאווי — כלב וחתול מצטנפים"),
        ("chihuahua-sweater", "צ׳יוואווה בסוודר"), ("waiting-room-terrier", "טרייר בחדר ההמתנה"),
        ("lhasa-owner", "להסה אפסו עם הבעלים"), ("miley-on-desk", "מיילי על השולחן"),
    ]
    tiles = "".join(f'<li>{picture(n, a, sizes="160px")}</li>' for n, a in pets)
    return f'''
<div class="marq" aria-label="המטופלים שלנו">
  <ul class="marq__track">{tiles}{tiles}</ul>
</div>'''


def stats_band():
    stats = [
        (str(FOUNDED), "שנת ההקמה — המרפאה הוותיקה בתל אביב"),
        ("2", "דורות של רופאים, אבא ובן"),
        ("אלפי", "ניתוחים שבוצעו במרפאה"),
        ("דקות", "לתוצאות מעבדה — בזמן הביקור"),
    ]
    lis = "".join(f'<li><span class="stat__n">{esc(n)}</span><span class="stat__l">{esc(l)}</span></li>' for n, l in stats)
    return f'<section class="stats"><div class="wrap"><ul class="stats__list">{lis}</ul></div></section>'


def hero_home():
    chips = [
        ("star", f"{GOOGLE_RATING}★ בגוגל"),
        ("users", "שני רופאים, אבא ובן"),
        ("flask", "מעבדה: תוצאות תוך דקות"),
        ("car", "חניה נוחה, ליד הקניון"),
    ]
    chips_html = "".join(f'<li>{icon(i, "ic ic--sm")} {esc(t)}</li>' for i, t in chips)
    return f'''
<section class="hero" id="top">
  <div class="wrap hero__grid">
    <div class="hero__copy">
      <p class="eyebrow eyebrow--light">מרפאה וטרינרית · {STREET}, צמוד לקניון רמת אביב</p>
      <h1>הווטרינרים של רמת אביב.<br><span class="hl">מאז 1985.</span></h1>
      <p class="lead">{DR_MOSHE} ו{DR_TOMER} — אבא ובן, שני דורות של רפואה וטרינרית לכלבים ולחתולים. מעבדה, רנטגן דיגיטלי, אולטרסאונד וחדר ניתוח במקום אחד, עם אותם רופאים שמכירים את החיה שלכם לאורך כל חייה.</p>
      <div class="cta-row">{btn_call("חייגו " + PHONE_DISPLAY, "btn btn--accent btn--lg")}{btn_wa("קביעת תור בוואטסאפ", "btn btn--light btn--lg")}</div>
      <ul class="chips">{chips_html}</ul>
    </div>
    <div class="hero__media">
      <figure class="tagframe">
        {picture("team-moshe-tomer", "ד״ר תומר בן ארי וד״ר משה בן ארי בחלוקים ירוקים מחבקים כלב פודל במרפאה", sizes="(max-width: 900px) 100vw, 46vw", cls="tagframe__pic", priority=True)}
        <figcaption class="tagframe__cap">ד״ר תומר וד״ר משה בן ארי</figcaption>
      </figure>
      <div class="hero__status">
        {status_pill()}
        <a class="hero__addr" href="{WAZE}" target="_blank" rel="noopener" data-track="waze">{icon("waze", "ic ic--sm")} {STREET}, רמת אביב · נווטו</a>
      </div>
    </div>
  </div>
</section>
{marquee()}'''


# ---------------------------------------------------------------------------
# Schema.org
# ---------------------------------------------------------------------------
DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def schema_hours():
    out = []
    for d, spans in HOURS.items():
        for o, c in spans:
            out.append({"@type": "OpeningHoursSpecification", "dayOfWeek": DAYS[d], "opens": o, "closes": c})
    return out


def schema_clinic():
    return {
        "@type": ["VeterinaryCare", "LocalBusiness"],
        "@id": absurl("#clinic"),
        "name": NAME,
        "alternateName": [NAME_EN, "מרפאת ד״ר משה בן ארי", "וטרינר בצפון תל אביב - ד״ר משה בן ארי"],
        "description": f"מרפאה וטרינרית לכלבים ולחתולים ברמת אביב, תל אביב, הפועלת מאז {FOUNDED}. ד״ר משה בן ארי וד״ר תומר בן ארי: מעבדה במקום, רנטגן דיגיטלי, אולטרסאונד, כירורגיה, חיסונים, שיניים, ייעוץ תזונה והתנהגות.",
        "url": absurl(""),
        "logo": {"@type": "ImageObject", "url": absurl("assets/img/" + IMG["logo"]["fallback"])},
        "image": [absurl("assets/img/og.jpg"), absurl("assets/img/" + IMG["team-moshe-tomer"]["fallback"])],
        "telephone": PHONE_TEL,
        "email": EMAIL,
        "foundingDate": str(FOUNDED),
        "founder": {"@id": absurl("#moshe")},
        "employee": [{"@id": absurl("#moshe")}, {"@id": absurl("#tomer")}],
        "address": {"@type": "PostalAddress", "streetAddress": STREET, "addressLocality": CITY, "addressRegion": "מחוז תל אביב", "addressCountry": COUNTRY},
        "geo": {"@type": "GeoCoordinates", "latitude": LAT, "longitude": LNG},
        "hasMap": GMAPS,
        "openingHoursSpecification": schema_hours(),
        "priceRange": "₪₪",
        "currenciesAccepted": "ILS",
        "areaServed": [{"@type": "Place", "name": n} for n in ["רמת אביב", "רמת אביב ג׳", "נווה אביבים", "אפקה", "תל ברוך", "הדר יוסף", "צהלה", "רמת החייל", "צפון תל אביב", "תל אביב-יפו", "רמת השרון", "הרצליה"]],
        "sameAs": [FACEBOOK, "https://www.bvet.co.il/"],
        "knowsLanguage": ["he", "en"],
        "contactPoint": [
            {"@type": "ContactPoint", "telephone": PHONE_TEL, "contactType": "customer service", "areaServed": "IL", "availableLanguage": ["Hebrew", "English"]},
            {"@type": "ContactPoint", "telephone": MOBILE_TEL, "contactType": "emergency", "areaServed": "IL"},
        ],
        "availableService": [{"@type": "Service", "name": s["name"], "url": absurl(s["slug"]), "serviceType": s["name"]} for s in C.SERVICES],
    }


def schema_people():
    out = []
    for key, m in zip(["moshe", "tomer"], C.TEAM):
        out.append({
            "@type": "Person", "@id": absurl("#" + key), "name": m["name"], "alternateName": m["name_en"],
            "honorificPrefix": "ד״ר", "jobTitle": "רופא וטרינר", "worksFor": {"@id": absurl("#clinic")},
            "alumniOf": {"@type": "CollegeOrUniversity", "name": m["alma_en"]},
            "image": absurl("assets/img/" + IMG[m["image"]]["fallback"]), "description": " · ".join(m["facts"][:3]),
            "url": absurl("team/"), "knowsAbout": ["רפואה וטרינרית", "כלבים", "חתולים", "כירורגיה", "רפואה פנימית"],
        })
    return out


def schema_website():
    return {"@type": "WebSite", "@id": absurl("#website"), "url": absurl(""), "name": NAME, "inLanguage": "he", "publisher": {"@id": absurl("#clinic")}}


def schema_webpage(page):
    d = {
        "@type": "WebPage", "@id": absurl(page["slug"]) + "#webpage", "url": absurl(page["slug"]),
        "name": page["title"], "description": page["description"], "inLanguage": page.get("lang", "he"),
        "isPartOf": {"@id": absurl("#website")}, "about": {"@id": absurl("#clinic")},
        "dateModified": BUILD_DATE,
        "primaryImageOfPage": {"@type": "ImageObject", "url": absurl("assets/img/" + IMG[page.get("og_image", "team-moshe-tomer")]["fallback"])},
    }
    if page.get("crumbs"):
        d["breadcrumb"] = {"@id": absurl(page["slug"]) + "#breadcrumb"}
    return d


def schema_breadcrumb(page):
    items = [("בית", "")] + page["crumbs"]
    return {"@type": "BreadcrumbList", "@id": absurl(page["slug"]) + "#breadcrumb",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": absurl(p)} for i, (n, p) in enumerate(items)]}


def schema_faq(items):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": H.unescape(_strip(a))}} for q, a in items]}


def _strip(s):
    import re
    return re.sub(r"<[^>]+>", "", s)


def schema_for(page):
    graph = [schema_clinic(), *schema_people(), schema_website(), schema_webpage(page)]
    if page.get("crumbs"):
        graph.append(schema_breadcrumb(page))
    if page.get("faq"):
        graph.append(schema_faq(page["faq"]))
    graph.extend(page.get("schema", []))
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def layout(page, body):
    lang = page.get("lang", "he")
    rtl = lang == "he"
    canonical = absurl(page["slug"])
    robots = "noindex, nofollow" if page.get("noindex") else "index, follow, max-image-preview:large"
    og_img = absurl("assets/img/og.jpg")
    alt = ""
    if page["slug"] == "":
        alt = f'<link rel="alternate" hreflang="he" href="{absurl("")}"><link rel="alternate" hreflang="en" href="{absurl("en/")}"><link rel="alternate" hreflang="x-default" href="{absurl("")}">'
    elif page["slug"] == "en/":
        alt = f'<link rel="alternate" hreflang="he" href="{absurl("")}"><link rel="alternate" hreflang="en" href="{absurl("en/")}"><link rel="alternate" hreflang="x-default" href="{absurl("")}">'
    pre = "".join(f'<link rel="preload" as="font" type="font/woff2" crossorigin href="{h("assets/fonts/" + f)}">' for f in
                  ["heebo-400-hebrew.woff2", "heebo-700-hebrew.woff2", "frank-ruhl-libre-900-hebrew.woff2"])
    hero_pre = ""
    if page["slug"] == "":
        m = IMG["team-moshe-tomer"]
        hero_pre = f'<link rel="preload" as="image" href="{h("assets/img/team-moshe-tomer-800.webp")}" imagesrcset="{", ".join(h("assets/img/team-moshe-tomer-" + str(w) + ".webp") + " " + str(w) + "w" for w in m["widths"])}" imagesizes="(max-width: 900px) 100vw, 46vw">'
    return f'''<!doctype html>
<html lang="{lang}" dir="{"rtl" if rtl else "ltr"}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(page["title"])}</title>
<meta name="description" content="{esc(page["description"])}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
{alt}
<meta name="theme-color" content="#0C3E44">
<meta name="color-scheme" content="light">
<meta name="geo.region" content="IL-TA"><meta name="geo.placename" content="Tel Aviv-Yafo"><meta name="geo.position" content="{LAT};{LNG}"><meta name="ICBM" content="{LAT}, {LNG}">
<meta property="og:type" content="{"website" if page["slug"] in ("", "en/") else "article"}">
<meta property="og:locale" content="{"he_IL" if rtl else "en_US"}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(page["title"])}">
<meta property="og:description" content="{esc(page["description"])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="ד״ר תומר וד״ר משה בן ארי במרפאה">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{h("favicon.ico")}" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="{h("assets/icons/favicon-32.png")}">
<link rel="apple-touch-icon" href="{h("assets/icons/apple-touch-icon.png")}">
<link rel="manifest" href="{h("manifest.webmanifest")}">
{pre}{hero_pre}
<link rel="stylesheet" href="{h("assets/css/fonts.css")}">
<link rel="stylesheet" href="{h("assets/css/site.css?v=" + BUILD_DATE.replace("-", ""))}">
<script type="application/ld+json">{schema_for(page)}</script>
<!-- Analytics: paste the GA4 / GTM snippet here. Click events are pushed to window.dataLayer as {{event:'cta', type:'call|whatsapp|waze|form'}} by assets/js/site.js. -->
</head>
<body class="{page.get("body_class", "")}">
{header(page) if rtl else header_en(page)}
<main id="main">
{body}
</main>
{footer() if rtl else footer_en()}
{mobile_bar()}
<script src="{h("assets/js/site.js?v=" + BUILD_DATE.replace("-", ""))}" defer></script>
</body>
</html>'''


# ---------------------------------------------------------------------------
# English chrome
# ---------------------------------------------------------------------------
def header_en(page):
    return f'''
<a class="skip" href="#main">Skip to content</a>
<div class="topbar">
  <div class="wrap topbar__in">
    {status_pill()}
    <div class="topbar__links">
      <a href="tel:{PHONE_TEL}" data-track="call">{icon("phone", "ic ic--sm")} {PHONE_DISPLAY}</a>
      <a href="{wa_link("Hello, I would like to book an appointment at Ben Ari Veterinary Clinic.")}" target="_blank" rel="noopener" data-track="whatsapp">{icon("whatsapp", "ic ic--sm")} WhatsApp</a>
      <a href="{WAZE}" target="_blank" rel="noopener" data-track="waze">{icon("pin", "ic ic--sm")} 43 Brodetsky St., Ramat Aviv</a>
    </div>
  </div>
</div>
<header class="site-header" id="site-header">
  <div class="wrap header__in">
    <a class="brand" href="{h("en/")}" aria-label="{NAME_EN} — home">
      {picture("logo", "Ben Ari Veterinary Clinic logo", sizes="56px", cls="brand__logo", priority=True)}
      <span class="brand__text"><span class="brand__name">{NAME_EN}</span><span class="brand__sub">Ramat Aviv, Tel Aviv · since {FOUNDED}</span></span>
    </a>
    <nav class="nav" id="nav" aria-label="Main">
      <ul><li><a href="#services">Services</a></li><li><a href="#why">Why us</a></li><li><a href="#hours">Hours &amp; directions</a></li><li><a href="#faq">FAQ</a></li><li><a href="{h("")}" lang="he">עברית</a></li></ul>
      <div class="nav__cta">{btn_wa("WhatsApp", "btn btn--wa btn--sm", wa_link("Hello, I would like to book an appointment at Ben Ari Veterinary Clinic."))}{btn_call(PHONE_DISPLAY, "btn btn--accent btn--sm")}</div>
    </nav>
    <button class="burger" id="burger" aria-label="Open menu" aria-expanded="false" aria-controls="nav">{icon("menu")}{icon("close")}</button>
  </div>
</header>'''


def footer_en():
    hours = "".join(f'<tr><th scope="row">{d}</th><td>{a}{(" · " + b) if b else ""}</td></tr>' for d, a, b in [("Sun–Thu", "10:00-13:00", "16:00-19:00"), ("Friday", "14:30-17:00", ""), ("Saturday", "Closed", "")])
    return f'''
<footer class="site-footer">
  <div class="wrap foot__grid">
    <div class="foot__brand">
      {picture("logo", NAME_EN, sizes="72px", cls="foot__logo")}
      <p class="foot__name">{NAME_EN}</p>
      <p class="foot__tag">Veterinary clinic for dogs and cats in Ramat Aviv, Tel Aviv. Dr. Moshe Ben Ari &amp; Dr. Tomer Ben Ari — since {FOUNDED}.</p>
      <address class="foot__addr">
        <a href="{GMAPS}" target="_blank" rel="noopener">{icon("pin", "ic ic--sm")} 43 Brodetsky St., Ramat Aviv, Tel Aviv — next to Ramat Aviv Mall</a>
        <a href="tel:{PHONE_TEL}" data-track="call">{icon("phone", "ic ic--sm")} {PHONE_DISPLAY}</a>
        <a href="tel:{MOBILE_TEL}" data-track="call-mobile">{icon("phone", "ic ic--sm")} {MOBILE_DISPLAY} (mobile)</a>
        <a href="mailto:{EMAIL}">{icon("mail", "ic ic--sm")} {EMAIL}</a>
        <a href="{FACEBOOK}" target="_blank" rel="noopener">{icon("fb", "ic ic--sm")} Facebook</a>
      </address>
    </div>
    <div><h2 class="foot__h">Opening hours</h2><table class="hours hours--foot"><tbody>{hours}</tbody></table></div>
    <div><h2 class="foot__h">Hebrew site</h2><ul class="foot__list"><li><a href="{h("")}" lang="he">דף הבית</a></li><li><a href="{h("services/")}" lang="he">שירותים</a></li><li><a href="{h("emergency/")}" lang="he">חירום</a></li><li><a href="{h("team/")}" lang="he">הצוות</a></li><li><a href="{h("accessibility/")}" lang="he">נגישות ופרטיות</a></li></ul></div>
  </div>
  <div class="wrap foot__bottom"><span>© {TODAY.year} {NAME_EN}</span><span>Vet in Ramat Aviv · Veterinarian North Tel Aviv</span></div>
</footer>'''
