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
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        logging.info(f"استجابة التلجرام: {res.json()}")
    except Exception as e:
        logging.error(f"خطأ إرسال تلجرام: {e}")

def get_penny_stocks_under_10():
    # سحب قائمة الأسهم الأكثر صعوداً وانفجاراً بالماركت الأمريكي
    url = "https://query1.finance.yahoo.com/v1/finance/scrumb/screener/tokens/day_gainers"
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
                
                # الفلترة الصارمة بطلبك: السعر تحت 10 دولار فقط ومستحيل يتجاوزها بالملي!
                if 0.50 <= price <= 10.00 and change_percent > 1.0 and volume > 100000:
                    scanned_count += 1
                    alert_text = f"⚡ *رادار رعد: سهم فوليوم تحت 10$* ⚡\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر الحالي:** `${price:.2f}`\n" \
                                 f"📈 **نسبة الارتفاع:** `+{change_percent:.2f}%`\n" \
                                 f"📊 **حجم التداول (Volume):** `{volume:,}`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الحالة:* سيولة وزخم ممتاز لسعر تحت 10 دولار!"
                    send_msg(alert_text)
                    time.sleep(1) # فاصل لمنع الحظر
            logging.info(f"🔄 تم فحص أسهم الزخم بنجاح واكتشاف {scanned_count} أسهم تحت الـ 10$.")
    except Exception as e:
        logging.error(f"خطأ أثناء جلب البيانات: {e}")

logging.info("🚀 تشغيل رادار رعد للأسهم الأقل من 10 دولار...")

# رسالة تأكيد فوري عند إقلاع الحاوية بالفلتر الجديد
send_msg("🔥 *تم تعديل الرادار بنجاح للنسخة الفولاذية (تحت 10$ فقط)* 🔥\n\nالرادار موجه الآن بالكامل لقنص أسهم الـ Penny Stocks الرخيصة والمشتعلة سيولة. جاري بدء الفحص...")

while True:
    get_penny_stocks_under_10()
    time.sleep(180)
