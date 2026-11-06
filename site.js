// Redesign 2026: mobile sheet, command palette, copy email, Prague clock, lightbox
(function () {
  var root = document.documentElement;

  // ---- Mobile context pill → sheet ----
  var ctx = document.querySelector('.ctx');
  var scrim = document.querySelector('.scrim');
  function sheet(open) {
    root.classList.toggle('sheet-open', open);
    if (ctx) ctx.setAttribute('aria-expanded', open);
  }
  if (ctx) ctx.addEventListener('click', function () { sheet(!root.classList.contains('sheet-open')); });
  if (scrim) scrim.addEventListener('click', function () { sheet(false); });
  document.querySelectorAll('.sheet .grab, .sheet .s-label, .sheet .s-item').forEach(function (el, i) { el.style.setProperty('--n', i); });

  // ---- Light / dark mode (saved per visitor; follows the system until chosen) ----
  function toggleTheme() {
    var dark = root.dataset.theme !== 'dark';
    if (dark) root.dataset.theme = 'dark'; else delete root.dataset.theme;
    try { localStorage.setItem('theme', dark ? 'dark' : 'light'); } catch (e) {}
  }
  document.querySelectorAll('[data-theme-toggle]').forEach(function (b) { b.addEventListener('click', toggleTheme); });

  // ---- Command palette (⌘K) ----
  var cmdk = document.querySelector('.cmdk');
  var input = cmdk && cmdk.querySelector('input');
  var list = cmdk && cmdk.querySelector('.cmdk-list');
  var items = (window.SITE_INDEX || []);
  var active = 0;
  // Search: every word of the query must appear in the title, subtitle or keywords (accents ignored)
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
  var hits = [];
  function render() {
    var words = norm(input.value).split(/\s+/).filter(Boolean);
    hits = items.filter(function (i) {
      var hay = norm(i.t + ' ' + i.s + ' ' + (i.k || ''));
      // loose stems so 'architecture' finds 'architectural', 'designs' finds 'design'
      return words.every(function (w) { return hay.indexOf(w) > -1 || (w.length > 5 && hay.indexOf(w.slice(0, -2)) > -1); });
    });
    active = Math.min(active, Math.max(0, hits.length - 1));
    list.innerHTML = hits.map(function (i, n) {
      return '<a href="' + (i.h || '#') + '" data-n="' + n + '"' + (n === active ? ' class="is-active"' : '') + '><span>' + i.t + '</span><small>' + i.s + '</small></a>';
    }).join('') || '<p class="cmdk-empty">Nothing found. Try “phone”, “email”, “CV” or a project name.</p>';
  }
  function run(i, e) {
    if (!i) return;
    if (i.a) {
      if (e) e.preventDefault();
      if (i.a === 'copy' && navigator.clipboard) navigator.clipboard.writeText(i.s).then(function () { list.innerHTML = '<p class="cmdk-empty">Copied ' + i.s + '</p>'; setTimeout(function () { palette(false); }, 900); });
      if (i.a === 'theme') { toggleTheme(); palette(false); }
      return;
    }
    if (!e) location.href = i.h;
  }
  function palette(open) {
    if (!cmdk) return;
    cmdk.classList.toggle('is-open', open);
    if (open) { input.value = ''; active = 0; render(); input.focus(); }
  }
  document.querySelectorAll('[data-cmdk]').forEach(function (b) { b.addEventListener('click', function () { sheet(false); palette(true); }); });
  if (cmdk) {
    cmdk.addEventListener('click', function (e) { if (e.target === cmdk) palette(false); });
    input.addEventListener('input', function () { active = 0; render(); });
    list.addEventListener('click', function (e) { var a = e.target.closest('a[data-n]'); if (a) run(hits[+a.dataset.n], e); });
    input.addEventListener('keydown', function (e) {
      var links = list.querySelectorAll('a');
      if (e.key === 'ArrowDown') { active = Math.min(active + 1, links.length - 1); render(); e.preventDefault(); }
      if (e.key === 'ArrowUp') { active = Math.max(active - 1, 0); render(); e.preventDefault(); }
      if (e.key === 'Enter') { e.preventDefault(); run(hits[active]); }
    });
  }
  document.addEventListener('keydown', function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); palette(!(cmdk && cmdk.classList.contains('is-open'))); }
    if (e.key === 'Escape') { palette(false); sheet(false); lightbox(null); }
  });

  // ---- Copy email (contact card) ----
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      if (!navigator.clipboard) return;
      navigator.clipboard.writeText(b.dataset.copy).then(function () {
        b.classList.add('is-copied');
        setTimeout(function () { b.classList.remove('is-copied'); }, 1600);
      }, function () {});
    });
  });

  // ---- Prague clock ----
  var clock = document.querySelector('[data-clock]');
  function tick() {
    try { clock.textContent = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Prague' }).format(new Date()); } catch (e) {}
  }
  if (clock) { tick(); setInterval(tick, 15000); }

  // ---- Lightbox for gallery images and full pages ----
  var lb = document.querySelector('.lb');
  function lightbox(src, alt) {
    if (!lb) return;
    if (!src) { lb.classList.remove('is-open'); root.style.overflow = ''; return; }
    lb.querySelector('img').src = src;
    lb.querySelector('img').alt = alt || '';
    lb.classList.add('is-open');
    lb.scrollTop = 0;
    root.style.overflow = 'hidden';
    lb.querySelector('.lb-close').focus();
  }
  document.querySelectorAll('[data-full]').forEach(function (el) {
    el.addEventListener('click', function () { lightbox(el.dataset.full, el.dataset.alt); });
  });
  if (lb) {
    lb.querySelector('.lb-close').addEventListener('click', function () { lightbox(null); });
    lb.addEventListener('click', function (e) { if (e.target === lb) lightbox(null); });
  }
})();

// ---- Full-page previews scroll themselves (same rhythm as the live site):
// 1s on the top, down at 90px/s, 3s on the bottom, back up at the same speed.
// Runs only while on screen; hovering or touching hands control to the visitor.
(function () {
  var screens = document.querySelectorAll('.screen-scroll');
  if (!screens.length || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var SPEED = 90, TOP = 1000, BOTTOM = 3000;
  screens.forEach(function (el) {
    var pos = 0, dir = 1, holdUntil = 0, visible = false, held = false, last = 0, raf = 0, touchTimer = 0;
    function frame(now) {
      raf = 0;
      if (!visible || held) return;
      var dt = last ? Math.min(0.1, (now - last) / 1000) : 0;
      last = now;
      var max = el.scrollHeight - el.clientHeight;
      if (Math.abs(el.scrollTop - pos) > 2) pos = el.scrollTop;   // visitor scrolled: continue from there
      if (max > 0 && now >= holdUntil) {
        pos += dir * SPEED * dt;
        if (pos >= max) { pos = max; dir = -1; holdUntil = now + BOTTOM; }
        else if (pos <= 0) { pos = 0; dir = 1; holdUntil = now + TOP; }
        el.scrollTop = pos;
      }
      raf = requestAnimationFrame(frame);
    }
    function run() { if (!raf && visible && !held) { last = 0; raf = requestAnimationFrame(frame); } }
    function hold(on) { held = on; if (!on) run(); }
    holdUntil = performance.now() + TOP;
    var box = el.closest('.screen') || el;
    box.addEventListener('mouseenter', function () { hold(true); });
    box.addEventListener('mouseleave', function () { hold(false); });
    el.addEventListener('touchstart', function () {
      hold(true); clearTimeout(touchTimer);
      touchTimer = setTimeout(function () { hold(false); }, 4000);
    }, { passive: true });
    el.addEventListener('focus', function () { hold(true); });
    el.addEventListener('blur', function () { hold(false); });
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting; run();
    }, { threshold: 0.5 }).observe(el);
  });
})();

// ---- Entrance motion: stagger what's on screen at load, reveal the rest on scroll ----
(function () {
  if (!document.documentElement.classList.contains('js')) return;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var sel = [
    '.col > *:not(.entries)', '.entries > .entry', '.overview .page-head', '.tiles > .tile', '.contact-wrap .card',
    '.hero-top', '.hero-text > .lead', '.hero-text > .more', '.facts', '.cover',
    '.gallery > *', '.outro'
  ].join(',');
  var els = Array.prototype.slice.call(document.querySelectorAll(sel));
  // images fade in when decoded (skip ones already painted from cache)
  document.querySelectorAll('main img').forEach(function (img) {
    if (reduce || (img.complete && img.naturalWidth)) return;
    img.classList.add('fade');
    var done = function () { img.classList.add('is-loaded'); };
    img.addEventListener('load', done); img.addEventListener('error', done);
  });
  if (reduce || !('IntersectionObserver' in window)) return;
  var vh = innerHeight, n = 0;
  els.forEach(function (el) {
    el.classList.add('enter');
    var top = el.getBoundingClientRect().top;
    if (top < vh) el.style.setProperty('--d', Math.min(n++ * 70, 560) + 'ms');
  });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in'); io.unobserve(e.target);
    });
  }, { rootMargin: '0px 0px -8% 0px' });
  requestAnimationFrame(function () { els.forEach(function (el) { io.observe(el); }); });
})();

// ---- Client list: hovering a name with work on the site shows its image next to the cursor ----
(function () {
  var links = document.querySelectorAll('[data-peek]');
  if (!links.length || !matchMedia('(hover: hover)').matches) return;
  var peek = document.createElement('div'); peek.className = 'peek'; peek.setAttribute('aria-hidden', 'true');
  var img = document.createElement('img'); img.alt = ''; peek.appendChild(img); document.body.appendChild(peek);
  links.forEach(function (a) { var pre = new Image(); pre.src = a.dataset.peek; });
  function move(e) {
    var w = peek.offsetWidth, h = peek.offsetHeight;
    var x = Math.min(e.clientX + 24, innerWidth - w - 16), y = e.clientY - h - 16;
    if (y < 16) y = e.clientY + 24;
    peek.style.setProperty('--x', x + 'px'); peek.style.setProperty('--y', y + 'px');
  }
  links.forEach(function (a) {
    a.addEventListener('mouseenter', function (e) { img.src = a.dataset.peek; move(e); peek.classList.add('is-on'); });
    a.addEventListener('mousemove', move);
    a.addEventListener('mouseleave', function () { peek.classList.remove('is-on'); });
  });
})();

// ---- Dock motion: the bar keeps its shape across page loads ----
// Pages are static, so the Work group arrives already open or closed. Before a dock link navigates we
// save the Work segment's width and the category chip's position; the next page animates from them.
(function () {
  var dock = document.querySelector('.dock');
  if (!dock || !dock.animate) return;
  var KEY = 'dock', EASE = 'cubic-bezier(0.22, 1, 0.36, 1)';
  function seg() { return dock.querySelector('.d-work') || dock.querySelector('.d-item[href="work.html"]'); }
  function box(el, ref) { var r = el.getBoundingClientRect(); return { x: r.left - ref.left, w: r.width }; }

  dock.addEventListener('click', function (e) {
    if (!e.target.closest('a[href]') || !dock.offsetWidth) return;
    var w = seg(), r = w.getBoundingClientRect(), chip = w.querySelector('.d-sub.is-on');
    var s = { w: r.width, open: w.classList.contains('d-work'), t: Date.now() };
    if (chip) s.chip = box(chip, r);
    try { sessionStorage.setItem(KEY, JSON.stringify(s)); } catch (err) {}
  });

  var s;
  try { s = JSON.parse(sessionStorage.getItem(KEY)); sessionStorage.removeItem(KEY); } catch (err) {}
  if (!s || Date.now() - s.t > 10000 || !dock.offsetWidth || matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var w = seg(), open = w.classList.contains('d-work'), cs = getComputedStyle(w);
  var css = getComputedStyle(document.documentElement);
  var yellow = css.getPropertyValue('--bg').trim(), ink = css.getPropertyValue('--ink').trim();
  var label = open ? w.querySelector('.d-item') : w;

  if (open && !s.open) {
    // Expand: the yellow segment grows out of the Work label, the categories follow in a short stagger
    var dim = getComputedStyle(dock.querySelector('.d-item:not(.is-on)') || label).color;
    w.style.overflow = 'hidden';
    w.animate([{ width: s.w + 'px', backgroundColor: 'transparent' }, { width: cs.width, backgroundColor: cs.backgroundColor }],
      { duration: 800, easing: EASE }).onfinish = function () { w.style.overflow = ''; };
    label.animate([{ color: dim }, { color: getComputedStyle(label).color }], { duration: 500, easing: EASE });
    w.querySelectorAll('.sep, .d-sub').forEach(function (el, i) {
      el.animate([{ opacity: 0, transform: 'translateX(-8px)' }, { opacity: 1, transform: 'none' }],
        { duration: 600, delay: 150 + i * 60, easing: EASE, fill: 'backwards' });
    });
  } else if (!open && s.open) {
    // Collapse: the segment shrinks back into the Work label and its yellow fades out
    w.animate([{ width: s.w + 'px', backgroundColor: yellow, color: ink }, { width: cs.width, backgroundColor: cs.backgroundColor, color: cs.color }],
      { duration: 700, easing: EASE });
  } else if (open && s.open) {
    // Category switch: the light chip slides from the old category to the new one (or into the Work label)
    var r = w.getBoundingClientRect(), chip = w.querySelector('.d-sub.is-on');
    var from = s.chip || box(label, r), to = chip ? box(chip, r) : box(label, r);
    if (from.x === to.x && from.w === to.w) return;
    var g = document.createElement('span');
    g.className = 'd-ghost';
    w.appendChild(g);
    w.classList.add('is-sliding');
    g.animate([{ transform: 'translateX(' + from.x + 'px)', width: from.w + 'px', opacity: s.chip ? 1 : 0 },
               { transform: 'translateX(' + to.x + 'px)', width: to.w + 'px', opacity: chip ? 1 : 0 }],
      { duration: 700, easing: EASE, fill: 'both' }).onfinish = function () { w.classList.remove('is-sliding'); g.remove(); };
  }
})();

