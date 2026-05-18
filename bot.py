import os
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# التوكن الصحيح والـ ID الخاص بك
TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        logging.info(f"استجابة التلجرام: {res.json()}")
    except Exception as e:
        logging.error(f"خطأ إرسال تلجرام: {e}")

def get_live_market_data():
    # رابط خفيف وسريع جداً لجلب حالة أسهم الماركت النشطة فوراً
    url = "https://query1.finance.yahoo.com/v1/finance/scrumb/screener/tokens/most_actives"
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
                
                if not ticker or price is None or change_percent is None:
                    continue
                
                # تصفية رادار رعد: أسهم بين 1$ و 30$ وصعود أعلى من 1% لقنص الزخم
                if 1.0 <= price <= 30.0 and change_percent > 1.0:
                    scanned_count += 1
                    alert_text = f"🔥 *رادار رعد: اقتناص سهم فوليوم* 🔥\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي:** `${price:.2f}`\n" \
                                 f"📈 **نسبة الارتفاع:** `+{change_percent:.2f}%`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الوضع:* سيولة نشطة بالماركت الحين!"
                    send_msg(alert_text)
            logging.info(f"🔄 تم فحص السوق بنجاح واكتشاف {scanned_count} أسهم.")
    except Exception as e:
        logging.error(f"خطأ أثناء جلب البيانات: {e}")

logging.info("🚀 تشغيل رادار رعد الأساسي والمحدث...")

# رسالة الفحص الفوري (ستصلك في التلجرام فور تشغيل السيرفر للتأكد من الربط)
send_msg("🚀 *تم تشغيل رادار رعد بنجاح!*\n\nالربط سليم 100% والتوكن صحيح، الرادار جاري فحص الأسهم الحية بالخلفية الحين...")

while True:
    get_live_market_data()
    time.sleep(180)
