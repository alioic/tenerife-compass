# Tenerife Compass

Static travel-guide site for **tenerifecompass.com**. Covers all of Tenerife, region by region, with the sunny south built out first. English content, revenue via affiliate links.

## Structure

```
/                       Home — interactive region map (real Tenerife outline, all regions live)
/south/                 South Tenerife hub + Leaflet map with pins
/north/                 North hub (Puerto de la Cruz, La Orotava, Icod, Garachico)
/santa-cruz/            Capital + La Laguna + Anaga hub
/east/                  El Médano & golf coast hub
/west/                  Los Gigantes, Alcalá & Playa San Juan hub
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
GitHub → **SiteGround** via FTPS: every push to `main` runs `.github/workflows/deploy.yml`, same pattern as spilanet.is.

Required repo secrets (Settings → Secrets and variables → Actions):
- `FTP_SERVER` — SiteGround FTP hostname
- `FTP_USERNAME` — FTP user
- `FTP_PASSWORD` — FTP password

`server-dir` is set to `tenerifecompass.com/public_html/` — verify the real path in Site Tools → File Manager if the first run fails.

`.htaccess` handles cache headers (no-cache for HTML so edits show immediately despite SuperCacher), forces https and non-www, gives tidy URLs without `.html`, and sets the 404 page.

A Netlify site also exists (peaceful-queijadas-e6b870.netlify.app) and still auto-deploys; useful as a preview URL. `netlify.toml` is excluded from the SiteGround upload.

## Local preview
```bash
python3 -m http.server 8137 --bind 127.0.0.1
```
Then open http://localhost:8137

## Places database
All map pins live in `assets/places.js` (one array, each entry tagged `region: 'south'|'north'|'scruz'|'east'|'west'`). Each region hub filters by its region. To add a place anywhere on the island, add one line there.

## Roadmap
All five regions are live. Next: region deep-dive articles (Loro Parque, Anaga hiking, La Laguna, El Médano windsurfing), more pins, affiliate link swap, custom domain.
