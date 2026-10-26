# -*- coding: utf-8 -*-
"""Single source of truth for clinic facts, URLs and build settings.

Everything on the site that is a *fact* about the clinic (name, address, phone,
hours, links) comes from here. Change it once, rebuild, and every page, the
JSON-LD, the sitemap and llms.txt update together.
"""
import datetime

# ---- Deployment -----------------------------------------------------------
# GitHub Pages serves this repo under the account's custom domain.
# When the site moves to the clinic's own domain, change these two lines
# (e.g. SITE_URL = "https://www.bvet.co.il", BASE = "/") and rebuild.
SITE_URL = "https://d85c.com/bvet"   # no trailing slash
BASE = "/bvet/"                       # path prefix every internal link uses

TODAY = datetime.date.today()
BUILD_DATE = TODAY.isoformat()

# ---- Identity -------------------------------------------------------------
NAME = "מרפאת בן ארי"
NAME_EN = "Ben Ari Veterinary Clinic"
TAGLINE = "הווטרינרים של רמת אביב. מאז 1985."
FOUNDED = 1985
YEARS = TODAY.year - FOUNDED

DR_MOSHE = "ד״ר משה בן ארי"
DR_TOMER = "ד״ר תומר בן ארי"

# ---- Contact --------------------------------------------------------------
PHONE_DISPLAY = "03-6413361"
PHONE_TEL = "+97236413361"
MOBILE_DISPLAY = "052-9709423"       # mobile shown on the clinic's second site
MOBILE_TEL = "+972529709423"
WHATSAPP_NUMBER = "972529709423"     # international format, digits only
EMAIL = "benarivet@gmail.com"

STREET = "ברודצקי 43"
NEIGHBORHOOD = "רמת אביב"
CITY = "תל אביב-יפו"
CITY_SHORT = "תל אביב"
COUNTRY = "IL"
ADDRESS_LINE = f"{STREET}, {NEIGHBORHOOD}, {CITY_SHORT}"
LANDMARK = "במרכז המסחרי הצמוד לקניון רמת אביב"
LAT, LNG = 32.111776, 34.797624

# ---- Hours ----------------------------------------------------------------
# weekday index: 0=Sunday ... 6=Saturday (Israeli week)
HOURS = {
    0: [("10:00", "13:00"), ("16:00", "19:00")],
    1: [("10:00", "13:00"), ("16:00", "19:00")],
    2: [("10:00", "13:00"), ("16:00", "19:00")],
    3: [("10:00", "13:00"), ("16:00", "19:00")],
    4: [("10:00", "13:00"), ("16:00", "19:00")],
    5: [("14:30", "17:00")],
    6: [],
}
HOURS_ROWS = [
    ("ראשון–חמישי", "10:00-13:00", "16:00-19:00"),
    ("שישי", "14:30-17:00", ""),
    ("שבת", "סגור", ""),
]
HOURS_SHORT = "א׳–ה׳ 10:00-13:00, 16:00-19:00 · ו׳ 14:30-17:00"

# ---- Links ----------------------------------------------------------------
FACEBOOK = "https://www.facebook.com/BenArivet/"
WAZE = f"https://waze.com/ul?ll={LAT},{LNG}&navigate=yes"
GMAPS = "https://www.google.com/maps/search/?api=1&query=%D7%91%D7%A8%D7%95%D7%93%D7%A6%D7%A7%D7%99+43+%D7%AA%D7%9C+%D7%90%D7%91%D7%99%D7%91"
GMAPS_EMBED = "https://www.google.com/maps?q=%D7%91%D7%A8%D7%95%D7%93%D7%A6%D7%A7%D7%99+43+%D7%AA%D7%9C+%D7%90%D7%91%D7%99%D7%91&z=16&output=embed&hl=he"
GOOGLE_REVIEW = "https://www.google.com/maps/search/?api=1&query=%D7%9E%D7%A8%D7%A4%D7%90%D7%AA+%D7%91%D7%9F+%D7%90%D7%A8%D7%99+%D7%91%D7%A8%D7%95%D7%93%D7%A6%D7%A7%D7%99+43+%D7%AA%D7%9C+%D7%90%D7%91%D7%99%D7%91"

# ---- Social proof (verify against the live Google Business Profile) -------
GOOGLE_RATING = "4.8"
GOOGLE_REVIEWS = 48
FB_RECOMMEND = "100%"
FB_REVIEWS = 30

# ---- Form backend ---------------------------------------------------------
FORM_ACTION = f"https://formsubmit.co/{EMAIL}"

# ---- Partner / fallback emergency hospital (public information) -----------
HOSPITAL_NAME = "בית החולים הווטרינרי האוניברסיטאי (בית דגן)"
HOSPITAL_PHONE_DISPLAY = "03-9688588"
HOSPITAL_PHONE_TEL = "+97239688588"
HOSPITAL_SHORT = "*8818"


def url(path: str = "") -> str:
    """Absolute URL for a site path like 'services/lab/'."""
    return SITE_URL + "/" + path.lstrip("/")


def href(path: str = "") -> str:
    """Root-relative href with the Pages base prefix."""
    return BASE + path.lstrip("/")


def wa_link(text: str) -> str:
    from urllib.parse import quote
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(text)}"


WA_DEFAULT = wa_link("שלום, אשמח לקבוע תור במרפאת בן ארי.\nשם החיה: \nכלב/חתול: \nהסיבה לביקור: ")
WA_EMERGENCY = wa_link("שלום, יש לי מקרה דחוף. אפשר לדבר?")
