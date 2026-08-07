# bvet — מרפאת בן ארי

Modern, SEO-optimized website for **מרפאת בן ארי** — Dr. Moshe Ben Ari's veterinary
clinic in Ramat Aviv, north Tel Aviv.

Single static page (`index.html`), Hebrew RTL, light/dark, mobile-first. Includes
`VeterinaryCare` + `FAQPage` structured data (JSON-LD) for search.

## Live site

Deployed via GitHub Pages: **https://d-a-n-i.github.io/bvet/**

Deployment is automated — every push to `main` runs `.github/workflows/deploy.yml`,
which builds and publishes the site to Pages.

## Custom subdomain (optional)

To serve at e.g. `new.bvet.co.il`:

1. Add a `CNAME` file at the repo root containing `new.bvet.co.il`.
2. DNS: add a `CNAME` record `new` → `d-a-n-i.github.io`.
3. Repo **Settings → Pages → Custom domain** → `new.bvet.co.il` → Save → Enforce HTTPS.

## Editing

Edit `index.html` and push to `main`; the site redeploys automatically.
Everything (CSS, JS, SVG illustrations) is inline in the one file — no build step.
