/* app.js — 초기화 및 모듈 연결 */
(async function main() {
  MapView.init();
  const meta = await Data.load();

  function refresh() {
    const rows = Data.query(UI.state);
    MapView.render(rows.slice(0, 500), UI.state.fuel);
    UI.renderList(rows, UI.state.fuel, st => MapView.focus(st));
    UI.renderStats(meta, rows.length);
  }

  UI.bind(refresh);
  UI.locateBtn.addEventListener("click", () => MapView.locate());
  refresh();
})();
