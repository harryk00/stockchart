import yfinance as yf
import requests
import json
import os
from datetime import datetime, timezone

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

def get_yahoo(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d")
        if not hist.empty:
            return round(float(hist["Close"].dropna().iloc[-1]), 2)
    except Exception as e:
        print(f"  [Yahoo 오류] {ticker}: {e}")
    return None

def get_fred(series_id):
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

def main():
    print(f"데이터 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    vix   = get_yahoo("^VIX");  print(f"  VIX:  {vix}")
    skew  = get_yahoo("^SKEW"); print(f"  SKEW: {skew}")
    ovx   = get_yahoo("^OVX");  print(f"  OVX:  {ovx}")
    gvz   = get_yahoo("^GVZ");  print(f"  GVZ:  {gvz}")
    pcr   = get_yahoo("^CPC");  print(f"  PCR:  {pcr}")

    hy_spread = get_fred("BAMLH0A0HYM2"); print(f"  HY Spread: {hy_spread}")
    ig_spread = get_fred("BAMLC0A0CM");   print(f"  IG Spread: {ig_spread}")
    ted       = get_fred("TEDRATE");      print(f"  TED Spread: {ted}")
    sofr      = get_fred("SOFR");         print(f"  SOFR: {sofr}")

    from zoneinfo import ZoneInfo
    output = {
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "updated_kst": datetime.now(timezone.utc).astimezone(
            ZoneInfo("Asia/Seoul")
        ).strftime("%Y-%m-%d %H:%M KST"),
        "indicators": {
            "VIX":        {"value": vix,       "unit": "",    "source": "Yahoo"},
            "SKEW":       {"value": skew,      "unit": "",    "source": "Yahoo"},
            "OVX":        {"value": ovx,       "unit": "",    "source": "Yahoo"},
            "GVZ":        {"value": gvz,       "unit": "",    "source": "Yahoo"},
            "PCR":        {"value": pcr,       "unit": "",    "source": "Yahoo"},
            "HY_SPREAD":  {"value": hy_spread, "unit": "%",   "source": "FRED"},
            "IG_SPREAD":  {"value": ig_spread, "unit": "%",   "source": "FRED"},
            "TED_SPREAD": {"value": ted,       "unit": "bp",  "source": "FRED"},
            "SOFR":       {"value": sofr,      "unit": "%",   "source": "FRED"},
        },
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("data.json 저장 완료")

if __name__ == "__main__":
    main()
