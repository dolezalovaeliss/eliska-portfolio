(function () {
  var els = document.querySelectorAll('.reveal');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Items revealed in sequence inside a [data-stagger] section.
  var STAGGER_SEL = '.label, .trow, .about-cols p, .svc-head, .svc-tags';

  if (reduce || !('IntersectionObserver' in window)) {
    els.forEach(function (el) { el.classList.add('is-visible'); });
    document.querySelectorAll('[data-stagger] ' + STAGGER_SEL.split(', ').join(', [data-stagger] '))
      .forEach(function (it) { it.classList.add('anim-in'); });
    return;
  }

  function show(el) {
    var delay = el.getAttribute('data-delay');
    if (delay) el.style.transitionDelay = delay + 'ms';
    el.classList.add('is-visible');
    // Stagger the children of a [data-stagger] section, one after another.
    if (el.hasAttribute('data-stagger')) {
      var items = el.querySelectorAll(STAGGER_SEL);
      for (var i = 0; i < items.length; i++) {
        items[i].style.transitionDelay = (i * 95) + 'ms';
        items[i].classList.add('anim-in');
      }
    }
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        show(entry.target);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0, rootMargin: '0px 0px -6% 0px' });

  // Reveal anything already in (or near) the viewport immediately; observe the rest.
  els.forEach(function (el) {
    var r = el.getBoundingClientRect();
    if (r.top < window.innerHeight * 1.1) show(el);
    else io.observe(el);
  });

  // Safety net: never leave content hidden if something goes wrong.
  window.addEventListener('load', function () {
    document.querySelectorAll('.reveal:not(.is-visible)').forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight * 1.1) show(el);
    });
  });

  // Above-the-fold content reveals immediately.
  window.addEventListener('load', function () {
    document.querySelectorAll('[data-reveal-now]').forEach(function (el) {
      el.classList.add('is-visible');
    });
  });

  // ---- Case study: highlight the section index while scrolling ----
  var index = document.querySelector('.case-index');
  if (index) {
    var links = index.querySelectorAll('a');
    var map = {};
    links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          links.forEach(function (a) { a.classList.remove('active'); });
          var a = map[entry.target.id];
          if (a) a.classList.add('active');
        }
      });
    }, { rootMargin: '-25% 0px -65% 0px', threshold: 0 });
    document.querySelectorAll('.case-section[id]').forEach(function (s) { spy.observe(s); });
  }


  // ---- Sticky header: hide on scroll down, reveal on scroll up ----
  var header = document.getElementById('site-header');
  if (header) {
    var lastY = window.scrollY;
    var ticking = false;
    var update = function () {
      var y = window.scrollY;
      header.classList.toggle('scrolled', y > 40); // mobile: name hides, hamburger → yellow circle
      if (y < 80) {
        header.classList.remove('is-hidden');      // always visible near the top
      } else if (y > lastY + 4) {
        header.classList.add('is-hidden');         // scrolling down
      } else if (y < lastY - 4) {
        header.classList.remove('is-hidden');      // scrolling up
      }
      lastY = y;
      ticking = false;
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
  }

  // ---- Mobile menu: hamburger toggle ----
  var toggle = document.getElementById('nav-toggle');
  var nav = toggle && toggle.closest('.nav');
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle('open', open);
      document.body.classList.toggle('nav-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    toggle.addEventListener('click', function () {
      setOpen(!nav.classList.contains('open'));
    });
    // close after tapping a link
    nav.querySelectorAll('.nav-links a').forEach(function (a) {
      a.addEventListener('click', function () { setOpen(false); });
    });
  }

  // ---- Hero entrance animation (home): photo up, title down (split apart) ----
  var heroContent = document.getElementById('hero-content');
  if (heroContent) {
    var heroPhoto = heroContent.querySelector('.hero-photo-anim');
    var heroTitle = heroContent.querySelector('.hero-title');
    var runHero = function () {
      if (heroPhoto) heroPhoto.classList.add('is-in');
      if (heroTitle) heroTitle.classList.add('is-in');
    };
    // Let the hidden initial state paint first, then animate apart
    requestAnimationFrame(function () { requestAnimationFrame(runHero); });
  }

  // ---- CV fullscreen lightbox ----
  var cvOverlay = document.getElementById('cv-overlay');
  if (cvOverlay) {
    var cvLink = document.getElementById('cv-link');
    var cvClose = document.getElementById('cv-close');
    var openCV = function (e) {
      if (e) e.preventDefault();
      cvOverlay.classList.add('open');
      document.body.classList.add('cv-open');
    };
    var closeCV = function () {
      cvOverlay.classList.remove('open');
      document.body.classList.remove('cv-open');
    };
    if (cvLink) cvLink.addEventListener('click', openCV);
    if (cvClose) cvClose.addEventListener('click', closeCV);
    cvOverlay.addEventListener('click', function (e) {
      if (e.target === cvOverlay) closeCV();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && cvOverlay.classList.contains('open')) closeCV();
    });
  }
})();

// ---- Work page: discipline filter chips (synced with #hash) ----
(function () {
  var bar = document.querySelector('.work-filters');
  if (!bar) return;
  var chips = bar.querySelectorAll('.chip');
  var tiles = document.querySelectorAll('.work-grid .work-tile');
  var empty = document.querySelector('.work-empty');
  chips.forEach(function (c) {
    if (c.querySelector('sup') && c.querySelector('sup').textContent === '0') c.classList.add('is-empty');
  });
  function apply(f, push) {
    if (!bar.querySelector('[data-filter="' + f + '"]')) f = 'all';
    chips.forEach(function (c) {
      var on = c.getAttribute('data-filter') === f;
      c.classList.toggle('is-active', on);
      c.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    var shown = 0;
    tiles.forEach(function (t) {
      var match = f === 'all' || (t.getAttribute('data-tags') || '').split(' ').indexOf(f) > -1;
      t.classList.toggle('is-hidden', !match);
      t.classList.remove('is-filtered-in');
      if (match) { shown++; t.classList.add('is-visible'); void t.offsetWidth; t.classList.add('is-filtered-in'); }
    });
    if (empty) empty.hidden = shown > 0;
    if (push) history.replaceState(null, '', f === 'all' ? location.pathname : '#' + f);
  }
  chips.forEach(function (c) {
    c.addEventListener('click', function () { apply(c.getAttribute('data-filter'), true); });
  });
  if (location.hash) apply(location.hash.slice(1), false);
})();

// ---- Project detail: gallery lightbox (click, arrows, swipe, Esc) ----
(function () {
  var figs = document.querySelectorAll('[data-gallery] .pj-fig');
  if (figs.length < 2) return;
  var srcs = Array.prototype.map.call(figs, function (f) { return f.querySelector('img'); });
  var lb = document.createElement('div');
  lb.className = 'pj-lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.innerHTML = '<span class="pj-lb-count"></span><img alt="" />' +
    '<button class="pj-lb-prev" type="button" aria-label="Previous image">←</button>' +
    '<button class="pj-lb-next" type="button" aria-label="Next image">→</button>' +
    '<button class="pj-lb-close" type="button" aria-label="Close">✕</button>';
  document.body.appendChild(lb);
  var img = lb.querySelector('img'), count = lb.querySelector('.pj-lb-count'), i = 0;
  function show(n) {
    i = (n + srcs.length) % srcs.length;
    img.src = srcs[i].currentSrc || srcs[i].src;
    img.alt = srcs[i].alt;
    // Full-page screenshots: let them scroll instead of shrinking to fit
    var r = srcs[i].naturalHeight / Math.max(1, srcs[i].naturalWidth);
    lb.classList.toggle('is-tall', r > 1.6);
    lb.classList.toggle('is-narrow', r > 1.6 && srcs[i].naturalWidth < 800);
    lb.scrollTop = 0;
    count.textContent = (i + 1) + ' of ' + srcs.length;
  }
  function open(n) { show(n); lb.classList.add('open'); document.body.classList.add('lb-open'); }
  function close() { lb.classList.remove('open'); document.body.classList.remove('lb-open'); }
  figs.forEach(function (f, n) { f.addEventListener('click', function () { open(n); }); });
  lb.querySelector('.pj-lb-prev').addEventListener('click', function () { show(i - 1); });
  lb.querySelector('.pj-lb-next').addEventListener('click', function () { show(i + 1); });
  lb.querySelector('.pj-lb-close').addEventListener('click', close);
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(i - 1);
    if (e.key === 'ArrowRight') show(i + 1);
  });
  var x0 = null;
  lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 40) show(dx < 0 ? i + 1 : i - 1);
    x0 = null;
  });
})();

// ---- Project hero: image slider (scroll-snap + arrows + thumbs + keys) ----
(function () {
  document.querySelectorAll('[data-slider]').forEach(function (slider) {
    var track = slider.querySelector('.pj-track');
    var slides = track.children;
    var head = slider.closest('.pj-head');
    var cur = head && head.querySelector('.pj-cur');
    var thumbs = head ? head.querySelectorAll('.pj-thumb') : [];
    var prev = slider.querySelector('.pj-prev');
    var next = slider.querySelector('.pj-next');
    var i = 0;
    function go(n) { n = Math.max(0, Math.min(slides.length - 1, n)); track.scrollTo({ left: n * track.clientWidth }); }
    function sync() {
      i = Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
      if (cur) cur.textContent = i + 1;
      thumbs.forEach(function (t, k) { t.classList.toggle('is-active', k === i); });
      if (prev) prev.disabled = i === 0;
      if (next) next.disabled = i === slides.length - 1;
    }
    var raf;
    track.addEventListener('scroll', function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(sync); }, { passive: true });
    if (prev) prev.addEventListener('click', function () { go(i - 1); });
    if (next) next.addEventListener('click', function () { go(i + 1); });
    thumbs.forEach(function (t, k) { t.addEventListener('click', function () { go(k); }); });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(i - 1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); go(i + 1); }
    });
    window.addEventListener('resize', function () { track.style.scrollBehavior = 'auto'; go(i); track.style.scrollBehavior = ''; });
    sync();
  });
})();

// ---- Full-page previews: scroll down at one speed, hold 3s at the bottom, scroll back up ----
(function () {
  var figs = document.querySelectorAll('.pj-fig--page');
  if (!figs.length || !Element.prototype.animate) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var SPEED = 90;          // px per second, same for every page
  var START = 1000;        // pause on the top before scrolling (ms)
  var HOLD = 3000;         // stay on the bottom (ms)

  figs.forEach(function (fig) {
    var img = fig.querySelector('img');
    var anim = null, visible = false, hovered = false;
    function sync() {
      if (!anim) return;
      if (visible && !hovered) anim.play(); else anim.pause();
    }
    function build() {
      if (!img.naturalWidth) return;
      var dist = Math.max(0, fig.clientWidth * img.naturalHeight / img.naturalWidth - fig.clientHeight);
      // Page shorter than the window: show it whole, nothing to scroll
      fig.classList.toggle('is-short', dist === 0);
      if (dist === 0) { if (anim) anim.cancel(); anim = null; return; }
      var scroll = Math.max(1500, dist / SPEED * 1000);
      var total = START + scroll + HOLD + scroll;
      var t = function (ms) { return ms / total; };
      if (anim) anim.cancel();
      // Top pause → scroll down → 3s on the bottom → scroll back up at the same speed
      anim = img.animate([
        { objectPosition: '50% 0%', offset: 0 },
        { objectPosition: '50% 0%', offset: t(START), easing: 'ease-in-out' },
        { objectPosition: '50% 100%', offset: t(START + scroll) },
        { objectPosition: '50% 100%', offset: t(START + scroll + HOLD), easing: 'ease-in-out' },
        { objectPosition: '50% 0%', offset: 1 }
      ], { duration: total, iterations: Infinity });
      anim.pause();
      sync();
    }
    if (img.complete) build(); else img.addEventListener('load', build);
    window.addEventListener('resize', build);
    fig.addEventListener('mouseenter', function () { hovered = true; sync(); });
    fig.addEventListener('mouseleave', function () { hovered = false; sync(); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { visible = e.isIntersecting; sync(); });
      }, { threshold: 0.5 }).observe(fig);
    } else { visible = true; sync(); }
  });
})();
