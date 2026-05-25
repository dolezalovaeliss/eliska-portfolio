/* Scroll-driven section background + word-by-word headline reveal.
   Shared across all pages — kept in sync via a single source. */
(function () {
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ===== 1) Scroll-driven body background — any [data-bg] section =====
  // Currently used by #services and #contact (the footer). Uses a
  // viewport-overlap check with hysteresis so accordion <details> expand
  // inside services does not flip the bg back to light.
  var darkSections = Array.prototype.slice.call(
    document.querySelectorAll('section[data-bg]')
  );
  if (darkSections.length) {
    var isActive = false;

    function setActive(active, bgColor) {
      if (active === isActive) return;
      isActive = active;
      document.body.style.backgroundColor = active ? bgColor : '';
      document.body.classList.toggle('fg-light', active);
      document.body.classList.toggle('fg-dark', !active);
      // Nudge other scroll-aware systems (scroll-words colors etc.)
      // to re-read the new body state on the same frame.
      window.dispatchEvent(new Event('scroll'));
    }
    // Initial paint
    document.body.classList.add('fg-dark');

    var ticking2 = false;
    function checkDarkSection() {
      if (ticking2) return;
      ticking2 = true;
      requestAnimationFrame(function () {
        var vh = window.innerHeight;
        var bestFraction = 0;
        var bestSection = null;
        for (var i = 0; i < darkSections.length; i++) {
          var rect = darkSections[i].getBoundingClientRect();
          var visibleTop    = Math.max(rect.top, 0);
          var visibleBottom = Math.min(rect.bottom, vh);
          var visible       = Math.max(0, visibleBottom - visibleTop);
          var fraction      = visible / vh;
          if (fraction > bestFraction) {
            bestFraction = fraction;
            bestSection = darkSections[i];
          }
        }
        // Hysteresis: activate at 65% fill, deactivate at 50%.
        var shouldBe = isActive ? (bestFraction > 0.50) : (bestFraction > 0.65);
        var bg = bestSection ? bestSection.getAttribute('data-bg') : '';
        setActive(shouldBe, bg);
        ticking2 = false;
      });
    }
    window.addEventListener('scroll', checkDarkSection, { passive: true });
    window.addEventListener('resize', checkDarkSection, { passive: true });
    checkDarkSection();
  }

  // ===== 2) Word-by-word slide-up for headlines =====
  // Targets every <h1>/<h2> inside a <section>. Uses a MutationObserver to
  // re-split when other systems (i18n, CMS fetch) overwrite the text.
  function splitWords(el) {
    var nodes = [];
    (function walk(n) {
      for (var i = 0; i < n.childNodes.length; i++) {
        var c = n.childNodes[i];
        if (c.nodeType === 3 && c.nodeValue && /\S/.test(c.nodeValue)) {
          nodes.push(c);
        } else if (c.nodeType === 1 &&
                   !c.classList.contains('word') &&
                   !c.classList.contains('word-i') &&
                   !c.classList.contains('scroll-words') &&
                   c.tagName !== 'BR') {
          walk(c);
        }
      }
    })(el);

    if (!nodes.length) return false;

    var wordIdx = 0;
    nodes.forEach(function (textNode) {
      var parts = textNode.nodeValue.split(/(\s+)/);
      var frag = document.createDocumentFragment();
      parts.forEach(function (p) {
        if (!p) return;
        if (/^\s+$/.test(p)) {
          frag.appendChild(document.createTextNode(p));
        } else {
          var outer = document.createElement('span');
          outer.className = 'word';
          var inner = document.createElement('span');
          inner.className = 'word-i';
          inner.textContent = p;
          inner.style.setProperty('--word-d', (wordIdx * 70) + 'ms');
          outer.appendChild(inner);
          frag.appendChild(outer);
          wordIdx++;
        }
      });
      textNode.parentNode.replaceChild(frag, textNode);
    });
    return true;
  }

  function markAnimContainer(h) {
    // The element bearing [data-anim] gets .word-anim so CSS bypasses its
    // own fade-up and reveals the words instead. h might be the data-anim
    // element itself, or it might be inside one.
    var c = h.hasAttribute('data-anim') ? h : h.closest('[data-anim]');
    if (c) c.classList.add('word-anim');
  }

  function processHeading(h) {
    // Skip if already correctly split (still contains .word elements)
    if (h.querySelector('.word')) return;
    markAnimContainer(h);
    splitWords(h);
  }

  function initWordReveal() {
    if (reduced) return;
    var headings = document.querySelectorAll('section h1, section h2');
    headings.forEach(processHeading);

    // Watch each heading for text changes (CMS fetch / i18n switch wipes
    // children) and re-split when they get overwritten.
    if ('MutationObserver' in window) {
      headings.forEach(function (h) {
        var mo = new MutationObserver(function (muts) {
          // If our spans were removed by an outside writer, re-split.
          if (!h.querySelector('.word')) {
            processHeading(h);
          }
        });
        mo.observe(h, { childList: true, subtree: true, characterData: true });
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWordReveal);
  } else {
    initWordReveal();
  }

  // ===== Contact link: explicit instant scroll =====
  // scroll-behavior: smooth can be interrupted in in-app browsers
  // (Instagram, Facebook WebView) and on iOS Safari when the toolbar
  // shows/hides mid-scroll, leaving the user stranded mid-page. Force
  // an instant jump straight to #contact (now on the contact <ul>).
  document.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest('a[href="#contact"]');
    if (!link) return;
    var target = document.getElementById('contact');
    if (!target) return;
    e.preventDefault();
    // Close mobile drawer if open so body scroll lock is released first
    var ham = document.querySelector('.nav-hamburger');
    if (ham && ham.getAttribute('aria-expanded') === 'true') ham.click();
    requestAnimationFrame(function () {
      target.scrollIntoView({ behavior: 'auto', block: 'start' });
      // Some in-app browsers ignore scrollIntoView; double-tap with scrollTo
      var rect = target.getBoundingClientRect();
      var marginTop = parseFloat(getComputedStyle(target).scrollMarginTop) || 0;
      window.scrollTo({
        top: window.scrollY + rect.top - marginTop,
        behavior: 'auto',
      });
    });
  });
})();
