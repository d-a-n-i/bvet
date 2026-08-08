# bvet — מרפאת בן ארי

Modern, SEO-optimized website for **מרפאת בן ארי** — Dr. Moshe Ben Ari's veterinary
clinic in Ramat Aviv, north Tel Aviv.

Single static page (`index.html`), Hebrew RTL, light/dark, mobile-first. Includes
`VeterinaryCare` + `FAQPage` structured data (JSON-LD) for search.

## Live site

**https://d85c.com/bvet/**

> The GitHub default URL `https://d-a-n-i.github.io/bvet/` 301-redirects to
> `https://d85c.com/bvet/`. That's expected: the account's user site
> (`d-a-n-i.github.io`) has the custom domain `d85c.com`, so GitHub serves every
> project page under that domain.

## Deployment

Pages serves the repo directly ("deploy from a branch") — no build, no Actions
workflow. The single self-contained `index.html` plus `.nojekyll` at the repo
root is all that's published.

**One-time setup** (repo **Settings → Pages**):

1. **Source** → *Deploy from a branch*.
2. **Branch** → `main`, folder → `/ (root)` → **Save**.

Pages then builds on every push to `main`. First build takes ~1 min; after that
`https://d85c.com/bvet/` serves the site (a 404 there means the build hasn't run
or the source above isn't set).

## Editing

Edit `index.html` and push to `main`; Pages rebuilds automatically. CSS and JS
are inline in the one file — no build step. Photos live in `assets/` and are
referenced with relative paths (they resolve under `d85c.com/bvet/assets/…`).

## Custom subdomain (optional)

To serve at e.g. `new.bvet.co.il` instead of the `d85c.com/bvet/` path:

1. Add a `CNAME` file at the repo root containing `new.bvet.co.il`.
2. DNS: add a `CNAME` record `new` → `d-a-n-i.github.io`.
3. Repo **Settings → Pages → Custom domain** → `new.bvet.co.il` → Save → Enforce HTTPS.
