# מרפאת בן ארי — website

Static, multi-page website for **מרפאת בן ארי** (Ben Ari Veterinary Clinic), Brodetsky 43,
Ramat Aviv, Tel Aviv — Dr. Moshe Ben Ari and Dr. Tomer Ben Ari, since 1985.

**Live:** https://d85c.com/bvet/  (the GitHub default URL `d-a-n-i.github.io/bvet/` 301s there,
because the account's user site carries the custom domain `d85c.com`).

## What's in here

| Path | What |
|---|---|
| `build/clinic.py` | **Every fact about the clinic in one place**: name, address, phones, WhatsApp, hours, links, ratings, geo. Change here → rebuild → every page, JSON-LD, sitemap and `llms.txt` update. |
| `build/content.py` | All Hebrew copy: services, team bios, patient stories, testimonials, FAQs, emergency guide, four guides, the toxic-foods list, neighbourhood pages, the English page. |
| `build/render.py` | Components (header, hero, cards, FAQ, forms…), page layout, Schema.org JSON-LD. |
| `build/build.py` | The generator: image pipeline, page assembly, `sitemap.xml`, `robots.txt`, `llms.txt`, manifest, old-URL redirect stubs. |
| `src/img/` | Original photos (the clinic's own, from bvet.co.il). Add new photos here. |
| `assets/img/` | Generated responsive WebP/JPEG sets (240–1600 px) + `og.jpg`. Don't edit by hand. |
| `assets/css/site.css`, `assets/js/site.js` | Hand-written stylesheet and behaviour (live open/closed status, menu, reveals, WhatsApp composer, toxic-food checker). |
| `assets/fonts/` | Self-hosted Heebo + Frank Ruhl Libre (Hebrew + Latin subsets). |
| `*/index.html` | **Generated pages — committed**, so GitHub Pages serves them with no build step. |

32 pages: home, services hub + 8 service pages, emergency, team, about, stories, reviews, FAQ,
contact, guides hub + 4 guides (incl. the interactive toxic-foods checker), areas hub + 5
neighbourhood pages, English landing page, thanks, 404, accessibility/privacy.

## Editing & building

Requires Python 3 and ImageMagick (`convert`, `identify`). No other dependencies.

```bash
python3 build/build.py            # full build (regenerates only changed images)
python3 build/build.py --no-img   # text-only rebuild, ~1 s
```

Then commit and push to `main`. Pages redeploys in about a minute.

Typical edits:
- Hours / phone / WhatsApp number → `build/clinic.py`
- A service description or FAQ → `build/content.py`
- A new photo → drop it in `src/img/`, reference its basename in content, rebuild

## Deployment

GitHub Pages, **Settings → Pages → Deploy from a branch → `main` / (root)**. `.nojekyll` keeps
Pages from running Jekyll. Nothing else to configure.

## Moving to the clinic's own domain (bvet.co.il)

1. In `build/clinic.py` set `SITE_URL = "https://www.bvet.co.il"` and `BASE = "/"`, rebuild, commit.
2. Add a `CNAME` file at the repo root containing `www.bvet.co.il`.
3. DNS: `www` → CNAME `d-a-n-i.github.io`; apex `bvet.co.il` → the four GitHub Pages A records
   (185.199.108.153 … 111.153). Settings → Pages → Custom domain → enforce HTTPS.
4. The build already writes meta-refresh stubs at the **old WordPress URLs**
   (`/אודות-המרפאה/`, `/המלצות/`, `/סיפורי-מטופלים/`, `/posts/`, every `/פוסטים/…/` post), so
   existing links and Google's index land on the right new page. Submit `sitemap.xml` in Search
   Console afterwards.
5. Retire the duplicate site vet-all.co.il with a redirect to the new domain (it splits authority).

Note: while the site lives under `/bvet/`, its `robots.txt` is informational only (crawlers read
the domain root); `sitemap.xml` can still be submitted directly in Search Console.

## SEO / GEO notes

- One clean `<title>` (≤ 68 chars) and unique meta description per page; one `<h1>` per page;
  breadcrumbs with `BreadcrumbList`; hreflang he/en on the home pages.
- JSON-LD on every page: `VeterinaryCare` + `LocalBusiness` (address, geo, opening hours,
  phones, areaServed, services), `Person` for both doctors (alumniOf), `WebSite`, `WebPage`,
  `FAQPage` where there are FAQs, `Service` on service pages, `Article` on guides.
- `llms.txt` at the site root summarises the clinic in plain facts for AI assistants.
- Every CTA pushes `{event:'cta', type:'call|whatsapp|waze|form'}` to `window.dataLayer`; paste
  a GA4/GTM snippet where the comment in `<head>` says so.
- Contact form posts to formsubmit.co (`FORM_ACTION` in `clinic.py`); the "send on WhatsApp"
  button composes the same details into a wa.me message.

## Things the clinic should verify

WhatsApp number (052-9709423), the after-hours policy and fallback hospital on the emergency
page, the review figures in `clinic.py`, "English spoken" on the English page, and the Google
review link (replace `GOOGLE_REVIEW` with the clinic's own g.page link when available).
