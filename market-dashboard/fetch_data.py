"""
금융시장 변동성 지표 수집 스크립트
추가: 전일 대비 변화량, 10Y-2Y 금리역전, DXY, STLFSI
"""

import yfinance as yf
import requests
import json
import os
from datetime import datetime, timezone

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


def get_yahoo_prev(ticker: str) -> float | None:
    """전일 종가 (2번째 최근값)"""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="10d")
        closes = hist["Close"].dropna()
        if len(closes) >= 2:
            return round(float(closes.iloc[-2]), 2)
    except Exception as e:
        print(f"  [Yahoo 전일 오류] {ticker}: {e}")
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
            "limit": 10,
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        obs_list = [o for o in r.json().get("observations", []) if o.get("value",".")  not in (".",  "")]
        if len(obs_list) >= 1:
            return round(float(obs_list[0]["value"]), 3)
    except Exception as e:
        print(f"  [FRED 오류] {series_id}: {e}")
    return None


def get_fred_prev(series_id: str) -> float | None:
    """FRED 전일(이전) 관측값"""
    if not FRED_API_KEY:
        return None
    try:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 10,
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        obs_list = [o for o in r.json().get("observations", []) if o.get("value", ".") not in (".", "")]
        if len(obs_list) >= 2:
            return round(float(obs_list[1]["value"]), 3)
    except Exception as e:
        print(f"  [FRED 전일 오류] {series_id}: {e}")
    return None


def calc_change(curr, prev):
    """전일 대비 변화량 계산"""
    if curr is None or prev is None:
        return None
    return round(curr - prev, 3)


def load_existing_data() -> dict:
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def calc_backwardation_days(existing: dict, vix_diff) -> dict:
    from zoneinfo import ZoneInfo
    today_kst = datetime.now(timezone.utc).astimezone(
        ZoneInfo("Asia/Seoul")
    ).strftime("%Y-%m-%d")

    prev = existing.get("backwardation", {
        "consecutive_days": 0, "last_date": "",
        "status": "normal", "history": []
    })

    consecutive = prev.get("consecutive_days", 0)
    last_date   = prev.get("last_date", "")
    history     = prev.get("history", [])

    if vix_diff is None:
        return prev

    is_backwardation = vix_diff > 0

    if last_date == today_kst:
        if history and history[-1]["date"] == today_kst:
            history[-1]["diff"] = vix_diff
            history[-1]["backwardation"] = is_backwardation
    else:
        consecutive = (consecutive + 1) if is_backwardation else 0
        history.append({"date": today_kst, "diff": vix_diff, "backwardation": is_backwardation})
        history = history[-15:]

    if not is_backwardation:        status = "normal"
    elif consecutive >= 7:          status = "crisis"
    elif consecutive >= 5:          status = "danger"
    else:                           status = "warn"

    print(f"  백워데이션 연속일: {consecutive}일 ({status})")
    return {
        "consecutive_days": consecutive, "last_date": today_kst,
        "status": status, "is_backwardation": is_backwardation, "history": history
    }


def make_ind(value, unit, source, prev=None):
    change = calc_change(value, prev)
    return {
        "value": value,
        "prev":  prev,
        "change": change,
        "unit": unit,
        "source": source,
    }


def main():
    from zoneinfo import ZoneInfo
    print(f"📡 데이터 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    existing = load_existing_data()

    # ── Yahoo Finance ──────────────────────────────────────────────
    print("\n[Yahoo Finance]")
    vix      = get_yahoo("^VIX");    vix_p  = get_yahoo_prev("^VIX");   print(f"  VIX:   {vix} (전일 {vix_p})")
    vix3m    = get_yahoo("^VIX3M");  vix3m_p= get_yahoo_prev("^VIX3M"); print(f"  VIX3M: {vix3m}")
    skew     = get_yahoo("^SKEW");   skew_p = get_yahoo_prev("^SKEW");   print(f"  SKEW:  {skew}")
    ovx      = get_yahoo("^OVX");    ovx_p  = get_yahoo_prev("^OVX");    print(f"  OVX:   {ovx}")
    gvz      = get_yahoo("^GVZ");    gvz_p  = get_yahoo_prev("^GVZ");    print(f"  GVZ:   {gvz}")
    pcr      = get_yahoo("^PCCE");   pcr_p  = get_yahoo_prev("^PCCE");   print(f"  PCR:   {pcr}")
    dxy      = get_yahoo("DX-Y.NYB");dxy_p  = get_yahoo_prev("DX-Y.NYB");print(f"  DXY:   {dxy}")

    vix_diff   = round(vix - vix3m, 2)   if vix   and vix3m   else None
    vix_diff_p = round(vix_p - vix3m_p, 2) if vix_p and vix3m_p else None
    print(f"  VIX 기간구조: {vix_diff}")

    # ── FRED API ──────────────────────────────────────────────────
    print("\n[FRED API]")
    hy   = get_fred("BAMLH0A0HYM2"); hy_p  = get_fred_prev("BAMLH0A0HYM2"); print(f"  HY Spread: {hy}")
    ig   = get_fred("BAMLC0A0CM");   ig_p  = get_fred_prev("BAMLC0A0CM");   print(f"  IG Spread: {ig}")
    ted  = get_fred("TEDRATE");      ted_p = get_fred_prev("TEDRATE");       print(f"  TED:       {ted}")
    sofr = get_fred("SOFR");         sofr_p= get_fred_prev("SOFR");          print(f"  SOFR:      {sofr}")
    # 10Y-2Y 금리 역전 (경기침체 선행지표)
    t10y2y   = get_fred("T10Y2Y");   t10y2y_p = get_fred_prev("T10Y2Y");    print(f"  10Y-2Y:    {t10y2y}")
    # STLFSI (연준 공식 금융 스트레스 지수)
    stlfsi   = get_fred("STLFSI4");  stlfsi_p = get_fred_prev("STLFSI4");   print(f"  STLFSI4:   {stlfsi}")

    print("\n[백워데이션 추적]")
    backwardation = calc_backwardation_days(existing, vix_diff)

    output = {
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "updated_kst": datetime.now(timezone.utc).astimezone(
            ZoneInfo("Asia/Seoul")
        ).strftime("%Y-%m-%d %H:%M KST"),
        "backwardation": backwardation,
        "indicators": {
            "VIX":       make_ind(vix,      "",   "Yahoo", vix_p),
            "VIX3M":     make_ind(vix3m,    "",   "Yahoo", vix3m_p),
            "VIX_DIFF":  make_ind(vix_diff, "",   "Yahoo", vix_diff_p),
            "SKEW":      make_ind(skew,     "",   "Yahoo", skew_p),
            "OVX":       make_ind(ovx,      "",   "Yahoo", ovx_p),
            "GVZ":       make_ind(gvz,      "",   "Yahoo", gvz_p),
            "PCR":       make_ind(pcr,      "",   "Yahoo", pcr_p),
            "DXY":       make_ind(dxy,      "",   "Yahoo", dxy_p),
            "HY_SPREAD": make_ind(hy,       "%",  "FRED",  hy_p),
            "IG_SPREAD": make_ind(ig,       "%",  "FRED",  ig_p),
            "TED_SPREAD":make_ind(ted,      "bp", "FRED",  ted_p),
            "SOFR":      make_ind(sofr,     "%",  "FRED",  sofr_p),
            "T10Y2Y":    make_ind(t10y2y,   "%",  "FRED",  t10y2y_p),
            "STLFSI":    make_ind(stlfsi,   "",   "FRED",  stlfsi_p),
        },
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ data.json 저장 완료")


if __name__ == "__main__":
    main()
