"""한국석유관리원 CSV 로드·정제.

- 석유품질관리지원협약주유소: 소비자가 믿을 수 있도록 품질을 수시 관리받는 주유소
- 전산보고 주유소: 판매량 자동집계 보고(임의수정 불가) 주유소
CSV는 data.go.kr에서 다운로드하여 data-raw/에 배치 (EUC-KR/CP949 대응).
"""
import csv
import re
import sys
from pathlib import Path

from config import RAW_DIR, KPETRO_QUALITY_PATTERN, KPETRO_EREPORT_PATTERN


def _find_csv(pattern: str) -> Path:
    matches = sorted(RAW_DIR.glob(pattern.rstrip("*") + "*.csv"))
    if not matches:
        raise FileNotFoundError(f"data-raw/에서 '{pattern}' CSV를 찾지 못했습니다.")
    return matches[-1]  # 최신 파일


def _read_csv(path: Path) -> list:
    for enc in ("cp949", "euc-kr", "utf-8-sig", "utf-8"):
        try:
            with open(path, encoding=enc, newline="") as f:
                rows = list(csv.DictReader(f))
            if rows:
                print(f"로드: {path.name} ({len(rows)}행, {enc})", file=sys.stderr)
                return rows
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise UnicodeError(f"인코딩 판별 실패: {path}")


def normalize_name(name: str) -> str:
    """상호 정규화: 법인표기·공백·괄호 제거로 매칭률 향상."""
    if not name:
        return ""
    n = re.sub(r"[\s()\[\]㈜]|주식회사|\(주\)|유한회사", "", name)
    n = re.sub(r"(주유소|셀프|직영|self)$", "", n, flags=re.I)
    return n.lower()


def normalize_addr(addr: str) -> str:
    """주소 정규화: 시도 축약 통일 + 번지 앞까지."""
    if not addr:
        return ""
    a = addr.strip()
    repl = {"서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구",
            "인천광역시": "인천", "광주광역시": "광주", "대전광역시": "대전",
            "울산광역시": "울산", "세종특별자치시": "세종", "경기도": "경기",
            "강원특별자치도": "강원", "강원도": "강원", "충청북도": "충북",
            "충청남도": "충남", "전북특별자치도": "전북", "전라북도": "전북",
            "전라남도": "전남", "경상북도": "경북", "경상남도": "경남",
            "제주특별자치도": "제주"}
    for k, v in repl.items():
        a = a.replace(k, v)
    return re.sub(r"\s+", " ", a)


def _pick(row: dict, *candidates) -> str:
    """컬럼명이 연도별로 조금씩 달라도 견디도록 후보명으로 조회."""
    for key in row:
        for cand in candidates:
            if cand in key:
                return (row[key] or "").strip()
    return ""


def load_quality_stations() -> list:
    """품질관리협약주유소 → [{name, addr, name_norm, addr_norm}]"""
    rows = _read_csv(_find_csv(KPETRO_QUALITY_PATTERN))
    out = []
    for r in rows:
        name = _pick(r, "주유소명", "업소명", "상호")
        addr = _pick(r, "주소", "소재지")
        if name:
            out.append({"name": name, "addr": addr,
                        "name_norm": normalize_name(name),
                        "addr_norm": normalize_addr(addr)})
    return out


def load_ereport_stations() -> list:
    """전산보고 주유소 → 동일 스키마."""
    rows = _read_csv(_find_csv(KPETRO_EREPORT_PATTERN))
    out = []
    for r in rows:
        name = _pick(r, "주유소명", "업소명", "상호")
        addr = _pick(r, "주소", "소재지")
        if name:
            out.append({"name": name, "addr": addr,
                        "name_norm": normalize_name(name),
                        "addr_norm": normalize_addr(addr)})
    return out


if __name__ == "__main__":
    q = load_quality_stations()
    e = load_ereport_stations()
    print(f"품질협약 {len(q)}곳 / 전산보고 {len(e)}곳")
    print("샘플:", q[:2], e[:2])
