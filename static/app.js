const $ = (id) => document.getElementById(id);
let airports = [], routes = [], map, airportLayer, routeLayer, resultLayer;
const colors = {route:"#6c809c", active:"#46d7a5"};
function escapeHtml(value){return String(value ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
async function api(url, options={}) {
  const response = await fetch(url,{headers:{"Content-Type":"application/json"},...options});
  let body={}; try{body=await response.json()}catch{}
  if(!response.ok) throw new Error(body.error || body.message || `Request failed (${response.status})`);
  return body;
}
function toast(message){$("toast").textContent=message;$("toast").classList.add("show");setTimeout(()=>$("toast").classList.remove("show"),3200);}
function setMessage(id,message,error=false){$(id).textContent=message;$(id).style.color=error?"#ff9aa4":"#45d6a2";}
function airportOptions(select,selected){select.innerHTML=airports.map(a=>`<option value="${a.id}" ${String(a.id)===String(selected)?"selected":""}>${escapeHtml(a.code)} — ${escapeHtml(a.city)}</option>`).join("");}
function refreshSelectors(){
  const oldStart=$("startAirport").value,oldEnd=$("endAirport").value;
  airportOptions($("startAirport"),oldStart || (airports[0]?.id ?? ""));
  airportOptions($("endAirport"),oldEnd || (airports[1]?.id ?? ""));
  airportOptions($("routeSource"),airports[0]?.id ?? "");
  airportOptions($("routeDestination"),airports[1]?.id ?? "");
  $("blockedRoute").innerHTML=routes.map(r=>`<option value="${r.id}">${escapeHtml(r.source_code)} ↔ ${escapeHtml(r.destination_code)} (${r.distance} km)</option>`).join("");
}
function initMap(){
  map=L.map("map").setView([22.8,82.5],4);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:18,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
  routeLayer=L.layerGroup().addTo(map); resultLayer=L.layerGroup().addTo(map); airportLayer=L.layerGroup().addTo(map);
}
function drawMap(pathIds=[]){
  routeLayer.clearLayers();resultLayer.clearLayers();airportLayer.clearLayers();
  const byId=Object.fromEntries(airports.map(a=>[a.id,a]));
  routes.forEach(r=>{
    const a=byId[r.source_id],b=byId[r.destination_id];if(!a||!b)return;
    const line=L.polyline([[a.lat,a.lon],[b.lat,b.lon]],{color:r.active?colors.route:"#d95365",weight:r.active?1.5:1,dashArray:r.active?null:"5 7",opacity:r.active?.72:.5});
    line.bindPopup(`<b>${escapeHtml(r.source_code)} ↔ ${escapeHtml(r.destination_code)}</b><br>${r.distance} km<br>Status: ${r.active?"Active":"Inactive"}`);
    line.addTo(routeLayer);
  });
  if(pathIds.length){
    const path=pathIds.map(id=>byId[id]).filter(Boolean);
    if(path.length>1)L.polyline(path.map(a=>[a.lat,a.lon]),{color:colors.active,weight:5,opacity:.95}).addTo(resultLayer);
    if(path.length>1)map.fitBounds(path.map(a=>[a.lat,a.lon]),{padding:[40,40],maxZoom:6});
  }
  airports.forEach(a=>{
    const marker=L.circleMarker([a.lat,a.lon],{radius:6,weight:2,color:"#dceaff",fillColor:"#428df5",fillOpacity:1});
    marker.bindPopup(`<b>${escapeHtml(a.code)} — ${escapeHtml(a.city)}</b><br>${escapeHtml(a.name)}<br><small>${a.lat}, ${a.lon}</small>`).addTo(airportLayer);
  });
}
function renderTables(){
  $("airportTable").innerHTML=airports.map(a=>`<tr><td><b>${escapeHtml(a.code)}</b></td><td>${escapeHtml(a.name)}<br><span class="muted">${escapeHtml(a.city)}</span></td><td><button onclick="editAirport(${a.id})">Edit</button><button onclick="deleteAirport(${a.id})">Delete</button></td></tr>`).join("");
  $("routeTable").innerHTML=routes.map(r=>`<tr><td><b>${escapeHtml(r.source_code)} ↔ ${escapeHtml(r.destination_code)}</b></td><td>${r.distance} km</td><td><span class="tag ${r.active?"active":"inactive"}">${r.active?"Active":"Inactive"}</span></td><td><button onclick="editRoute(${r.id})">Edit</button><button onclick="toggleRoute(${r.id},${!r.active})">${r.active?"Close":"Restore"}</button><button onclick="deleteRoute(${r.id})">Delete</button></td></tr>`).join("");
  $("airportCount").textContent=airports.length;$("routeCount").textContent=routes.length;$("activeCount").textContent=routes.filter(r=>r.active).length;
}
async function loadAll(){
  const [a,r]=await Promise.all([api("/api/airports"),api("/api/routes")]);airports=a;routes=r;
  refreshSelectors();renderTables();drawMap();
}
function showRouteResult(id,data){
  $(id).innerHTML=`<div class="metric">${data.total_distance.toLocaleString()} km</div><strong>${data.airports.map(a=>escapeHtml(a.code)).join(" → ")}</strong><br>${data.stops} intermediate stop(s) · ${data.legs.length} leg(s)<br><span class="muted">${escapeHtml(data.note)}</span>`;
  drawMap(data.airport_ids);
}
$("findBtn").addEventListener("click",async()=>{
  try{const data=await api("/api/route",{method:"POST",body:JSON.stringify({start_id:$("startAirport").value,end_id:$("endAirport").value,mode:$("algorithm").value})});showRouteResult("routeResult",data);}
  catch(e){$("routeResult").textContent=e.message;toast(e.message);}
});
$("divertBtn").addEventListener("click",async()=>{
  try{const data=await api("/api/diversion",{method:"POST",body:JSON.stringify({start_id:$("startAirport").value,end_id:$("endAirport").value,blocked_route_id:$("blockedRoute").value})});showRouteResult("diversionResult",data);}
  catch(e){$("diversionResult").textContent=e.message;toast(e.message);}
});
$("airportForm").addEventListener("submit",async e=>{
  e.preventDefault();const f=new FormData(e.target),data=Object.fromEntries(f.entries());data.lat=Number(data.lat);data.lon=Number(data.lon);
  try{await api("/api/airports",{method:"POST",body:JSON.stringify(data)});e.target.reset();setMessage("airportMessage","Airport saved to JSON file.");await loadAll();}
  catch(err){setMessage("airportMessage",err.message,true);}
});
$("routeForm").addEventListener("submit",async e=>{
  e.preventDefault();const f=new FormData(e.target),data=Object.fromEntries(f.entries());data.source_id=Number(data.source_id);data.destination_id=Number(data.destination_id);data.distance=Number(data.distance);
  try{await api("/api/routes",{method:"POST",body:JSON.stringify(data)});e.target.reset();setMessage("routeMessage","Route saved to JSON file.");await loadAll();}
  catch(err){setMessage("routeMessage",err.message,true);}
});
window.editAirport=async id=>{
  const a=airports.find(x=>x.id===id);if(!a)return;
  const code=prompt("Airport code:",a.code);if(code===null)return;
  const city=prompt("City:",a.city);if(city===null)return;
  const name=prompt("Airport name:",a.name);if(name===null)return;
  const lat=prompt("Latitude:",a.lat);if(lat===null)return;
  const lon=prompt("Longitude:",a.lon);if(lon===null)return;
  try{await api(`/api/airports/${id}`,{method:"PUT",body:JSON.stringify({code,city,name,lat:Number(lat),lon:Number(lon)})});await loadAll();toast("Airport updated.");}
  catch(e){toast(e.message);}
};
window.deleteAirport=async id=>{
  const a=airports.find(x=>x.id===id);if(!a||!confirm(`Delete ${a.code}? Its connected routes will also be deleted.`))return;
  try{await api(`/api/airports/${id}`,{method:"DELETE"});await loadAll();toast("Airport deleted.");}catch(e){toast(e.message);}
};
window.editRoute=async id=>{
  const r=routes.find(x=>x.id===id);if(!r)return;
  const distance=prompt(`Distance for ${r.source_code} ↔ ${r.destination_code} (km):`,r.distance);if(distance===null)return;
  try{await api(`/api/routes/${id}`,{method:"PUT",body:JSON.stringify({distance:Number(distance)})});await loadAll();toast("Route updated.");}catch(e){toast(e.message);}
};
window.toggleRoute=async(id,active)=>{
  try{await api(`/api/routes/${id}`,{method:"PUT",body:JSON.stringify({active})});await loadAll();toast(active?"Route restored.":"Route closed.");}catch(e){toast(e.message);}
};
window.deleteRoute=async id=>{
  if(!confirm("Permanently delete this route?"))return;
  try{await api(`/api/routes/${id}`,{method:"DELETE"});await loadAll();toast("Route deleted.");}catch(e){toast(e.message);}
};
$("refreshBtn").addEventListener("click",()=>loadAll().then(()=>toast("Data refreshed.")).catch(e=>toast(e.message)));
async function start(){
  initMap();
  try{await api("/api/health");$("dbStatus").textContent="JSON files connected";$("dbStatus").classList.add("ok");await loadAll();}
  catch(e){$("dbStatus").textContent="File storage error";$("dbStatus").classList.add("bad");toast(e.message);}
}
start();
