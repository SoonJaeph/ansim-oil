"""전체 파이프라인: 수집 → 정제 → 병합·점수화 → stations.json.

사용법:
  OPINET_API_KEY=<키> python run_pipeline.py            # 전체 실행
  OPINET_API_KEY=<키> python run_pipeline.py --cached   # 오피넷 캐시 재사용
"""
import json
import sys

from config import RAW_DIR, OPINET_API_KEY
import fetch_opinet
import fetch_kpetro
import build_score


def main():
    use_cache = "--cached" in sys.argv
    cache = RAW_DIR / "opinet_stations.json"

    if use_cache and cache.exists():
        stations = json.loads(cache.read_text(encoding="utf-8"))
        print(f"오피넷 캐시 사용: {len(stations)}곳", file=sys.stderr)
    else:
        if not OPINET_API_KEY:
            sys.exit("OPINET_API_KEY 환경변수가 필요합니다.")
        stations = fetch_opinet.collect_stations()
        fetch_opinet.enrich_details(stations)
        fetch_opinet.save_cache(stations, cache)

    quality = fetch_kpetro.load_quality_stations()
    ereport = fetch_kpetro.load_ereport_stations()

    try:
        import fetch_violations
        violations = fetch_violations.to_kpetro_schema(fetch_violations.fetch_all())
    except Exception as e:  # 공표 페이지 변경 등에도 파이프라인은 계속
        print(f"불법행위 공표 수집 실패(건너뜀): {e}", file=sys.stderr)
        violations = []

    result = build_score.build(stations, quality, ereport, violations)
    build_score.save(result)


if __name__ == "__main__":
    main()
