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

  // ---- Homepage: highlight the sticky outline while scrolling ----
  var homeIndex = document.querySelector('.home-index');
  if (homeIndex) {
    var hLinks = homeIndex.querySelectorAll('a');
    var hMap = {};
    hLinks.forEach(function (a) { hMap[a.getAttribute('href').slice(1)] = a; });
    var hSpy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          hLinks.forEach(function (a) { a.classList.remove('active'); });
          var a = hMap[entry.target.id];
          if (a) a.classList.add('active');
        }
      });
    }, { rootMargin: '-45% 0px -45% 0px', threshold: 0 });
    document.querySelectorAll('.home-main .section[id]').forEach(function (s) { hSpy.observe(s); });
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
