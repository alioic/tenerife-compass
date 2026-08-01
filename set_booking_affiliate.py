#!/usr/bin/env python3
"""
Tenerife Compass — kveikir á Booking-samstarfinu í öllum hlekkjum í einu.

Booking rekur ekki lengur beina skráningu fyrir nýja aðila: umsóknin fer í
gegnum CJ (Commission Junction). Þess vegna ræður þetta við tvö snið, því
við vitum ekki fyrirfram hvort okkur býðst annað eða hitt:

  param — Booking eigið ?aid=<aid>, sem eldri beinir samstarfsaðilar fá
          (spadmin.booking.com).
          → https://www.booking.com/searchresults.html?ss=...&aid=1234567

  cj    — CJ djúptengill, þar sem forskeytið vefur utan um kóðaða slóð.
          → https://www.anrdoezrs.net/links/<PID>/type/dlg/https%3A%2F%2F...

Keyrsla:
    python3 set_booking_affiliate.py --mode param --aid 1234567
    python3 set_booking_affiliate.py --mode cj --prefix "https://www.anrdoezrs.net/links/PID/type/dlg/"
    python3 set_booking_affiliate.py --status        # sýnir stöðuna
    python3 set_booking_affiliate.py --off           # tekur allt til baka

Aðgerðin er endurkeyranleg: hlekkur sem er þegar merktur er ekki merktur aftur,
og --off skilar öllum hlekkjum í upprunalegt horf.
"""
import argparse, glob, json, os, re, subprocess, sys, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
CONF = os.path.join(ROOT, 'data', 'affiliates.json')
BASE = 'https://www.booking.com/searchresults.html'

# Hráir hlekkir (ómerktir) og CJ-vafðir hlekkir, hvor um sig.
RAW_RE = re.compile(r'https://www\.booking\.com/searchresults\.html\?ss=([^"&]+)')
CJ_RE  = re.compile(r'https://[^"]*?/type/dlg/(https%3A%2F%2Fwww\.booking\.com[^"]*)')


def load():
    return json.load(open(CONF, encoding='utf-8'))


def save(conf):
    json.dump(conf, open(CONF, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def html_files():
    for p in sorted(glob.glob(ROOT + '/**/*.html', recursive=True)):
        rel = p[len(ROOT) + 1:]
        if rel.startswith(('research/', '.github/')):
            continue
        yield p, rel


def strip_to_raw(text):
    """Skilar öllum Booking-hlekkjum í ómerkt horf, sama hvaða snið var notað."""
    # CJ-vafning → afkóða aftur í beina slóð
    text = CJ_RE.sub(lambda m: urllib.parse.unquote(m.group(1)), text)
    # ?aid= eða &aid= burt
    text = re.sub(r'(https://www\.booking\.com/searchresults\.html\?[^"]*?)&amp;aid=\d+', r'\1', text)
    text = re.sub(r'(https://www\.booking\.com/searchresults\.html\?[^"]*?)&aid=\d+', r'\1', text)
    return text


def apply_mode(text, mode, aid, prefix):
    text = strip_to_raw(text)
    if mode == 'none':
        return text
    if mode == 'param':
        # &amp; því þetta situr í HTML-eigind
        return RAW_RE.sub(lambda m: f'{BASE}?ss={m.group(1)}&amp;aid={aid}', text)
    if mode == 'cj':
        def wrap(m):
            dest = urllib.parse.quote(f'{BASE}?ss={m.group(1)}', safe='')
            return prefix + dest
        return RAW_RE.sub(wrap, text)
    raise SystemExit(f'óþekkt mode: {mode}')


def count_links():
    raw = tagged = 0
    for p, _ in html_files():
        s = open(p, encoding='utf-8').read()
        tagged += len(CJ_RE.findall(s)) + len(re.findall(r'booking\.com[^"]*aid=\d+', s))
        raw += len([m for m in RAW_RE.finditer(s)
                    if 'aid=' not in s[m.start():m.end() + 24]])
    return raw, tagged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['param', 'cj'])
    ap.add_argument('--aid')
    ap.add_argument('--prefix')
    ap.add_argument('--off', action='store_true')
    ap.add_argument('--status', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    conf = load()
    b = conf['booking']

    if a.status:
        raw, tagged = count_links()
        print(f"stilling : mode={b['mode']} aid={b['aid'] or '—'} prefix={b['cj_prefix'] or '—'}")
        print(f"hlekkir  : {tagged} merktir, {raw} ómerktir")
        return

    if a.off:
        mode, aid, prefix = 'none', '', ''
    elif a.mode == 'param':
        if not a.aid or not a.aid.isdigit():
            raise SystemExit('--aid vantar (aðeins tölustafir)')
        mode, aid, prefix = 'param', a.aid, ''
    elif a.mode == 'cj':
        if not a.prefix or '/type/dlg/' not in a.prefix:
            raise SystemExit('--prefix vantar og verður að innihalda /type/dlg/')
        mode, aid, prefix = 'cj', '', a.prefix
    else:
        raise SystemExit('veldu --mode param|cj, eða --off, eða --status')

    changed = 0
    for p, rel in html_files():
        s = open(p, encoding='utf-8').read()
        if 'booking.com' not in s:
            continue
        s2 = apply_mode(s, mode, aid, prefix)
        if s2 != s:
            changed += 1
            if not a.dry_run:
                open(p, 'w', encoding='utf-8').write(s2)

    if not a.dry_run:
        b.update({'mode': mode, 'aid': aid, 'cj_prefix': prefix})
        save(conf)
        # Rafalarnir lesa stillinguna, svo nýjar síður fá hana líka.
        for script in ('build_places.py', 'build_answers.py'):
            subprocess.run([sys.executable, os.path.join(ROOT, script)],
                           cwd=ROOT, check=True, capture_output=True)

    raw, tagged = count_links()
    print(f"{'[þurrkeyrsla] ' if a.dry_run else ''}mode={mode} — {changed} skrár snertar")
    print(f"hlekkir: {tagged} merktir, {raw} ómerktir")


if __name__ == '__main__':
    main()
