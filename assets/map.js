/* Tenerife Compass — sameiginlegt kortakerfi.
   Notað af öllum svæðissíðum og /south/map.html.
   Gögn: window.TC_DATA[region] úr /assets/places-<region>.js
   Stytt lyklaheiti í gögnunum: c=cat, n=name, a=area, y=lat, x=lng,
   t=cuisine, s=stars, d=desc, l=link, w=website, f=featured */
(function () {
  var CATS = {
    stay:  { color: '#B0674C', label: 'Hotel' },
    eat:   { color: '#C08A3E', label: 'Restaurant' },
    do:    { color: '#4A6FA5', label: 'Things to do' },
    beach: { color: '#4F8A8B', label: 'Beach' },
    drink: { color: '#8A5B7A', label: 'Bar / nightlife' }
  };
  var MAX_ROWS = 220; // hámark raða í hliðarlista (frammistaða)

  window.TCMap = function (opts) {
    var region = opts.region;
    var data = (window.TC_DATA && window.TC_DATA[region]) || [];
    var map = L.map(opts.el, { scrollWheelZoom: !!opts.scrollWheel })
                .setView(opts.center, opts.zoom || 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var listEl  = document.getElementById('place-list');
    var countEl = document.getElementById('place-count');
    var cuisineWrap = document.getElementById('cuisine-filters');
    var searchEl = document.getElementById('place-search');

    var curCat = 'all', curCuisine = 'all', curText = '';

    // ---- byggja hluti fyrir hvern stað --------------------------------
    var items = data.map(function (p) {
      var c = CATS[p.c] || CATS.do;
      var featured = !!p.f;
      var html = '<strong>' + esc(p.n) + '</strong><br>' +
        '<span style="color:#52707a">' + (p.t ? esc(p.t) : c.label) +
        (p.s ? ' · ' + p.s + '★' : '') + ' · ' + esc(p.a) + '</span>' +
        (p.d ? '<br>' + esc(p.d) : '') +
        (p.l ? '<br><a href="' + p.l + '">Read more →</a>' : '') +
        (!p.l && p.w ? '<br><a href="' + p.w + '" rel="nofollow" target="_blank">Website ↗</a>' : '');
      var marker = L.circleMarker([p.y, p.x], {
        radius: featured ? 8 : 5,
        color: '#fff',
        weight: featured ? 2 : 1,
        fillColor: c.color,
        fillOpacity: featured ? 1 : 0.8
      }).bindPopup(html);
      return { p: p, m: marker, c: c, featured: featured,
               hay: (p.n + ' ' + p.a + ' ' + (p.t || '') + ' ' + c.label).toLowerCase() };
    });

    // þyrping fyrir frammistöðu ef plugin er til staðar
    var layer = (typeof L.markerClusterGroup === 'function')
      ? L.markerClusterGroup({ maxClusterRadius: 45, spiderfyOnMaxZoom: true, showCoverageOnHover: false })
      : L.layerGroup();
    map.addLayer(layer);

    // ---- matarflokka-síur (byggðar úr gögnunum) ----------------------
    if (cuisineWrap) {
      var counts = {};
      data.forEach(function (p) { if (p.c === 'eat' && p.t) counts[p.t] = (counts[p.t] || 0) + 1; });
      var kinds = Object.keys(counts).filter(function (k) { return counts[k] >= 3 && k !== 'Other'; })
                        .sort(function (a, b) { return counts[b] - counts[a]; });
      cuisineWrap.innerHTML = '';
      [['all', 'All food']].concat(kinds.map(function (k) { return [k, k + ' (' + counts[k] + ')']; }))
        .forEach(function (pair, i) {
          var b = document.createElement('button');
          b.className = 'chip' + (i === 0 ? ' is-on' : '');
          b.textContent = pair[1];
          b.dataset.cuisine = pair[0];
          b.addEventListener('click', function () {
            cuisineWrap.querySelectorAll('.chip').forEach(function (x) { x.classList.remove('is-on'); });
            b.classList.add('is-on');
            curCuisine = pair[0];
            if (curCat !== 'eat') setCat('eat');
            else refresh();
          });
          cuisineWrap.appendChild(b);
        });
    }

    // ---- síun + teikning ---------------------------------------------
    function visible(it) {
      if (curCat !== 'all' && it.p.c !== curCat) return false;
      if (curCat === 'eat' && curCuisine !== 'all' && it.p.t !== curCuisine) return false;
      if (curText && it.hay.indexOf(curText) === -1) return false;
      return true;
    }
    function refresh() {
      var shown = items.filter(visible);
      layer.clearLayers();
      shown.forEach(function (it) { layer.addLayer(it.m); });

      if (listEl) {
        listEl.innerHTML = '';
        var frag = document.createDocumentFragment();
        shown.slice(0, MAX_ROWS).forEach(function (it) {
          var row = document.createElement('div');
          row.className = 'place-item' + (it.featured ? ' is-featured' : '');
          row.innerHTML = '<span class="dot" style="background:' + it.c.color + '"></span>' +
            '<span><b>' + esc(it.p.n) + '</b><small>' +
            (it.p.t ? esc(it.p.t) : it.c.label) + (it.p.s ? ' · ' + it.p.s + '★' : '') +
            ' · ' + esc(it.p.a) + '</small></span>';
          row.addEventListener('click', function () {
            map.setView([it.p.y, it.p.x], 16, { animate: true });
            it.m.openPopup();
          });
          frag.appendChild(row);
        });
        listEl.appendChild(frag);
        if (shown.length > MAX_ROWS) {
          var more = document.createElement('p');
          more.className = 'place-more';
          more.textContent = '+ ' + (shown.length - MAX_ROWS) + ' more on the map. Filter or search to narrow it down.';
          listEl.appendChild(more);
        }
      }
      if (countEl) countEl.textContent = shown.length.toLocaleString('en-GB') + ' place' + (shown.length === 1 ? '' : 's') +
        (curText ? ' matching “' + curText + '”' : '');
    }

    function setCat(cat) {
      curCat = cat;
      document.querySelectorAll('.map-filter').forEach(function (b) {
        var on = b.dataset.cat === cat;
        b.classList.toggle('is-on', on);
        b.classList.toggle('btn--ghost', !on);
        b.style.background = on ? 'var(--ocean)' : '#fff';
        b.style.color = on ? '#fff' : 'var(--ocean-deep)';
      });
      if (cuisineWrap) cuisineWrap.style.display = (cat === 'eat') ? '' : 'none';
      if (cat !== 'eat') curCuisine = 'all';
      refresh();
    }

    document.querySelectorAll('.map-filter').forEach(function (btn) {
      btn.addEventListener('click', function () { setCat(btn.dataset.cat); });
    });
    if (searchEl) {
      searchEl.addEventListener('input', function (e) {
        curText = e.target.value.trim().toLowerCase(); refresh();
      });
    }

    if (cuisineWrap) cuisineWrap.style.display = 'none';
    refresh();
    return map;
  };

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
})();
