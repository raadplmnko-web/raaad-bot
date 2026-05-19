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
    # إضافة أمر تفصيلي للياهو بجلب أسعار ما بعد وما قبل السوق الحية فوراً
    url = "https://query1.finance.yahoo.com/v1/finance/scrumb/screener/tokens/day_gainers?includePrePost=true"
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
                
                # قراءة سعر فترة ما بعد/قبل السوق إذا كان السوق مغلقاً، وإلا يقرأ السعر الرسمي
                price = stock.get('postMarketPrice') or stock.get('preMarketPrice') or stock.get('regularMarketPrice')
                change_percent = stock.get('postMarketChangePercent') or stock.get('preMarketChangePercent') or stock.get('regularMarketChangePercent')
                volume = stock.get('regularMarketVolume', 0)
                
                if not ticker or price is None or change_percent is None:
                    continue
                
                # الفلترة الملكية الصارمة: أقل من 10 دولار
                if 0.50 <= price <= 10.00 and change_percent > 1.0 and volume > 100000:
                    scanned_count += 1
                    alert_text = f"⚡ *رادار رعد: قنص فترات السوق الممتدة* ⚡\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي (خارج السوق):** `${price:.2f}`\n" \
                                 f"📈 **نسبة التغير اللحظية:** `+{change_percent:.2f}%`\n" \
                                 f"📊 **حجم التداول العام:** `{volume:,}`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الحالة:* رصد حركة سيولة نشطة خارج أوقات الماركت الرسمية!"
                    send_msg(alert_text)
                    time.sleep(1)
            logging.info(f"🔄 تم فحص أسهم الزخم الممتد بنجاح واكتشاف {scanned_count} أسهم.")
    except Exception as e:
        logging.error(f"خطأ أثناء جلب البيانات: {e}")

logging.info("🚀 تشغيل رادار رعد للفلترة الشاملة (رسمي + ممتد)...")

send_msg("🔥 *تم تحديث الرادار لدعم فترات Pre-Market و After-Hours!* 🔥\n\nالرادار الآن يراقب أي حركة فجائية من الساعة 11:00 صباحاً وحتى 3:00 الفجر للأسهم الأقل من 10$.")

while True:
    get_penny_stocks_under_10()
    time.sleep(180)
