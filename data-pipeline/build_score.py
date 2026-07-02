"""데이터 병합 + 안심지수 계산 → web/data/stations.json 생성.

매칭 전략: 오피넷 주유소 ↔ 석유관리원 리스트를
 1) 정규화 상호 + 시군구 일치  2) 정규화 주소 앞부분 일치
두 단계로 매칭한다 (주유소는 상호 변경이 잦아 주소 백업 매칭 필수).
"""
import json
import sys
from datetime import date

from config import (OUT_DIR, SCORE_QUALITY, SCORE_EREPORT, SCORE_NO_VIOLATION,
                    GRADE_SAFE, GRADE_GOOD)
from fetch_kpetro import normalize_name, normalize_addr


def _addr_key(addr_norm: str) -> str:
    """공백 제거 후 앞 14자 — '문장로146'/'문장로 146' 표기 차이 흡수."""
    return addr_norm.replace(" ", "")[:14]


def _index(kpetro_list: list) -> tuple:
    by_name = {}
    by_addr = {}
    for s in kpetro_list:
        if s["name_norm"]:
            by_name.setdefault(s["name_norm"], []).append(s)
        if s["addr_norm"]:
            by_addr[_addr_key(s["addr_norm"])] = s
    return by_name, by_addr


def _match(station: dict, by_name: dict, by_addr: dict) -> bool:
    name_n = normalize_name(station["name"])
    addr_n = normalize_addr(station.get("addr", ""))
    addr_compact = addr_n.replace(" ", "")
    for cand in by_name.get(name_n, []):
        # 상호 동일 + 시군구(주소 앞부분) 일치
        if cand["addr_norm"].replace(" ", "")[:6] == addr_compact[:6]:
            return True
    return _addr_key(addr_n) in by_addr if addr_n else False


def score_station(st: dict, in_quality: bool, in_ereport: bool,
                  violated: bool) -> None:
    score = 0
    badges = []
    if in_quality or st.get("kpetro_cert"):
        score += SCORE_QUALITY
        badges.append("quality")
    if in_ereport:
        score += SCORE_EREPORT
        badges.append("ereport")
    if violated:
        badges.append("violation")
        score = min(score, 20)  # 적발 이력 시 강한 페널티
        grade = "warning"
    else:
        score += SCORE_NO_VIOLATION
        grade = ("safe" if score >= GRADE_SAFE
                 else "good" if score >= GRADE_GOOD else "basic")
    st["score"] = score
    st["grade"] = grade
    st["badges"] = badges


def build(opinet_stations: dict, quality_list: list, ereport_list: list,
          violation_list: list | None = None) -> dict:
    q_name, q_addr = _index(quality_list)
    e_name, e_addr = _index(ereport_list)
    v_name, v_addr = _index(violation_list or [])

    out = []
    stats = {"quality": 0, "ereport": 0, "violation": 0}
    for st in opinet_stations.values():
        if "lat" not in st:
            continue
        in_q = _match(st, q_name, q_addr)
        in_e = _match(st, e_name, e_addr)
        in_v = _match(st, v_name, v_addr)
        score_station(st, in_q, in_e, in_v)
        stats["quality"] += in_q
        stats["ereport"] += in_e
        stats["violation"] += in_v
        out.append(st)

    result = {
        "updated": date.today().isoformat(),
        "sources": [
            "한국석유공사 오피넷 유가정보 API",
            "한국석유관리원 석유품질관리지원협약주유소",
            "한국석유관리원 전산보고",
        ],
        "stats": {"total": len(out), **stats},
        "stations": out,
    }
    print(f"병합 결과: {stats}", file=sys.stderr)
    return result


def save(result: dict):
    payload = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    path = OUT_DIR / "stations.json"
    path.write_text(payload, encoding="utf-8")
    # file:// 시연용 폴백 (fetch 불가 환경 대비)
    (OUT_DIR / "stations.js").write_text(
        "window.STATIONS_FALLBACK=" + payload + ";", encoding="utf-8")
    print(f"저장: {path} ({result['stats']['total']}곳)", file=sys.stderr)
