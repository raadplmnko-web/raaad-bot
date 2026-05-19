import os
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

# مفتاح Finnhub السريع واللحظي
FINNHUB_KEY = "cf96u91r01qgoct1706gcf96u91r01qgoct17070"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logging.error(f"خطأ تلجرام: {e}")

# لستة شاملة وموسعة لأكثر أسهم الزخم الصغيرة حركة تحت 10$ الحين بالماركت
WATCHLIST = [
    "VRAX", "GOVX", "SPRC", "EDBL", "TCBP", "IMPP", "MRAI", "CTNT", "SISI", 
    "PHUN", "BDRX", "GWAV", "KOSS", "JYNT", "HOLO", "WISA", "AEI", "BURU", 
    "MDAI", "GNS", "NVOS", "VCNX", "OCEA", "TSHA", "LPA"
]

def scan_live_watchlist():
    scanned_count = 0
    for ticker in WATCHLIST:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                
                price = float(data.get('c', 0))          # السعر الحالي اللحظي
                change_percent = float(data.get('dp', 0)) # نسبة التغير اللحظية %
                
                # التصفية الملكية الدقيقة: السعر تحت 10 دولار والصعود إيجابي ومتحرك فوق 1%
                if 0.30 <= price <= 10.00 and change_percent > 1.0:
                    scanned_count += 1
                    alert_text = f"🚨 *رادار رعد: اقتناص زخم لحظي* 🚨\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر الآن:** `${price:.2f}`\n" \
                                 f"📈 **التغير اللحظي:** `+{change_percent:.2f}%`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 الحركة حية ومباشرة من الماركت الحين!"
                    send_msg(alert_text)
                    time.sleep(1) # تهدئة الإرسال
        except Exception as e:
            logging.error(f"خطأ في فحص {ticker}: {e}")
            
    logging.info(f"🔄 تم فحص اللستة اللحظية واكتشاف {scanned_count} أسهم صاعدة.")

send_msg("🔥 *تم تحويل الرادار للتشغيل اللحظي المباشر عبر Finnhub!* \n\nجاري جلد قائمة أسهم الزخم الحالية وفحص حركتها الحية...")

while True:
    scan_live_watchlist()
    time.sleep(60) # فحص متكرر كل دقيقة بدون أي تأخير
