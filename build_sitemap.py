#!/usr/bin/env python3
"""
Tenerife Compass — sitemap-rafall.

Skannar allar HTML-síður, sleppir noindex og research/, og skrifar
sitemap.xml með <lastmod> úr GIT-sögunni — ekki skráartíma, því
staðarsíðurnar eru endurbyggðar í hverri keyrslu og skráartíminn myndi
því segja "breytt í dag" um efni sem breyttist ekki.

Keyrsla:  python3 build_sitemap.py   (build_places.py kallar á hana)
"""
import os, re, glob, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://tenerifecompass.com'
SKIP_DIRS = ('research/', '.github/', '.claude/')

# Forgangur og tíðni eftir tegund síðu.
def rank(url):
    if url == '/':                     return ('weekly',  '1.0')
    if url in ('/places/',):           return ('weekly',  '0.9')
    if re.fullmatch(r'/\w[\w-]*/', url): return ('weekly', '0.9')   # svæðishubbar
    if url.startswith('/place/'):      return ('monthly', '0.7')
    if url in ('/about.html',):        return ('yearly',  '0.4')
    if url in ('/privacy.html',):      return ('yearly',  '0.3')
    if '/' in url.strip('/'):          return ('monthly', '0.7')    # undirsíður svæða
    return ('monthly', '0.8')                                        # eyjarsíður

def git_date(path):
    """Síðasta skipting sem snerti skrána, á ISO-formi. Tóm ef ósaflað."""
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', path],
                             cwd=ROOT, capture_output=True, text=True, timeout=10)
        return out.stdout.strip()
    except Exception:
        return ''

def main():
    urls = []
    files = sorted(p[len(ROOT) + 1:] for p in glob.glob(ROOT + '/**/*.html', recursive=True))
    for f in files:
        if f.startswith(SKIP_DIRS):
            continue
        s = open(os.path.join(ROOT, f), encoding='utf-8').read()
        if 'noindex' in s:
            continue
        url = '/' + f
        if url.endswith('/index.html'):
            url = url[:-len('index.html')]
        urls.append((url, git_date(f)))

    urls.sort(key=lambda u: (u[0] != '/', u[0].count('/'), u[0]))
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, date in urls:
        lm = f'<lastmod>{date}</lastmod>' if date else ''
        freq, pri = rank(url)
        out.append(f'  <url><loc>{BASE}{url}</loc>{lm}'
                   f'<changefreq>{freq}</changefreq><priority>{pri}</priority></url>')
    out.append('</urlset>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print(f'sitemap: {len(urls)} slóðir, {sum(1 for _, d in urls if d)} með lastmod')

if __name__ == '__main__':
    main()
