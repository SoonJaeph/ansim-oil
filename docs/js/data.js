/* data.js — stations.json 로드 및 필터/정렬 */
const Data = (() => {
  let all = [];
  let meta = {};

  async function load() {
    let json;
    try {
      const res = await fetch("data/stations.json");
      if (!res.ok) throw new Error(res.status);
      json = await res.json();
    } catch (e) {
      // file:// 로 열었을 때 등 fetch 불가 시 stations.js 폴백 사용
      json = window.STATIONS_FALLBACK || { stations: [], stats: {} };
    }
    all = json.stations || [];
    meta = { updated: json.updated, stats: json.stats, sources: json.sources };
    detectAnomalies(all);
    return meta;
  }

  /** 이상 저가 탐지: 같은 시군구 평균 대비 12% 이상 싸면 플래그.
   *  비정상적 저가는 가짜석유·정량미달의 대표적 신호. */
  function detectAnomalies(stations) {
    ["B027", "D047"].forEach(fuel => {
      const groups = {};
      stations.forEach(s => {
        const p = s.prices && s.prices[fuel];
        if (!p) return;
        const key = `${s.sido}|${s.sigungu}`;
        (groups[key] = groups[key] || []).push(p);
      });
      const avg = {};
      Object.entries(groups).forEach(([k, arr]) => {
        avg[k] = arr.reduce((a, b) => a + b, 0) / arr.length;
      });
      stations.forEach(s => {
        const p = s.prices && s.prices[fuel];
        const a = avg[`${s.sido}|${s.sigungu}`];
        if (p && a && p < a * 0.88) {
          (s.anomaly = s.anomaly || {})[fuel] = Math.round(a - p);
        }
      });
    });
  }

  /** 필터: 검색어(지역/상호), 유종 보유 여부 → 정렬: 안심순/최저가순 */
  function query({ keyword = "", fuel = "B027", mode = "safe", bounds = null } = {}) {
    const kw = keyword.trim();
    let rows = all.filter(s => s.prices && s.prices[fuel]);
    if (kw) {
      rows = rows.filter(s =>
        (s.name && s.name.includes(kw)) ||
        (s.addr && s.addr.includes(kw)) ||
        (s.sigungu && s.sigungu.includes(kw)) ||
        (s.sido && s.sido.includes(kw)));
    }
    if (bounds) {
      rows = rows.filter(s => bounds.contains([s.lat, s.lon]));
    }
    rows.sort(mode === "price"
      ? (a, b) => a.prices[fuel] - b.prices[fuel]
      : (a, b) => (b.score - a.score) || (a.prices[fuel] - b.prices[fuel]));
    return rows;
  }

  return { load, query, get meta() { return meta; } };
})();
