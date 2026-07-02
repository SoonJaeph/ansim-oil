"""공통 설정: 경로, API 키, 상수."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data-raw"
OUT_DIR = BASE_DIR / "docs" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 오피넷 API (한국석유공사) — 환경변수로 주입
OPINET_API_KEY = os.environ.get("OPINET_API_KEY", "")
OPINET_BASE = "https://www.opinet.co.kr/api"

# 제품코드: 휘발유 B027, 경유 D047, 고급휘발유 B034, 등유 C004
PRODUCTS = {"B027": "휘발유", "D047": "경유"}

# 석유관리원 CSV 파일명 패턴 (data-raw/ 안에서 자동 탐색)
KPETRO_QUALITY_PATTERN = "*품질관리*협약*"   # 석유품질관리지원협약주유소
KPETRO_EREPORT_PATTERN = "*전산보고*"        # 전산보고 주유소

# 안심지수 가중치
SCORE_QUALITY = 40    # 품질관리협약
SCORE_EREPORT = 30    # 전산보고
SCORE_NO_VIOLATION = 30  # 불법행위(가짜석유 등) 적발 이력 없음

# 등급 컷
GRADE_SAFE = 80   # 🟢 안심
GRADE_GOOD = 50   # 🔵 양호

REQUEST_DELAY_SEC = 0.15  # API 호출 간격 (예의상 스로틀)
