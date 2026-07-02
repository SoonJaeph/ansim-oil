"""오피넷 데이터 수집: 전국 시군구별 최저가 Top20 + 상세정보(품질인증·좌표).

KATEC(TM128) → WGS84 좌표 변환 포함.
산출: 주유소 딕셔너리 리스트 (UNI_ID 기준 중복 제거)
"""
import json
import sys

from pyproj import Transformer

import opinet_client as api
from config import PRODUCTS, RAW_DIR

# 오피넷 KATEC 좌표계 정의 (통용 파라미터)
KATEC = ("+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 "
         "+ellps=bessel +units=m +no_defs "
         "+towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43")
_transformer = Transformer.from_pipeline(
    f"+proj=pipeline +step +inv {KATEC} +step +proj=unitconvert +xy_in=rad +xy_out=deg")


def katec_to_wgs84(x: float, y: float):
    lon, lat = _transformer.transform(x, y)
    return round(lat, 6), round(lon, 6)


def collect_stations(progress=True) -> dict:
    """전국 시군구 × 제품별 최저가 Top20 수집 후 UNI_ID로 병합."""
    stations = {}
    sidos = api.area_codes()
    for sido in sidos:
        sigungus = api.area_codes(area=sido["AREA_CD"])
        for sgg in sigungus:
            for prodcd in PRODUCTS:
                for row in api.low_top20(prodcd, sgg["AREA_CD"]):
                    uid = row["UNI_ID"]
                    st = stations.setdefault(uid, {
                        "id": uid,
                        "name": row.get("OS_NM", ""),
                        "brand": row.get("POLL_DIV_CD", ""),
                        "addr": row.get("NEW_ADR") or row.get("VAN_ADR", ""),
                        "sido": sido["AREA_NM"],
                        "sigungu": sgg["AREA_NM"],
                        "prices": {},
                    })
                    st["prices"][prodcd] = int(float(row.get("PRICE", 0)))
                    if "lat" not in st and row.get("GIS_X_COOR"):
                        lat, lon = katec_to_wgs84(
                            float(row["GIS_X_COOR"]), float(row["GIS_Y_COOR"]))
                        st["lat"], st["lon"] = lat, lon
            if progress:
                print(f"  {sido['AREA_NM']} {sgg['AREA_NM']}: 누적 {len(stations)}곳",
                      file=sys.stderr)
    return stations


def enrich_details(stations: dict, progress=True) -> None:
    """상세 API로 품질인증(KPETRO_YN)·주소·부가정보 보강."""
    for i, (uid, st) in enumerate(stations.items()):
        d = api.detail_by_id(uid)
        if not d:
            continue
        st["kpetro_cert"] = d.get("KPETRO_YN", "N") == "Y"
        st["self"] = d.get("SELF_YN", "N") == "Y"
        if not st.get("addr"):
            st["addr"] = d.get("NEW_ADR") or d.get("VAN_ADR", "")
        if "lat" not in st and d.get("GIS_X_COOR"):
            lat, lon = katec_to_wgs84(float(d["GIS_X_COOR"]), float(d["GIS_Y_COOR"]))
            st["lat"], st["lon"] = lat, lon
        if progress and i % 200 == 0:
            print(f"  상세보강 {i}/{len(stations)}", file=sys.stderr)


def save_cache(stations: dict, path=None):
    path = path or (RAW_DIR / "opinet_stations.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stations, f, ensure_ascii=False)
    print(f"저장: {path} ({len(stations)}곳)", file=sys.stderr)


if __name__ == "__main__":
    sts = collect_stations()
    enrich_details(sts)
    save_cache(sts)
