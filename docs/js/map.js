/* map.js — Leaflet 지도 렌더링 */
const MapView = (() => {
  let map, layer;
  const markers = new Map(); // station id → marker

  function init() {
    map = L.map("map", { zoomControl: true }).setView([36.5, 127.8], 7);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; OpenStreetMap contributors', maxZoom: 19,
    }).addTo(map);
    layer = L.layerGroup().addTo(map);
    return map;
  }

  function pinIcon(st) {
    const g = Score.gradeMeta(st.grade);
    return L.divIcon({
      className: "",
      html: `<div class="marker-pin pin-${g.cls}"><span>${st.score}</span></div>`,
      iconSize: [26, 26], iconAnchor: [13, 26], popupAnchor: [0, -24],
    });
  }

  function popupHtml(st, fuel) {
    const g = Score.gradeMeta(st.grade);
    const price = st.prices[fuel]
      ? `${st.prices[fuel].toLocaleString()}원` : "가격정보 없음";
    const fuelName = fuel === "B027" ? "휘발유" : "경유";
    return `<div class="popup">
      <h3>${g.emoji} ${st.name} <small>(${st.score}점)</small></h3>
      <div>${st.addr || ""}</div>
      <div class="price-line">${fuelName} ${price}</div>
      <div class="score-detail">${Score.explain(st).join("<br>")}</div>
    </div>`;
  }

  function render(stations, fuel) {
    layer.clearLayers();
    markers.clear();
    stations.forEach(st => {
      const m = L.marker([st.lat, st.lon], { icon: pinIcon(st) })
        .bindPopup(popupHtml(st, fuel));
      layer.addLayer(m);
      markers.set(st.id, m);
    });
  }

  function focus(st) {
    map.setView([st.lat, st.lon], 14);
    const m = markers.get(st.id);
    if (m) m.openPopup();
  }

  function locate(onFound) {
    map.locate({ setView: true, maxZoom: 13 });
    map.once("locationfound", e => onFound && onFound(e));
  }

  return {
    init, render, focus, locate,
    get bounds() { return map.getBounds(); },
    onMove(fn) { map.on("moveend", fn); },
  };
})();
