import os
import time
import logging
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import pytz

# ========== الإعدادات ==========
TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"
MAX_PRICE = 10.0  # فقط أسهم أقل من 10 دولار
CHECK_INTERVAL = 300  # كل 5 دقائق

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== قائمة الأسهم الأمريكية الرخيصة ==========
WATCHLIST = [
    "SNDL","CLOV","EXPR","AMC","BBIG","MMAT","NKLA","RIDE","WKHS",
    "SPCE","FFIE","MULN","IDEX","CENN","ILUS","NAKD","SIGA","ZNGA",
    "SENS","GNUS","IMPP","PROG","ATER","BBBY","SKLZ","WATT","CLVS",
    "BNGO","SOLO","XELA","BNED","ACST","FCEL","BLNK","PLUG","NRXP",
    "PRTY","BKKT","OPAD","CIFS","AULT","ENOB","NUVB","ABIO","MGAM",
    "KPLT","BOXD","MVST","SMFL","GFAI","DPRO","PNTM","MOGO","CODA",
    "FXLV","ATXI","CREX","MOXC","INPX","CRBP","DARE","PRPO","AIOT",
    "CODA","ABSI","APCX","HOFV","JBDI","LGVN","MATH","NLIT","RNXT"
]

# ========== إرسال رسالة تيليغرام ==========
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.status_code == 200:
            logger.info("✅ تم إرسال الرسالة")
        else:
            logger.error(f"❌ خطأ في الإرسال: {r.text}")
    except Exception as e:
        logger.error(f"❌ استثناء: {e}")

# ========== حساب المؤشر ==========
def calculate_signals(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False, auto_adjust=True)
        if df is None or len(df) < 35:
            return None

        close = df['Close'].squeeze()
        high  = df['High'].squeeze()
        low   = df['Low'].squeeze()
        volume= df['Volume'].squeeze()
        open_ = df['Open'].squeeze()

        # السعر الحالي
        current_price = float(close.iloc[-1])
        if current_price > MAX_PRICE or current_price <= 0:
            return None

        # ATR
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low  - close.shift()).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]

        # EMA9
        ema9 = close.ewm(span=9, adjust=False).mean()

        # MFI (7)
        tp = (high + low + close) / 3
        mf = tp * volume
        pos_mf = mf.where(tp > tp.shift(), 0).rolling(7).sum()
        neg_mf = mf.where(tp < tp.shift(), 0).rolling(7).sum()
        mfi = (100 - 100 / (1 + pos_mf / neg_mf.replace(0, np.nan))).iloc[-1]

        # المقاومة والدعم
        res_val = high.iloc[-31:-1].max()
        sup_val = low.iloc[-31:-1].min()
        stop_loss = min(sup_val, low.iloc[-11:-1].min()) - (atr * 0.5)

        # الحجم
        avg_vol    = volume.rolling(20).mean().iloc[-1]
        is_high_vol = volume.iloc[-1] > avg_vol * 1.5
        is_mega_vol = volume.iloc[-1] > avg_vol * 2.5

        # الاختراق
        is_breakout = (close.iloc[-1] > res_val) and (close.iloc[-2] <= res_val) and is_high_vol

        # الإشارات
        is_adventure = (is_breakout or (is_mega_vol and close.iloc[-1] > open_.iloc[-1])) and mfi > 45
        is_super_buy = (ema9.iloc[-2] >= close.iloc[-2]) and (ema9.iloc[-1] < close.iloc[-1]) and close.iloc[-1] > res_val * 0.98 and mfi > 50
        is_dip_buy   = low.iloc[-1] <= sup_val * 1.01 and (min(open_.iloc[-1], close.iloc[-1]) - low.iloc[-1]) > abs(close.iloc[-1] - open_.iloc[-1]) * 0.6
        is_exit      = ((close.iloc[-2] >= ema9.iloc[-2]) and (close.iloc[-1] < ema9.iloc[-1])) or close.iloc[-1] < stop_loss

        target1  = current_price + (atr * 1.2)
        target_g = current_price + (atr * 3.0)

        return {
            "ticker": ticker,
            "price": current_price,
            "mfi": round(mfi, 1),
            "res": round(res_val, 3),
            "sup": round(sup_val, 3),
            "stop": round(stop_loss, 3),
            "t1": round(target1, 3),
            "tg": round(target_g, 3),
            "is_adventure": is_adventure,
            "is_super_buy": is_super_buy,
            "is_dip_buy": is_dip_buy,
            "is_exit": is_exit,
        }
    except Exception as e:
        logger.debug(f"خطأ في {ticker}: {e}")
        return None

# ========== الرسالة ==========
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
💰 السعر: <b>${sig['price']:.3f}</b>
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

# ========== الحلقة الرئيسية ==========
def main():
    send_telegram("🚀 <b>رادار رعد الأسطوري يعمل الآن!</b>\n\nسأراقب الأسهم الأمريكية تحت $10 وأرسل الإشارات فوراً ⚡")
    logger.info("✅ البوت بدأ")

    sent_signals = {}  # لتجنب التكرار

    while True:
        now_et = datetime.now(pytz.timezone('US/Eastern'))
        hour = now_et.hour
        weekday = now_et.weekday()

        # شغّل فقط في أوقات السوق (9:30 - 16:00 ET، الإثنين-الجمعة)
        is_market_hours = (weekday < 5) and ((hour == 9 and now_et.minute >= 30) or (10 <= hour < 16))

        if not is_market_hours:
            logger.info(f"⏸ السوق مغلق - {now_et.strftime('%H:%M ET %A')}")
            time.sleep(60)
            continue

        logger.info(f"🔍 فحص {len(WATCHLIST)} سهم...")

        for ticker in WATCHLIST:
            sig = calculate_signals(ticker)
            if not sig:
                continue

            signals_found = []
            if sig['is_adventure']: signals_found.append("adventure")
            if sig['is_super_buy']:  signals_found.append("super_buy")
            if sig['is_dip_buy']:    signals_found.append("dip_buy")
            if sig['is_exit']:       signals_found.append("exit")

            for stype in signals_found:
                key = f"{ticker}_{stype}_{now_et.date()}"
                # لا ترسل نفس الإشارة أكثر من مرة في اليوم
                last = sent_signals.get(key, 0)
                if time.time() - last > 3600:  # مرة كل ساعة كحد أقصى
                    msg = format_message(sig, stype)
                    send_telegram(msg)
                    sent_signals[key] = time.time()
                    time.sleep(1)

        logger.info(f"✅ انتهى الفحص - انتظار {CHECK_INTERVAL//60} دقائق")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
