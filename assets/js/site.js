/* מרפאת בן ארי — site behaviour (no dependencies) */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement;
  var isEn = root.lang === 'en';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- analytics hook: every CTA pushes to dataLayer ------------------- */
  window.dataLayer = window.dataLayer || [];
  doc.addEventListener('click', function (e) {
    var a = e.target.closest('[data-track]');
    if (!a) return;
    window.dataLayer.push({ event: 'cta', type: a.getAttribute('data-track'), page: location.pathname });
  });

  /* ---- live open / closed status (Israel time) ------------------------- */
  function israelNow() {
    try {
      var f = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Jerusalem', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false });
      var p = {}; f.formatToParts(new Date()).forEach(function (x) { p[x.type] = x.value; });
      var days = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
      return { d: days[p.weekday], m: parseInt(p.hour, 10) % 24 * 60 + parseInt(p.minute, 10) };
    } catch (err) { var n = new Date(); return { d: n.getDay(), m: n.getHours() * 60 + n.getMinutes() }; }
  }
  function toMin(s) { var a = s.split(':'); return parseInt(a[0], 10) * 60 + parseInt(a[1], 10); }
  var DAYNAMES = isEn ? ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'] : ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת'];
  function statusText(hours) {
    var now = israelNow(), spans = hours[now.d] || [], i, s;
    for (i = 0; i < spans.length; i++) {
      s = spans[i];
      if (now.m >= toMin(s[0]) && now.m < toMin(s[1])) {
        var left = toMin(s[1]) - now.m;
        var soon = left <= 30 ? (isEn ? ' · closing soon' : ' · נסגר בקרוב') : '';
        return { open: true, text: (isEn ? 'Open now · until ' : 'פתוח עכשיו · עד ') + s[1] + soon };
      }
    }
    for (i = 0; i < spans.length; i++) {
      if (now.m < toMin(spans[i][0])) return { open: false, text: (isEn ? 'Closed now · opens today at ' : 'סגור עכשיו · נפתח היום ב-') + spans[i][0] };
    }
    for (var k = 1; k <= 7; k++) {
      var d = (now.d + k) % 7, sp = hours[d] || [];
      if (sp.length) {
        var when = k === 1 ? (isEn ? 'tomorrow' : 'מחר') : (isEn ? 'on ' + DAYNAMES[d] : 'ביום ' + DAYNAMES[d]);
        return { open: false, text: (isEn ? 'Closed now · opens ' : 'סגור עכשיו · נפתח ') + when + (isEn ? ' at ' : ' ב-') + sp[0][0] };
      }
    }
    return { open: false, text: '' };
  }
  function updateStatus() {
    var els = doc.querySelectorAll('#open-status, .status[data-hours]');
    if (!els.length) return;
    var hours;
    try { hours = JSON.parse(els[0].getAttribute('data-hours')); } catch (err) { return; }
    var st = statusText(hours);
    Array.prototype.forEach.call(els, function (el) {
      el.classList.toggle('is-open', st.open);
      el.classList.toggle('is-closed', !st.open);
      var t = el.querySelector('.status__text'); if (t && st.text) t.textContent = st.text;
    });
    var today = israelNow().d;
    Array.prototype.forEach.call(doc.querySelectorAll('.hours tr[data-days]'), function (tr) {
      var idx = parseInt(tr.getAttribute('data-days'), 10);
      var match = (idx === 0 && today <= 4) || (idx === 1 && today === 5) || (idx === 2 && today === 6);
      tr.classList.toggle('is-today', match);
    });
  }
  updateStatus(); setInterval(updateStatus, 60000);

  /* ---- sticky header shadow ------------------------------------------- */
  var header = doc.getElementById('site-header');
  function onScroll() { if (header) header.classList.toggle('is-stuck', window.scrollY > 6); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  /* ---- mobile menu ----------------------------------------------------- */
  var burger = doc.getElementById('burger'), nav = doc.getElementById('nav');
  if (burger && nav) {
    function setMenu(open) {
      nav.classList.toggle('is-open', open);
      doc.body.classList.toggle('nav-open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.setAttribute('aria-label', open ? (isEn ? 'Close menu' : 'סגירת תפריט') : (isEn ? 'Open menu' : 'פתיחת תפריט'));
    }
    burger.addEventListener('click', function () { setMenu(!nav.classList.contains('is-open')); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
    window.matchMedia('(min-width: 901px)').addEventListener('change', function (m) { if (m.matches) setMenu(false); });
  }

  /* ---- scroll reveal --------------------------------------------------- */
  var targets = doc.querySelectorAll('.scard, .tcard, .story, .rev, .why li, .values li, .gcard, .acard, .inc li, .steps li, .signs li, .tl li');
  Array.prototype.forEach.call(targets, function (el) { el.classList.add('reveal'); });
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -4% 0px', threshold: 0.01 });
    Array.prototype.forEach.call(targets, function (el, i) { el.style.transitionDelay = ((i % 6) * 60) + 'ms'; io.observe(el); });
    // Safety net: a cheap scroll-position check so nothing can stay hidden if the
    // observer misses a fast scroll, and everything above the fold shows on load.
    var pending = Array.prototype.slice.call(targets), ticking = false;
    function sweep() {
      ticking = false;
      var H = window.innerHeight;
      pending = pending.filter(function (el) {
        if (el.classList.contains('in')) return false;
        var r = el.getBoundingClientRect();
        if (r.top < H * 1.1 && r.bottom > -H) { el.classList.add('in'); return false; }
        return true;
      });
      if (!pending.length) window.removeEventListener('scroll', onSweep);
    }
    function onSweep() { if (!ticking) { ticking = true; requestAnimationFrame(sweep); } }
    window.addEventListener('scroll', onSweep, { passive: true });
    setTimeout(sweep, 200); setTimeout(sweep, 1500);
    window.addEventListener('beforeprint', function () { Array.prototype.forEach.call(targets, function (el) { el.classList.add('in'); }); });
  } else {
    Array.prototype.forEach.call(targets, function (el) { el.classList.add('in'); });
  }

  /* ---- contact form → WhatsApp composer -------------------------------- */
  var formWa = doc.getElementById('form-wa'), form = doc.getElementById('contact-form');
  if (formWa && form) {
    formWa.addEventListener('click', function () {
      var get = function (n) { var el = form.querySelector('[name="' + n + '"]'); return el ? el.value.trim() : ''; };
      var lines = ['שלום, אשמח לקבוע תור במרפאת בן ארי.'];
      if (get('שם')) lines.push('שם: ' + get('שם'));
      if (get('בעל חיים')) lines.push('בעל חיים: ' + get('בעל חיים'));
      if (get('סיבה')) lines.push('סיבה: ' + get('סיבה'));
      if (get('הודעה')) lines.push(get('הודעה'));
      if (get('טלפון')) lines.push('טלפון לחזרה: ' + get('טלפון'));
      window.dataLayer.push({ event: 'cta', type: 'whatsapp-form', page: location.pathname });
      window.open('https://wa.me/' + formWa.getAttribute('data-wa') + '?text=' + encodeURIComponent(lines.join('\n')), '_blank', 'noopener');
    });
    form.addEventListener('submit', function () {
      var b = form.querySelector('button[type="submit"]'); if (b) { b.disabled = true; b.querySelector('span').textContent = isEn ? 'Sending…' : 'שולח…'; }
    });
  }

  /* ---- toxic foods checker --------------------------------------------- */
  var tool = doc.getElementById('toxtool');
  if (tool) {
    var q = doc.getElementById('tox-q'), list = doc.getElementById('toxlist'), empty = doc.getElementById('tox-empty');
    var items = Array.prototype.slice.call(list.children), species = 'dc';
    function norm(s) { return (s || '').toLowerCase().replace(/[֑-ׇ]/g, '').replace(/[״"'׳]/g, ''); }
    function apply() {
      var term = norm(q.value), shown = 0;
      items.forEach(function (li) {
        var okSp = species === 'dc' || li.getAttribute('data-s').indexOf(species) !== -1;
        var okQ = !term || norm(li.textContent).indexOf(term) !== -1;
        var show = okSp && okQ; li.hidden = !show; if (show) shown++;
      });
      empty.hidden = shown > 0;
    }
    q.addEventListener('input', apply);
    Array.prototype.forEach.call(tool.querySelectorAll('.seg__b'), function (b) {
      b.addEventListener('click', function () {
        species = b.getAttribute('data-sp');
        Array.prototype.forEach.call(tool.querySelectorAll('.seg__b'), function (x) { x.classList.toggle('is-on', x === b); });
        apply();
      });
    });
    var hash = decodeURIComponent(location.hash.replace('#', ''));
    if (hash) { q.value = hash; }
    apply();
  }
})();
