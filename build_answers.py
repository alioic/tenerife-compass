#!/usr/bin/env python3
"""
Tenerife Compass — spurningasíðu-rafall.

Býr til svarsíður (t.d. /can-you-drink-the-tap-water-in-tenerife.html) úr
data/answer-content.json. Þetta eru síðurnar sem nýtt lén getur raunverulega
raðast á: langar, nákvæmar spurningar sem fólk slær inn.

Uppbygging hverrar síðu er valin með það í huga:
  H1 = spurningin orðrétt
  "Short answer" strax undir — það er þessi kassi sem Google dregur út
  í svarreitinn efst í leitarniðurstöðum
  svo kaflarnir, FAQ með FAQPage-merkingu, og tenglar áfram

Keyrsla:  python3 build_answers.py
"""
import json, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
PARTNER = 'ONAATAD'
BASE = 'https://tenerifecompass.com'

def _aff():
    return json.load(open(os.path.join(ROOT, 'data', 'affiliates.json'), encoding='utf-8'))

def gyg_url(key, cmp):
    """GetYourGuide-hlekkur á staðsetningarsíðu. Þeir hættu að virða /s/?q= —
    sú slóð skilar almennum niðurstöðum (Aþenu), ekki Tenerife."""
    a = _aff()
    slug = a['getyourguide_locations'].get(key, 'tenerife-l350')
    return (f"https://www.getyourguide.com/{slug}/"
            f"?partner_id={a['getyourguide_partner']}&amp;cmp={cmp}")

def esc(s):
    return html.escape(str(s or ''), quote=True)

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
      <div><h4>Regions</h4><ul><li><a href="/places/">All places</a></li><li><a href="/south/">South Tenerife</a></li><li><a href="/north/">North</a></li><li><a href="/santa-cruz/">Santa Cruz &amp; La Laguna</a></li><li><a href="/east/">El M&eacute;dano &amp; East</a></li><li><a href="/west/">West &amp; Teno</a></li></ul></div>
      <div><h4>About</h4><ul><li><a href="/questions/">Questions answered</a></li><li><a href="/about.html">About us</a></li><li><a href="/about.html#contact">Contact</a></li><li><a href="/privacy.html">Privacy &amp; cookies</a></li><li><a href="/privacy.html#affiliate">Affiliate disclosure</a></li></ul></div>
    </div>
    <div class="footer-bottom"><span>&copy; 2026 Tenerife Compass. All rights reserved.</span><span>Made for travellers, not brochures.</span></div>
  </div>
</footer>
<script>
  const t = document.querySelector('.nav-toggle'), l = document.querySelector('.nav-links');
  t && t.addEventListener('click', () => { const o = l.classList.toggle('open'); t.setAttribute('aria-expanded', o); });
</script>
</body>
</html>'''

def answer_page(slug, A, all_answers):
    q = A['question']
    img = A['image']

    # Kaflarnir, til skiptis hvítir og mistlitir.
    body = ''
    for i, sec in enumerate(A['sections']):
        bg = 'section--white' if i % 2 == 0 else 'section--mist'
        # Fyrsti kaflinn situr beint undir svarkassanum, líka hvítur — annars
        # staflast fyllingin tvöfalt og skilur eftir gat.
        pad = ' style="padding-top:14px;"' if i == 0 else ''
        paras = ''.join(f'<p>{esc(p)}</p>' for p in sec['p'])
        extra = ''
        if sec.get('list'):
            extra = '<ul class="doc-tags">' + ''.join(f'<li>{esc(x)}</li>' for x in sec['list']) + '</ul>'
        if sec.get('rows'):
            extra = '<ul class="doc-list">' + ''.join(
                f'<li><span><b>{esc(r[0])}</b><small>{esc(r[2])}</small></span><em>{esc(r[1])}</em></li>'
                for r in sec['rows']) + '</ul>'
        body += f'''<section class="section {bg}"{pad}>
  <div class="container">
    <div class="prose"><h2>{esc(sec['h2'])}</h2>{paras}</div>
    {f'<div style="max-width:760px;margin:22px auto 0;">{extra}</div>' if extra else ''}
  </div>
</section>
'''

    faq_html = ''
    if A.get('faq'):
        faq_html = ('<section class="section section--sand"><div class="container">'
                    '<div class="section-head"><span class="eyebrow">Also asked</span>'
                    '<h2>Related questions</h2></div><div class="faq">')
        for fq, fa in A['faq']:
            faq_html += f'<details><summary>{esc(fq)}</summary><div><p>{esc(fa)}</p></div></details>'
        faq_html += '</div></div></section>'

    # Skema: spurningin sjálf fyrst, svo aukaspurningarnar.
    entities = [{"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": A['short']}}]
    entities += [{"@type": "Question", "name": fq,
                  "acceptedAnswer": {"@type": "Answer", "text": fa}} for fq, fa in A.get('faq', [])]
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}

    related = ''
    if A.get('related'):
        links = ''.join(
            f'<li><a href="{href}"><b>{esc(label)}</b><small>{esc(sub)}</small></a></li>'
            for href, label, sub in A['related'])
        related = ('<section class="section section--white"><div class="container">'
                   '<div class="section-head" style="margin-bottom:24px;">'
                   '<span class="eyebrow">Keep reading</span><h2>Next questions</h2></div>'
                   f'<ul class="doc-links">{links}</ul></div></section>')

    cta = ''
    if A.get('cta'):
        cta = (f'<p class="text-center" style="margin:2.4em 0 3em;">'
               f'<a class="btn btn--ocean" href="{gyg_url(A["cta"], "q-" + slug)}" rel="nofollow sponsored" target="_blank">'
               f'{esc(A.get("ctaLabel", "See tours & tickets"))}</a></p>')

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(A.get('title', q))} — Tenerife Compass</title>
<meta name="description" content="{esc(A['meta'])}">
<link rel="canonical" href="{BASE}/{slug}.html">
<meta name="theme-color" content="#0d9bb5">
<meta property="og:type" content="article"><meta property="og:site_name" content="Tenerife Compass">
<meta property="og:title" content="{esc(q)}">
<meta property="og:description" content="{esc(A['meta'])}">
<meta property="og:url" content="{BASE}/{slug}.html">
<meta property="og:image" content="{BASE}/assets/img/{img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/compass.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/style.css?v=7">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
{nav()}

<section class="hero" style="min-height:42vh;">
  <img class="hero__bg" src="/assets/img/{img}" alt="{esc(A['alt'])}" loading="eager" fetchpriority="high">
  <div class="container hero__inner" style="padding:46px 0;">
    <span class="eyebrow">{esc(A.get('eyebrow', 'Your questions answered'))}</span>
    <h1>{esc(q)}</h1>
  </div>
</section>

<div class="container"><nav class="breadcrumb"><a href="/">Home</a><span>›</span> <a href="/questions/">Questions</a><span>›</span> {esc(A.get('crumb', q))}</nav></div>

<section class="section section--white" style="padding:34px 0 10px;">
  <div class="container">
    <div class="callout callout--gold" style="max-width:760px;margin:0 auto;">
      <h4>Short answer</h4>
      <p style="font-size:1.08rem;margin-bottom:0;">{esc(A['short'])}</p>
    </div>
  </div>
</section>

{body}
{faq_html}
{related}
{cta}
{footer()}'''

# Eldri spurningasíður sem voru handskrifaðar áður en rafallinn kom til.
# Þær eiga heima í yfirlitinu líka, svo hubbinn sé heill.
LEGACY = [
    ('/best-time-to-visit-tenerife.html', 'When is the best time to visit Tenerife?',
     'Month by month, and why north and south differ', 'Choosing your trip'),
    ('/do-you-need-a-car-in-tenerife.html', 'Do you need a car in Tenerife?',
     'When it earns its keep and when it is dead money', 'Getting around'),
    ('/tenerife-south-airport-transfers.html', 'How do you get from Tenerife South Airport?',
     'Taxi, bus, transfer and hire car compared', 'Getting around'),
    ('/which-part-of-tenerife.html', 'Which part of Tenerife suits you?',
     'A two-minute quiz that picks your region', 'Choosing your trip'),
    ('/masca-gorge-hike.html', 'Can you still hike the Masca gorge?',
     'Permits, booking and what the walk is really like', 'Things to do'),
]

def index_page(A):
    items = [(f'/{s}.html', p['question'], p['meta'][:78].rsplit(' ', 1)[0] + '…',
              p.get('eyebrow', 'Questions')) for s, p in A.items()]
    items += [(h, q, sub, eb) for h, q, sub, eb in LEGACY]
    groups = {}
    for href, q, sub, eb in items:
        groups.setdefault(eb, []).append((href, q, sub))

    secs, bg = '', ['section--white', 'section--mist']
    for i, (eb, rows) in enumerate(sorted(groups.items())):
        li = ''.join(f'<li><a href="{h}"><b>{esc(q)}</b><small>{esc(sub)}</small></a></li>'
                     for h, q, sub in sorted(rows, key=lambda r: r[1]))
        secs += f'''<section class="section {bg[i % 2]}">
  <div class="container">
    <div class="section-head" style="margin-bottom:24px;"><span class="eyebrow">{len(rows)} question{'s' if len(rows) != 1 else ''}</span><h2>{esc(eb)}</h2></div>
    <ul class="doc-links">{li}</ul>
  </div>
</section>
'''
    n = len(items)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tenerife Questions Answered | Practical Travel Advice — Tenerife Compass</title>
<meta name="description" content="Straight answers to the questions people actually ask about Tenerife: tap water, costs, calima, sharks, stargazing, car hire, airport transfers and when to visit.">
<link rel="canonical" href="{BASE}/questions/">
<meta name="theme-color" content="#0d9bb5">
<meta property="og:type" content="website"><meta property="og:site_name" content="Tenerife Compass">
<meta property="og:title" content="Tenerife Questions Answered">
<meta property="og:description" content="Straight answers to the questions people actually ask about Tenerife.">
<meta property="og:url" content="{BASE}/questions/">
<meta property="og:image" content="{BASE}/assets/img/beach-sunbeds.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/compass.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/style.css?v=7">
</head>
<body>
{nav()}
<section class="hero" style="min-height:40vh;">
  <img class="hero__bg" src="/assets/img/beach-sunbeds.jpg" alt="A Costa Adeje beach" loading="eager" fetchpriority="high">
  <div class="container hero__inner" style="padding:44px 0;">
    <span class="eyebrow">Straight answers</span>
    <h1>Tenerife questions answered</h1>
    <p class="lede">The things people actually ask before they book, answered without the sales pitch.</p>
  </div>
</section>
<div class="container"><nav class="breadcrumb"><a href="/">Home</a><span>›</span> Questions</nav></div>
<section class="section section--white" style="padding:34px 0 6px;">
  <div class="container"><div class="prose" style="text-align:center;">
    <p>{n} questions so far. Where sources disagree or rules change often, we say so and point you at the official source rather than guessing.</p>
  </div></div>
</section>
{secs}
<p class="text-center" style="margin:1em 0 3em;"><a class="btn btn--primary" href="/places/">Browse places instead</a></p>
{footer()}'''

def main():
    A = json.load(open(os.path.join(ROOT, 'data', 'answer-content.json'), encoding='utf-8'))
    for slug, page in A.items():
        open(os.path.join(ROOT, slug + '.html'), 'w', encoding='utf-8').write(
            answer_page(slug, page, A))
    os.makedirs(os.path.join(ROOT, 'questions'), exist_ok=True)
    open(os.path.join(ROOT, 'questions', 'index.html'), 'w', encoding='utf-8').write(index_page(A))
    print(f'búið til: {len(A)} spurningasíður + /questions/')

if __name__ == '__main__':
    main()
