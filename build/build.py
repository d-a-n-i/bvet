# -*- coding: utf-8 -*-
"""Static site generator for מרפאת בן ארי.

    python3 build/build.py          # build everything
    python3 build/build.py --no-img # skip the image pipeline (faster)

Requires Python 3 and ImageMagick (`convert`, `identify`). No other deps.
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import clinic as S  # noqa: E402
import content as C  # noqa: E402
import render as R  # noqa: E402
from render import icon, picture, esc, h, absurl  # noqa: E402

SRC_IMG = os.path.join(ROOT, "src", "img")
OUT_IMG = os.path.join(ROOT, "assets", "img")
OUT_ICO = os.path.join(ROOT, "assets", "icons")
MANIFEST = os.path.join(HERE, "img-manifest.json")
PAGES_MANIFEST = os.path.join(HERE, "pages-manifest.json")
WIDTHS = [240, 480, 800, 1200, 1600]


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------
def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def identify(path):
    out = subprocess.check_output(["identify", "-format", "%w %h %A", path + "[0]"], text=True).split()
    return int(out[0]), int(out[1]), out[2] in ("True", "Blend")


def newer(src, dst):
    return not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src)


def build_images(skip=False):
    os.makedirs(OUT_IMG, exist_ok=True)
    os.makedirs(OUT_ICO, exist_ok=True)
    manifest = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    for fn in sorted(os.listdir(SRC_IMG)):
        name, ext = os.path.splitext(fn)
        src = os.path.join(SRC_IMG, fn)
        w, hgt, alpha = identify(src)
        widths = sorted({min(x, w) for x in WIDTHS})
        fb_w = max([x for x in widths if x <= 1200] or [widths[0]])
        fb_ext = "png" if alpha else "jpg"
        fallback = f"{name}-{fb_w}.{fb_ext}"
        if not skip:
            for x in widths:
                dst = os.path.join(OUT_IMG, f"{name}-{x}.webp")
                if newer(src, dst):
                    run(["convert", src, "-auto-orient", "-strip", "-resize", f"{x}x{x}>", "-quality", "80", "-define", "webp:method=6", dst])
            dst = os.path.join(OUT_IMG, fallback)
            if newer(src, dst):
                if alpha:
                    run(["convert", src, "-auto-orient", "-strip", "-resize", f"{fb_w}x{fb_w}>", dst])
                else:
                    run(["convert", src, "-auto-orient", "-strip", "-resize", f"{fb_w}x{fb_w}>", "-quality", "82", "-sampling-factor", "4:2:0", "-interlace", "Plane", dst])
        fw, fh, _ = identify(os.path.join(OUT_IMG, fallback))
        manifest[name] = {"widths": widths, "w": fw, "h": fh, "fallback": fallback, "alpha": alpha}
    json.dump(manifest, open(MANIFEST, "w"), indent=0)

    # Icons + OG image
    logo = os.path.join(SRC_IMG, "logo.png")
    if not skip:
        for size, out in [(32, "favicon-32.png"), (16, "favicon-16.png"), (48, "favicon-48.png"), (180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png")]:
            dst = os.path.join(OUT_ICO, out)
            if newer(logo, dst):
                bg = "white" if size <= 48 or out == "apple-touch-icon.png" else "none"
                pad = int(size * 0.08)
                run(["convert", logo, "-strip", "-resize", f"{size - 2 * pad}x{size - 2 * pad}", "-gravity", "center", "-background", bg, "-extent", f"{size}x{size}", dst])
        ico = os.path.join(ROOT, "favicon.ico")
        if newer(logo, ico):
            run(["convert", os.path.join(OUT_ICO, "favicon-16.png"), os.path.join(OUT_ICO, "favicon-32.png"), os.path.join(OUT_ICO, "favicon-48.png"), ico])
        og = os.path.join(OUT_IMG, "og.jpg")
        team = os.path.join(SRC_IMG, "team-moshe-tomer.jpg")
        if newer(team, og) or newer(logo, og):
            run(["convert", team, "-auto-orient", "-strip", "-resize", "1200x630^", "-gravity", "center", "-extent", "1200x630", "-quality", "84", og])
            run(["convert", og, "(", logo, "-resize", "170x170", ")", "-gravity", "southeast", "-geometry", "+36+30", "-composite", og])
    return manifest


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------
def page(slug, title, description, h1, lead, body, **kw):
    d = {"slug": slug, "title": title, "description": description, "h1": h1, "lead": lead, "body": body}
    d.update(kw)
    return d


def home_page():
    body = (R.hero_home() + R.stats_band() + R.clinic_summary() + R.services_section() + R.why_section()
            + R.team_section() + R.stories_section() + R.reviews_section() + R.emergency_band()
            + R.location_section() + R.faq_block(C.FAQ_HOME, "שאלות שכולם שואלים", f'לא מצאתם? {R.link_arrow("לכל השאלות והתשובות", "faq/")}')
            + R.contact_section())
    return page("", f"מרפאת בן ארי | וטרינר ברמת אביב, תל אביב — מאז 1985",
                f"מרפאה וטרינרית ברמת אביב, ליד קניון רמת אביב: ד״ר משה וד״ר תומר בן ארי, אבא ובן, מאז 1985. מעבדה עם תוצאות תוך דקות, רנטגן דיגיטלי, אולטרסאונד, ניתוחים, חיסונים ושיניים לכלבים ולחתולים. חייגו {S.PHONE_DISPLAY}.",
                "", "", body, faq=C.FAQ_HOME, body_class="home")


def service_page(s):
    inc = "".join(f'<li><span class="chk">{icon("check")}</span><div><b>{esc(t)}</b><span>{esc(d)}</span></div></li>' for t, d in s["includes"])
    steps = "".join(f'<li><span class="step__n">{i + 1}</span><div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></li>' for i, (t, d) in enumerate(s["steps"]))
    note = f'<aside class="note">{icon("info")}<p>{esc(s["note"])}</p></aside>' if s["note"] else ""
    body = R.page_hero({"h1": s["h1"], "lead": s["lead"], "crumbs": [("שירותים", "services/"), (s["name"], s["slug"])], "eyebrow": "שירותי המרפאה"}, s["image"], s["image_alt"])
    body += R.summary_box([
        ("איפה", f"{S.STREET}, רמת אביב — {S.LANDMARK}"),
        ("מתי", S.HOURS_SHORT),
        ("קביעת תור", f'<a href="tel:{S.PHONE_TEL}" data-track="call">{S.PHONE_DISPLAY}</a> או <a href="{S.WA_DEFAULT}" target="_blank" rel="noopener" data-track="whatsapp">וואטסאפ</a>'),
    ], "בקצרה")
    body += f'''
<section class="band">
  <div class="wrap two">
    <div>{R.section_head("מה כולל השירות")}<ul class="inc">{inc}</ul></div>
    <div>{R.section_head("איך זה עובד אצלנו")}<ol class="steps">{steps}</ol>{note}</div>
  </div>
</section>'''
    body += R.faq_block(s["faq"], "שאלות נפוצות על " + s["name"])
    body += R.related_links(s["related"], "שירותים ומדריכים קשורים")
    body += R.cta_band("צריכים ייעוץ? דברו איתנו", "שיחה קצרה עם הרופא עוזרת להחליט מה הצעד הנכון. התקשרו או שלחו וואטסאפ.")
    body += R.location_section(with_map=False)
    schema = [{"@type": "Service", "@id": absurl(s["slug"]) + "#service", "name": s["name"], "serviceType": s["name"], "description": s["description"],
               "provider": {"@id": absurl("#clinic")}, "areaServed": {"@type": "City", "name": "תל אביב-יפו"}, "url": absurl(s["slug"])}]
    return page(s["slug"], s["title"], s["description"], s["h1"], s["lead"], body,
                crumbs=[("שירותים", "services/"), (s["name"], s["slug"])], faq=s["faq"], schema=schema, og_image=s["image"])


def services_hub():
    body = R.page_hero({"h1": "כל השירותים הווטרינריים — במרפאה אחת ברמת אביב", "lead": "שמונה תחומי טיפול, שני רופאים, מעבדה, רנטגן דיגיטלי, אולטרסאונד וחדר ניתוח — כדי שהאבחנה והטיפול יקרו באותו ביקור, בלי לרוץ בין מקומות.", "crumbs": [("שירותים", "services/")], "eyebrow": "השירותים שלנו"})
    body += f'<section class="band"><div class="wrap">{R.services_grid(big=True)}</div></section>'
    body += R.why_section() + R.emergency_band() + R.cta_band()
    return page("services/", "שירותים וטרינריים ברמת אביב — ניתוחים, חיסונים, מעבדה, רנטגן, שיניים",
                "כל שירותי מרפאת בן ארי ברמת אביב: כירורגיה ואורתופדיה, חיסונים ורפואה מונעת, מעבדה במקום, רנטגן דיגיטלי ואולטרסאונד, טיפולי שיניים, רפואה פנימית, ייעוץ תזונה והתנהגות.",
                "", "", body, crumbs=[("שירותים", "services/")])


def emergency_page():
    signs = "".join(f'<li><b>{esc(t)}</b><span>{esc(d)}</span></li>' for t, d in C.EMERGENCY_SIGNS)
    do = "".join(f'<li><span class="step__n">{i + 1}</span><div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></li>' for i, (t, d) in enumerate(C.EMERGENCY_DO))
    lead = f"במקרה חירום בשעות הפעילות — הגיעו ישירות למרפאה ב{S.STREET}, רמת אביב, והתקשרו בדרך. יש לנו במקום רנטגן דיגיטלי, אולטרסאונד, מעבדת דם עם תוצאות תוך דקות וחדר ניתוח, כך שברוב המקרים אפשר לאבחן ולטפל מיד. מחוץ לשעות הפעילות חייגו לנייד."
    extra = f'<div class="emerg-nums"><a class="btn btn--light btn--lg" href="tel:{S.MOBILE_TEL}" data-track="call-mobile">{icon("phone")}<span>נייד / אחרי שעות: {S.MOBILE_DISPLAY}</span></a></div>'
    body = R.page_hero({"h1": "וטרינר חירום ברמת אביב: מה לעשות, ולאן לפנות", "lead": lead, "crumbs": [("חירום", "emergency/")], "eyebrow": "חירום · 24 שעות של תשובות"}, "tomer-surgery-monitoring", "ד״ר תומר בן ארי מטפל בחיה תחת ניטור בחדר הניתוח", extra)
    body += R.summary_box([
        ("בשעות הפעילות", f'<a href="tel:{S.PHONE_TEL}" data-track="call">{S.PHONE_DISPLAY}</a> — הגיעו ישירות, אין צורך בתור. {S.HOURS_SHORT}.'),
        ("מחוץ לשעות הפעילות", f'<a href="tel:{S.MOBILE_TEL}" data-track="call-mobile">{S.MOBILE_DISPLAY}</a> (נייד).'),
        ("אין מענה ומצב מסכן חיים", f'בית חולים וטרינרי 24/7: {S.HOSPITAL_NAME} — <a href="tel:{S.HOSPITAL_PHONE_TEL}">{S.HOSPITAL_PHONE_DISPLAY}</a> / {S.HOSPITAL_SHORT}.'),
        ("בדרך", "התקשרו כדי שנתכונן; הביאו אריזה של מה שנאכל; חתול בכלוב, כלב גדול על שמיכה."),
    ], "בקצרה: למי מתקשרים")
    body += f'''
<section class="band">
  <div class="wrap two">
    <div>{R.section_head("מתי זה חירום?", "אם אחד מאלה קורה — אל תחכו לבוקר.")}<ul class="signs">{signs}</ul></div>
    <div>{R.section_head("מה עושים עד שמגיעים")}<ol class="steps">{do}</ol>
      <aside class="note">{icon("info")}<p>הכלל: אם אתם מתלבטים אם זה חירום — התקשרו. שיחה של דקה חוסכת לפעמים לילה שלם של דאגה, ולפעמים מצילה חיים.</p></aside></div>
  </div>
</section>'''
    body += R.emergency_band()
    body += R.faq_block(C.EMERGENCY_FAQ, "שאלות על חירום")
    body += R.related_links(["guides/toxic-foods/", "guides/when-to-see-a-vet/", "services/imaging/", "services/surgery-orthopedics/"], "מדריכים ושירותים קשורים")
    body += R.location_section()
    return page("emergency/", "וטרינר חירום ברמת אביב | מרפאת בן ארי — מה לעשות ולאן לפנות",
                f"וטרינר חירום ברמת אביב: בשעות הפעילות הגיעו ישירות למרפאת בן ארי (ברודצקי 43) — רנטגן, אולטרסאונד, מעבדה וחדר ניתוח במקום. אחרי שעות הפעילות: {S.MOBILE_DISPLAY}. סימני חירום ומה לעשות בדרך.",
                "", "", body, crumbs=[("חירום", "emergency/")], faq=C.EMERGENCY_FAQ, og_image="tomer-surgery-monitoring")


def team_page():
    profiles = []
    for i, m in enumerate(C.TEAM):
        facts = "".join(f"<li>{icon('check', 'ic ic--sm')} {esc(f)}</li>" for f in m["facts"])
        profiles.append(f'''<article class="prof{" prof--rev" if i % 2 else ""}">
          <div class="prof__media">{picture(m["photo2"], m["photo2_alt"], sizes="(max-width: 900px) 100vw, 40vw", cls="prof__pic")}{picture(m["image"], m["image_alt"], sizes="120px", cls="prof__av")}</div>
          <div class="prof__body"><p class="eyebrow">{esc(m["role"])}</p><h2>{esc(m["name"])}</h2><p class="prof__alma">{icon("book", "ic ic--sm")} {esc(m["alma"])}</p>
          <ul class="prof__facts">{facts}</ul><blockquote class="prof__q">„{esc(m["quote"])}“</blockquote></div></article>''')
    values = "".join(f'<li><h3>{esc(t)}</h3><p>{esc(d)}</p></li>' for t, d in C.VALUES)
    body = R.page_hero({"h1": "אבא ובן. שני בתי ספר. רופאים שמכירים את החיה שלכם בשמה.", "lead": f"{S.DR_MOSHE} הקים את המרפאה ב-1985 אחרי לימודים בבולוניה. {S.DR_TOMER}, בוגר האוניברסיטה העברית, הצטרף אחרי שנתיים במרפאת חירום גדולה בתל אביב. בכל ביקור תפגשו אחד מהם — לא צוות מתחלף.", "crumbs": [("הצוות", "team/")], "eyebrow": "הצוות"}, "team-moshe-tomer", "ד״ר תומר וד״ר משה בן ארי עם כלב פודל במרפאה")
    body += f'<section class="band"><div class="wrap profs">{"".join(profiles)}</div></section>'
    body += f'''<section class="band band--cream"><div class="wrap">{R.section_head("איך אנחנו עובדים", "ה„אני מאמין“ שלנו — כפי שכתבנו אותו, וכפי שאנחנו מנסים לקיים אותו בכל ביקור.", "אני מאמין")}<ul class="values">{values}</ul>
    <p class="sig">תמיד איתכם,<br><b>משה ותומר</b></p></div></section>'''
    body += R.reviews_section(2) + R.cta_band("רוצים להכיר אותנו?", "הביקור הראשון הוא היכרות — עם החיה ואיתכם. התקשרו ונקבע.")
    return page("team/", f"הרופאים: {S.DR_MOSHE} ו{S.DR_TOMER} | וטרינרים ברמת אביב",
                "הכירו את רופאי מרפאת בן ארי ברמת אביב: ד״ר משה בן ארי (אוניברסיטת בולוניה, מייסד 1985, עורך מדעי של ספר הכלב וספר החתול) וד״ר תומר בן ארי (האוניברסיטה העברית, רפואת חירום). אבא ובן.",
                "", "", body, crumbs=[("הצוות", "team/")], og_image="team-moshe-tomer")


def about_page():
    tl = "".join(f'<li><span class="tl__y">{esc(y)}</span><p>{esc(t)}</p></li>' for y, t in C.TIMELINE)
    values = "".join(f'<li><h3>{esc(t)}</h3><p>{esc(d)}</p></li>' for t, d in C.VALUES)
    body = R.page_hero({"h1": "המרפאה הווטרינרית הוותיקה בתל אביב — באותו מקום, מאז 1985", "lead": f"מרפאת בן ארי הוקמה על ידי {S.DR_MOSHE} בשנת 1985 ברחוב ברודצקי 43, במרכז המסחרי הצמוד לקניון רמת אביב. היום מנהלים אותה משה ובנו, {S.DR_TOMER} — עם מעבדה, רנטגן דיגיטלי, אולטרסאונד וחדר ניתוח, ועם אותה גישה: רפואה וטרינרית היא רפואת משפחה.", "crumbs": [("אודות", "about/")], "eyebrow": "אודות המרפאה"}, "dr-moshe-hug-dog", "ד״ר משה בן ארי מחבק כלב גדול במרפאה")
    body += f'''<section class="band"><div class="wrap two"><div>{R.section_head("ציוני דרך")}<ol class="tl">{tl}</ol></div>
    <div>{R.section_head("מה מחזיק אותנו כאן 40 שנה")}<p class="prose">אנו שמחים בחלקנו על המקצוע שבחרנו. גם אחרי שנים רבות, אנחנו עדיין מתרגשים בכל פעם מחדש למראה ילד שמאמץ גור, או למראה קשיש שמחליט להכניס שמחה חדשה לחייו.</p>
    <p class="prose">אנו רואים בווטרינריה רפואת משפחה — גם עבורכם, הבעלים. אנו לעולם רואים לא רק את הבעיה הרפואית, אלא את המטופל ואת בני משפחתו, ומשתפים אתכם בכל מחשבה וכיוון טיפולי: איך גומלים כלב מצרכים? איך מלמדים את הילדים לעזור בטיפול? מה עושים אם הכלב לא מפסיק לנבוח? איך מונעים מהחתול להרוס את הבית?</p>
    <p class="prose">טיפול בבעל חיים הוא מסע משותף — מורכב, מאתגר, ובעיקר מהנה ומרגש. אנחנו רואים את עצמנו חלק בלתי נפרד ממנו.</p>
    <div class="books books--inline">{picture("book-dog", "ספר הכלב", sizes="110px")}{picture("book-cat", "ספר החתול", sizes="110px")}<p>ד״ר משה בן ארי שימש כיועץ וכעורך המדעי של „ספר הכלב“ ו„ספר החתול“ במהדורתם העברית (הוצאת כתר) — הספרים המובילים בתחום, שמלווים מגדלים ואוהבי כלבים וחתולים כבר שנים.</p></div></div></div></section>'''
    body += f'''<section class="band band--cream"><div class="wrap">{R.section_head("הערכים שלנו", "", "אני מאמין")}<ul class="values">{values}</ul></div></section>'''
    body += f'''<section class="band"><div class="wrap two"><div>{picture("sos-adoption-day", "ד״ר משה וד״ר תומר בן ארי ביום אימוץ של עמותת SOS לחיות", sizes="(max-width: 900px) 100vw, 45vw", cls="rounded")}</div>
    <div>{R.section_head("SOS לחיות — מהיום הראשון", "", "קהילה")}<p class="prose">אנחנו מלווים את עמותת SOS לחיות מיום היווסדה: משתתפים בימי אימוץ, מסייעים בטיפול בבעלי חיים חסרי בית, ומלווים משפחות מאמצות בתקופת ההתאקלמות של בעל החיים בביתו החדש — ובהמשך חייו. מצאתם חיה? התקשרו, נעזור.</p>
    <p class="prose">שני הרופאים חברים בארגון הרופאים הווטרינרים לחיות מחמד ומשתתפים בקביעות בהשתלמויות ובכנסים מקצועיים בארץ ובחו״ל.</p></div></div></section>'''
    body += R.team_section() + R.cta_band()
    return page("about/", "אודות מרפאת בן ארי — מרפאה וטרינרית ברמת אביב מאז 1985",
                "הסיפור של מרפאת בן ארי: הוקמה ב-1985 על ידי ד״ר משה בן ארי ליד קניון רמת אביב, המרפאה הווטרינרית הוותיקה בתל אביב. היום — אבא ובן, מעבדה, רנטגן וחדר ניתוח, ו„אני מאמין“ של רפואת משפחה.",
                "", "", body, crumbs=[("אודות", "about/")], og_image="dr-moshe-hug-dog")


def stories_page():
    cards = "".join(R.story_card(s) for s in C.STORIES)
    body = R.page_hero({"h1": "סיפורים מהמרפאה", "lead": "ביז׳ו שבלע מטבע, סטיבי שאוכל מגבות, בוני שרזתה ועברה בין סורגי המרפסת, ומוריס שחב את חייו לניתוח. עשרה מטופלים אמיתיים מרמת אביב, כפי שד״ר בן ארי סיפר עליהם.", "crumbs": [("סיפורים", "stories/")], "eyebrow": "40 שנה של מטופלים"}, "story-bijou", "ביז׳ו החתול, שבלע מטבע ונותח בהצלחה במרפאת בן ארי")
    body += f'<section class="band"><div class="wrap stgrid stgrid--all">{cards}</div></section>'
    body += R.cta_band("גם לחיה שלכם מגיע רופא שזוכר אותה", "אותם שני רופאים, מגור ועד זקנה. התקשרו ונקבע היכרות.")
    schema = [{"@type": "ItemList", "name": "סיפורים מהמרפאה", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": s[0]} for i, s in enumerate(C.STORIES)]}]
    return page("stories/", "סיפורים מהמרפאה — מטופלים אמיתיים של מרפאת בן ארי, רמת אביב",
                "עשרה סיפורי מטופלים ממרפאת בן ארי ברמת אביב: החתול שבלע מטבע, הגולדן שאכל קילו שוקולד, הביגל שרזתה, והחתול הפרסי שניצל בניתוח. רפואה וטרינרית אמיתית מאז 1985.",
                "", "", body, crumbs=[("סיפורים", "stories/")], schema=schema, og_image="story-bijou")


def reviews_page():
    cards = "".join(R.review_card(r) for r in C.REVIEWS)
    body = R.page_hero({"h1": "מה הלקוחות מספרים על מרפאת בן ארי", "lead": f"{S.GOOGLE_RATING} כוכבים בגוגל, {S.FB_RECOMMEND} ממליצים בפייסבוק, ולקוחות שמגיעים אלינו דור אחרי דור. הנה כמה מהמילים שכתבו לנו — ואם טיפלנו גם בחיה שלכם, נשמח לביקורת.", "crumbs": [("המלצות", "reviews/")], "eyebrow": "המלצות"}, "waiting-room-terrier", "לקוחה מחייכת עם כלב טרייר בחדר ההמתנה של מרפאת בן ארי")
    body += f'<section class="band"><div class="wrap">{R.rating_badges()}<div class="rgrid rgrid--all">{cards}</div><p class="band__more"><a class="btn btn--accent" href="{S.GOOGLE_REVIEW}" target="_blank" rel="noopener">{icon("star")}<span>כתבו לנו ביקורת בגוגל</span></a> <a class="btn btn--ghost" href="{S.FACEBOOK}" target="_blank" rel="noopener">{icon("fb")}<span>העמוד שלנו בפייסבוק</span></a></p></div></section>'
    body += R.team_section() + R.cta_band()
    return page("reviews/", "המלצות על מרפאת בן ארי — וטרינר מומלץ ברמת אביב, תל אביב",
                f"המלצות וביקורות על מרפאת בן ארי ברמת אביב: {S.GOOGLE_RATING} כוכבים בגוגל ({S.GOOGLE_REVIEWS} ביקורות), {S.FB_RECOMMEND} ממליצים בפייסבוק. מה לקוחות כותבים על ד״ר משה וד״ר תומר בן ארי.",
                "", "", body, crumbs=[("המלצות", "reviews/")], og_image="waiting-room-terrier")


def faq_page():
    all_faq = C.FAQ_HOME + C.FAQ_MORE
    body = R.page_hero({"h1": "שאלות ותשובות על המרפאה", "lead": "איפה, מתי, כמה, מה להביא ומה עושים בחירום — התשובות הקצרות. ולכל שאר השאלות: התקשרו, אנחנו אוהבים שאלות.", "crumbs": [("שאלות ותשובות", "faq/")], "eyebrow": "שאלות ותשובות"})
    body += R.faq_block(all_faq, "על המרפאה והביקור")
    body += R.faq_block(C.EMERGENCY_FAQ, "חירום", open_first=False)
    body += R.related_links(["emergency/", "services/vaccines-preventive/", "guides/when-to-see-a-vet/", "guides/toxic-foods/"])
    body += R.cta_band("יש שאלה שלא כאן?", "התקשרו או כתבו לנו בוואטסאפ — נענה בשמחה.")
    return page("faq/", "שאלות ותשובות — מרפאת בן ארי, וטרינר ברמת אביב",
                "שאלות נפוצות על מרפאת בן ארי ברמת אביב: שעות פעילות, קביעת תור, חניה, מחירים, חירום, מה להביא לביקור ראשון, ניתוחים, מעבדה ורנטגן במקום.",
                "", "", body, crumbs=[("שאלות ותשובות", "faq/")], faq=all_faq + C.EMERGENCY_FAQ)


def contact_page():
    areas = "".join(f'<li><a href="{h(a["slug"])}">{esc(a["name"])} {icon("arrow", "ic ic--sm")}</a></li>' for a in C.AREAS)
    body = R.page_hero({"h1": "צרו קשר עם מרפאת בן ארי", "lead": f"טלפון, וואטסאפ, מייל או טופס — ואם אתם כבר בדרך: {S.STREET}, רמת אביב, {S.LANDMARK}.", "crumbs": [("צור קשר", "contact/")], "eyebrow": "צור קשר"})
    body += R.contact_section() + R.location_section()
    body += f'<section class="band band--tight"><div class="wrap"><h2 class="rel__h">הוראות הגעה לפי שכונה</h2><ul class="rel">{areas}</ul></div></section>'
    return page("contact/", f"צור קשר — מרפאת בן ארי, ברודצקי 43 רמת אביב | {S.PHONE_DISPLAY}",
                f"צרו קשר עם מרפאת בן ארי ברמת אביב: טלפון {S.PHONE_DISPLAY}, נייד {S.MOBILE_DISPLAY}, וואטסאפ, מייל וטופס. כתובת: ברודצקי 43, תל אביב, ליד קניון רמת אביב. שעות: {S.HOURS_SHORT}.",
                "", "", body, crumbs=[("צור קשר", "contact/")])


def guide_page(g):
    secs = "".join(f'<section class="gsec"><h2>{esc(t)}</h2><ul class="gl">{"".join(f"<li>{esc(x)}</li>" for x in items)}</ul></section>' for t, items in g["sections"])
    tool = ""
    if g["slug"] == "guides/toxic-foods/":
        data = json.dumps([{"n": n, "s": sp, "l": lv, "w": w, "d": d} for n, sp, lv, w, d in C.TOXIC], ensure_ascii=False)
        rows = "".join(f'<li class="tox tox--{lv}" data-s="{sp}"><div class="tox__h"><b>{esc(n)}</b><span class="tox__lvl">{["", "זהירות", "מסוכן", "חירום"][lv]}</span></div><p>{esc(w)}</p><p class="tox__do">{icon("info", "ic ic--sm")} {esc(d)}</p></li>' for n, sp, lv, w, d in C.TOXIC)
        tool = f'''<section class="band band--tight"><div class="wrap">
        <div class="toxtool" id="toxtool">
          <div class="toxtool__bar">
            <label class="toxtool__search">{icon("info", "ic ic--sm")}<input type="search" id="tox-q" placeholder="חפשו: שוקולד, ענבים, בצל…" autocomplete="off"></label>
            <div class="seg" role="group" aria-label="סינון לפי בעל חיים"><button type="button" class="seg__b is-on" data-sp="dc">הכול</button><button type="button" class="seg__b" data-sp="d">כלבים</button><button type="button" class="seg__b" data-sp="c">חתולים</button></div>
          </div>
          <p class="toxtool__legend"><span class="tox__lvl tox__lvl--3">חירום</span> התקשרו מיד · <span class="tox__lvl tox__lvl--2">מסוכן</span> התקשרו · <span class="tox__lvl tox__lvl--1">זהירות</span> הימנעו</p>
          <ul class="toxlist" id="toxlist">{rows}</ul>
          <p class="toxtool__empty" id="tox-empty" hidden>לא מצאנו את זה ברשימה — זה לא אומר שזה בטוח. התקשרו אלינו: <a href="tel:{S.PHONE_TEL}">{S.PHONE_DISPLAY}</a>.</p>
          <aside class="note note--accent">{icon("siren")}<p>החיה שלכם אכלה משהו מהרשימה? אל תחכו לסימנים. <a href="tel:{S.PHONE_TEL}" data-track="call">{S.PHONE_DISPLAY}</a> · מחוץ לשעות הפעילות <a href="tel:{S.MOBILE_TEL}" data-track="call-mobile">{S.MOBILE_DISPLAY}</a>.</p></aside>
        </div></div></section>'''
    body = R.page_hero({"h1": g["h1"], "lead": g["lead"], "crumbs": [("מדריכים", "guides/"), (g["name"], g["slug"])], "eyebrow": "מדריך מרופאי המרפאה"}, g["image"], g["image_alt"])
    body += tool
    if secs or g["closing"]:
        body += f'<section class="band"><div class="wrap guide">{secs}{g["closing"]}</div></section>'
    body += R.faq_block(g["faq"], "שאלות נפוצות")
    body += R.related_links(g["related"], "שירותים ומדריכים קשורים")
    body += R.emergency_band() if g["slug"] in ("guides/toxic-foods/", "guides/when-to-see-a-vet/") else R.cta_band()
    schema = [{"@type": "Article", "@id": absurl(g["slug"]) + "#article", "headline": g["h1"], "description": g["description"], "inLanguage": "he",
               "author": [{"@id": absurl("#moshe")}, {"@id": absurl("#tomer")}], "publisher": {"@id": absurl("#clinic")},
               "datePublished": "2026-10-26", "dateModified": S.BUILD_DATE, "mainEntityOfPage": absurl(g["slug"]),
               "image": absurl("assets/img/" + R.IMG[g["image"]]["fallback"])}]
    return page(g["slug"], g["title"], g["description"], g["h1"], g["lead"], body,
                crumbs=[("מדריכים", "guides/"), (g["name"], g["slug"])], faq=g["faq"], schema=schema, og_image=g["image"])


def guides_hub():
    cards = "".join(f'''<a class="gcard" href="{h(g["slug"])}">{picture(g["image"], g["image_alt"], sizes="(max-width: 700px) 100vw, 50vw", cls="gcard__pic")}<div class="gcard__body"><h2>{esc(g["name"])}</h2><p>{esc(g["description"][:150])}…</p><span class="link-arrow">לקריאה {icon("arrow", "ic ic--sm")}</span></div></a>''' for g in C.GUIDES)
    body = R.page_hero({"h1": "מדריכים מרופאי המרפאה", "lead": "מה מסוכן לכלב לאכול, מתי שינוי קטן הוא סימן אזהרה, מה עושים בשנה הראשונה עם גור, ואיך מתמודדים עם הקרציות של תל אביב. כתוב על ידי רופאים, לא על ידי אלגוריתם.", "crumbs": [("מדריכים", "guides/")], "eyebrow": "מדריכים"})
    body += f'<section class="band"><div class="wrap ggrid">{cards}</div></section>' + R.cta_band()
    return page("guides/", "מדריכים לבעלי כלבים וחתולים — מרופאי מרפאת בן ארי, רמת אביב",
                "מדריכים מקצועיים לבעלי כלבים וחתולים מרופאי מרפאת בן ארי: מאכלים מסוכנים, סימני אזהרה, השנה הראשונה עם גור, קדחת קרציות ותולעת הפארק בתל אביב.",
                "", "", body, crumbs=[("מדריכים", "guides/")])


def area_page(a):
    faq = [
        (f"איך מגיעים מ{a['name']} למרפאה?", f"{a['directions']} {a['drive']}; {a['walk']}."),
        ("איפה חונים?", a["parking"]),
    ]
    body = R.page_hero({"h1": a["h1"], "lead": f"מרפאת בן ארי נמצאת ב{S.STREET}, רמת אביב, {S.LANDMARK} — {a['drive']} מ{a['name']}. ד״ר משה וד״ר תומר בן ארי מטפלים בכלבים ובחתולים של השכונה מאז 1985, עם מעבדה, רנטגן דיגיטלי, אולטרסאונד וחדר ניתוח במקום.", "crumbs": [("אזורי שירות", "areas/"), (a["name"], a["slug"])], "eyebrow": f"וטרינר ב{a['name']}"}, "team-moshe-tomer", "ד״ר תומר וד״ר משה בן ארי במרפאה")
    body += R.summary_box([
        ("מרחק", f"{icon('car', 'ic ic--sm')} {a['drive']} · {icon('walk', 'ic ic--sm')} {a['walk']}"),
        ("הדרך", a["directions"]),
        ("חניה", a["parking"]),
        ("שעות", S.HOURS_SHORT),
        ("טלפון", f'<a href="tel:{S.PHONE_TEL}" data-track="call">{S.PHONE_DISPLAY}</a> · <a href="{S.WA_DEFAULT}" target="_blank" rel="noopener" data-track="whatsapp">וואטסאפ</a>'),
    ], f"מ{a['name']} אלינו")
    body += f'<section class="band"><div class="wrap"><p class="prose prose--lg">{esc(a["extra"])}</p>{R.services_grid(limit=4)}<p class="band__more">{R.link_arrow("לכל השירותים", "services/")}</p></div></section>'
    body += R.why_section() + R.faq_block(faq, f"שאלות של תושבי {a['name']}") + R.emergency_band() + R.location_section()
    return page(a["slug"], a["title"], a["description"], a["h1"], "", body, crumbs=[("אזורי שירות", "areas/"), (a["name"], a["slug"])], faq=faq)


def areas_hub():
    cards = "".join(f'<a class="acard" href="{h(a["slug"])}"><span class="acard__ic">{icon("pin")}</span><h2>{esc(a["name"])}</h2><p>{icon("car", "ic ic--sm")} {esc(a["drive"])}</p><span class="link-arrow">הוראות הגעה {icon("arrow", "ic ic--sm")}</span></a>' for a in C.AREAS)
    body = R.page_hero({"h1": "וטרינר בצפון תל אביב: הוראות הגעה לפי שכונה", "lead": f"המרפאה ב{S.STREET}, רמת אביב, משרתת את כל צפון תל אביב — {C.AREA_LIST_OTHERS}. בחרו את השכונה שלכם לזמני נסיעה, מסלול וחניה.", "crumbs": [("אזורי שירות", "areas/")], "eyebrow": "אזורי שירות"})
    body += f'<section class="band"><div class="wrap agrid">{cards}</div></section>' + R.location_section()
    return page("areas/", "וטרינר בצפון תל אביב — הוראות הגעה לפי שכונה | מרפאת בן ארי",
                "מרפאת בן ארי ברמת אביב משרתת את כל צפון תל אביב: רמת אביב ג׳, נווה אביבים, אפקה, תל ברוך, הדר יוסף, צהלה ורמת החייל. הוראות הגעה, זמני נסיעה וחניה לפי שכונה.",
                "", "", body, crumbs=[("אזורי שירות", "areas/")])


def en_page():
    e = C.EN
    wa = S.wa_link("Hello, I would like to book an appointment at Ben Ari Veterinary Clinic.")
    summ = "".join(f'<div class="sum__row"><dt>{esc(k)}</dt><dd>{v}</dd></div>' for k, v in e["summary"])
    svcs = "".join(f'<li class="scard scard--static"><h3>{esc(t)}</h3><p>{esc(d)}</p></li>' for t, d in e["services"])
    why = "".join(f'<li><span class="why__ic">{icon("check")}</span><div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></li>' for t, d in e["why"])
    faq = "".join(f'<details class="faq__item"{" open" if i == 0 else ""}><summary><span>{esc(q)}</span>{icon("chev")}</summary><div class="faq__a"><p>{a}</p></div></details>' for i, (q, a) in enumerate(e["faq"]))
    hours = "".join(f'<tr><th scope="row">{d}</th><td>{a}</td><td>{b}</td></tr>' for d, a, b in [("Sun–Thu", "10:00-13:00", "16:00-19:00"), ("Friday", "14:30-17:00", ""), ("Saturday", "Closed", "")])
    body = f'''
<section class="hero" id="top"><div class="wrap hero__grid">
  <div class="hero__copy"><p class="eyebrow eyebrow--light">Veterinary clinic · 43 Brodetsky St., next to Ramat Aviv Mall</p>
  <h1>Ramat Aviv's veterinarians.<br><span class="hl">Since 1985.</span></h1><p class="lead">{e["lead"]}</p>
  <div class="cta-row">{R.btn_call("Call " + S.PHONE_DISPLAY, "btn btn--accent btn--lg")}{R.btn_wa("Book on WhatsApp", "btn btn--light btn--lg", wa)}</div>
  <ul class="chips"><li>{icon("star", "ic ic--sm")} {S.GOOGLE_RATING}★ on Google</li><li>{icon("users", "ic ic--sm")} Two doctors, father &amp; son</li><li>{icon("flask", "ic ic--sm")} Lab results in minutes</li><li>{icon("globe", "ic ic--sm")} English spoken</li></ul></div>
  <div class="hero__media"><figure class="tagframe">{picture("team-moshe-tomer", "Dr. Tomer Ben Ari and Dr. Moshe Ben Ari with a poodle at the clinic", sizes="(max-width: 900px) 100vw, 46vw", cls="tagframe__pic", priority=True)}<figcaption class="tagframe__cap">Dr. Tomer &amp; Dr. Moshe Ben Ari</figcaption></figure>
  <div class="hero__status">{R.status_pill()}<a class="hero__addr" href="{S.WAZE}" target="_blank" rel="noopener" data-track="waze">{icon("waze", "ic ic--sm")} Navigate with Waze</a></div></div>
</div></section>
{R.marquee()}
<section class="sum" aria-label="At a glance"><div class="wrap"><div class="sum__box"><p class="sum__title">{icon("info")} At a glance</p><dl>{summ}</dl></div></div></section>
<section class="band" id="services"><div class="wrap">{R.section_head("Everything under one roof", "Lab, digital X-ray, ultrasound and surgery in the clinic — so diagnosis and treatment happen in the same visit.", "Services")}<ul class="sgrid">{svcs}</ul></div></section>
<section class="band band--cream" id="why"><div class="wrap why__grid"><div>{R.section_head("Why Ramat Aviv has chosen Ben Ari for 40 years", "", "Why us")}<ul class="why">{why}</ul></div>
<div class="why__media"><figure class="photo-stack">{picture("sos-adoption-day", "Dr. Moshe and Dr. Tomer Ben Ari at an SOS Pets adoption day", sizes="(max-width: 900px) 100vw, 40vw", cls="photo-stack__a")}{picture("kiwi-smile", "Kiwi the dog smiling on the exam table", sizes="(max-width: 900px) 60vw, 24vw", cls="photo-stack__b")}<figcaption>SOS Pets adoption day — and Kiwi, a regular.</figcaption></figure></div></div></section>
<section class="band band--cream" id="hours"><div class="wrap loc__grid"><div class="loc__info">{R.section_head("Next to Ramat Aviv Mall. Easy to reach, easy to park.", "", "Hours &amp; directions")}
<address class="loc__addr"><p><strong>43 Brodetsky St., Ramat Aviv, Tel Aviv</strong><br>In the shopping centre adjacent to Ramat Aviv Mall. Parking on Brodetsky St. and in the mall car park. Many bus lines to Ramat Aviv Mall / Tel Aviv University; the "University" train station is a short ride away.</p></address>
<table class="hours"><tbody>{hours}</tbody></table><p class="loc__note">{R.status_pill()}</p>
<div class="cta-row">{R.btn_waze("Navigate with Waze")}<a class="btn btn--ghost" href="{S.GMAPS}" target="_blank" rel="noopener">{icon("pin")}<span>Google Maps</span></a>{R.btn_call(S.PHONE_DISPLAY)}</div></div>
<div class="map"><iframe src="{S.GMAPS_EMBED.replace("hl=he", "hl=en")}" title="Map: Ben Ari Veterinary Clinic, 43 Brodetsky St., Tel Aviv" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div></div></section>
<section class="band band--faq" id="faq"><div class="wrap faq__grid"><div>{R.section_head("Questions", "")}</div><div class="faq">{faq}</div></div></section>
<section class="ctab"><div class="wrap ctab__in"><div><h2>Ready to book?</h2><p>Call or WhatsApp — we'll find a time that suits you.</p></div><div class="cta-row">{R.btn_call("Call " + S.PHONE_DISPLAY)}{R.btn_wa("WhatsApp", "btn btn--wa", wa)}</div></div></section>'''
    return page("en/", e["title"], e["description"], e["h1"], e["lead"], body, lang="en", faq=e["faq"], body_class="home en")


def small_pages():
    thanks = page("thanks/", "תודה — נחזור אליכם בקרוב | מרפאת בן ארי", "הפנייה התקבלה. נחזור אליכם בשעות הפעילות.", "", "",
                  f'<section class="band band--tall"><div class="wrap narrow"><p class="eyebrow">תודה</p><h1>קיבלנו, ונחזור אליכם בהקדם.</h1><p class="lead">בשעות הפעילות אנחנו עונים מהר. אם זה דחוף — אל תחכו: <a href="tel:{S.PHONE_TEL}">{S.PHONE_DISPLAY}</a> או <a href="tel:{S.MOBILE_TEL}">{S.MOBILE_DISPLAY}</a>.</p><div class="cta-row">{R.btn_call()}{R.btn_wa()}<a class="btn btn--ghost" href="{h("")}">{icon("home")}<span>חזרה לדף הבית</span></a></div></div></section>',
                  noindex=True)
    nf = page("404.html", "העמוד לא נמצא | מרפאת בן ארי", "העמוד שחיפשתם לא נמצא.", "", "",
              f'<section class="band band--tall"><div class="wrap narrow"><p class="eyebrow">404</p><h1>הדף הזה ברח לנו.</h1><p class="lead">כנראה קישור ישן. מה שחיפשתם כנראה כאן:</p><ul class="rel">' + "".join(f'<li><a href="{h(p)}">{esc(t)} {icon("arrow", "ic ic--sm")}</a></li>' for t, p in [("דף הבית", ""), ("שירותים", "services/"), ("חירום", "emergency/"), ("הצוות", "team/"), ("סיפורים", "stories/"), ("צור קשר", "contact/")]) + f'</ul><div class="cta-row">{R.btn_call()}{R.btn_wa()}</div></div></section>',
              noindex=True)
    acc = page("accessibility/", "הצהרת נגישות ומדיניות פרטיות | מרפאת בן ארי", "הצהרת הנגישות ומדיניות הפרטיות של אתר מרפאת בן ארי.", "", "",
               f'''<section class="band"><div class="wrap narrow prose-block">{R.breadcrumbs([("נגישות ופרטיות", "accessibility/")])}<h1>הצהרת נגישות</h1>
<p>מרפאת בן ארי רואה חשיבות רבה בהנגשת האתר והשירות לאנשים עם מוגבלות. האתר נבנה בהתאם להנחיות הנגישות WCAG 2.1 ברמה AA ככל הניתן: מבנה כותרות תקין, ניגודיות צבעים גבוהה, ניווט מלא במקלדת, תיאורי טקסט לתמונות, תמיכה בהגדלת טקסט ובקוראי מסך, וכיבוד העדפת „הפחתת תנועה“ של מערכת ההפעלה.</p>
<p>המרפאה עצמה נמצאת בקומת הקרקע של המרכז המסחרי הצמוד לקניון רמת אביב. אם יש לכם צורך בהתאמה מיוחדת לביקור — התקשרו מראש ל-<a href="tel:{S.PHONE_TEL}">{S.PHONE_DISPLAY}</a> ונעשה כל מאמץ לסייע.</p>
<p>נתקלתם בבעיית נגישות באתר? כתבו לנו ל-<a href="mailto:{S.EMAIL}">{S.EMAIL}</a> ונטפל בכך בהקדם.</p>
<h2>מדיניות פרטיות</h2>
<p>פרטים שאתם משאירים בטופס יצירת הקשר (שם, טלפון, הודעה) נשלחים ישירות לתיבת המייל של המרפאה ומשמשים אך ורק כדי לחזור אליכם. אנחנו לא מוכרים ולא מעבירים מידע לצדדים שלישיים. האתר עשוי להשתמש בכלי מדידה אנונימיים לשיפור השירות. לכל שאלה: <a href="mailto:{S.EMAIL}">{S.EMAIL}</a>.</p>
<p class="muted">עודכן: {S.BUILD_DATE}</p></div></section>''',
               crumbs=[("נגישות ופרטיות", "accessibility/")])
    return [thanks, nf, acc]



# Old WordPress URLs (bvet.co.il) → new pages. Generated as meta-refresh stubs so
# that, once this site serves the clinic's own domain, every old link still lands
# on the right page. Harmless while hosted under the Pages base path.
REDIRECTS = {
    "אודות-המרפאה/": "about/",
    "המלצות/": "reviews/",
    "סיפורי-מטופלים/": "stories/",
    "ספר-הכלב-וספר-החתול/": "about/",
    "posts/": "guides/",
    "פוסטים/": "guides/",
    "פוסטים/וטרינר-חירום-ברמת-אביב-מה-חשוב-לדעת-2/": "emergency/",
    "פוסטים/כך-תזהו-בזמן-שהכלב-או-החתול-שלכם-זקוקים/": "guides/when-to-see-a-vet/",
    "פוסטים/רבים-מבעלי-חיות-המחמד-פונים-למרפאה-וטר/": "services/vaccines-preventive/",
    "פוסטים/במצבים-וטרינריים-מורכבים-הזמן-בין-אבח/": "services/lab/",
    "פוסטים/מעקב-רפואי-לאורך-זמן-מאפשר-להכיר-את-מצב/": "services/internal-medicine/",
    "פוסטים/טיפול-וטרינרי-הוא-חלק-מהמעקב-השוטף-אחר/": "services/vaccines-preventive/",
    "פוסטים/וטרינרים-בתל-אביב-דר-משה-בן-ארי-ודר-ת/": "team/",
    "פוסטים/מרפאה-וטרינרית-מקצועית-בתל-אביב/": "services/",
}


def redirect_stub(old, new):
    target = absurl(new)
    return (f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>מעבר לעמוד החדש — {S.NAME}</title>'
            f'<meta name="robots" content="noindex"><link rel="canonical" href="{target}"><meta http-equiv="refresh" content="0; url={target}">'
            f'<script>location.replace({json.dumps(target)})</script></head><body><p>העמוד עבר לכתובת חדשה: <a href="{target}">{target}</a></p></body></html>')

# ---------------------------------------------------------------------------
# Site-level files
# ---------------------------------------------------------------------------
def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


def sitemap(pages):
    rows = []
    for p in pages:
        if p.get("noindex") or p["slug"].endswith(".html"):
            continue
        pri = "1.0" if p["slug"] == "" else ("0.9" if p["slug"].count("/") == 1 else "0.8")
        rows.append(f"  <url><loc>{absurl(p['slug'])}</loc><lastmod>{S.BUILD_DATE}</lastmod><changefreq>monthly</changefreq><priority>{pri}</priority></url>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n"


def llms_txt(pages):
    lines = [f"# {S.NAME} — {S.NAME_EN}", "",
             f"> מרפאה וטרינרית לכלבים ולחתולים ב{S.STREET}, רמת אביב, תל אביב ({S.LANDMARK}). הוקמה ב-{S.FOUNDED} על ידי {S.DR_MOSHE} (אוניברסיטת בולוניה); היום מנוהלת יחד עם בנו {S.DR_TOMER} (האוניברסיטה העברית). המרפאה הווטרינרית הוותיקה בתל אביב.", "",
             "## Facts",
             f"- Address: {S.STREET}, {S.NEIGHBORHOOD}, {S.CITY} (43 Brodetsky St., Ramat Aviv, Tel Aviv-Yafo, Israel). Next to Ramat Aviv Mall. Coordinates {S.LAT}, {S.LNG}.",
             f"- Phone: {S.PHONE_DISPLAY} (+972-3-6413361). Mobile / after hours: {S.MOBILE_DISPLAY} (+972-52-9709423). WhatsApp: +{S.WHATSAPP_NUMBER}. Email: {S.EMAIL}.",
             f"- Hours: Sun–Thu 10:00-13:00 and 16:00-19:00; Fri 14:30-17:00; Sat closed.",
             f"- Founded: {S.FOUNDED}. Doctors: Dr. Moshe Ben Ari (DVM, University of Bologna; scientific editor of the Hebrew editions of 'The Dog Book' and 'The Cat Book', Keter) and Dr. Tomer Ben Ari (DVM, Hebrew University of Jerusalem; two years in a large Tel Aviv emergency clinic).",
             "- Patients: dogs and cats. Languages: Hebrew, English.",
             "- On site: in-house blood lab (results in minutes), digital X-ray, ultrasound, surgical suite with monitored gas anaesthesia, dental.",
             f"- Services: {', '.join(s['name'] for s in C.SERVICES)}.",
             "- Service area: Ramat Aviv, Ramat Aviv Gimel, Neve Avivim, Afeka, Tel Baruch, Hadar Yosef, Tzahala, Ramat HaHayal, North Tel Aviv, Ramat HaSharon, Herzliya.",
             f"- Reviews: Google {S.GOOGLE_RATING}/5 ({S.GOOGLE_REVIEWS} reviews); Facebook {S.FB_RECOMMEND} recommend. Facebook: {S.FACEBOOK}",
             "- Community: supports the SOS Pets association (adoption days, homeless animals) since its founding.", "",
             "## Pages"]
    for p in pages:
        if p.get("noindex") or p["slug"].endswith(".html"):
            continue
        lines.append(f"- [{p['title']}]({absurl(p['slug'])}): {p['description']}")
    return "\n".join(lines) + "\n"


def manifest_json():
    return json.dumps({"name": S.NAME, "short_name": "בן ארי", "lang": "he", "dir": "rtl", "start_url": S.BASE, "display": "browser",
                       "background_color": "#F6F9F9", "theme_color": "#0C3E44",
                       "icons": [{"src": S.BASE + "assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": S.BASE + "assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False)


def main():
    skip_img = "--no-img" in sys.argv
    R.IMG.update(build_images(skip=skip_img))

    pages = [home_page(), services_hub()] + [service_page(s) for s in C.SERVICES] + [emergency_page(), team_page(), about_page(), stories_page(), reviews_page(), faq_page(), contact_page(), guides_hub()] + [guide_page(g) for g in C.GUIDES] + [areas_hub()] + [area_page(a) for a in C.AREAS] + [en_page()] + small_pages()

    # remove pages generated by a previous build that no longer exist
    prev = json.load(open(PAGES_MANIFEST)) if os.path.exists(PAGES_MANIFEST) else []
    outs = []
    for p in pages:
        out = p["slug"] if p["slug"].endswith(".html") else p["slug"] + "index.html"
        outs.append(out)
        write(out, R.layout(p, p["body"]))
    for old, new in REDIRECTS.items():
        out = old + "index.html"
        outs.append(out)
        write(out, redirect_stub(old, new))
    for old in prev:
        if old not in outs and os.path.exists(os.path.join(ROOT, old)):
            os.remove(os.path.join(ROOT, old))
    json.dump(outs, open(PAGES_MANIFEST, "w"), indent=0)

    write("sitemap.xml", sitemap(pages))
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {absurl('sitemap.xml')}\n")
    write("llms.txt", llms_txt(pages))
    write("manifest.webmanifest", manifest_json())
    write(".nojekyll", "")
    print(f"built {len(pages)} pages → {ROOT}")
    for t in [p["title"] for p in pages if len(p["title"]) > 70]:
        print("  title >70 chars:", len(t), t)


if __name__ == "__main__":
    main()
