import os
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logging.error(f"خطأ تلجرام: {e}")

def scan_live_market_gainers():
    # سحب الأسهم الأكثر صعوداً وفوليوم الحين أثناء السوق المفتوح
    url = "https://query1.finance.yahoo.com/v1/finance/scrumb/screener/tokens/day_gainers?size=50"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
            
            scanned_count = 0
            for stock in quotes:
                ticker = stock.get('symbol', '').upper()
                price = stock.get('regularMarketPrice')
                change_percent = stock.get('regularMarketChangePercent')
                volume = stock.get('regularMarketVolume', 0)
                
                if not ticker or price is None or change_percent is None:
                    continue
                
                # الفلترة الملكية اللحظية الحين: السعر تحت 10 دولار + صعود فوق 1% + فوليوم عالي
                if 0.30 <= price <= 10.00 and change_percent > 1.0 and volume > 100000:
                    scanned_count += 1
                    alert_text = f"🔥 *رادار رعد: انفجار لحظي في السوق!* 🔥\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي الحالي:** `${price:.2f}`\n" \
                                 f"📈 **نسبة الصعود الحالية:** `+{change_percent:.2f}%`\n" \
                                 f"📊 **حجم التداول (Volume):** `{volume:,}`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الحالة:* سيولة ضخمة وزخم اشتعال حيي بالماركت الحين!"
                    send_msg(alert_text)
                    time.sleep(1) # فاصل سريع لمنع تعليق الرسائل
            logging.info(f"🔄 تم مسح السوق المفتوح بنجاح واكتشاف {scanned_count} أسهم تحت الـ 10$.")
    except Exception as e:
        logging.error(f"خطأ أثناء قراءة الماركت: {e}")

# رسالة عاجلة لتأكيد التشغيل وسط المعركة
send_msg("🚀 *تم إطلاق رادار رعد الحي في قلب السوق المفتوح الآن!* \n\nالفحص مضبوط كل 60 ثانية لاقتناص الأسهم الطائرة تحت 10$ فوراً.")

while True:
    scan_live_market_gainers()
    time.sleep(60) # فحص حار وجديد كل دقيقة عشان ما تفوتك ولا حركة!
