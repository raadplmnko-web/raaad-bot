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
    if now.weekday() >= 5:  # السبت والأحد
        return False
    h, m = now.hour, now.minute
    total = h * 60 + m
    pre_market  = (4 * 60) <= total < (9 * 60 + 30)   # 4:00 - 9:30
    market      = (9 * 60 + 30) <= total < (16 * 60)  # 9:30 - 4:00
    return pre_market or market

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        logging.info(f"تلجرام: {res.status_code}")
    except Exception as e:
        logging.error(f"خطأ تلجرام: {e}")

def get_candles(symbol, resolution="1", count=30):
    """جلب شمعات للحساب"""
    url = "https://finnhub.io/api/v1/quote"
    params = {"symbol": symbol, "token": FINNHUB_KEY}
    try:
        res = requests.get(url, params=params, timeout=5)
        return res.json()
    except:
        return {}

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

def get_stock_data(symbol):
    """جلب بيانات السهم الكاملة"""
    url = "https://finnhub.io/api/v1/quote"
    params = {"symbol": symbol, "token": FINNHUB_KEY}
    try:
        res = requests.get(url, params=params, timeout=5)
        d = res.json()
        return {
            "price": d.get("c", 0),       # السعر الحالي
            "open":  d.get("o", 0),       # الافتتاح
            "high":  d.get("h", 0),       # الأعلى
            "low":   d.get("l", 0),       # الأدنى
            "prev":  d.get("pc", 0),      # إغلاق أمس
            "volume": d.get("v", 0),      # الفوليوم
        }
    except:
        return {}

def calc_indicators(d, avg_vol):
    """حساب المؤشرات - نفس منطق TradingView"""
    price  = d["price"]
    open_  = d["open"]
    high   = d["high"]
    low    = d["low"]
    prev   = d["prev"]
    vol    = d["volume"]

    if not price or not prev or prev == 0:
        return None

    # ROC - سرعة الزخم
    roc = ((price - prev) / prev) * 100

    # فوليوم
    is_high_vol = vol > avg_vol * 2.0
    is_mega_vol = vol > avg_vol * 3.5

    # MFI تقريبي - نسبة الشمعة الصاعدة
    candle_range = high - low if high > low else 0.01
    bull_body    = max(0, price - open_) / candle_range
    mfi_approx   = bull_body * 100  # 0-100

    # RSI تقريبي بالشمعة الواحدة
    change = price - prev
    rsi_approx = 50 + (change / prev * 500)
    rsi_approx = max(0, min(100, rsi_approx))

    # ADX تقريبي - قوة الحركة
    adx_approx = abs(roc) * 5
    adx_approx = min(100, adx_approx)

    # مستويات الدعم والمقاومة
    resistance = high
    support    = low
    mid        = (resistance + support) / 2

    # تدفق الأموال
    bull_pct = bull_body * 100
    bear_pct = 100 - bull_pct

    # ATR تقريبي
    atr = candle_range

    # الأهداف ووقف الخسارة
    target1   = price + (atr * 1.0)
    target2   = price + (atr * 2.0)
    target_g  = price + (atr * 3.5)
    stop_loss = support - (atr * 0.3)

    return {
        "roc":        roc,
        "mfi":        mfi_approx,
        "rsi":        rsi_approx,
        "adx":        adx_approx,
        "bull_pct":   bull_pct,
        "bear_pct":   bear_pct,
        "is_high_vol": is_high_vol,
        "is_mega_vol": is_mega_vol,
        "resistance": resistance,
        "support":    support,
        "target1":    target1,
        "target2":    target2,
        "target_g":   target_g,
        "stop_loss":  stop_loss,
        "price":      price,
    }

def check_signal(ind):
    """فحص إشارات الزخم - نفس منطق المؤشر"""
    if not ind:
        return None

    roc        = ind["roc"]
    mfi        = ind["mfi"]
    rsi        = ind["rsi"]
    adx        = ind["adx"]
    bull_pct   = ind["bull_pct"]
    is_high_vol = ind["is_high_vol"]
    is_mega_vol = ind["is_mega_vol"]
    price      = ind["price"]
    resistance = ind["resistance"]

    is_roc_strong = roc > 2.0
    trend_strong  = adx > 25
    trend_weak    = adx < 20

    # ✅ انفجار زخم 💥 - أقوى إشارة
    is_momentum_blast = (
        is_mega_vol and
        is_roc_strong and
        price >= resistance * 0.98 and
        mfi > 60 and
        trend_strong
    )

    # ✅ CALL 🟢
    is_call = (
        bull_pct > 65 and
        rsi > 55 and
        trend_strong and
        is_roc_strong
    )

    if is_momentum_blast and is_call:
        return "blast"   # انفجار زخم + CALL معاً ✅ الأقوى
    elif is_momentum_blast:
        return "blast"
    elif is_call and is_high_vol and is_roc_strong:
        return "call"

    return None

def scan(symbols, avg_volumes):
    found = 0
    for i, symbol in enumerate(symbols):
        d = get_stock_data(symbol)
        if not d or not d.get("price"):
            continue

        price = d["price"]
        if not (0.50 <= price <= 10.00):
            continue

        avg_vol = avg_volumes.get(symbol, d["volume"] * 0.5)
        ind     = calc_indicators(d, avg_vol)
        signal  = check_signal(ind)

        if signal:
            found += 1
            if signal == "blast":
                emoji = "💥"
                label = "انفجار زخم + CALL"
            else:
                emoji = "🟢"
                label = "CALL زخم"

            msg = (
                f"{emoji} *{label}* {emoji}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📌 *السهم:* `{symbol}`\n"
                f"💵 *السعر:* `${price:.2f}`\n"
                f"⚡ *ROC:* `{ind['roc']:.2f}%`\n"
                f"📊 *MFI:* `{ind['mfi']:.0f}%`\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🎯 *هدف 1:* `${ind['target1']:.2f}`\n"
                f"🎯 *هدف 2:* `${ind['target2']:.2f}`\n"
                f"🏆 *الهدف الذهبي:* `${ind['target_g']:.2f}`\n"
                f"🛑 *وقف الخسارة:* `${ind['stop_loss']:.2f}`\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🚀 *رادار رعد - زخم حقيقي*"
            )
            send_msg(msg)
            time.sleep(1)

        # احترام حد الـ API
        if i % 55 == 0 and i > 0:
            time.sleep(61)

    logging.info(f"✅ انتهى الفحص - {found} إشارة")

# ── تشغيل ──
logging.info("🚀 رادار رعد V2 يعمل...")
send_msg("🔥 *رادار رعد V2 شغّال* 🔥\n\nيراقب أسهم تحت $10 مع إشارات انفجار الزخم...")

symbols     = get_us_stocks()
avg_volumes = {}  # نبني معدل الفوليوم مع الوقت

while True:
    if not is_market_time():
        now = datetime.now(NY_TZ)
        logging.info(f"⏸️ خارج وقت السوق - {now.strftime('%H:%M')} نيويورك")
        time.sleep(300)
        continue

    if symbols:
        scan(symbols, avg_volumes)
    else:
        symbols = get_us_stocks()

    logging.info("⏰ انتظار 3 دقائق...")
    time.sleep(180)
