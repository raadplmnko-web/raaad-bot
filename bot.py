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

def get_active_penny_stocks():
    """جلب أسهم نشطة تحت $10 من Yahoo Finance Screener"""
    results = []
    
    # قائمة 1: أكثر الأسهم ارتفاعاً اليوم
    urls = [
        "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?scrIds=day_gainers&count=100",
        "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?scrIds=most_actives&count=100",
    ]
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
                for q in quotes:
                    sym = q.get('symbol', '')
                    price = q.get('regularMarketPrice', 0)
                    if sym and 0.50 <= price <= 10.00:
                        results.append(sym)
        except Exception as e:
            logging.error(f"خطأ Yahoo: {e}")
    
    # إزالة المكرر
    results = list(set(results))
    logging.info(f"📋 {len(results)} سهم نشط تحت $10")
    return results

def check_signal(symbol):
    url = "https://finnhub.io/api/v1/quote"
    params = {"symbol": symbol, "token": FINNHUB_KEY}
    try:
        res = requests.get(url, params=params, timeout=5)
        d = res.json()
    except:
        return None

    price  = d.get("c", 0)
    open_  = d.get("o", 0)
    high   = d.get("h", 0)
    low    = d.get("l", 0)
    prev   = d.get("pc", 0)
    volume = d.get("v", 0)

    if not price or not prev or prev == 0:
        return None
    if not (0.50 <= price <= 10.00):
        return None

    roc = ((price - prev) / prev) * 100
    candle_range = high - low if high > low else 0.001
    candle_body  = price - open_
    bull_pct     = max(0, candle_body / candle_range * 100)
    mfi          = bull_pct
    rsi          = max(0, min(100, 50 + roc * 3))
    adx          = min(100, abs(roc) * 6)

    is_roc_strong = roc > 3.0
    trend_strong  = adx > 25
    is_high_vol   = volume > 300_000
    is_mega_vol   = volume > 1_000_000

    # انفجار زخم 💥
    is_blast = (
        is_mega_vol and
        is_roc_strong and
        mfi > 55 and
        trend_strong and
        price > open_
    )

    # CALL 🟢
    is_call = (
        bull_pct > 60 and
        rsi > 55 and
        is_roc_strong and
        is_high_vol and
        price > open_
    )

    if not (is_blast or is_call):
        return None

    atr       = candle_range
    target1   = round(price + atr * 1.0, 2)
    target2   = round(price + atr * 2.0, 2)
    target_g  = round(price + atr * 3.5, 2)
    stop_loss = round(low - atr * 0.3, 2)
    label     = "💥 انفجار زخم + CALL" if is_blast else "🟢 CALL زخم"

    return {
        "symbol": symbol, "price": price,
        "roc": round(roc, 2), "volume": volume,
        "bull_pct": round(bull_pct, 1),
        "target1": target1, "target2": target2,
        "target_g": target_g, "stop_loss": stop_loss,
        "label": label,
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

        # احترام حد الـ API
        if i % 55 == 0 and i > 0:
            time.sleep(61)

    logging.info(f"✅ انتهى الفحص - {found} إشارة")

# ── تشغيل ──
logging.info("🚀 رادار رعد V4 يعمل...")
send_msg("🔥 *رادار رعد V4* 🔥\n\nيفحص الأسهم النشطة فقط - أسرع وأدق!")

while True:
    if not is_market_time():
        now = datetime.now(NY_TZ)
        logging.info(f"⏸️ خارج وقت السوق - {now.strftime('%H:%M')} نيويورك")
        time.sleep(300)
        continue

    symbols = get_active_penny_stocks()
    if symbols:
        scan(symbols)
    else:
        logging.warning("⚠️ ما في أسهم نشطة")

    logging.info("⏰ انتظار 3 دقائق...")
    time.sleep(180)
