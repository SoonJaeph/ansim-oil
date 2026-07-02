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
    return meta;
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
