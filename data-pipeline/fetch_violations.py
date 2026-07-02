"""오피넷 불법행위 공표사항 수집 (한국석유공사).

지자체가 공표한 가짜석유·품질부적합·정량미달 등 위반 업소 목록.
페이지: https://www.opinet.co.kr/dlarSelect.do (POST, 시도별 페이징)
"""
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

URL = "https://www.opinet.co.kr/dlarSelect.do"
SIDO_CODES = ["01", "02", "03", "04", "05", "06", "08", "09",
              "10", "11", "14", "15", "17", "18", "19", "20"]
HEADERS = {"User-Agent": "AnsimOil/1.0 (public data contest)"}


def _parse_rows(html: str) -> list:
    """공표 테이블 → [{type, biz, name, addr, ceo}]"""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for tr in soup.select("table tbody tr"):
        tds = [td.get_text(strip=True) for td in tr.select("td")]
        if len(tds) >= 5 and tds[2]:
            out.append({"type": tds[0], "biz": tds[1], "name": tds[2],
                        "addr": tds[3], "ceo": tds[4]})
    return out


def fetch_all(only_stations=True, delay=0.3) -> list:
    """전 시도 × 전 페이지 수집. only_stations=True면 업종=주유소만."""
    sess = requests.Session()
    sess.headers.update(HEADERS)
    sess.get(URL, timeout=30)  # 세션 쿠키 확보

    results, seen = [], set()
    for sido in SIDO_CODES:
        page = 1
        while True:
            resp = sess.post(URL, data={
                "pageIndex": page, "initFlag": "N",
                "sido_cd": sido, "serch_sido_cd": sido,
                "sigun_cd": "", "serch_sigun_cd": "",
                "DIV_CD": "", "OS_NM": "", "CEO_NM": "", "ACT": "",
            }, timeout=30)
            rows = _parse_rows(resp.text)
            new = [r for r in rows
                   if (r["name"], r["addr"]) not in seen]
            if not new:
                break
            for r in new:
                seen.add((r["name"], r["addr"]))
                if not only_stations or "주유소" in r["biz"]:
                    results.append(r)
            page += 1
            time.sleep(delay)
        print(f"  시도 {sido}: 누적 {len(results)}건", file=sys.stderr)
    return results


def to_kpetro_schema(violations: list) -> list:
    """build_score 매칭용 스키마로 변환."""
    from fetch_kpetro import normalize_name, normalize_addr
    return [{"name": v["name"], "addr": v["addr"],
             "name_norm": normalize_name(v["name"]),
             "addr_norm": normalize_addr(v["addr"]),
             "vtype": v["type"]} for v in violations]


if __name__ == "__main__":
    vs = fetch_all()
    print(f"불법행위 공표(주유소) {len(vs)}건")
    print(vs[:3])
