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
