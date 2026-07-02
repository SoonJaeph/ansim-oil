/* ui.js — 검색·필터·목록 패널 */
const UI = (() => {
  const els = {
    search: document.getElementById("search"),
    fuel: document.getElementById("fuel"),
    modePrice: document.getElementById("mode-price"),
    modeSafe: document.getElementById("mode-safe"),
    locate: document.getElementById("locate"),
    list: document.getElementById("list"),
    statsbar: document.getElementById("statsbar"),
    updated: document.getElementById("updated"),
  };
  const state = { keyword: "", fuel: "B027", mode: "safe" };
  let onChange = () => {};

  function bind(handler) {
    onChange = handler;
    let t;
    els.search.addEventListener("input", () => {
      clearTimeout(t);
      t = setTimeout(() => { state.keyword = els.search.value; onChange(); }, 250);
    });
    els.fuel.addEventListener("change", () => { state.fuel = els.fuel.value; onChange(); });
    els.modePrice.addEventListener("click", () => setMode("price"));
    els.modeSafe.addEventListener("click", () => setMode("safe"));
  }

  function setMode(mode) {
    state.mode = mode;
    els.modePrice.classList.toggle("active", mode === "price");
    els.modeSafe.classList.toggle("active", mode === "safe");
    onChange();
  }

  function cardHtml(st, fuel) {
    const g = Score.gradeMeta(st.grade);
    let badges = st.badges.map(b => {
      const m = Score.badgeMeta(b);
      return m ? `<span class="badge ${b}" title="${m.title}">${m.label}</span>` : "";
    }).join("");
    if (st.anomaly && st.anomaly[fuel] && st.grade !== "safe") {
      badges += `<span class="badge anomaly" title="지역 평균보다 ${st.anomaly[fuel].toLocaleString()}원 저렴 — 이상탐지 알고리즘이 감지한 비정상 저가입니다. 품질 신호를 함께 확인하세요.">⚡이상저가</span>`;
    }
    return `
      <div class="row1">
        <span class="name">${g.emoji} ${st.name}</span>
        <span class="price">${(st.prices[fuel] || 0).toLocaleString()}원</span>
      </div>
      <div class="addr">${st.addr || `${st.sido} ${st.sigungu}`}</div>
      <div class="badges">
        <span class="badge score-${g.cls}">안심지수 ${st.score}</span>${badges}
      </div>`;
  }

  function renderList(stations, fuel, onSelect) {
    els.list.innerHTML = "";
    stations.slice(0, 100).forEach(st => {
      const li = document.createElement("li");
      li.className = "station-card";
      li.innerHTML = cardHtml(st, fuel);
      li.addEventListener("click", () => onSelect(st));
      els.list.appendChild(li);
    });
  }

  function renderStats(meta, shown) {
    const s = meta.stats || {};
    els.statsbar.innerHTML =
      `전국 <b>${(s.total || 0).toLocaleString()}</b>곳 중 화면에 <b>${shown.toLocaleString()}</b>곳 · ` +
      `품질협약 <b>${(s.quality || 0).toLocaleString()}</b> · 전산보고 <b>${(s.ereport || 0).toLocaleString()}</b>`;
    if (meta.updated) els.updated.textContent = `데이터 기준일: ${meta.updated}`;
  }

  return { bind, state, renderList, renderStats, locateBtn: els.locate };
})();
