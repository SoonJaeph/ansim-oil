# 안심주유 (Ansim-Oil)

**가격보다 믿음을 채우는 주유소 지도** — 제14회 산업통상부 공공데이터 활용 아이디어 공모전 출품작 (제품 및 서비스 부문)

## 서비스 개요

기존 유가 서비스는 "싼 주유소"만 알려줍니다. 안심주유는 산업통상부 산하기관 공공데이터를 결합해
주유소별 **안심지수**를 산출, "싸면서도 믿을 수 있는 주유소"를 알려줍니다.

## 활용 공공데이터

| 데이터 | 제공기관 | 용도 |
|---|---|---|
| 석유품질관리지원협약주유소 | 한국석유관리원 | 품질인증 신호 (+) |
| 전산보고 주유소 | 한국석유관리원 | 투명거래 신호 (+) |
| 주유소 판매가격 (오피넷 API) | 한국석유공사 | 실시간 가격·위치 |
| 가짜석유판매업소 공표 (오피넷 API) | 한국석유공사 | 위험 신호 (−) |

## 프로젝트 구조 (기능별 모듈화)

```
ansim-oil/
├── data-pipeline/          # 데이터 수집·정제·점수화 (Python)
│   ├── config.py           # 공통 설정·경로·API 키
│   ├── fetch_opinet.py     # 오피넷 API: 가격, 주유소 위치, 가짜석유 공표
│   ├── fetch_kpetro.py     # 석유관리원 CSV: 품질협약, 전산보고 로드·정제
│   ├── build_score.py      # 데이터 병합 + 안심지수 계산
│   └── run_pipeline.py     # 전체 파이프라인 실행 → docs/data/stations.json
├── docs/                    # 정적 웹앱 (GitHub Pages 배포)
│   ├── index.html
│   ├── css/style.css
│   ├── js/
│   │   ├── data.js         # stations.json 로드
│   │   ├── score.js        # 안심지수 등급/뱃지 로직
│   │   ├── map.js          # Leaflet 지도 렌더링
│   │   └── ui.js           # 검색·필터·패널 UI
│   └── data/stations.json  # 파이프라인 산출물
├── data-raw/               # 원본 CSV (git 제외)
└── .github/workflows/      # 매일 자동 데이터 갱신 (GitHub Actions)
```

## 안심지수 산정 (100점 만점)

- 품질관리협약 주유소: +40
- 전산보고 주유소: +30
- 가짜석유 적발 이력 없음: +30 (적발 이력 시 0점 + 경고 표시)
- 등급: 80↑ 🟢안심 / 50↑ 🔵양호 / 그 외 ⚪정보부족 / 적발이력 ⚠️주의

## 실행

```bash
pip install -r data-pipeline/requirements.txt
OPINET_API_KEY=<키> python data-pipeline/run_pipeline.py
# docs/ 폴더를 정적 서버로 서빙
```
