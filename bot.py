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

# تتبع الأسهم المرسلة - لا نكرر نفس السهم كل دورة
sent_today = {}

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
    results = []
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

    # ── المؤشرات ──
    roc          = ((price - prev) / prev) * 100
    candle_range = high - low if high > low else 0.001
    candle_body  = price - open_
    bull_pct     = max(0, candle_body / candle_range * 100)
    rsi          = max(0, min(100, 50 + roc * 3))
    adx          = min(100, abs(roc) * 5)

    is_green     = price > open_
    is_roc_ok    = roc > 2.0        # ✅ خُفف من 3%
    trend_ok     = adx > 20         # ✅ خُفف من 25
    is_high_vol  = volume > 200_000 # ✅ خُفف من 300K
    is_mega_vol  = volume > 800_000 # ✅ خُفف من 1M

    # 💥 انفجار زخم
    is_blast = (
        is_mega_vol and
        is_roc_ok and
        bull_pct > 50 and
        trend_ok and
        is_green
    )

    # 🟢 CALL زخم
    is_call = (
        bull_pct > 55 and
        rsi > 52 and
        is_roc_ok and
        is_high_vol and
        is_green
    )

    # ⚡ بداية زخم - إشارة أخف
    is_early = (
        roc > 1.5 and
        is_green and
        is_high_vol and
        bull_pct > 45
    )

    if not (is_blast or is_call or is_early):
        return None

    # الأهداف
    atr       = candle_range
    target1   = round(price + atr * 1.0, 3)
    target2   = round(price + atr * 2.0, 3)
    target_g  = round(price + atr * 3.5, 3)
    stop_loss = round(low - atr * 0.3, 3)

    if is_blast:
        label = "💥 انفجار زخم"
    elif is_call:
        label = "🟢 CALL زخم"
    else:
        label = "⚡ بداية زخم"

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
    now_key = datetime.now(NY_TZ).strftime("%Y-%m-%d")

    for i, symbol in enumerate(symbols):
        # لا نكرر نفس السهم أكثر من مرة كل 30 دقيقة
        last_sent = sent_today.get(symbol, 0)
        if time.time() - last_sent < 1800:
            continue

        result = check_signal(symbol)
        if result:
            found += 1
            sent_today[symbol] = time.time()
            msg = (
                f"{result['label']}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📌 *السهم:* `{result['symbol']}`\n"
                f"💵 *السعر:* `${result['price']:.3f}`\n"
                f"⚡ *ROC:* `{result['roc']}%`\n"
                f"📊 *زخم الشمعة:* `{result['bull_pct']}%`\n"
                f"📦 *الفوليوم:* `{result['volume']:,}`\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🎯 *هدف 1:* `${result['target1']}`\n"
                f"🎯 *هدف 2:* `${result['target2']}`\n"
                f"🏆 *الهدف الذهبي:* `${result['target_g']}`\n"
                f"🛑 *وقف الخسارة:* `${result['stop_loss']}`\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🚀 *رادار رعد V5*"
            )
            send_msg(msg)
            time.sleep(1)

        if i % 55 == 0 and i > 0:
            time.sleep(61)

    logging.info(f"✅ انتهى الفحص - {found} إشارة")

# ── تشغيل ──
logging.info("🚀 رادار رعد V5 يعمل...")
send_msg("🔥 *رادار رعد V5* 🔥\n\nشروط محسّنة - 3 مستويات إشارات!")

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
        logging.warning("⚠️ ما في أسهم")

    logging.info("⏰ انتظار 3 دقائق...")
    time.sleep(180)
