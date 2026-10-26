const PILOT_BOUNDS = L.latLngBounds([PILOT_BBOX[0], PILOT_BBOX[1]], [PILOT_BBOX[2], PILOT_BBOX[3]]);
// Urdesa / Kennedy area (flooded on 24-oct-2026): the lower-risk route clearly differs here.
const DEMO_TRIP = { start: [-2.16899, -79.91956], end: [-2.14642, -79.92559] };
const RISK_COLORS = ['#21a179', '#a7c957', '#f4a259', '#e76f51', '#b42318'];
const ROUTE_STYLE = {
  safe: { name: 'Lower risk', color: '#078a70' },
  fast: { name: 'Fastest', color: '#3b6fe0', dashArray: '8 6' },
  alt: { name: 'Alternative', color: '#8e44ad' },
};
const POINT_LABEL = { start: 'Start', end: 'End' };

const $ = id => document.getElementById(id);
const conditions = $('conditions');

// --- Map ---
// maxBounds is padded so the map can still be dragged freely around the pilot area.
const map = L.map('map', { maxBounds: PILOT_BOUNDS.pad(0.5) }).fitBounds(PILOT_BOUNDS);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19, attribution: '&copy; OpenStreetMap contributors',
}).addTo(map);
map.attributionControl.addAttribution(
  'Weather: <a href="https://open-meteo.com/">Open-Meteo.com</a> · Copernicus DEM GLO-30 · Tides: INOCAR · Flood zones: Municipality of Guayaquil');

// Covered area: everything outside is shaded and the border is dashed.
// Own pane above the risk layer (overlay pane = 400), below markers (600).
map.createPane('coverage').style.zIndex = 450;
const outside = PILOT_BOUNDS.pad(3);
L.polygon([
  [outside.getNorthWest(), outside.getNorthEast(), outside.getSouthEast(), outside.getSouthWest()],
  [PILOT_BOUNDS.getNorthWest(), PILOT_BOUNDS.getNorthEast(), PILOT_BOUNDS.getSouthEast(), PILOT_BOUNDS.getSouthWest()],
], { pane: 'coverage', stroke: false, fillColor: '#102a43', fillOpacity: 0.28, interactive: false }).addTo(map);
L.rectangle(PILOT_BOUNDS, { pane: 'coverage', color: '#073b4c', weight: 2, dashArray: '8 6', fill: false, interactive: false }).addTo(map);

const legend = L.control({ position: 'bottomright' });
legend.onAdd = () => {
  const d = L.DomUtil.create('div', 'map-legend');
  d.innerHTML = '<b>Estimated flood risk</b><div class="scale"></div><div class="ends"><span>Low</span><span>High</span></div>'
    + '<div><i style="background:#078a70"></i>Lower risk route</div>'
    + '<div><i style="border-top:3px dashed #3b6fe0"></i>Fastest route</div>'
    + '<div><i style="background:#8e44ad"></i>Alternative (click to view)</div>'
    + '<div><i style="border-top:2px dashed #073b4c"></i>Covered area</div>';
  return d;
};
legend.addTo(map);

let floodLayer, routeLayer;
const points = { start: null, end: null };
const markers = { start: null, end: null };
let pickMode = 'start';
let routes = [], selected = 0;

function riskColor(v) { return RISK_COLORS[Math.min(4, Math.floor(v * 5))]; }
function riskLabel(v) { return v < 0.3 ? 'low' : v < 0.6 ? 'medium' : 'high'; }

async function getJson(url) {
  const r = await fetch(url), data = await r.json();
  if (!r.ok) throw new Error(data.error || 'Request failed');
  return data;
}

async function loadRiskLayer() {
  try {
    const data = await getJson('/api/risk');
    L.geoJSON(data, {
      interactive: false,
      style: f => ({ weight: 0, fillColor: riskColor(f.properties.risk), fillOpacity: 0.3 }),
    }).addTo(map);
  } catch (e) { console.warn('Risk layer unavailable', e); }
}

async function toggleFloodZones() {
  if (floodLayer) { map.removeLayer(floodLayer); floodLayer = null; }
  if (!$('floodToggle').checked) return;
  try {
    const data = await getJson('/api/reference/flood-zones');
    floodLayer = L.geoJSON(data, {
      style: { color: '#7b2cbf', weight: 1.5, dashArray: '5 4', fillColor: '#7b2cbf', fillOpacity: 0.08 },
      onEachFeature: (f, l) => l.bindPopup('Flood-prone zone (municipal records, not live flooding)'),
    }).addTo(map);
  } catch (e) { $('floodToggle').checked = false; }
}

// --- Conditions ---
function isForecast() { return conditions.value === 'forecast'; }
function stateQuery() { return isForecast() ? 'mode=forecast' : `mode=simulation&scenario=${conditions.value}`; }

async function refreshState() {
  $('simBanner').hidden = isForecast();
  const box = $('alert');
  try {
    const s = await getJson(`/api/state?${stateQuery()}`);
    box.className = `alert ${s.level}`;
    $('level').textContent = `${s.level[0].toUpperCase()}${s.level.slice(1)} alert`;
    const tide = s.tide_m == null ? 'tide not available' : `tide ${s.tide_m} m`;
    $('alertDetail').textContent = `${s.rain_24h} mm rain in 24 h · ${tide}`;
  } catch (e) {
    box.className = 'alert';
    $('level').textContent = 'Live forecast unavailable';
    $('alertDetail').textContent = 'Choose a simulation scenario instead.';
  }
}

async function refreshForecast() {
  try {
    const f = await getJson('/api/weather');
    $('rain3h').textContent = `${f.next_3h_mm} mm`;
    $('rain24h').textContent = `${f.next_24h_mm} mm`;
    drawRainChart(f.hours);
  } catch (e) {
    $('rain3h').textContent = $('rain24h').textContent = 'offline';
  }
}

function drawRainChart(hours) {
  const canvas = $('rainChart'), ctx = canvas.getContext('2d');
  const w = canvas.clientWidth, h = canvas.clientHeight, dpr = window.devicePixelRatio || 1;
  canvas.width = w * dpr; canvas.height = h * dpr; ctx.scale(dpr, dpr);
  const max = Math.max(1, ...hours.map(x => x.precip_mm)), gap = 3, bw = (w - gap * (hours.length - 1)) / hours.length;
  hours.forEach((v, i) => {
    const bh = (h - 16) * (v.precip_mm / max), x = i * (bw + gap);
    ctx.fillStyle = v.precip_mm > 0 ? '#168aad' : '#d9e2ec';
    ctx.fillRect(x, h - 14 - Math.max(2, bh), bw, Math.max(2, bh));
    if (i % 4 === 0) { ctx.fillStyle = '#627d98'; ctx.font = '9px system-ui'; ctx.fillText(v.time.slice(11, 16), x, h - 2); }
  });
}

// --- Start / end points ---
function setPickMode(kind) {
  pickMode = kind;
  $('pickStart').classList.toggle('active', kind === 'start');
  $('pickEnd').classList.toggle('active', kind === 'end');
  updateRouteControls();
}

function pinIcon(kind) {
  return L.divIcon({ className: `pin ${kind}`, html: kind === 'start' ? 'S' : 'E', iconSize: [26, 26], iconAnchor: [13, 13] });
}

// Places (or moves) the start or end point. Markers can also be dragged to adjust them.
function setPoint(kind, latlng) {
  if (!PILOT_BOUNDS.contains(latlng)) {
    updateRouteControls('That point is outside the covered area. Click inside the dashed border.');
    return;
  }
  points[kind] = [latlng[0], latlng[1]];
  if (markers[kind]) {
    markers[kind].setLatLng(latlng);
  } else {
    markers[kind] = L.marker(latlng, { icon: pinIcon(kind), draggable: true, title: `${POINT_LABEL[kind]} (drag to move)` })
      .on('dragend', e => {
        const p = e.target.getLatLng();
        setPoint(kind, [p.lat, p.lng]);
      })
      .addTo(map);
  }
  // After placing the start, the next click sets the end (if it is still missing).
  if (kind === 'start' && !points.end) setPickMode('end');
  if (routes.length) calculateRoutes();
  else updateRouteControls();
}

function clearRoutes() {
  if (routeLayer) { map.removeLayer(routeLayer); routeLayer = null; }
  routes = [];
  $('routeResults').innerHTML = '';
}

function clearAll() {
  clearRoutes();
  for (const kind of ['start', 'end']) {
    if (markers[kind]) map.removeLayer(markers[kind]);
    markers[kind] = points[kind] = null;
  }
  setPickMode('start');
}

function updateRouteControls(message) {
  const ready = points.start && points.end;
  $('routeButton').disabled = !ready;
  $('routeHint').textContent = message
    || (routes.length ? 'Click a route to view it. Drag S or E to adjust.'
      : ready ? 'Press "Calculate routes". Drag S or E to adjust.'
        : `Click inside the dashed border to set the ${POINT_LABEL[pickMode].toLowerCase()} point.`);
}

// --- Routes ---
function buildRouteList(data) {
  const sameAsFast = JSON.stringify(data.safe.coords) === JSON.stringify(data.fast.coords);
  const list = [{ ...data.safe, kind: 'safe', name: sameAsFast ? 'Fastest and lower risk' : 'Lower risk' }];
  if (!sameAsFast) list.push({ ...data.fast, kind: 'fast', name: 'Fastest' });
  data.alternatives.forEach((r, i) => list.push({ ...r, kind: 'alt', name: `Alternative ${i + 1}` }));
  return list;
}

function drawRoutes() {
  if (routeLayer) map.removeLayer(routeLayer);
  routeLayer = L.featureGroup().addTo(map);
  // Unselected routes first (faded), the selected one last so it is drawn on top.
  const order = routes.map((r, i) => i).filter(i => i !== selected).concat(selected);
  order.forEach(i => {
    const r = routes[i], style = ROUTE_STYLE[r.kind], active = i === selected;
    if (active) L.polyline(r.coords, { color: '#fff', weight: 10, opacity: 0.95, interactive: false }).addTo(routeLayer);
    L.polyline(r.coords, {
      color: style.color, dashArray: style.dashArray, weight: active ? 6 : 4, opacity: active ? 1 : 0.45, interactive: false,
    }).addTo(routeLayer);
    // Wide invisible line on top makes the route easy to click; the click does not reach the map.
    L.polyline(r.coords, { color: '#000', weight: 18, opacity: 0, bubblingMouseEvents: false })
      .on('click', () => selectRoute(i)).bindTooltip(r.name, { sticky: true }).addTo(routeLayer);
  });
}

function riskPill(value) {
  const label = riskLabel(value);
  return `<span class="pill ${label}">${label[0].toUpperCase()}${label.slice(1)}</span>`;
}

// Overall risk = mean over the route's streets; riskiest stretch = its single highest-risk street.
function routeCard(r, i) {
  const style = ROUTE_STYLE[r.kind];
  const swatch = style.dashArray ? `border-top:4px dashed ${style.color}` : `background:${style.color}`;
  return `<div class="route-card${i === selected ? ' selected' : ''}" data-index="${i}">`
    + `<div class="route-head"><span class="swatch" style="${swatch}"></span><b>${r.name}</b>`
    + `<small>${(r.length_m / 1000).toFixed(1)} km · ${Math.round(r.time_min)} min</small></div>`
    + `<div class="route-risk"><span>Overall risk ${riskPill(r.mean_risk)}</span>`
    + `<span>Riskiest stretch ${riskPill(r.max_risk)}</span></div></div>`;
}

function renderRouteList(warning) {
  $('routeResults').innerHTML = routes.map(routeCard).join('')
    + (warning ? `<p class="notice">${warning}</p>` : '');
  document.querySelectorAll('.route-card').forEach(card =>
    card.addEventListener('click', () => selectRoute(Number(card.dataset.index))));
}

function selectRoute(i) {
  selected = i;
  drawRoutes();
  document.querySelectorAll('.route-card').forEach(card =>
    card.classList.toggle('selected', Number(card.dataset.index) === i));
}

async function calculateRoutes() {
  if (!points.start || !points.end) return;
  const button = $('routeButton');
  button.disabled = true; button.textContent = 'Calculating…';
  const q = new URLSearchParams({ from: points.start.join(','), to: points.end.join(',') });
  try {
    const data = await getJson(`/api/route?${q}&${stateQuery()}`);
    routes = buildRouteList(data);
    selected = 0;
    drawRoutes();
    renderRouteList(data.warning);
    map.fitBounds(routeLayer.getBounds(), { padding: [40, 40] });
    updateRouteControls();
  } catch (e) {
    clearRoutes();
    updateRouteControls(e.message);
  }
  button.textContent = 'Calculate routes';
  button.disabled = !(points.start && points.end);
}

function loadDemoTrip() {
  clearAll();
  setPoint('start', DEMO_TRIP.start);
  setPoint('end', DEMO_TRIP.end);
  calculateRoutes();
}

// --- Wiring ---
map.on('click', e => setPoint(pickMode, [e.latlng.lat, e.latlng.lng]));
conditions.addEventListener('change', () => { refreshState(); if (routes.length) calculateRoutes(); });
$('pickStart').addEventListener('click', () => setPickMode('start'));
$('pickEnd').addEventListener('click', () => setPickMode('end'));
$('routeButton').addEventListener('click', calculateRoutes);
$('demoButton').addEventListener('click', loadDemoTrip);
$('clearButton').addEventListener('click', clearAll);
$('floodToggle').addEventListener('change', toggleFloodZones);

loadRiskLayer();
refreshState();
refreshForecast();
updateRouteControls();
