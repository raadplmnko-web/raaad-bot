import os
import time
import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# ========== الإعدادات ==========
TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"
FINNHUB_KEY = "d6fnilhr01qqnmbpbjc0d6fnilhr01qqnmbpbjcg"
MAX_PRICE = 10.0
CHECK_INTERVAL = 300

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

WATCHLIST = [
    "SNDL","CLOV","EXPR","AMC","BBIG","MMAT","NKLA","RIDE","WKHS",
    "SPCE","FFIE","MULN","IDEX","CENN","NAKD","SIGA","SENS","GNUS",
    "IMPP","PROG","ATER","SKLZ","WATT","CLVS","BNGO","SOLO","XELA",
    "BNED","ACST","FCEL","BLNK","PLUG","NRXP","PRTY","BKKT","OPAD",
    "CIFS","AULT","ENOB","NUVB","ABIO","KPLT","MVST","GFAI","DPRO",
    "MOGO","FXLV","ATXI","CREX","INPX","CRBP","DARE","PRPO","AIOT",
    "ABSI","APCX","HOFV","LGVN","RNXT","ANY","EZFL","HCDI","KULR"
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.status_code == 200:
            logger.info("✅ تم الإرسال")
        else:
            logger.error(f"❌ خطأ: {r.text}")
    except Exception as e:
        logger.error(f"❌ {e}")

def get_realtime_price(ticker):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=5)
        data = r.json()
        price = data.get("c", 0)
        return price if price and price > 0 else None
    except:
        return None

def get_candles(ticker, days=60):
    try:
        now = int(time.time())
        from_time = now - (days * 24 * 3600)
        url = f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution=D&from={from_time}&to={now}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=8)
        data = r.json()
        if data.get("s") != "ok":
            return None
        df = pd.DataFrame({
            "close":  data["c"],
            "high":   data["h"],
            "low":    data["l"],
            "open":   data["o"],
            "volume": data["v"],
        })
        return df
    except:
        return None

def calculate_signals(ticker):
    try:
        current_price = get_realtime_price(ticker)
        if not current_price or current_price > MAX_PRICE:
            return None

        df = get_candles(ticker, days=60)
        if df is None or len(df) < 35:
            return None

        close  = df["close"]
        high   = df["high"]
        low    = df["low"]
        open_  = df["open"]
        volume = df["volume"]

        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low  - close.shift()).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]

        ema9 = close.ewm(span=9, adjust=False).mean()

        tp = (high + low + close) / 3
        mf = tp * volume
        pos_mf = mf.where(tp > tp.shift(), 0).rolling(7).sum()
        neg_mf = mf.where(tp < tp.shift(), 0).rolling(7).sum()
        mfi = (100 - 100 / (1 + pos_mf / neg_mf.replace(0, np.nan))).iloc[-1]

        res_val   = high.iloc[-31:-1].max()
        sup_val   = low.iloc[-31:-1].min()
        stop_loss = min(sup_val, low.iloc[-11:-1].min()) - (atr * 0.5)

        avg_vol     = volume.rolling(20).mean().iloc[-1]
        is_high_vol = volume.iloc[-1] > avg_vol * 1.5
        is_mega_vol = volume.iloc[-1] > avg_vol * 2.5

        price = current_price

        is_breakout  = (price > res_val) and is_high_vol
        is_adventure = (is_breakout or (is_mega_vol and close.iloc[-1] > open_.iloc[-1])) and mfi > 45
        is_super_buy = (ema9.iloc[-2] >= close.iloc[-2]) and (price > ema9.iloc[-1]) and price > res_val * 0.98 and mfi > 50
        is_dip_buy   = low.iloc[-1] <= sup_val * 1.01 and (min(open_.iloc[-1], close.iloc[-1]) - low.iloc[-1]) > abs(close.iloc[-1] - open_.iloc[-1]) * 0.6
        is_exit      = (price < ema9.iloc[-1]) or price < stop_loss

        target1  = price + (atr * 1.2)
        target_g = price + (atr * 3.0)

        return {
            "ticker": ticker,
            "price":  price,
            "mfi":    round(float(mfi), 1),
            "res":    round(float(res_val), 3),
            "sup":    round(float(sup_val), 3),
            "stop":   round(float(stop_loss), 3),
            "t1":     round(float(target1), 3),
            "tg":     round(float(target_g), 3),
            "is_adventure": bool(is_adventure),
            "is_super_buy": bool(is_super_buy),
            "is_dip_buy":   bool(is_dip_buy),
            "is_exit":      bool(is_exit),
        }
    except Exception as e:
        logger.debug(f"خطأ في {ticker}: {e}")
        return None

def format_message(sig, signal_type):
    emoji_map = {
        "adventure": "🔥 مغامرة",
        "super_buy": "⚡ دخول رعد",
        "dip_buy":   "⚓ ارتداد",
        "exit":      "🛑 خروج",
    }
    label = emoji_map.get(signal_type, "📢 إشارة")
    msg = f"""
<b>رادار رعد الأسطوري ⚡</b>
━━━━━━━━━━━━━━━
📌 السهم: <b>${sig['ticker']}</b>
🏷 الإشارة: <b>{label}</b>
💰 السعر الفوري: <b>${sig['price']:.3f}</b>
━━━━━━━━━━━━━━━
📊 السيولة (MFI): {sig['mfi']}%
📈 المقاومة: ${sig['res']}
📉 الارتداد: ${sig['sup']}
🛑 وقف الخسارة: ${sig['stop']}
🎯 هدف 1: ${sig['t1']}
🏆 الهدف الذهبي: ${sig['tg']}
━━━━━━━━━━━━━━━
🕐 {datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M ET')}
"""
    return msg.strip()

def main():
    send_telegram("🚀 <b>رادار رعد الأسطوري يعمل الآن!</b>\n\n⚡ بيانات فورية عبر Finnhub\nسأراقب الأسهم الأمريكية تحت $10 وأرسل الإشارات فوراً!")
    logger.info("✅ البوت بدأ")

    sent_signals = {}

    while True:
        now_et  = datetime.now(pytz.timezone('US/Eastern'))
        hour    = now_et.hour
        minute  = now_et.minute
        weekday = now_et.weekday()

        is_market = (weekday < 5) and (
            (hour == 9 and minute >= 30) or (10 <= hour < 16)
        )

        if not is_market:
            logger.info(f"⏸ السوق مغلق - {now_et.strftime('%H:%M ET %A')}")
            time.sleep(60)
            continue

        logger.info(f"🔍 فحص {len(WATCHLIST)} سهم...")

        for ticker in WATCHLIST:
            sig = calculate_signals(ticker)
            if not sig:
                time.sleep(0.5)
                continue

            signals_found = []
            if sig['is_adventure']: signals_found.append("adventure")
            if sig['is_super_buy']:  signals_found.append("super_buy")
            if sig['is_dip_buy']:    signals_found.append("dip_buy")
            if sig['is_exit']:       signals_found.append("exit")

            for stype in signals_found:
                key  = f"{ticker}_{stype}_{now_et.date()}"
                last = sent_signals.get(key, 0)
                if time.time() - last > 3600:
                    msg = format_message(sig, stype)
                    send_telegram(msg)
                    sent_signals[key] = time.time()
                    time.sleep(1)

            time.sleep(0.8)

        logger.info(f"✅ انتهى الفحص - انتظار {CHECK_INTERVAL//60} دقائق")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
