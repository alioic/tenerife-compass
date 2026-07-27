# Tenerife Compass

Static travel-guide site for **tenerifecompass.com**. Covers all of Tenerife, region by region, with the sunny south built out first. English content, revenue via affiliate links.

## Structure

```
/                       Home — interactive region map (real Tenerife outline)
/south/                 South Tenerife hub + Leaflet map with pins
/south/where-to-stay.html
/south/things-to-do.html
/south/food-and-drink.html
/south/practical.html
/about.html
/privacy.html           Privacy, cookies & affiliate disclosure
/404.html
/assets/style.css       Whole design system (one file)
/assets/compass.svg     Logo / favicon
/sitemap.xml, /robots.txt, /.htaccess
/research/              Source research notes (NOT deployed — gitignored)
```

## Design system
All styling lives in `assets/style.css` (CSS variables at the top). Bright, fresh palette: turquoise ocean, coral, sun-gold, warm white. View the full component kit at `/styleguide.html`.

## Placeholder images → real photos
Cards and heroes currently use gradient placeholders (`<div class="ph ph--teal"><span>Label</span></div>`). To use a real photo, replace that block with:
```html
<img src="/assets/img/your-photo.jpg" alt="Descriptive alt text">
```
The `.card__media` / `.hero` styles handle the rest. Drop photos in `/assets/img/`.

## Affiliate links
Booking buttons are placeholders pointing at partner search URLs, marked with `<!-- AFFILIATE: ... -->` comments and `rel="nofollow sponsored"`. Once approved by each programme, swap them for your partner deep links:
- Tours/activities → GetYourGuide / Viator
- Hotels → Booking.com
- Car hire → DiscoverCars
The affiliate disclosure lives at `/privacy.html#affiliate`.

## Deploy
Mirrors the Spilanet setup: push to `main` → GitHub Actions uploads via FTPS to SiteGround (`.github/workflows/deploy.yml`). Set repo secrets `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`, and confirm `server-dir` matches the domain's public_html.

## Local preview
```bash
python3 -m http.server 8137 --bind 127.0.0.1
```
Then open http://localhost:8137

## Roadmap
South is live. Next regions (map already shows them as "coming soon"): North (Puerto de la Cruz), Santa Cruz & La Laguna, El Médano & East, Teno & West. Each reuses the same templates and design system.
