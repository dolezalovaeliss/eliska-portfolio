"""One-off: pulled content from the pre-redesign pages into projects.json (now the source of truth; the old pages are overwritten by build.py)."""
import re, json, html, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
work = re.sub(r'<!--.*?-->', '', (ROOT / "_build" / "work-old.html").read_text(), flags=re.S)
order = re.findall(r'<a class="work-tile reveal" href="([^"]+)" data-tags="([^"]*)"', work)
covers = dict(re.findall(r'<a class="work-tile reveal" href="([^"]+)"[^>]*>\s*<div class="work-tile-card"><(?:img src|video src)="([^"]+)"', work))
posters = dict(re.findall(r'<a class="work-tile reveal" href="([^"]+)"[^>]*>\s*<div class="work-tile-card"><video [^>]*poster="([^"]+)"', work))
def txt(s): return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()
out = []
for href, tags in order:
    s = (ROOT / href).read_text()
    title = txt(re.search(r'<h1 class="pj-title">(.*?)</h1>', s, re.S).group(1))
    lead = re.search(r'<p class="pj-lead">(.*?)</p>', s, re.S).group(1).strip()
    more = [m.strip() for m in re.findall(r'<p class="pj-more">(.*?)</p>', s, re.S)]
    meta = [(txt(k), v.strip()) for k, v in re.findall(r'<div class="pj-k">([^<]*)</div><div class="pj-v">(.*?)</div>', s)]
    outputs = [txt(o) for o in re.findall(r'<span class="chip chip--static">(.*?)</span>', s)]
    hero = re.search(r'<div class="pj-hero-media">(.*?)</header>', s, re.S).group(1)
    slides = []
    for m in re.finditer(r'<figure class="pj-slide[^"]*">(.*?)</figure>', hero, re.S):
        f = m.group(1)
        v = re.search(r'<video src="([^"]+)" poster="([^"]+)"[^>]*aria-label="([^"]*)"', f)
        i = re.search(r'<img src="([^"]+)" alt="([^"]*)"', f)
        slides.append({'type': 'video', 'src': v.group(1), 'poster': v.group(2), 'alt': html.unescape(v.group(3))} if v else {'type': 'img', 'src': i.group(1), 'alt': html.unescape(i.group(2))})
    gal = re.search(r'<section class="pj-gallery-wrap wrap">(.*?)</section>', s, re.S)
    items = []
    if gal:
        for blk in re.finditer(r'<div class="pj-gallery([^"]*)"[^>]*>(.*?)\n    </div>', gal.group(1), re.S):
            cls, inner = blk.groups()
            for m in re.finditer(r'<(?:button|div) class="pj-fig([^"]*)"[^>]*>(.*?)</(?:button|div)>', inner, re.S):
                fc, f = m.groups()
                v = re.search(r'<video src="([^"]+)" poster="([^"]+)"[^>]*aria-label="([^"]*)"', f)
                i = re.search(r'<img src="([^"]+)" alt="([^"]*)"', f)
                if v: items.append({'type': 'video', 'src': v.group(1), 'poster': v.group(2), 'alt': html.unescape(v.group(3))})
                elif i: items.append({'type': 'page' if 'pj-fig--page' in fc else 'img', 'src': i.group(1), 'alt': html.unescape(i.group(2))})
    out.append({'href': href, 'tags': tags.split(), 'title': title, 'lead': lead, 'more': more, 'meta': meta,
                'outputs': outputs, 'slides': slides, 'gallery': items,
                'cover': posters.get(href) or covers.get(href), 'cover_video': covers.get(href) if href in posters else None})
(ROOT / '_build' / 'projects.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
for p in out:
    print(p['href'], p['tags'], len(p['slides']), [g['type'] for g in p['gallery']], [k for k, _ in p['meta']])
