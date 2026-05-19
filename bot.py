import time
import requests
import logging
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"
FINNHUB_KEY = "d6fnilhr01qqnmbpbjc0d6fnilhr01qqnmbpbjcg"
NY_TZ = pytz.timezone("America/New_York")

def is_market_time():
    now = datetime.now(NY_TZ)
    if now.weekday() >= 5:
        return False
    t = now.hour * 60 + now.minute
    return (4 * 60) <= t < (16 * 60)

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        logging.info(f"تلجرام: {res.status_code}")
    except Exception as e:
        logging.error(f"خطأ تلجرام: {e}")

def get_us_stocks():
    url = "https://finnhub.io/api/v1/stock/symbol"
    params = {"exchange": "US", "token": FINNHUB_KEY}
    try:
        res = requests.get(url, params=params, timeout=15)
        symbols = [s['symbol'] for s in res.json() if s.get('type') == 'Common Stock']
        logging.info(f"✅ {len(symbols)} سهم")
        return symbols
    except Exception as e:
        logging.error(f"خطأ: {e}")
        return []

def get_quote(symbol):
    url = "https://finnhub.io/api/v1/quote"
    params = {"symbol": symbol, "token": FINNHUB_KEY}
    try:
        res = requests.get(url, params=params, timeout=5)
        return res.json()
    except:
        return {}

def check_signal(symbol):
    d = get_quote(symbol)
    if not d:
        return None

    price  = d.get("c", 0)
    open_  = d.get("o", 0)
    high   = d.get("h", 0)
    low    = d.get("l", 0)
    prev   = d.get("pc", 0)
    volume = d.get("v", 0)

    if not price or not prev or prev == 0:
        return None

    # فلتر السعر
    if not (0.50 <= price <= 10.00):
        return None

    # ROC - سرعة الزخم
    roc = ((price - prev) / prev) * 100

    # نسبة الشمعة الخضراء
    candle_body  = price - open_
    candle_range = high - low if high > low else 0.001
    bull_pct     = max(0, candle_body / candle_range * 100)

    # فوليوم - نقارن بمعدل بسيط
    # الـ API المجاني ما يعطي average volume مباشرة
    # نعوض بفحص إذا الفوليوم كبير نسبياً
    is_high_vol = volume > 500_000
    is_mega_vol = volume > 1_500_000

    # MFI تقريبي
    mfi = bull_pct

    # RSI تقريبي
    rsi = 50 + (roc * 3)
    rsi = max(0, min(100, rsi))

    # ADX تقريبي - قوة الحركة
    adx = min(100, abs(roc) * 6)

    trend_strong = adx > 25
    is_roc_strong = roc > 3.0  # رفعناه لـ 3% عشان نكون أدق

    # ✅ شروط انفجار الزخم
    is_blast = (
        is_mega_vol and
        is_roc_strong and
        mfi > 55 and
        trend_strong and
        price > open_  # شمعة خضراء
    )

    # ✅ شروط CALL
    is_call = (
        bull_pct > 60 and
        rsi > 55 and
        is_roc_strong and
        is_high_vol and
        price > open_
    )

    if not (is_blast or is_call):
        return None

    # الأهداف ووقف الخسارة
    atr       = candle_range
    target1   = round(price + atr * 1.0, 2)
    target2   = round(price + atr * 2.0, 2)
    target_g  = round(price + atr * 3.5, 2)
    stop_loss = round(low - atr * 0.3, 2)

    label = "💥 انفجار زخم + CALL" if is_blast else "🟢 CALL زخم"

    return {
        "symbol":    symbol,
        "price":     price,
        "roc":       round(roc, 2),
        "volume":    volume,
        "bull_pct":  round(bull_pct, 1),
        "target1":   target1,
        "target2":   target2,
        "target_g":  target_g,
        "stop_loss": stop_loss,
        "label":     label,
    }

def scan(symbols):
    found = 0
    for i, symbol in enumerate(symbols):
        result = check_signal(symbol)
        if result:
            found += 1
            msg = (
                f"{result['label']}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📌 *السهم:* `{result['symbol']}`\n"
                f"💵 *السعر:* `${result['price']:.2f}`\n"
                f"⚡ *ROC:* `{result['roc']}%`\n"
                f"📊 *زخم الشمعة:* `{result['bull_pct']}%`\n"
                f"📦 *الفوليوم:* `{result['volume']:,}`\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🎯 *هدف 1:* `${result['target1']}`\n"
                f"🎯 *هدف 2:* `${result['target2']}`\n"
                f"🏆 *الهدف الذهبي:* `${result['target_g']}`\n"
                f"🛑 *وقف الخسارة:* `${result['stop_loss']}`\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🚀 *رادار رعد*"
            )
            send_msg(msg)
            time.sleep(1)

        if i % 55 == 0 and i > 0:
            time.sleep(61)

    logging.info(f"✅ انتهى الفحص - {found} إشارة")

# ── تشغيل ──
logging.info("🚀 رادار رعد V3 يعمل...")
send_msg("🔥 *رادار رعد V3* 🔥\n\nالشروط محسّنة - جاري الفحص...")
symbols = get_us_stocks()

while True:
    if not is_market_time():
        now = datetime.now(NY_TZ)
        logging.info(f"⏸️ خارج وقت السوق - {now.strftime('%H:%M')} نيويورك")
        time.sleep(300)
        continue

    if symbols:
        scan(symbols)
    else:
        symbols = get_us_stocks()

    logging.info("⏰ انتظار 3 دقائق...")
    time.sleep(180)
