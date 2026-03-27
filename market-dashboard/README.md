# 📊 금융시장 변동성 모니터 — 무료 대시보드

**GitHub Pages + GitHub Actions** 조합으로 완전 무료로 운영하는 금융 지표 대시보드입니다.

---

## ✅ 포함 지표

| 지표 | 데이터 소스 | 임계값 기준 |
|------|------------|------------|
| VIX | Yahoo Finance | 20↑경계, 30↑위험 |
| SKEW | Yahoo Finance | 130↑경계, 140↑극단 |
| OVX (원유 변동성) | Yahoo Finance | 40↑경계, 60↑위험 |
| GVZ (금 변동성) | Yahoo Finance | 15↑경계, 25↑위험 |
| PCR (Put/Call) | Yahoo Finance | 0.6↓과열, 1.3↑패닉 |
| HY 스프레드 | FRED | 5%↑경계, 7%↑위험 |
| IG 스프레드 | FRED | 1.5%↑경계, 2.5%↑위험 |
| TED 스프레드 | FRED | 50bp↑경계, 100bp↑위험 |
| SOFR | FRED | 참고용 |

---

## 🚀 세팅 방법 (30분 이내 완료)

### 1단계: GitHub 저장소 생성
1. [github.com](https://github.com) 로그인 → **New repository**
2. 저장소 이름: `market-monitor` (또는 원하는 이름)
3. **Public** 선택 → Create repository

### 2단계: 파일 업로드
이 폴더 안의 파일들을 저장소에 업로드:
```
index.html
data.json
fetch_data.py
requirements.txt
.github/workflows/update.yml
```
> Git이 낯설다면 GitHub 웹사이트에서 직접 드래그앤드롭으로 업로드 가능

### 3단계: FRED API 키 발급 (무료, 3분)
1. [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html) 접속
2. 이메일 가입 → API 키 발급 (즉시 발급됨)

### 4단계: GitHub Secrets 등록
1. 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
   - Name: `FRED_API_KEY`
   - Value: 발급받은 API 키 붙여넣기
3. Save

### 5단계: GitHub Pages 활성화
1. 저장소 → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / `/ (root)` 선택 → Save
4. 1~2분 후 `https://[유저명].github.io/market-monitor/` 접속 가능

### 6단계: 첫 데이터 수집 실행
1. 저장소 → **Actions** 탭
2. **시장 지표 자동 업데이트** 워크플로우 클릭
3. **Run workflow** 버튼 클릭 → 30초 후 완료

---

## ⏰ 자동 업데이트 스케줄
평일 KST 기준 하루 3회 자동 실행:
- **오전 7:00** (미국 전날 마감 후)
- **오후 3:00** (한국 장 마감 후)
- **오후 11:00** (미국 장 중)

수동 실행은 Actions 탭 → Run workflow

---

## 🔧 지표 추가하기

`fetch_data.py`의 `main()` 함수에 새 항목 추가:
```python
# FRED 시리즈 ID는 https://fred.stlouisfed.org 에서 검색
cdx_ig = get_fred("DPCREDIT")  # 예시
```

`index.html`의 `INDICATORS` 객체에 임계값 정의 추가.

---

## ⚠️ 무료 플랜 제한사항
- **MOVE Index**: ICE 독점 데이터 → 무료 제공 없음
- **FRA-OIS**: Bloomberg 전용 → SOFR로 대체 모니터링
- **업데이트 주기**: 실시간이 아닌 하루 3회 (GitHub Actions 무료 플랜)
- **GitHub Actions 무료 한도**: 월 2,000분 (하루 3회 × 30일 = 약 90분 사용, 여유 있음)
