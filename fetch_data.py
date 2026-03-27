"""
금융시장 변동성 지표 수집 스크립트
- Yahoo Finance: VIX, VIX3M, SKEW, OVX, GVZ, PCR
- FRED API (무료): HY Spread, IG Spread, TED Spread, SOFR
- VIX 백워데이션 연속 거래일 추적
"""

import yfinance as yf
import requests
import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")


def get_yahoo(ticker: str) -> float | None:
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d")
        if not hist.empty:
            return round(float(hist["Close"].dropna().iloc[-1]), 2)
    except Exception as e:
        print(f"  [Yahoo 오류] {ticker}: {e}")
    return None


def get_fred(series_id: str) -> float | None:
    if not FRED_API_KEY:
        print(f"  [FRED 건너뜀] API 키 없음 ({series_id})")
        return None
    try:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 5,
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        for obs in r.json().get("observations", []):
            val = obs.get("value", ".")
            if val not in (".", ""):
                return round(float(val), 3)
    except Exception as e:
        print(f"  [FRED 오류] {series_id}: {e}")
    return None


def load_existing_data() -> dict:
    """기존 data.json 읽기 (백워데이션 연속일 추적용)"""
    try:
        # 경로 수정: market-dashboard 폴더 안의 데이터를 읽음
        with open("market-dashboard/data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def calc_backwardation_days(existing: dict, vix_diff: float | None) -> dict:
    """
    백워데이션(vix_diff > 0) 연속 거래일 계산 (수정본)
    """
    if vix_diff is None:
        return existing.get("backwardation", {})

    is_backwardation = vix_diff > 0

    # 1. KST 대신 미국 동부 시간(New_York) 기준으로 날짜 판별
    today_est = datetime.now(timezone.utc).astimezone(
        ZoneInfo("America/New_York")
    ).strftime("%Y-%m-%d")

    prev = existing.get("backwardation", {})
    history = prev.get("history", [])

    # 2. 히스토리 기록 (같은 거래일이면 덮어쓰고, 아니면 새로 추가)
    if history and history[-1]["date"] == today_est:
        history[-1]["diff"] = vix_diff
        history[-1]["backwardation"] = is_backwardation
    else:
        history.append({
            "date": today_est,
            "diff": vix_diff,
            "backwardation": is_backwardation
        })
        history = history[-15:] # 최근 15일 유지

    # 3. 연속 백워데이션 일수 '전면 재계산' (버그 원천 차단)
    consecutive = 0
    for day in reversed(history):
        if day.get("backwardation", False):
            consecutive += 1
        else:
            break

    # 4. 위험 상태 판정
    if not is_backwardation:
        status = "normal"
    elif consecutive >= 7:
        status = "crisis"    # 매우 심각한 위기
    elif consecutive >= 5:
        status = "danger"    # 위험
    elif consecutive >= 1:
        status = "warn"      # 백워데이션 시작

    print(f"  백워데이션 연속일: {consecutive}일 ({status})")

    return {
        "consecutive_days": consecutive,
        "last_date": today_est, # EST 기준으로 저장
        "status": status,
        "is_backwardation": is_backwardation,
        "history": history
    }


def main():
    print(f"📡 데이터 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    existing = load_existing_data()

    print("\n[Yahoo Finance]")
    vix   = get_yahoo("^VIX");   print(f"  VIX:   {vix}")
    vix3m = get_yahoo("^VIX3M"); print(f"  VIX3M: {vix3m}")
    skew  = get_yahoo("^SKEW");  print(f"  SKEW:  {skew}")
    ovx   = get_yahoo("^OVX");   print(f"  OVX:   {ovx}")
    gvz   = get_yahoo("^GVZ");   print(f"  GVZ:   {gvz}")
    pcr   = get_yahoo("^PCCE");  print(f"  PCR:   {pcr}")

    vix_diff = round(vix - vix3m, 2) if vix is not None and vix3m is not None else None
    print(f"  VIX 기간구조 차이(1m-3m): {vix_diff}")

    print("\n[FRED API]")
    hy_spread = get_fred("BAMLH0A0HYM2"); print(f"  HY Spread: {hy_spread}")
    ig_spread = get_fred("BAMLC0A0CM");   print(f"  IG Spread: {ig_spread}")
    ted       = get_fred("TEDRATE");      print(f"  TED Spread: {ted}")
    sofr      = get_fred("SOFR");         print(f"  SOFR: {sofr}")

    print("\n[백워데이션 추적]")
    backwardation = calc_backwardation_days(existing, vix_diff)

    output = {
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "updated_kst": datetime.now(timezone.utc).astimezone(
            ZoneInfo("Asia/Seoul")
        ).strftime("%Y-%m-%d %H:%M KST"),
        "backwardation": backwardation,
        "indicators": {
            "VIX":        {"value": vix,       "unit": "",   "source": "Yahoo"},
            "VIX3M":      {"value": vix3m,     "unit": "",   "source": "Yahoo"},
            "VIX_DIFF":   {"value": vix_diff,  "unit": "",   "source": "Yahoo"},
            "SKEW":       {"value": skew,      "unit": "",   "source": "Yahoo"},
            "OVX":        {"value": ovx,       "unit": "",   "source": "Yahoo"},
            "GVZ":        {"value": gvz,       "unit": "",   "source": "Yahoo"},
            "PCR":        {"value": pcr,       "unit": "",   "source": "Yahoo"},
            "HY_SPREAD":  {"value": hy_spread, "unit": "%",  "source": "FRED"},
            "IG_SPREAD":  {"value": ig_spread, "unit": "%",  "source": "FRED"},
            "TED_SPREAD": {"value": ted,       "unit": "bp", "source": "FRED"},
            "SOFR":       {"value": sofr,      "unit": "%",  "source": "FRED"},
        },
    }

    # 경로 수정: market-dashboard 폴더 안에 확실하게 저장
    with open("market-dashboard/data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ data.json 저장 완료")


if __name__ == "__main__":
    main()
