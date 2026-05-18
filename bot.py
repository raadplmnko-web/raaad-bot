import os
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPyd1dzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logging.error(f"خطأ إرسال تلجرام: {e}")

def get_hot_volume_stocks():
    # رابط عام ومفتوح ومجاني 100% لسحب أكثر الأسهم نشاطاً وسيولة في السوق الأمريكي لحظياً
    url = "https://query1.finance.yahoo.com/v1/finance/scrumb/screener/tokens/most_actives"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # استخراج قائمة الأسهم من الهيكل البرمجي للياهو
            quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
            
            scanned_count = 0
            for stock in quotes:
                ticker = stock.get('symbol')
                price = stock.get('regularMarketPrice')
                change_percent = stock.get('regularMarketChangePercent')
                
                if not ticker or price is None or change_percent is None:
                    continue
                
                # تصفية ملكية صارمة: السعر بين 1 و 30 دولار والصعود فوق 5% لقطف الزخم المشتعل
                if 1.0 <= price <= 30.0 and change_percent > 5.0:
                    scanned_count += 1
                    alert_text = f"🔥 *اكتشاف سهم فوليوم انفجاري (رادار رعد)* 🔥\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي الحالي:** `${price:.2f}`\n" \
                                 f"📈 **نسبة الصعود اللحظية:** `+{change_percent:.2f}%`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الحالة:* سيولة ضخمة وزخم تداول نشط جداً بالماركت الحين!"
                    send_msg(alert_text)
            
            logging.info(f"🔄 تم فحص قائمة السيولة بنجاح واكتشاف {scanned_count} أسهم تطابق الشروط الملكية.")
    except Exception as e:
        logging.error(f"خطأ أثناء جلب قائمة السيولة: {e}")

# رسالة التشغيل التي ستراها في السجل
logging.info("🚀 رادار الفوليوم المجاني والنهائي نشط ومحصن 100% ضد التوقف...")

while True:
    get_hot_volume_stocks()
    # يفحص القائمة النشطة تلقائياً كل 3 دقائق دون توقف
    time.sleep(180)
