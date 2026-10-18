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

  // ---- Command palette (⌘K) ----
  var cmdk = document.querySelector('.cmdk');
  var input = cmdk && cmdk.querySelector('input');
  var list = cmdk && cmdk.querySelector('.cmdk-list');
  var items = (window.SITE_INDEX || []);
  var active = 0;
  function render() {
    var q = input.value.trim().toLowerCase();
    var hits = items.filter(function (i) { return !q || (i.t + ' ' + i.s).toLowerCase().indexOf(q) > -1; });
    active = Math.min(active, Math.max(0, hits.length - 1));
    list.innerHTML = hits.map(function (i, n) {
      return '<a href="' + i.h + '"' + (n === active ? ' class="is-active"' : '') + '><span>' + i.t + '</span><small>' + i.s + '</small></a>';
    }).join('') || '<a href="#" onclick="return false"><span>Nothing found</span></a>';
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
    input.addEventListener('keydown', function (e) {
      var links = list.querySelectorAll('a');
      if (e.key === 'ArrowDown') { active = Math.min(active + 1, links.length - 1); render(); e.preventDefault(); }
      if (e.key === 'ArrowUp') { active = Math.max(active - 1, 0); render(); e.preventDefault(); }
      if (e.key === 'Enter' && links[active]) { location.href = links[active].getAttribute('href'); }
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
