#!/usr/bin/env python3
"""
Tenerife Compass — staðarsíðu-rafall.

Býr til /place/<slug>/index.html fyrir hvern stað í data/place-content.json,
auk yfirlitssíðunnar /places/index.html.

Ritað efni kemur úr place-content.json. "Nálægt"-hlutarnir (gisting,
veitingastaðir, aðrir staðir) eru reiknaðir úr assets/places-<region>.js,
þ.e. sama OSM-gagnagrunni og kortin nota — svo hver síða fær raunverulegt
gagn og innri tengla án handavinnu.

Keyrsla:  python3 build_places.py
"""
import json, os, re, math, html

ROOT = os.path.dirname(os.path.abspath(__file__))
PARTNER = 'ONAATAD'
REGION_NAME = {'south':'South Tenerife','north':'North Tenerife',
               'scruz':'Santa Cruz & La Laguna','east':'El Médano & the east',
               'west':'West Tenerife'}
REGION_HREF = {'south':'/south/','north':'/north/','scruz':'/santa-cruz/',
               'east':'/east/','west':'/west/'}
CAT_LABEL = {'stay':'Hotel','eat':'Restaurant','do':'Things to do',
             'beach':'Beach','drink':'Bar'}

def esc(s):
    return html.escape(str(s or ''), quote=True)

# ---------------------------------------------------------------- gagnagrunnur
def load_places():
    """Les staðina úr assets/places-<region>.js (stytt lyklaheiti)."""
    out = []
    for reg in REGION_NAME:
        p = os.path.join(ROOT, 'assets', f'places-{reg}.js')
        if not os.path.exists(p):
            continue
        src = open(p, encoding='utf-8').read()
        for m in re.finditer(r'\{c:\'(\w+)\',n:\'((?:[^\'\\]|\\.)*)\',a:\'((?:[^\'\\]|\\.)*)\',y:([-\d.]+),x:([-\d.]+)([^}]*)\}', src):
            rest = m.group(6)
            t = re.search(r"t:'((?:[^'\\]|\\.)*)'", rest)
            s = re.search(r's:(\d)', rest)
            out.append({'cat': m.group(1), 'name': m.group(2).replace("\\'", "'"),
                        'area': m.group(3).replace("\\'", "'"),
                        'lat': float(m.group(4)), 'lng': float(m.group(5)),
                        'type': t.group(1).replace("\\'", "'") if t else None,
                        'stars': int(s.group(1)) if s else None,
                        'region': reg})
    return out

def km(a_lat, a_lng, b_lat, b_lng):
    return math.hypot((a_lat - b_lat) * 111.0, (a_lng - b_lng) * 98.0)

# Sum OSM-færslur eru íbúðaauglýsingar frekar en staðir með nafni.
JUNK = re.compile(r'\b(bedroom|sleeps?\s*\d|for \d+ people|apartment for|holiday (home|let)|'
                  r'\d+\s*(pax|guests)|vacation rental|villa for)\b', re.I)

def is_junk(name):
    return bool(JUNK.search(name)) or len(name) > 42 or name.strip().isdigit()

def nearest(db, lat, lng, cat, n, max_km=6.0, exclude_name=None, diverse=False):
    """Næstu staðir. diverse=True dreifir vali yfir undirtegundir svo listinn
    verði ekki fjórir kaffibarir í röð."""
    rows = []
    for p in db:
        if p['cat'] != cat: continue
        if is_junk(p['name']): continue
        if exclude_name and p['name'].lower() == exclude_name.lower(): continue
        d = km(lat, lng, p['lat'], p['lng'])
        if d <= max_km:
            rows.append((d, p))
    rows.sort(key=lambda r: r[0])
    if not diverse:
        return rows[:n]
    # Fyrri umferð: næsti staður af hverri undirtegund. Seinni: fylla upp í.
    picked, used, taken = [], set(), set()
    for i, (d, p) in enumerate(rows):
        if len(picked) >= n: break
        t = p.get('type') or ''
        if t not in used:
            picked.append((d, p)); used.add(t); taken.add(i)
    for i, (d, p) in enumerate(rows):
        if len(picked) >= n: break
        if i not in taken:
            picked.append((d, p))
    picked.sort(key=lambda r: r[0])
    return picked[:n]

# ------------------------------------------------------------------ sniðmátið
def nav():
    return '''<header class="site-header">
  <div class="container nav">
    <a class="brand" href="/"><img class="compass-mark" src="/assets/compass.svg" alt="" width="30" height="30"> Tenerife<b>Compass</b></a>
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    <ul class="nav-links">
      <li><a href="/#map">Explore by region</a></li>
      <li><a href="/places/">Places</a></li>
      <li><a href="/where-to-stay.html">Where to Stay</a></li>
      <li><a href="/best-beaches.html">Best Beaches</a></li>
      <li><a href="/south/practical.html">Plan Your Trip</a></li>
    </ul>
  </div>
</header>'''

def footer():
    return '''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div><div class="footer-brand"><img class="compass-mark" src="/assets/compass.svg" alt="" width="26" height="26"> Tenerife Compass</div><p>An independent travel guide to Tenerife, region by region. Honest advice, kept up to date.</p></div>
      <div><h4>Regions</h4><ul><li><a href="/places/">All places</a></li><li><a href="/south/">South Tenerife</a></li><li><a href="/north/">North</a></li><li><a href="/santa-cruz/">Santa Cruz &amp; La Laguna</a></li><li><a href="/east/">El Médano &amp; East</a></li><li><a href="/west/">West &amp; Teno</a></li></ul></div>
      <div><h4>About</h4><ul><li><a href="/about.html">About us</a></li><li><a href="/about.html#contact">Contact</a></li><li><a href="/privacy.html">Privacy &amp; cookies</a></li><li><a href="/privacy.html#affiliate">Affiliate disclosure</a></li></ul></div>
    </div>
    <div class="footer-bottom"><span>© 2026 Tenerife Compass. All rights reserved.</span><span>Made for travellers, not brochures.</span></div>
  </div>
</footer>
<script>
  const t = document.querySelector('.nav-toggle'), l = document.querySelector('.nav-links');
  t && t.addEventListener('click', () => { const o = l.classList.toggle('open'); t.setAttribute('aria-expanded', o); });
</script>
</body>
</html>'''

def place_page(slug, P, db, all_content):
    reg = P['region']
    # Teide og fleiri liggja í miðju eyjunnar — svæðismerkið má víkja frá
    # svæðinu sem síðan tengist. Sama fyrir forsetninguna: "in Santa Cruz",
    # en "at Playa del Duque".
    reg_label = P.get('regionLabel') or REGION_NAME[reg]
    # Eigið merki er lýsing, ekki svæðishlekkur — þá er brauðmolinn ótengdur
    # svo hann lofi ekki síðu sem hann fer ekki á.
    crumb_region = (esc(reg_label) if P.get('regionLabel')
                    else f'<a href="{REGION_HREF[reg]}">{esc(REGION_NAME[reg])}</a>')
    prep = P.get('prep', 'at')
    lat, lng = P['lat'], P['lng']
    # Titill þarf að rúmast í leitarniðurstöðu — nafn + tegund, ekki heil kynning.
    title = P.get('title') or f"{P['name']}, Tenerife — {P.get('type','Place')} Guide"
    desc = P.get('meta') or (P['intro'][:150].rsplit(' ', 1)[0] + '…')
    img = P.get('image', 'beach-sunbeds.jpg')

    # --- nálægir staðir úr gagnagrunni
    hotels = nearest(db, lat, lng, 'stay', 4)
    eats   = nearest(db, lat, lng, 'eat', 4, exclude_name=P['name'], diverse=True)
    # aðrar staðarsíður í grennd
    others = []
    for s2, P2 in all_content.items():
        if s2 == slug: continue
        d = km(lat, lng, P2['lat'], P2['lng'])
        others.append((d, s2, P2))
    others.sort(key=lambda r: r[0])
    others = others[:6]

    def li_place(d, p):
        bits = [p['type'] or CAT_LABEL.get(p['cat'], '')]
        if p.get('stars'): bits.append(f"{p['stars']}★")
        bits.append(p['area'])
        return (f'<li><span><b>{esc(p["name"])}</b>'
                f'<small>{esc(" · ".join(x for x in bits if x))}</small></span>'
                f'<em>{d:.1f} km</em></li>')

    hotels_html = '\n'.join(li_place(d, p) for d, p in hotels) or '<li><span>No hotels mapped within 6 km.</span></li>'
    eats_html   = '\n'.join(li_place(d, p) for d, p in eats) or '<li><span>No restaurants mapped within 6 km.</span></li>'
    near_html   = '\n'.join(
        f'<li><a href="/place/{s2}/"><b>{esc(P2["name"])}</b>'
        f'<small>{esc(P2.get("type",""))} · {esc(P2.get("area",""))} · {d:.0f} km</small></a></li>'
        for d, s2, P2 in others) or ''

    highlights = ''.join(f'<li>{esc(h)}</li>' for h in P.get('highlights', []))
    booking_q = (P.get('area') or P['name']).replace(' ', '+') + '+Tenerife'
    gyg_q = P.get('gyg', P['name']).replace(' ', '+')

    extra_link = ''
    if P.get('guide'):
        extra_link = (f'<div class="callout callout--gold"><h4>Full guide</h4>'
                      f'<p>We have a dedicated guide to {esc(P["name"])} with prices, '
                      f'booking details and an honest verdict. '
                      f'<a href="{P["guide"]}">Read it here</a>.</p></div>')

    faq = P.get('faq', [])
    faq_html = ''
    if faq:
        faq_html = '<section class="section section--white"><div class="container"><div class="section-head"><span class="eyebrow">Good to know</span><h2>' + esc(P['name']) + ' FAQ</h2></div><div class="faq">'
        for q, a in faq:
            faq_html += f'<details><summary>{esc(q)}</summary><div><p>{esc(a)}</p></div></details>'
        faq_html += '</div></div></section>'
        ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
        faq_html += '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'

    # staðar-schema
    place_ld = {"@context": "https://schema.org", "@type": "TouristAttraction",
                "name": P['name'], "description": desc,
                "address": {"@type": "PostalAddress", "addressLocality": P.get('area', ''),
                            "addressRegion": "Tenerife", "addressCountry": "ES"},
                "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
                "url": f"https://tenerifecompass.com/place/{slug}/"}

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} — Tenerife Compass</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="https://tenerifecompass.com/place/{slug}/">
<meta name="theme-color" content="#0d9bb5">
<meta property="og:type" content="article"><meta property="og:site_name" content="Tenerife Compass">
<meta property="og:title" content="{esc(P['name'])}, Tenerife">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="https://tenerifecompass.com/place/{slug}/">
<meta property="og:image" content="https://tenerifecompass.com/assets/img/{img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/compass.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<link rel="stylesheet" href="/assets/style.css?v=7">
<script type="application/ld+json">{json.dumps(place_ld, ensure_ascii=False)}</script>
</head>
<body>
{nav()}

<section class="hero" style="min-height:44vh;">
  <img class="hero__bg" src="/assets/img/{img}" alt="{esc(P.get('alt', P['name']))}" loading="eager" fetchpriority="high">
  <div class="container hero__inner" style="padding:46px 0;">
    <span class="eyebrow">{esc(P.get('type',''))} · {esc(reg_label)}</span>
    <h1>{esc(P['name'])}</h1>
    <p class="lede">{esc(P.get('tagline',''))}</p>
  </div>
</section>

<div class="container"><nav class="breadcrumb"><a href="/">Home</a><span>›</span> <a href="/places/">Places</a><span>›</span> {crumb_region}<span>›</span> {esc(P['name'])}</nav></div>

<section class="section section--white" style="padding-top:34px;">
  <div class="container">
    <div class="prose">
      <p style="font-size:1.15rem;color:var(--ink-soft);">{esc(P['intro'])}</p>
      {extra_link}
      <h2>What to see and do {prep} {esc(P['name'])}</h2>
      <p>{esc(P['see'])}</p>
      <h2>How to get to {esc(P['name'])}</h2>
      <p>{esc(P['getting'])}</p>
      <h2>Best time to go, and practical tips</h2>
      <p>{esc(P['tips'])}</p>
    </div>
  </div>
</section>

{'<section class="section section--mist"><div class="container"><div class="section-head" style="margin-bottom:22px;"><span class="eyebrow">In short</span><h2>Highlights</h2></div><ul class="doc-tags">' + highlights + '</ul></div></section>' if highlights else ''}

<section class="section section--white">
  <div class="container">
    <div class="section-head" style="margin-bottom:24px;">
      <span class="eyebrow">On the map</span><h2>Where {esc(P['name'])} is</h2>
      <p>And what else is worth knowing about within a short drive.</p>
    </div>
    <div id="placemap" style="height:380px;border-radius:var(--radius);box-shadow:var(--shadow);z-index:1;"></div>
  </div>
</section>

<section class="section section--sand">
  <div class="container">
    <div class="grid grid--2">
      <div>
        <h3>Where to stay nearby</h3>
        <ul class="doc-list">{hotels_html}</ul>
      </div>
      <div>
        <h3>Places to eat nearby</h3>
        <ul class="doc-list">{eats_html}</ul>
      </div>
    </div>
    <!-- GetYourGuide affiliate links live (partner_id={PARTNER}) -->
    <p class="text-center" style="margin-top:26px;">
      <a class="btn btn--primary" href="https://www.booking.com/searchresults.html?ss={booking_q}" rel="nofollow sponsored" target="_blank">Find a hotel nearby</a>
      <a class="btn btn--ocean" href="https://www.getyourguide.com/s/?q={gyg_q}&amp;partner_id={PARTNER}&amp;cmp=place-{slug}" rel="nofollow sponsored" target="_blank" style="margin-left:.5em;">See tours &amp; tickets</a>
    </p>
    <p class="disclosure" style="margin-top:16px;">Distances are straight-line and approximate. Some links are affiliate links; if you book through them we may earn a small commission at no extra cost to you.</p>
  </div>
</section>

{'<section class="section section--white"><div class="container"><div class="section-head" style="margin-bottom:24px;"><span class="eyebrow">Keep exploring</span><h2>Nearby places</h2></div><ul class="doc-links">' + near_html + '</ul></div></section>' if near_html else ''}

{faq_html}

<p class="text-center" style="margin:2em 0 3em;"><a class="btn btn--ocean" href="{REGION_HREF[reg]}">Explore {esc(REGION_NAME[reg])}</a></p>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<script>
  (function(){{
    var map = L.map('placemap', {{scrollWheelZoom:false}}).setView([{lat}, {lng}], 14);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }}).addTo(map);
    L.circleMarker([{lat}, {lng}], {{radius:11, color:'#fff', weight:3, fillColor:'#B0674C', fillOpacity:1}})
      .addTo(map).bindPopup('<strong>{esc(P["name"])}</strong>').openPopup();
  }})();
</script>
{footer()}'''

def index_page(content, db):
    by_region = {}
    for slug, P in content.items():
        by_region.setdefault(P['region'], []).append((slug, P))
    secs = ''
    order = ['south', 'west', 'north', 'scruz', 'east']
    bg = ['section--white', 'section--mist']
    for i, reg in enumerate([r for r in order if r in by_region]):
        rows = sorted(by_region[reg], key=lambda r: r[1]['name'])
        cards = ''
        for slug, P in rows:
            cards += f'''<article class="card">
        <div class="card__media"><img src="/assets/img/{P.get('image','beach-sunbeds.jpg')}" alt="{esc(P.get('alt',P['name']))}" loading="lazy"><span class="tag">{esc(P.get('type',''))}</span></div>
        <div class="card__body"><h3>{esc(P['name'])}</h3><p>{esc(P.get('tagline',''))}</p>
        <a class="card__link" href="/place/{slug}/">Read about {esc(P['name'])}</a></div>
      </article>'''
        n_reg = len(rows)
        secs += f'''<section class="section {bg[i%2]}">
  <div class="container">
    <div class="section-head"><span class="eyebrow">{n_reg} place{'s' if n_reg != 1 else ''}</span><h2>{esc(REGION_NAME[reg])}</h2>
    <p><a href="{REGION_HREF[reg]}">See the full {esc(REGION_NAME[reg])} guide →</a></p></div>
    <div class="grid grid--3">{cards}</div>
  </div>
</section>
'''
    n = len(content)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Places to Visit in Tenerife | Beaches, Villages & Landmarks — Tenerife Compass</title>
<meta name="description" content="Every place worth knowing in Tenerife, region by region: beaches, villages, viewpoints and landmarks, each with how to get there and what to expect.">
<link rel="canonical" href="https://tenerifecompass.com/places/">
<meta name="theme-color" content="#0d9bb5">
<meta property="og:type" content="website"><meta property="og:site_name" content="Tenerife Compass">
<meta property="og:title" content="Places to Visit in Tenerife">
<meta property="og:description" content="Beaches, villages, viewpoints and landmarks across the island.">
<meta property="og:url" content="https://tenerifecompass.com/places/">
<meta property="og:image" content="https://tenerifecompass.com/assets/img/beach-sunbeds.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/compass.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/style.css?v=7">
</head>
<body>
{nav()}
<section class="hero" style="min-height:42vh;">
  <img class="hero__bg" src="/assets/img/beach-sunbeds.jpg" alt="A Costa Adeje beach" loading="eager" fetchpriority="high">
  <div class="container hero__inner" style="padding:46px 0;">
    <span class="eyebrow">Island directory</span>
    <h1>Places to visit in Tenerife</h1>
    <p class="lede">Beaches, villages, viewpoints and landmarks, each with what to expect, how to get there and what is nearby.</p>
  </div>
</section>
<div class="container"><nav class="breadcrumb"><a href="/">Home</a><span>›</span> Places</nav></div>
<section class="section section--white" style="padding:34px 0 6px;">
  <div class="container"><div class="prose" style="text-align:center;">
    <p>{n} places so far, grouped by region. We add more as we research them properly, rather than listing everything for the sake of it.</p>
  </div></div>
</section>
{secs}
<p class="text-center" style="margin:1em 0 3em;"><a class="btn btn--primary" href="/#map">Explore Tenerife by region</a></p>
{footer()}'''

# ------------------------------------------------------------------------ main
def main():
    cpath = os.path.join(ROOT, 'data', 'place-content.json')
    content = json.load(open(cpath, encoding='utf-8'))
    db = load_places()
    print(f'gagnagrunnur: {len(db)} staðir | ritað efni: {len(content)} staðir')

    for slug, P in content.items():
        d = os.path.join(ROOT, 'place', slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(place_page(slug, P, db, content))
    os.makedirs(os.path.join(ROOT, 'places'), exist_ok=True)
    open(os.path.join(ROOT, 'places', 'index.html'), 'w', encoding='utf-8').write(index_page(content, db))
    print(f'búið til: {len(content)} staðarsíður + /places/')

if __name__ == '__main__':
    main()
