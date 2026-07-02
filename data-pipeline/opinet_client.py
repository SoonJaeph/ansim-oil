"""오피넷(한국석유공사) 무료 API 클라이언트.

무료 API 목록 근거: https://www.opinet.co.kr/user/custapi/custApiInfo.do
- areaCode.do      : 지역코드(시도/시군구) 조회
- lowTop10.do      : 전국/지역별 최저가 주유소 Top20
- aroundAll.do     : 반경 내 주유소 검색 (KATEC 좌표)
- detailById.do    : 주유소 상세(주소, 상표, 품질인증(KPETRO_YN), 가격, 좌표)
- avgSigunPrice.do : 시군구별 평균가격
"""
import time
import requests

from config import OPINET_API_KEY, OPINET_BASE, REQUEST_DELAY_SEC

session = requests.Session()
session.headers.update({"User-Agent": "AnsimOil/1.0 (public data contest)"})


def _get(endpoint: str, **params) -> dict:
    params.setdefault("code", OPINET_API_KEY)
    params.setdefault("out", "json")
    resp = session.get(f"{OPINET_BASE}/{endpoint}", params=params, timeout=30)
    resp.raise_for_status()
    time.sleep(REQUEST_DELAY_SEC)
    data = resp.json()
    return data.get("RESULT", {}).get("OIL", [])


def area_codes(area: str = "") -> list:
    """시도(area 미지정) 또는 시군구(area=시도코드) 지역코드 목록."""
    return _get("areaCode.do", area=area)


def low_top20(prodcd: str, area: str) -> list:
    """지역(시군구코드)별 최저가 주유소 Top20."""
    return _get("lowTop10.do", prodcd=prodcd, area=area, cnt=20)


def around_all(x: float, y: float, radius: int = 5000, prodcd: str = "B027", sort: int = 1) -> list:
    """반경 내 주유소 (KATEC 좌표, radius 최대 5000m)."""
    return _get("aroundAll.do", x=x, y=y, radius=radius, prodcd=prodcd, sort=sort)


def detail_by_id(station_id: str) -> dict:
    """주유소 상세정보. KPETRO_YN(품질인증), 좌표, 상표, 부가서비스 포함."""
    rows = _get("detailById.do", id=station_id)
    return rows[0] if rows else {}


def avg_sigun_price(sido: str, prodcd: str) -> list:
    """시군구별 평균가격 (참고 지표용)."""
    return _get("avgSigunPrice.do", area=sido, prodcd=prodcd)
