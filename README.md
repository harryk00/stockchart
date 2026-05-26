# stockchart
주식변동성차트 일일 지표 
# 📊 금융시장 변동성 모니터 (stockchart)

> 미국 금융시장의 주요 변동성·스트레스 지표를 실시간으로 모니터링하는 대시보드입니다.  
> GitHub Actions로 평일 하루 3회 자동 업데이트되며, GitHub Pages를 통해 정적 웹으로 배포됩니다.

---

## 🌐 라이브 데모

👉 https://harryk00.github.io/stockchart/market-dashboard/ 

---

## 📌 주요 기능

- **종합 시장 스트레스 지수** — 핵심 지표에 가중치를 부여한 복합 스트레스 점수 (0–100)
- **변동성 지표** — VIX, SKEW, OVX, GVZ, PCR
- **신용 스프레드** — HY Spread, IG Spread
- **단기 자금시장** — TED Spread, SOFR
- **VIX 기간구조** — VIX 1개월 vs 3개월 비교, 백워데이션/콘탱고 신호
- **거시경제 지표** — 10Y–2Y 금리역전, DXY
- **연준 공식 스트레스 지수** — STLFSI (St. Louis Fed Financial Stress Index)

---

## 🗂️ 프로젝트 구조

```
stockchart/
├── index.html                    # 대시보드 UI (Chart.js 기반)
├── market-dashboard/
│   ├── fetch_data.py             # 지표 수집 스크립트 (yfinance + FRED API)
│   ├── data.json                 # 수집된 지표 데이터 (자동 갱신)
│   └── requirements.txt          # Python 의존성
└── .github/
    └── workflows/
        └── update.yml            # GitHub Actions 자동 업데이트 워크플로우
```

---

## 📈 수집 지표 목록

| 지표 | 이름 | 데이터 소스 | 비고 |
|------|------|------------|------|
| VIX | CBOE 변동성 지수 | Yahoo Finance | 가중치 20% |
| SKEW | CBOE SKEW 지수 | Yahoo Finance | 가중치 10% |
| OVX | 원유 변동성 지수 | Yahoo Finance | 가중치 8% |
| GVZ | 금 변동성 지수 | Yahoo Finance | 가중치 7% |
| PCR | Put/Call Ratio | Yahoo Finance | — |
| HY_SPREAD | 미 하이일드 스프레드 | FRED | 가중치 22% |
| IG_SPREAD | 투자등급 회사채 스프레드 | FRED | 가중치 13% |
| TED_SPREAD | TED 스프레드 | FRED | 가중치 10% |
| SOFR | SOFR 금리 | FRED | 참고용 |
| VIX_DIFF | VIX 기간구조 (1M–3M) | Yahoo Finance | 가중치 10% |
| T10Y2Y | 장단기 금리역전 | FRED | — |
| DXY | 달러 인덱스 | Yahoo Finance | — |
| STLFSI | 연준 금융 스트레스 지수 | FRED | — |

> ⚠️ MOVE Index / FRA-OIS: ICE 전용 유료 데이터로 무료 API 미제공 → SOFR로 대체 모니터링

---

## ⚙️ 스트레스 점수 산출 방식

각 지표를 정규화(0–100)한 뒤 아래 가중치로 합산합니다.

```
HY_SPREAD  × 0.22
VIX        × 0.20
IG_SPREAD  × 0.13
TED_SPREAD × 0.10
VIX_DIFF   × 0.10
SKEW       × 0.10
OVX        × 0.08
GVZ        × 0.07
```

| 구간 | 상태 |
|------|------|
| 0–39 | 🟢 정상 |
| 40–59 | 🟡 경계 |
| 60–100 | 🔴 위험 |

---

## 🔄 자동 업데이트

GitHub Actions로 **평일 KST 15:00 · 23:00 · 07:00** 에 자동 갱신됩니다.

```yaml
schedule:
  - cron: "0 6,14,22 * * 1-5"   # UTC 기준 (= KST 15/23/07시)
```

`fetch_data.py`가 Yahoo Finance와 FRED API에서 최신 데이터를 수집하여 `data.json`을 업데이트하고 자동 커밋합니다.

> FRED 데이터는 T+1일 지연 공표됩니다.

---

## 🛠️ 로컬 실행 방법

```bash
# 의존성 설치
pip install -r market-dashboard/requirements.txt

# FRED API 키 환경변수 설정 (https://fred.stlouisfed.org/docs/api/api_key.html)
export FRED_API_KEY=your_api_key_here

# 데이터 수집
cd market-dashboard
python fetch_data.py

# 대시보드 로컬 서버 실행
cd ..
python -m http.server 8000
# → http://localhost:8000 접속
```

---

## 🧱 기술 스택

| 구분 | 사용 기술 |
|------|----------|
| Frontend | HTML, CSS, JavaScript, Chart.js 4.4 |
| 데이터 수집 | Python, yfinance, requests |
| 자동화 | GitHub Actions |
| 배포 | GitHub Pages |
| 데이터 소스 | FRED (St. Louis Fed), Yahoo Finance, CBOE |

---

## 📄 데이터 출처

- [FRED (St. Louis Fed)](https://fred.stlouisfed.org)
- Yahoo Finance
- CBOE

---

## 📝 License

MIT
