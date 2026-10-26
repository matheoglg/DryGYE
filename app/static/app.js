const PILOT_BOUNDS = L.latLngBounds([[-2.22, -79.94], [-2.14, -79.86]]);
// Urdesa / Kennedy area (flooded on 24-oct-2026): the lower-risk route clearly differs here.
const DEMO_TRIP = [[-2.16899, -79.91956], [-2.14642, -79.92559]];
const RISK_COLORS = ['#21a179', '#a7c957', '#f4a259', '#e76f51', '#b42318'];
const ROUTE_STYLE = {
  safe: { name: 'Lower risk', color: '#078a70' },
  fast: { name: 'Fastest', color: '#3b6fe0', dashArray: '8 6' },
  alt: { name: 'Alternative', color: '#8e44ad' },
};

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

const legend = L.control({ position: 'bottomright' });
legend.onAdd = () => {
  const d = L.DomUtil.create('div', 'map-legend');
  d.innerHTML = '<b>Estimated flood risk</b><div class="scale"></div><div class="ends"><span>Low</span><span>High</span></div>'
    + '<div><i style="background:#078a70"></i>Lower risk route</div>'
    + '<div><i style="border-top:3px dashed #3b6fe0"></i>Fastest route</div>'
    + '<div><i style="background:#8e44ad"></i>Alternative (click to view)</div>';
  return d;
};
legend.addTo(map);

let floodLayer, routeLayer;
let points = [], markers = [];
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

// --- Points ---
function clearRoutes() {
  if (routeLayer) { map.removeLayer(routeLayer); routeLayer = null; }
  routes = [];
  $('routeResults').innerHTML = '';
}

function clearAll() {
  clearRoutes();
  points = [];
  markers.forEach(m => map.removeLayer(m)); markers = [];
  updateRouteControls();
}

function addPoint(latlng) {
  if (points.length === 2) clearAll();
  points.push([latlng[0], latlng[1]]);
  const label = points.length === 1 ? 'Start' : 'End';
  markers.push(L.marker(latlng).addTo(map)
    .bindTooltip(label, { permanent: true, direction: 'top', offset: [-15, -12], className: 'endpoint' }));
  updateRouteControls();
}

function updateRouteControls(message) {
  const ready = points.length === 2;
  $('routeButton').disabled = !ready;
  $('routeHint').textContent = message
    || (points.length === 0 ? 'Click the map to set a start and an end point.'
      : points.length === 1 ? 'Now click the end point.'
        : routes.length ? 'Click a route on the map or in the list to view it.'
          : 'Press "Calculate routes".');
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

function routeCard(r, i) {
  const label = riskLabel(r.mean_risk), style = ROUTE_STYLE[r.kind];
  const swatch = style.dashArray
    ? `border-top:4px dashed ${style.color}` : `background:${style.color}`;
  return `<div class="route-card${i === selected ? ' selected' : ''}" data-index="${i}">`
    + `<span class="swatch" style="${swatch}"></span>`
    + `<span><b>${r.name}</b><small>${(r.length_m / 1000).toFixed(1)} km · ${Math.round(r.time_min)} min · max risk ${r.max_risk.toFixed(2)}</small></span>`
    + `<span class="pill ${label}">${label} risk</span></div>`;
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
  if (points.length !== 2) return;
  const button = $('routeButton');
  button.disabled = true; button.textContent = 'Calculating…';
  const q = new URLSearchParams({ from: points[0].join(','), to: points[1].join(',') });
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
  button.disabled = points.length !== 2;
}

function loadDemoTrip() {
  clearAll();
  DEMO_TRIP.forEach(p => addPoint(p));
  calculateRoutes();
}

// --- Wiring ---
map.on('click', e => addPoint([e.latlng.lat, e.latlng.lng]));
conditions.addEventListener('change', () => { refreshState(); if (routes.length) calculateRoutes(); });
$('routeButton').addEventListener('click', calculateRoutes);
$('demoButton').addEventListener('click', loadDemoTrip);
$('clearButton').addEventListener('click', clearAll);
$('floodToggle').addEventListener('change', toggleFloodZones);

loadRiskLayer();
refreshState();
refreshForecast();
