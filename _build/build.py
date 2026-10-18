"""Generate the redesigned site from _build/projects.json (content from the current site).
Run: python3 _build/extract.py  (once, on the old pages)  then  python3 _build/build.py
"""
import re, json, html, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = json.loads((ROOT / '_build' / 'projects.json').read_text())
V = '20261019c'
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
    ('Altoa — Healthcare platform', 'Altoa', 'altoa-orders', 'Back office for a premium healthcare service. Exam orders, patient escorts to clinics, clients, company contracts, cards and vouchers live in one system, together with the product catalogue and the website content in several language versions.'),
    ('Ataccama ONE — Data catalog', 'Ataccama', 'asset-layout-editor', 'Ataccama ONE is a platform for data quality, governance and observability that large companies use to find, understand and trust their data. I was a product designer in the Product Catalog team, working on the catalog where every dataset, table and business term lives. Shown here is the Asset Layout Editor, which lets admins decide what each asset page shows and in what order.'),
    ('WebScannerPro — Dashboard', 'WebScannerPro', 'wsp-dashboard', 'Home for a browser security product. Protection score, filters and alerts in one calm overview, with clear steps to fix what’s off.'),
    ('WebScannerPro — Browser extension', 'WebScannerPro', 'wsp-extension', 'Where the protection actually runs. Blocking, Browser VPN and dark web monitoring, each one click away from the toolbar.'),
    ('ArmaCover — Mobile app', 'ArmaCover', 'armacover-app', 'Cyber insurance in your pocket. Sign in, see that you’re covered, and get help fast when something goes wrong.'),
    ('ArmaCover — Dark web monitoring', 'ArmaCover', 'armacover-dwm', 'Dashboard that watches leaked data across the whole account and turns every breach into a few concrete next steps.'),
]
# Category intros reuse the "What I do" lines from the current About page
CATS = [
    ('product', 'Product design', 'work-product.html', PRODUCT_INTRO),
    ('web', 'Web design', 'work-web.html', 'Designing and shipping responsive websites, from a single landing page to a full site.'),
    ('brand', 'Branding', 'work-branding.html', 'Logos, colour and type systems, and the visual language that makes a brand feel like itself.'),
    ('motion', 'Visual & motion', 'work-visual-motion.html', 'Visuals and motion for existing brands: animations, key visuals and the graphics around them.'),
]
CAT = {c[0]: c for c in CATS}
COMPACT = set()  # every Work entry shows its image
PRIMARY = {}

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
TOTAL = len(PRODUCT) + len(P)
def in_cat(key): return PRODUCT if key == 'product' else [p for p in P if key in p['tags']]

def edge_fill(src):
    # Colour behind a 'contain'-fitted cover: average of the image's four corners, so letterboxing blends in
    try:
        im = Image.open(ROOT / src).convert('RGB'); w, h = im.size
        px = [im.getpixel((x, y)) for x in (2, w - 3) for y in (2, h - 3)]
        return '#%02x%02x%02x' % tuple(sum(c[i] for c in px) // 4 for i in range(3))
    except Exception:
        return '#000000'

def icon(name, w=16, alt=''):
    # Icons are masks filled with currentColor, so they follow the text colour in light and dark mode
    return f'<span class="i" style="--i: url(images/icons/{name}.svg); --s: {w}px" aria-hidden="true"></span>'

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
<script>document.documentElement.classList.add('js');try{{if(!sessionStorage.getItem('seen'))document.documentElement.classList.add('first-visit');sessionStorage.setItem('seen','1')}}catch(e){{}}try{{var t=localStorage.getItem('theme');if(t==='dark'||(!t&&matchMedia('(prefers-color-scheme: dark)').matches))document.documentElement.dataset.theme='dark'}}catch(e){{}}</script>
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
        work = f'<div class="d-work"><a class="d-item is-on" href="work.html"{CUR if cat == "all" else ""}>Work</a><span class="sep" aria-hidden="true"></span>{subs}</div>'
        cmd = f'<button class="d-cmd icon-only" type="button" data-cmdk aria-label="Search (⌘K)">{icon("search", 18)}</button>'
    else:
        work = item('work', 'Work', 'work.html')
        cmd = f'<button class="d-cmd" type="button" data-cmdk aria-label="Search">{icon("search", 18)}<span aria-hidden="true">⌘K</span></button>'
    dock = f'''
  <nav class="dock" aria-label="Main">
    <a href="index.html" aria-label="Home"><img class="avatar" src="{AVATAR}" alt="" width="32" height="32" /></a>
    {item('index', 'Home', 'index.html')}
    {work}
    {item('about', 'About', 'about.html')}
    {item('contact', 'Contact', 'contact.html')}
    <span class="d-div" aria-hidden="true"></span>
    {cmd}
    <button class="d-cmd icon-only d-theme" type="button" data-theme-toggle aria-label="Switch light or dark mode">{icon('moon', 18)}{icon('sun', 18)}</button>
  </nav>'''
    label = {'index': 'Home', 'about': 'About me', 'contact': 'Contact', 'work': 'Work'}[page]
    ctx_text = f'<span>Work</span><b>{CAT[cat][1]}</b>' if cat in CAT else f'<b>{label}</b>'
    sheet_work = f'<a class="s-item{" is-on" if cat == "all" else ""}" href="work.html"><span>All work</span><small>{TOTAL} projects</small>{icon("check-sheet", 18)}</a>' + ''.join(
        f'<a class="s-item{" is-on" if k == cat else ""}" href="{h}"><span>{l}</span><small>{len(in_cat(k))} projects</small>{icon("check-sheet", 18)}</a>'
        for k, l, h, _ in CATS)
    pages = ''.join(f'<a class="s-item{" is-on" if page == k else ""}" href="{h}"><span>{l}</span>{icon("check-sheet", 18)}</a>'
                    for k, l, h in (('index', 'Home', 'index.html'), ('about', 'About me', 'about.html'), ('contact', 'Contact', 'contact.html')))
    return dock + f'''
  <button class="ctx" type="button" aria-expanded="false" aria-controls="sheet"><img class="avatar" src="{AVATAR}" alt="" width="32" height="32" />{ctx_text}{icon("up", 18)}</button>
  <div class="scrim" aria-hidden="true"></div>
  <div class="sheet" id="sheet" role="dialog" aria-label="Menu">
    <span class="grab" aria-hidden="true"></span>
    <div class="s-group"><p class="s-label">Work</p>{sheet_work}</div>
    <div class="s-group"><p class="s-label">Pages</p>{pages}</div>
    <div class="s-group"><button class="s-item" type="button" data-theme-toggle><span class="s-theme-l">Dark mode</span><span class="s-theme-d">Light mode</span></button></div>
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

# Home client list: one colour, no separators; names with work on the site show its image on hover
def _cover(href):
    p = next((x for x in P if x['href'] == href), None)
    return p['cover'] if p else None
CLIENTS = [
    ('Cybertrends', 'project-cybertrends.html', _cover('project-cybertrends.html')),
    ('Ataccama', 'work-product.html#asset-layout-editor', 'images/projects/product/asset-layout-editor.png'),
    ('Shoptet', None, None),
    ('Apadore', 'project-esens.html', _cover('project-esens.html')),
    ('ZeroOne Company', 'project-startaiming.html', _cover('project-startaiming.html')),
    ('Nanook design studio', None, None),
    ('KVIFF', 'project-kviff.html', _cover('project-kviff.html')),
    ('Startaiming', 'project-startaiming.html', _cover('project-startaiming.html')),
    ('Altoa', 'work-product.html#altoa-orders', 'images/projects/product/altoa-orders.png'),
    ('Prague Pride', 'project-prague-pride.html', _cover('project-prague-pride.html')),
    ('Comfort Finance Group', 'project-cfg.html', _cover('project-cfg.html')),
    ('Dluhopisomat', 'project-dluhopisomat.html', _cover('project-dluhopisomat.html')),
    ('Atelier3', 'project-atelier3.html', _cover('project-atelier3.html')),
    ('Esens Letná', 'project-esens.html', _cover('project-esens.html')),
    ('Daramis', 'project-esens.html', _cover('project-esens.html')),
    ('Geomap', 'project-geomap.html', _cover('project-geomap.html')),
    ('Elspace', 'project-elspace.html', _cover('project-elspace.html')),
    ('Odstrčil', 'project-odstrcil.html', _cover('project-odstrcil.html')),
    ('1. Web IT', 'project-1webit.html', _cover('project-1webit.html')),
    ('Avon', None, None), ('Uniqway', None, None), ('Meffert', None, None),
]
DISCIPLINES = ['Product Design', 'UX Research', 'Information Architecture', 'Design Systems', 'Prototyping',
               'Usability Testing', 'Web Design', 'Landing Pages', 'Brand Identity', 'Logo Design', 'Art Direction',
               'Typography', 'Motion Design', 'Campaigns', 'AI Prototyping', 'Context Engineering']
INDUSTRIES = ['Technology & Software', 'Cybersecurity & Insurance', 'Data & AI', 'Finance & Investment',
              'Real Estate & Architecture', 'Healthcare', 'Film & Culture', 'Non-profit & Advocacy',
              'Retail & Jewellery', 'Beauty', 'Mobility']
def inline(items):
    return '\n        '.join(f'<span>{esc(n)}</span>' for n in items)

def clients_html():
    out = []
    for n, h, img in CLIENTS:
        if h:
            out.append(f'<a href="{h}" data-peek="{img}">{esc(n)}</a>')
        else:
            out.append(f'<span>{esc(n)}</span>')
    return '\n        '.join(out)

# ---------- Index ----------
STACK_IMGS = {
    'product': ['images/projects/product/armacover-app.png', 'images/projects/product/wsp-dashboard.png', 'images/projects/product/asset-layout-editor.png'],
    'web': ['images/projects/atelier3/cover.jpg', 'images/projects/esens/cover.jpg', 'images/projects/cybertrends/cover.jpg'],
    'brand': ['images/projects/armacover-logo/symbol.png', 'images/projects/cybertrends-logo/wordmark.png', 'images/projects/cybertrends-logo/symbol.png'],
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
      <p>I’m a product &amp; visual designer based in Prague. I design digital products, websites and brand visuals for tech companies, startups and cultural organisations, from the structure of a complex tool to the way a brand looks and moves.</p>
      <p>I like understanding the whole problem, not just one screen. My work spans <a class="u" href="work-product.html">data and security products</a>, healthcare software, <a class="u" href="work-web.html">websites</a> and festivals like <a class="u" href="project-kviff.html">KVIFF</a> and <a class="u" href="project-prague-pride.html">Prague Pride</a>.</p>
      <p>I’m open to new collaborations. Reach me via <a class="u" href="mailto:{EMAIL}">email</a>, find me on <a class="u" href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a> or download my <a class="u" href="{CV}" target="_blank" rel="noopener">CV</a>.</p>
    </div>

    <section>
      <div class="sel-head"><h2 class="medium">Selected work</h2><a href="work.html">View all →</a></div>
      <div class="stacks">
{stacks}
      </div>
    </section>

    <section class="lists" aria-label="Clients and expertise">
      <div class="list-group">
        <h2 class="block-title">Clients</h2>
        <p class="clients">
        {clients_html()}
        </p>
      </div>
      <div class="list-group">
        <h2 class="block-title">Disciplines</h2>
        <p class="clients">{inline(DISCIPLINES)}</p>
      </div>
      <div class="list-group">
        <h2 class="block-title">Industries</h2>
        <p class="clients">{inline(INDUSTRIES)}</p>
      </div>
      <div class="list-group">
        <h2 class="block-title">Elsewhere</h2>
        {links_row()}
      </div>
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
      <a class="back" href="index.html">← Home</a>
      <h1 class="h1">About me</h1>
    </div>

    <div class="bio">
      <p>I’m Eliška, a product &amp; visual designer based in Prague. I help teams turn complex products into clear, calm interfaces, and give brands a visual language that holds together across web, print, social and motion.</p>
      <p>I work with tech companies and startups, agencies and studios, and cultural organisations. Usually on product design, websites and visual identity, often all three for the same client.</p>
      <p>I started in graphic design, doing brands and websites, and spent a lot of those years around culture, working with festivals like <a class="u" href="project-kviff.html">KVIFF</a> and <a class="u" href="project-prague-pride.html">Prague Pride</a>. Later I moved into UX, studied it during my master’s, and ended up in product design, where I get to understand the whole problem and help decide where a product should go.</p>
      <p>I build my own AI skills and a context system in <a class="u" href="https://obsidian.md" target="_blank" rel="noopener">Obsidian</a>, so the tools work the way I do and I can prototype in real code.</p>
      <p>I’m open to new collaborations. <a class="u" href="mailto:{EMAIL}">Write me</a> and tell me what you’re working on.</p>
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
    client = esc(p.get('client') or CLIENT.get(href, ''))
    desc = esc(first_sentence(p['lead']))
    img = ''
    if href not in COMPACT:
        if cat == 'product':
            img = f'<a class="entry-img entry-img--shot" href="{href}" tabindex="-1" aria-hidden="true"><img src="{p["cover"]}" alt="" loading="lazy" /></a>'
        elif p.get('cover_video'):
            img = f'<a class="entry-img" style="--fill: {edge_fill(p["cover"])}" href="{href}" tabindex="-1" aria-hidden="true"><video src="{p["cover_video"]}" poster="{p["cover"]}" autoplay muted loop playsinline preload="metadata"></video></a>'
        else:
            img = f'<a class="entry-img{" is-contain" if p.get("fit") == "contain" else ""}" style="--fill: {edge_fill(p["cover"])}" href="{href}" tabindex="-1" aria-hidden="true"><img src="{p["cover"]}" alt="" loading="lazy" /></a>'
    btn = '' if cat == 'product' else f'<a class="btn-details" href="{href}" aria-label="{title} details">Details {icon("arrow-up-right", 20)}</a>'
    return f'''      <article class="entry">
        {img}
        <div class="entry-title"><a href="{href}">{title}</a><span class="client">{client}</span><span class="num">{n:02d}</span></div>
        <p class="entry-desc">{desc}</p>
        {btn}
      </article>'''

def product_entry(e, n):
    title, client, img, desc = e
    return f'''      <article class="entry" id="{img}">
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
      <a class="back" href="work.html">← Work</a>
      <p class="crumb"><span>Work</span>{icon("chev", 14)}<b>{label}</b></p>
      <h1 class="h1">{label}</h1>
      <p class="intro">{intro}</p>
    </div>
    <div class="entries">
{body}
    </div>
  </main>
''' + nav('work', key))

# ---------- Work overview: every project as a photo tile ----------
def tile(href, img, title, cat_label, video=None, contain=False):
    fill = f' style="--fill: {edge_fill(img)}"' if contain else ''
    media_html = (f'<video src="{video}" poster="{img}" autoplay muted loop playsinline preload="metadata" aria-hidden="true"></video>' if video
                  else f'<img src="{img}" alt="" loading="lazy" />')
    return f'''      <a class="tile{' is-contain' if contain else ''}" href="{href}"{fill}>
        {media_html}
        <span class="tile-label"><b>{esc(title)}</b><span>{cat_label}</span></span>
      </a>'''
groups = {k: [] for k, *_ in CATS}
for t, c, img, d in PRODUCT:
    groups['product'].append(tile(f'work-product.html#{img}', f'images/projects/product/{img}.png', t, 'Product design'))
for p in P:
    k = primary(p)
    groups[k].append(tile(p['href'], p['cover'], p['title'], CAT[k][1], p.get('cover_video'), p.get('fit') == 'contain'))
# interleave categories so the wall mixes products, websites, brand and visual work
tiles, order = [], ['web', 'product', 'motion', 'brand']
while any(groups[k] for k in order):
    for k in order:
        if groups[k]: tiles.append(groups[k].pop(0))
write('work.html', head('Work — Eliška Doležalová', 'All projects by Eliška Doležalová: product design, web design, branding, visual & motion.', 'work.html') + f'''
  <main class="overview">
    <div class="page-head">
      <a class="back" href="index.html">← Home</a>
      <h1 class="h1">Work</h1>
      <p class="intro">Everything in one place: product design, websites, branding and visual &amp; motion work.</p>
    </div>
    <div class="tiles">
{chr(10).join(tiles)}
    </div>
  </main>
''' + nav('work', 'all'))

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
    # Gallery layout: pictures in justified rows (each item's width follows its aspect ratio,
    # so every picture in a row has the same height and the row fills the width);
    # full-page website previews in their own rows of equal scroll windows.
    def ratio(m):
        try:
            w, h = Image.open(ROOT / (m['poster'] if m['type'] == 'video' else m['src'])).size
            return round(w / h, 4)
        except Exception:
            return 1.5
    def fig(m):
        r = ratio(m)
        if m['type'] == 'video':
            return f'        <div class="g-img g-vid" style="--r: {r}">{media(m)}</div>'
        return f'        <button class="g-img" type="button" style="--r: {r}" data-full="{m["src"]}" data-alt="{esc(m["alt"])}">{media(m, LAZY)}</button>'
    def screen(m):
        return f'''        <div class="screen">
          <div class="screen-scroll" tabindex="0" aria-label="{esc(m["alt"])}, scrollable"><img src="{m["src"]}" alt="{esc(m["alt"])}" loading="lazy" /></div>
          <p class="hint"><button type="button" data-full="{m["src"]}" data-alt="{esc(m["alt"])}">View full page ↗</button></p>
        </div>'''
    def chunk(items):
        # rows of two; an odd leftover joins the last row (three) unless it is alone
        n = len(items)
        if n <= 2: return [items] if items else []
        rows = [items[i:i + 2] for i in range(0, n - 3 if n % 2 else n, 2)]
        if n % 2: rows.append(items[n - 3:])
        return rows
    pics = [m for m in rest if m['type'] != 'page']
    pages = [m for m in rest if m['type'] == 'page']
    # Greedy justified rows: pictures of similar shape (within 3x aspect) share a row while it stays
    # at least 300px tall at 1120px wide; only very tall rows (over 1000px, i.e. portraits) are narrowed and centred, so everything else lines up with the full content width.
    W, GAP, MIN_H, MAX_H = 1120, 24, 300, 1000
    def row_h(r): return (W - GAP * (len(r) - 1)) / sum(ratio(x) for x in r)
    rows, cur = [], []
    for m in pics:
        trial = cur + [m]
        rs = [ratio(x) for x in trial]
        if cur and (row_h(trial) < MIN_H or max(rs) / min(rs) > 3):
            rows.append(cur); cur = [m]
        else:
            cur = trial
    if cur: rows.append(cur)
    out = []
    for r in rows:
        row = '\n'.join(fig(m) for m in r)
        if row_h(r) > MAX_H:
            # very tall pictures sit centred on a full-width panel in their own edge colour, so the edges still line up
            fill = edge_fill(r[0]['poster'] if r[0]['type'] == 'video' else r[0]['src'])
            inner = round(MAX_H * sum(ratio(x) for x in r) + GAP * (len(r) - 1))
            out.append(f'      <div class="g-panel" style="--fill: {fill}">\n      <div class="g-row" style="max-width: {inner}px">\n{row}\n      </div>\n      </div>')
        else:
            out.append(f'      <div class="g-row">\n{row}\n      </div>')
    rows = out
    for r in chunk(pages):
        rows.append('      <div class="g-row g-row--screens">\n' + '\n'.join(screen(m) for m in r) + '\n      </div>')
    gallery = '\n    <section class="gallery">\n' + '\n'.join(rows) + '\n    </section>' if rows else ''
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
      <div class="cover{" is-contain" if p.get("fit") == "contain" else ""}" style="--fill: {edge_fill(cover["poster"] if cover["type"] == "video" else cover["src"])}">{media(cover)}</div>
    </section>
{gallery}
    <section class="outro" aria-label="Contact">
      <p class="sentence">
        <span>Like what you see?</span>
        <a class="cta cta--dark" href="mailto:{EMAIL}?subject=Project%20inquiry" data-tip="{EMAIL}"><img class="avatar" src="{AVATAR}" alt="" width="40" height="40" />Write me</a>
        <a class="cta cta--icon" href="tel:{PHONE.replace(' ', '')}" data-tip="{PHONE}">{icon("phone-lg", 28)}call me</a>
        <span>or</span>
        <a class="cta" href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn ↗</a>
      </p>
    </section>
  </main>
''' + nav('work', cat))

# ---------- Search index ----------
TEL = 'tel:' + PHONE.replace(' ', '')
idx = [
    {'t': 'Home', 's': 'Page', 'h': 'index.html', 'k': 'index start intro uvod domu'},
    {'t': 'About me', 's': 'Page', 'h': 'about.html', 'k': 'about bio experience education cv resume work history skills o mne zkusenosti vzdelani'},
    {'t': 'Contact', 's': 'Page', 'h': 'contact.html', 'k': 'contact email mail phone number call telephone tel linkedin cv kontakt telefon cislo'},
    {'t': 'Call ' + PHONE, 's': 'Phone', 'h': TEL, 'k': 'phone number call telephone mobile tel contact zavolat telefon cislo'},
    {'t': 'Write an email', 's': EMAIL, 'h': 'mailto:' + EMAIL, 'k': 'email mail write message contact napsat'},
    {'t': 'Copy email address', 's': EMAIL, 'a': 'copy', 'k': 'email mail copy address clipboard kopirovat'},
    {'t': 'LinkedIn', 's': 'Profile ↗', 'h': LINKEDIN, 'k': 'linkedin profile social contact'},
    {'t': 'Download CV', 's': 'PDF', 'h': CV, 'k': 'cv resume curriculum pdf download zivotopis'},
    {'t': 'Switch light / dark mode', 's': 'Appearance', 'a': 'theme', 'k': 'dark light mode theme night appearance tmavy svetly rezim'},
]
idx += [{'t': 'All work', 's': f'{TOTAL} projects', 'h': 'work.html', 'k': 'work overview projects portfolio all'}]
idx += [{'t': l, 's': f'{len(in_cat(k))} projects', 'h': h, 'k': 'work category ' + intro} for k, l, h, intro in CATS]
idx += [{'t': p['title'], 's': CAT[primary(p)][1], 'h': p['href'],
         'k': ' '.join([p.get('client') or CLIENT.get(p['href'], ''), ' '.join(CAT[t][1] for t in p['tags']), ' '.join(p['outputs']), strip(p['lead'])])} for p in P]
idx += [{'t': t, 's': 'Product design · ' + c, 'h': 'work-product.html', 'k': d} for t, c, _, d in PRODUCT]
write('site-data.js', 'window.SITE_INDEX = ' + json.dumps(idx, ensure_ascii=False) + ';\n')
