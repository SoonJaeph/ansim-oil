/* score.js — 안심지수 등급·뱃지 표현 로직 (표시 전용) */
const Score = (() => {
  const GRADE_META = {
    safe:    { label: "안심",     emoji: "🟢", cls: "safe" },
    good:    { label: "양호",     emoji: "🔵", cls: "good" },
    basic:   { label: "정보부족", emoji: "⚪", cls: "basic" },
    warning: { label: "주의",     emoji: "⚠️", cls: "warning" },
  };
  const BADGE_META = {
    quality:   { label: "품질협약", title: "한국석유관리원 석유품질관리지원협약 주유소" },
    ereport:   { label: "전산보고", title: "판매량 자동집계 보고(임의수정 불가) 주유소" },
    violation: { label: "적발이력", title: "불법행위 공표 이력 있음" },
  };

  const gradeMeta = g => GRADE_META[g] || GRADE_META.basic;
  const badgeMeta = b => BADGE_META[b];

  /** 점수 구성 설명(팝업용) */
  function explain(st) {
    const parts = [];
    parts.push(st.badges.includes("quality")
      ? "✅ 품질관리협약 주유소 (+40)" : "▫️ 품질관리협약 미가입");
    parts.push(st.badges.includes("ereport")
      ? "✅ 전산보고 주유소 (+30)" : "▫️ 전산보고 미참여");
    parts.push(st.badges.includes("violation")
      ? "🚨 불법행위 공표 이력 있음" : "✅ 적발 이력 없음 (+30)");
    return parts;
  }

  return { gradeMeta, badgeMeta, explain };
})();
