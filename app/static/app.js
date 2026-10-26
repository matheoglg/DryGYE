const map = L.map('map').setView([-2.19, -79.89], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap contributors' }).addTo(map);
const legend=L.control({position:'bottomright'});
legend.onAdd=()=>{const d=L.DomUtil.create('div','map-legend');d.innerHTML='<b>Estimated terrain risk</b><div><i style="background:#21a179"></i>Lower</div><div><i style="background:#a7c957"></i>Moderate</div><div><i style="background:#f4a259"></i>Elevated</div><div><i style="background:#b42318"></i>Higher</div><hr><div><i class="line-fast"></i>Fastest route</div><div><i class="line-safe"></i>Lower estimated risk</div>';return d;};
legend.addTo(map);
const colors = ['#21a179','#a7c957','#f4a259','#e76f51','#b42318'];
let riskLayer, routeLayer, markers = [], points = [];
let forecastMarker;
const scenario = document.getElementById('scenario');
const dataMode = document.getElementById('dataMode');
function riskColor(v){ return colors[Math.min(4, Math.floor(v*5))]; }
async function refreshRisk(){
  try { const data = await fetch('/api/risk').then(r=>r.json());
    if(data.error) throw new Error(data.error);
    if(riskLayer) map.removeLayer(riskLayer);
    riskLayer = L.geoJSON(data,{style:f=>({color:riskColor(f.properties.risk),fillColor:riskColor(f.properties.risk),weight:0,fillOpacity:.34})}).addTo(map);
  } catch(e){ console.warn('Risk layer unavailable',e); }
}
async function refreshState(){
  const query=dataMode.value==='forecast'?'mode=forecast':`scenario=${scenario.value}`;
  const response=await fetch(`/api/state?${query}`),s=await response.json();
  if(!response.ok)throw new Error(s.error||'Conditions unavailable');
  document.getElementById('level').textContent=`${s.level.toUpperCase()} ALERT`;
  document.getElementById('rain').textContent=`${s.rain_24h} mm`;
  document.getElementById('tide').textContent=s.tide_m==null?'not included':`${s.tide_m} m`;
  document.getElementById('alert').className=`alert ${s.level}`;
  document.getElementById('conditionNote').textContent=s.mode==='forecast'?'Open-Meteo forecast point · tide not included':'Synthetic scenario · SIMULATION';
  document.getElementById('modeBadge').textContent=s.mode==='forecast'?'LIVE FORECAST':'SIMULATION';
  scenario.disabled=dataMode.value==='forecast';
}
function drawRainChart(hours){
  const canvas=document.getElementById('rainChart'),ctx=canvas.getContext('2d'),w=canvas.clientWidth,h=104,dpr=window.devicePixelRatio||1;
  canvas.width=w*dpr;canvas.height=h*dpr;ctx.scale(dpr,dpr);ctx.clearRect(0,0,w,h);
  const max=Math.max(1,...hours.map(x=>x.precip_mm)),gap=5,bw=(w-gap*(hours.length-1))/hours.length;
  hours.forEach((v,i)=>{const bh=(h-28)*(v.precip_mm/max);const x=i*(bw+gap);ctx.fillStyle=v.precip_mm>0?'#168aad':'#d9e2ec';ctx.beginPath();ctx.roundRect(x,h-20-bh,bw,Math.max(3,bh),3);ctx.fill();if(i%3===0){ctx.fillStyle='#627d98';ctx.font='9px system-ui';ctx.fillText(v.time.slice(11,16),x,h-4);}});
}
async function refreshWeather(){
  const status=document.getElementById('weatherStatus');
  try{
    const f=await fetch('/api/weather').then(async r=>{const d=await r.json();if(!r.ok)throw new Error(d.error||'Forecast unavailable');return d;});
    document.getElementById('rain3h').textContent=`${f.next_3h_mm} mm`;
    document.getElementById('rain24h').textContent=`${f.next_24h_mm} mm`;
    const updated=new Intl.DateTimeFormat('en',{timeZone:'America/Guayaquil',hour:'2-digit',minute:'2-digit',day:'2-digit',month:'short'}).format(new Date(f.fetched_at));
    document.getElementById('weatherUpdated').textContent=`${f.stale?'Cached':'Updated'} ${updated} local time · Open-Meteo point forecast`;
    status.textContent=f.stale?'Live forecast unavailable; showing cached data.':'Forecast near Guayaquil city center · not street-level rainfall';
    drawRainChart(f.hours);
    const p=f.location, rain=f.next_3h_mm;
    if(forecastMarker)map.removeLayer(forecastMarker);
    forecastMarker=L.circleMarker([p.lat,p.lon],{radius:8+Math.min(rain,8),color:'#075985',fillColor:'#38bdf8',fillOpacity:.85,weight:2}).addTo(map)
      .bindPopup(`<b>Open-Meteo point forecast</b><br>Next 3h: ${f.next_3h_mm} mm<br>Next 24h: ${f.next_24h_mm} mm<br><small>Forecast grid point; not a street sensor.</small>`);
  }catch(e){status.textContent=e.message;status.className='weather-status error';}
}
scenario.addEventListener('change',()=>{refreshState(); if(points.length===2) calculateRoute();});
dataMode.addEventListener('change',async()=>{try{await refreshState();}catch(e){document.getElementById('conditionNote').textContent=e.message;} if(points.length===2)calculateRoute();});
map.on('click',e=>{
  if(points.length===2){points=[];markers.forEach(m=>map.removeLayer(m));markers=[];if(routeLayer)map.removeLayer(routeLayer);document.getElementById('routes').innerHTML='';}
  points.push([e.latlng.lat,e.latlng.lng]);
  markers.push(L.marker(e.latlng).addTo(map).bindPopup(points.length===1?'Origin':'Destination').openPopup());
  const b=document.getElementById('routeButton'); b.disabled=points.length!==2; b.textContent=points.length===2?'Compare routes':'Choose destination';
});
async function calculateRoute(){
  const b=document.getElementById('routeButton');b.disabled=true;b.textContent='Calculating…';
  const q=new URLSearchParams({from:points[0].join(','),to:points[1].join(','),scenario:scenario.value,mode:dataMode.value});
  try{
    const r=await fetch(`/api/route?${q}`), data=await r.json();if(!r.ok)throw new Error(data.error||'Routing failed');
    if(routeLayer)map.removeLayer(routeLayer);
    routeLayer=L.featureGroup([
      L.polyline(data.fast.coords,{color:'#4776e6',weight:5,dashArray:'8 7'}),
      L.polyline(data.safe.coords,{color:'#078a70',weight:6})
    ]).addTo(map);map.fitBounds(routeLayer.getBounds(),{padding:[30,30]});
    document.getElementById('routes').innerHTML=`<div class="route-card"><b>Fastest route</b>${data.fast.length_m} m · ${data.fast.time_min} min · risk ${data.fast.mean_risk}</div><div class="route-card safe"><b>Lower estimated risk</b>${data.safe.length_m} m · ${data.safe.time_min} min · risk ${data.safe.mean_risk}</div>`;
  }catch(e){document.getElementById('routes').innerHTML=`<div class="route-card">${e.message}. Check internet access to OpenStreetMap.</div>`;}
  b.disabled=false;b.textContent='Compare again';
}
document.getElementById('routeButton').addEventListener('click',calculateRoute);
refreshRisk();refreshState().catch(e=>{document.getElementById('conditionNote').textContent=e.message;});refreshWeather();
