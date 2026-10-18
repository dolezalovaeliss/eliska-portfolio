"""Generate the redesigned site from _build/projects.json (content from the current site).
Run: python3 _build/extract.py  (once, on the old pages)  then  python3 _build/build.py
"""
import re, json, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = json.loads((ROOT / '_build' / 'projects.json').read_text())
V = '20261018j'
CUR = ' aria-current="page"'
LAZY = ' loading="lazy"'
EMAIL = 'hello@eliskadolezalova.cz'
PHONE = '+420 778 036 943'
LINKEDIN = 'https://www.linkedin.com/in/eliška-doležalová-1101631a1/'
CV = 'images/eliska-dolezalova-cv.pdf'
AVATAR = 'profile.jpg'

# Product design: exact content of Figma frame "Work — Product design" (62:19832); images exported from it, no detail pages
PRODUCT_INTRO = 'Data tools, security products and internal systems. Work where the hard part is the structure, not the screen.'
PRODUCT = [
    ('Asset Layout Editor', 'Ataccama', 'asset-layout-editor', 'A layout editor inside the data catalog. Admins decide which properties, relations and sections each asset page shows, and in what order.'),
    ('WebScannerPro — Dashboard', 'WebScannerPro', 'wsp-dashboard', 'Home for a browser security product. Protection score, filters and alerts in one calm overview, with clear steps to fix what’s off.'),
    ('WebScannerPro — Browser extension', 'WebScannerPro', 'wsp-extension', 'Where the protection actually runs. Blocking, Browser VPN and dark web monitoring, each one click away from the toolbar.'),
    ('ArmaCover — Mobile app', 'ArmaCover', 'armacover-app', 'Cyber insurance in your pocket. Sign in, see that you’re covered, and get help fast when something goes wrong.'),
    ('ArmaCover — Dark web monitoring', 'ArmaCover', 'armacover-dwm', 'Dashboard that watches leaked data across the whole account and turns every breach into a few concrete next steps.'),
    ('Altoa — Healthcare platform', 'Altoa', 'altoa-orders', 'Back office for a premium healthcare service. Exam orders, patient escorts to clinics, clients, company contracts, cards and vouchers live in one system, together with the product catalogue and the content of the Czech and Austrian websites.'),
]
# Category intros reuse the "What I do" lines from the current About page
CATS = [
    ('product', 'Product design', 'work-product.html', PRODUCT_INTRO),
    ('web', 'Web design', 'work.html', 'Designing and shipping responsive websites, from a single landing page to a full site.'),
    ('brand', 'Branding', 'work-branding.html', 'Logos, colour and type systems, and the visual language that makes a brand feel like itself.'),
    ('motion', 'Animations', 'work-animations.html', 'Motion design, UI animation and brand motion.'),
]
CAT = {c[0]: c for c in CATS}
# Smaller projects show as text-only entries, like Odstrčil / Rezidence & Elspace / 1. Web IT / Duhová stužka in the design
COMPACT = {'project-odstrcil.html', 'project-rezidence.html', 'project-elspace.html', 'project-geomap.html',
           'project-1webit.html', 'project-duhova-stuzka.html', 'project-prague-pride-merch.html'}
PRIMARY = {'project-1webit.html': 'brand', 'project-dluhopisomat.html': 'web'}

work_src = re.sub(r'<!--.*?-->', '', (ROOT / '_build' / 'work-old.html').read_text(), flags=re.S)
CLIENT = {h: html.unescape(m.split('·')[0].strip()) for h, m in re.findall(
    r'<a class="work-tile reveal" href="([^"]+)".*?<div class="work-tile-meta">(.*?)</div>', work_src, re.S)}

def strip(s): return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()
def first_sentence(s):
    t = strip(s)
    m = re.search(r'^(.+?[a-z\)])\.(\s|$)', t)
    return (m.group(1) + '.') if m else t
def esc(s): return html.escape(s, quote=True)
def primary(p): return PRIMARY.get(p['href']) or next(t for t in ('web', 'product', 'brand', 'motion') if t in p['tags'])
P = [p for p in P if 'product' not in p['tags']]
def in_cat(key): return PRODUCT if key == 'product' else [p for p in P if key in p['tags']]

def icon(name, w=16, alt=''):
    return f'<img src="images/icons/{name}.svg" width="{w}" height="{w}" alt="{alt}" />'

def head(title, desc, url, extra=''):
    t = esc(title)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{t}</title>
<meta name="description" content="{esc(desc)}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400..500&display=swap" rel="stylesheet" />
<link rel="icon" type="image/svg+xml" href="favicon.svg?v=2" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{t}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="https://elisdolezalova.cz/images/og-image.png" />
<meta property="og:url" content="https://elisdolezalova.cz/{url}" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="stylesheet" href="site.css?v={V}" />{extra}
</head>
<body>
'''

def nav(page, cat=None):
    """Desktop dock + mobile context pill/sheet + command palette + lightbox."""
    def item(key, label, href):
        on = ' is-on' if page == key else ''
        cur = ' aria-current="page"' if page == key else ''
        return f'<a class="d-item{on}" href="{href}"{cur}>{label}</a>'
    if cat:
        subs = ''.join(
            f'<a class="d-sub{" is-on" if k == cat else ""}" href="{h}"{CUR if k == cat and page == "work" else ""}>{l} <small>{len(in_cat(k))}</small></a>'
            for k, l, h, _ in CATS)
        work = f'<div class="d-work"><a class="d-item is-on" href="work.html">Work</a><span class="sep" aria-hidden="true"></span>{subs}</div>'
        cmd = f'<button class="d-cmd icon-only" type="button" data-cmdk aria-label="Search (⌘K)">{icon("search", 18)}</button>'
    else:
        work = item('work', 'Work', 'work.html')
        cmd = f'<button class="d-cmd" type="button" data-cmdk aria-label="Search">{icon("search", 18)}<span aria-hidden="true">⌘K</span></button>'
    dock = f'''
  <nav class="dock" aria-label="Main">
    <a href="index.html" aria-label="Index"><img class="avatar" src="{AVATAR}" alt="" width="32" height="32" /></a>
    {item('index', 'Index', 'index.html')}
    {work}
    {item('about', 'About', 'about.html')}
    {item('contact', 'Contact', 'contact.html')}
    <span class="d-div" aria-hidden="true"></span>
    {cmd}
  </nav>'''
    label = {'index': 'Index', 'about': 'About me', 'contact': 'Contact', 'work': 'Work'}[page]
    ctx_text = f'<span>Work</span><b>{CAT[cat][1]}</b>' if cat else f'<b>{label}</b>'
    sheet_work = ''.join(
        f'<a class="s-item{" is-on" if k == cat else ""}" href="{h}"><span>{l}</span><small>{len(in_cat(k))} projects</small>{icon("check-sheet", 18)}</a>'
        for k, l, h, _ in CATS)
    pages = ''.join(f'<a class="s-item{" is-on" if page == k else ""}" href="{h}"><span>{l}</span>{icon("check-sheet", 18)}</a>'
                    for k, l, h in (('index', 'Index', 'index.html'), ('about', 'About me', 'about.html'), ('contact', 'Contact', 'contact.html')))
    return dock + f'''
  <button class="ctx" type="button" aria-expanded="false" aria-controls="sheet"><img class="avatar" src="{AVATAR}" alt="" width="32" height="32" />{ctx_text}{icon("up", 18)}</button>
  <div class="scrim" aria-hidden="true"></div>
  <div class="sheet" id="sheet" role="dialog" aria-label="Menu">
    <span class="grab" aria-hidden="true"></span>
    <div class="s-group"><p class="s-label">Work</p>{sheet_work}</div>
    <div class="s-group"><p class="s-label">Pages</p>{pages}</div>
  </div>
  <div class="cmdk" role="dialog" aria-label="Search">
    <div class="cmdk-box">
      <label class="cmdk-input">{icon("search", 18)}<input type="text" placeholder="Search projects and pages" aria-label="Search projects and pages" /></label>
      <div class="cmdk-list"></div>
    </div>
  </div>
  <div class="lb" role="dialog" aria-label="Full image"><button class="lb-close" type="button">Close</button><img src="" alt="" /></div>
  <script src="site-data.js?v={V}"></script>
  <script src="site.js?v={V}"></script>
</body>
</html>
'''

def links_row():
    return f'''<div class="links"><a href="mailto:{EMAIL}">Email ↗</a><a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn ↗</a><a href="{CV}" target="_blank" rel="noopener">CV ↗</a></div>'''

def rows(items):
    # Columns: name · role · years, typography after jakub.kr (title 450 ink, details grey)
    return '\n'.join(f'      <div class="row"><p class="li-t">{a}</p><p class="li-s">{b}</p><p class="li-n">{c}</p></div>' for a, b, c in items)

EXPERIENCE = [
    ('Cybertrends', 'Head of Design', '2026'),
    ('Shoptet', 'UX Designer', '2026'),
    ('Ataccama', 'Product Designer', '2026'),
    ('1. Web IT', 'Visual Identity Lead, UX/UI Designer', '2025 – 26'),
    ('Apadore', 'B2B Web Designer', '2025 – 26'),
    ('Jitro / KVIFF', 'Apprenticeship', '2025'),
    ('Nanook', 'Graphic Designer', '2025'),
    ('Prague Pride', 'Visual Identity Lead', '2022 – 25'),
    ('Avon', 'Graphic Designer', '2023 – 25'),
    ('Uniqway', 'UX/UI Designer', '2022 – 23'),
    ('Meffert ČR', 'Graphic Designer', '2020 – 22'),
    ('5DM.cz', 'Graphic Designer', '2019 – 20'),
]
EDUCATION = [
    ('UX Design &amp; Research', 'Master’s, VŠE', '2022 – 25'),
    ('Multimedia Communication', 'Master’s studies, VŠE', '2022 – 24'),
    ('Information Media &amp; Services', 'Bachelor’s, VŠE', '2018 – 22'),
    ('Web Design', 'Bont Academy', ''),
]

def write(name, s):
    (ROOT / name).write_text(s)
    print('wrote', name)

# ---------- Index ----------
STACK_IMGS = {
    'product': ['images/projects/product/armacover-app.png', 'images/projects/product/wsp-dashboard.png', 'images/projects/product/asset-layout-editor.png'],
    'web': ['images/projects/atelier3/cover.jpg', 'images/projects/esens/cover.jpg', 'images/projects/cybertrends/cover.jpg'],
    'brand': ['images/projects/duhova-stuzka/cover.png', 'images/projects/prague-pride/cover.jpg', 'images/projects/cybertrends-logo/symbol.png'],
}
def stack_imgs(k): return ''.join('<img src="%s" alt="" loading="lazy" />' % s for s in STACK_IMGS[k])
stacks = '\n'.join(f'''        <a class="stack" href="{CAT[k][2]}">
          <div class="stack-cards" aria-hidden="true">{stack_imgs(k)}</div>
          <div class="stack-label"><b>{CAT[k][1]}</b><span>{len(in_cat(k))} projects</span></div>
        </a>''' for k in ('product', 'web', 'brand'))
write('index.html', head('Eliška Doležalová — Product & Visual Designer', 'Product & visual designer based in Prague.', '') + f'''
  <main class="col">
    <div class="identity">
      <img class="avatar" src="{AVATAR}" alt="Eliška Doležalová" width="48" height="48" />
      <div><h1 class="medium">Eliška Doležalová</h1><p class="muted">Product &amp; Visual Designer</p></div>
    </div>

    <div class="bio">
      <p>I’m a product &amp; visual designer based in Prague, currently Head of Design at <a class="u" href="project-cybertrends.html">Cybertrends</a>. I like understanding the whole problem, not just one screen, and helping decide where a product should go.</p>
      <p>I started in graphic design, doing brands and websites, and spent a lot of those years around culture, working with festivals like <a class="u" href="https://www.kviff.com" target="_blank" rel="noopener">KVIFF</a> and <a class="u" href="project-prague-pride.html">Prague Pride</a>. Later I moved into UX during my master’s.</p>
      <p>You can reach me via <a class="u" href="mailto:{EMAIL}">email</a>, find me on <a class="u" href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a> or download my <a class="u" href="{CV}" target="_blank" rel="noopener">CV</a>.</p>
    </div>

    <section>
      <div class="sel-head"><h2 class="medium">Selected work</h2><a href="work.html">View all →</a></div>
      <div class="stacks">
{stacks}
      </div>
    </section>

    <section class="block block--rows">
      <h2 class="block-title">Experience</h2>
{rows(EXPERIENCE)}
    </section>

    <section class="block">
      <h2 class="block-title">Elsewhere</h2>
      {links_row()}
    </section>
  </main>
''' + nav('index'))

# ---------- About ----------
WHAT = [
    ('Product design', 'Understanding the whole problem, not just one screen. From research and structure to flows that ship.'),
    ('AI‑leveraged workflow', 'Custom AI skills, context engineering, an Obsidian knowledge base and AI prototyping in Claude Code.'),
    ('Web design', 'Designing and shipping responsive websites, from a single landing page to a full site.'),
    ('Brand &amp; visual identity', 'Logos, colour and type systems, and the visual language that makes a brand feel like itself.'),
]
write('about.html', head('About — Eliška Doležalová', 'About Eliška Doležalová, product & visual designer based in Prague.', 'about.html') + f'''
  <main class="col">
    <div class="page-head">
      <a class="back" href="index.html">← Index</a>
      <h1 class="h1">About me</h1>
    </div>

    <div class="bio">
      <p>I’m Eliška, a designer based in Prague. I started in graphic design, doing brands and websites, and spent a lot of those years around culture, working with festivals like <a class="u" href="https://www.kviff.com" target="_blank" rel="noopener">KVIFF</a> and <a class="u" href="project-prague-pride.html">Prague Pride</a>.</p>
      <p>Later I moved into UX, studied it during my master’s, and ended up in product design. I like it because I get to understand the whole problem, not just one screen, and help decide where a product should go, based on its vision and what’s actually happening in the market.</p>
      <p>I build my own AI skills and a context system in <a class="u" href="https://obsidian.md" target="_blank" rel="noopener">Obsidian</a>, a knowledge base where I keep research, reports and reusable context. So the tools work the way I do and I can prototype in real code.</p>
    </div>

    <section class="block">
      <h2 class="block-title">What I do</h2>
{chr(10).join(f'      <div class="li"><p class="li-t">{a}</p><p class="li-s">{b}</p></div>' for a, b in WHAT)}
    </section>

    <section class="block block--rows">
      <h2 class="block-title">Experience</h2>
{rows(EXPERIENCE)}
    </section>

    <section class="block block--rows block--edu">
      <h2 class="block-title">Education</h2>
{rows(EDUCATION)}
    </section>

    <section class="block">
      <h2 class="block-title">Elsewhere</h2>
      {links_row()}
    </section>
  </main>
''' + nav('about'))

# ---------- Contact ----------
write('contact.html', head('Contact — Eliška Doležalová', 'Get in touch with Eliška Doležalová.', 'contact.html') + f'''
  <main class="contact-wrap">
    <div class="card">
      <div class="card-top">
        <img class="avatar" src="{AVATAR}" alt="" width="56" height="56" />
        <div class="card-id"><h1>Eliška Doležalová</h1><p>Product &amp; Visual Designer · Prague</p></div>
        <time class="card-time" data-clock aria-label="Local time in Prague"></time>
      </div>
      <div class="card-rows">
        <button class="card-row" type="button" data-copy="{EMAIL}" aria-label="Copy email {EMAIL}"><span class="k">Email</span><span class="v">{EMAIL}</span><span class="tooltip" role="status">{icon("check", 14)}Copied</span>{icon("copy")}</button>
        <a class="card-row" href="tel:{PHONE.replace(' ', '')}"><span class="k">Phone</span><span class="v">{PHONE}</span>{icon("phone")}</a>
        <a class="card-row" href="{LINKEDIN}" target="_blank" rel="noopener"><span class="k">LinkedIn</span><span class="v">Eliška Doležalová</span>{icon("arrow")}</a>
        <a class="card-row" href="{CV}" target="_blank" rel="noopener"><span class="k">CV</span><span class="v">Download PDF</span>{icon("down")}</a>
      </div>
    </div>
  </main>
''' + nav('contact'))

# ---------- Work category pages ----------
def entry(p, n, cat):
    href = p['href']
    title = esc(p['title'])
    client = esc(CLIENT.get(href, ''))
    desc = esc(first_sentence(p['lead']))
    img = ''
    if href not in COMPACT:
        if cat == 'product':
            img = f'<a class="entry-img entry-img--shot" href="{href}" tabindex="-1" aria-hidden="true"><img src="{p["cover"]}" alt="" loading="lazy" /></a>'
        elif p.get('cover_video'):
            img = f'<a class="entry-img" href="{href}" tabindex="-1" aria-hidden="true"><video src="{p["cover_video"]}" poster="{p["cover"]}" autoplay muted loop playsinline preload="metadata"></video></a>'
        else:
            img = f'<a class="entry-img" href="{href}" tabindex="-1" aria-hidden="true"><img src="{p["cover"]}" alt="" loading="lazy" /></a>'
    btn = '' if cat == 'product' else f'<a class="btn-details" href="{href}" aria-label="{title} details">Details {icon("arrow-up-right", 20)}</a>'
    return f'''      <article class="entry">
        {img}
        <div class="entry-title"><a href="{href}">{title}</a><span class="client">{client}</span><span class="num">{n:02d}</span></div>
        <p class="entry-desc">{desc}</p>
        {btn}
      </article>'''

def product_entry(e, n):
    title, client, img, desc = e
    return f'''      <article class="entry">
        <div class="entry-img entry-img--figma"><img src="images/projects/product/{img}.png" alt="{esc(title)}" loading="lazy" width="560" height="413" /></div>
        <div class="entry-title"><h2>{esc(title)}</h2><span class="client">{esc(client)}</span><span class="num">{n:02d}</span></div>
        <p class="entry-desc">{esc(desc)}</p>
      </article>'''

for key, label, href, intro in CATS:
    items = in_cat(key)
    if key == 'product':
        body = chr(10).join(product_entry(e, i + 1) for i, e in enumerate(items))
    else:
        body = chr(10).join(entry(p, i + 1, key) for i, p in enumerate(items))
    write(href, head(f'{label} — Eliška Doležalová', intro, href) + f'''
  <main class="col">
    <div class="page-head page-head--work">
      <a class="back" href="index.html">← Work</a>
      <p class="crumb"><span>Work</span>{icon("chev", 14)}<b>{label}</b></p>
      <h1 class="h1">{label}</h1>
      <p class="intro">{intro}</p>
    </div>
    <div class="entries">
{body}
    </div>
  </main>
''' + nav('work', key))

# ---------- Project details ----------
def media(m, cls=''):
    if m['type'] == 'video':
        return f'<video src="{m["src"]}" poster="{m["poster"]}" autoplay muted loop playsinline preload="metadata" aria-label="{esc(m["alt"])}"></video>'
    return f'<img src="{m["src"]}" alt="{esc(m["alt"])}"{cls} />'

for p in P:
    cat = primary(p)
    cover = p['slides'][0]
    seen = {cover['src']}
    rest = []
    for m in p['slides'][1:] + p['gallery']:
        if m['src'] in seen: continue
        seen.add(m['src']); rest.append(m)
    figs = []
    for m in rest:
        if m['type'] == 'page':
            figs.append(f'''      <div class="screen">
        <div class="screen-scroll" tabindex="0" aria-label="{esc(m["alt"])}, scrollable"><img src="{m["src"]}" alt="{esc(m["alt"])}" loading="lazy" /></div>
        <p class="hint"><b>Scroll to explore</b><i>·</i><button type="button" data-full="{m["src"]}" data-alt="{esc(m["alt"])}">View full page ↗</button></p>
      </div>''')
        elif m['type'] == 'video':
            figs.append(f'      <div class="g-img g-vid">{media(m)}</div>')
        else:
            figs.append(f'      <button class="g-img" type="button" data-full="{m["src"]}" data-alt="{esc(m["alt"])}">{media(m, LAZY)}</button>')
    if len(figs) == 1:
        figs[0] = figs[0].replace('class="', 'class="solo ', 1)
    gallery = f'\n    <section class="gallery">\n' + '\n'.join(figs) + '\n    </section>' if figs else ''
    meta = '\n'.join(f'          <div class="meta-row"><span class="k">{k}</span><span>{v}</span></div>' for k, v in p['meta'])
    disc = ''.join(f'<a class="pill" href="{CAT[t][2]}">{"Brand design" if t == "brand" else CAT[t][1]}</a>' for t in p['tags'])
    outs = ''.join(f'<span class="pill">{esc(o)}</span>' for o in p['outputs'])
    more = '\n'.join(f'        <p class="more">{m}</p>' for m in p['more'])
    write(p['href'], head(f'{p["title"]} — Eliška Doležalová', first_sentence(p['lead']), p['href']) + f'''
  <main class="detail">
    <section class="hero">
      <div class="hero-text">
        <div class="hero-top">
          <a class="back" href="{CAT[cat][2]}">← {CAT[cat][1]}</a>
          <h1 class="h1">{esc(p["title"])}</h1>
        </div>
        <p class="lead">{p["lead"]}</p>
{more}
        <div class="facts">
          <div>
{meta}
          </div>
          <div class="pills-block"><p>Disciplines</p><div class="pills">{disc}</div></div>
          {f'<div class="pills-block"><p>Outputs</p><div class="pills">{outs}</div></div>' if outs else ''}
        </div>
      </div>
      <div class="cover">{media(cover)}</div>
    </section>
{gallery}
    <section class="outro" aria-label="Contact">
      <p class="sentence">
        <span>Like what you see?</span>
        <a class="cta cta--dark" href="mailto:{EMAIL}?subject=Project%20inquiry"><img class="avatar" src="{AVATAR}" alt="" width="40" height="40" />Write me</a>
        <a class="cta cta--icon" href="tel:{PHONE.replace(' ', '')}">{icon("phone-lg", 28)}call me</a>
        <span>or</span>
        <a class="cta" href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn ↗</a>
      </p>
    </section>
  </main>
''' + nav('work', cat))

# ---------- Search index ----------
idx = [{'t': 'Index', 's': 'Page', 'h': 'index.html'}, {'t': 'About me', 's': 'Page', 'h': 'about.html'}, {'t': 'Contact', 's': 'Page', 'h': 'contact.html'}]
idx += [{'t': l, 's': f'{len(in_cat(k))} projects', 'h': h} for k, l, h, _ in CATS]
idx += [{'t': p['title'], 's': CAT[primary(p)][1], 'h': p['href']} for p in P]
write('site-data.js', 'window.SITE_INDEX = ' + json.dumps(idx, ensure_ascii=False) + ';\n')
