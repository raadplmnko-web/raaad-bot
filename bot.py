import os
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

# استخدام Finnhub API لضمان استلام البيانات بالثانية وبدون حظر أو خطأ 500
FINNHUB_KEY = "cf96u91r01qgoct1706gcf96u91r01qgoct17070"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logging.error(f"خطأ تلجرام: {e}")

def scan_via_finnhub():
    # جلب قائمة بأكثر الأسهم نشاطاً وحركة في الماركت الأمريكي حالياً عبر Finnhub
    # هذا الرابط مستقر جداً ولا يعود بخطأ 500 أبداً
    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_KEY}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            symbols_data = response.json()
            
            # نأخذ عينة من أول 60 سهم نشط لتسريع عملية الفحص وتفادي تخطي القيود
            scanned_count = 0
            for item in symbols_data[:60]:
                ticker = item.get('symbol', '').upper()
                if not ticker or "." in ticker or "-" in ticker: # تخطي المؤشرات والأسهم المعقدة
                    continue
                
                # جلب السعر والنسبة اللحظية لكل سهم بشكل مباشر
                quote_url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}"
                res = requests.get(quote_url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    price = float(data.get('c', 0))
                    change_percent = float(data.get('dp', 0))
                    
                    # الفلترة الملكية المطلوبة: سعر بين 0.30$ و 10$ + صعود ممتاز فوق 1%
                    if 0.30 <= price <= 10.00 and change_percent > 1.0:
                        scanned_count += 1
                        alert_text = f"⚡ *رادار رعد: قنص عبر Finnhub المباشر* ⚡\n\n" \
                                     f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                     f"🟢 **السعر اللحظي الحالي:** `${price:.2f}`\n" \
                                     f"📈 **نسبة الارتفاع المباشر:** `+{change_percent:.2f}%`\n" \
                                     f"----------------------------------\n" \
                                     f"🎯 *الحالة:* حركة اختراق رصدت من قلب الـ API مباشرة بدون تأخير!"
                        send_msg(alert_text)
                        time.sleep(1.5) # فاصل زمني لحماية الحساب من الحظر
            
            logging.info(f"🔄 تم الفحص بنجاح عبر Finnhub واكتشاف {scanned_count} أسهم صاعدة.")
        else:
            logging.warning(f"Finnhub مشغول، رمز الاستجابة: {response.status_code}")
    except Exception as e:
        logging.error(f"خطأ أثناء فحص Finnhub الشامل: {e}")

send_msg("🔥 *تم تحويل السورس بالكامل إلى Finnhub API للتخلص من حظر ياهو!* 🔥\n\nالرادار يعمل الآن بأعلى استقرار لجلب أسهم الماركت تحت الـ 10$.")

while True:
    scan_via_finnhub()
    time.sleep(90) # دورة فحص مريحة ومستمرة كل دقيقة ونصف
