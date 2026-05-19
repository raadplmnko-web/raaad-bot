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

def scan_all_us_market_final():
    # استخدام سورس خفيف ومستقر ومفتوح جلب أعلى الأسهم صعوداً وحركة بالماركت بدون حظر
    url = "https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey=demo"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            top_gainers = data.get('top_gainers', [])
            
            scanned_count = 0
            for stock in top_gainers:
                ticker = stock.get('ticker', '').upper()
                
                try:
                    price = float(stock.get('price', 0))
                    # تنظيف النسبة المئوية من علامة % وتحويلها لرقم
                    change_percent = float(stock.get('change_percentage', '0').replace('%', ''))
                    volume = int(stock.get('volume', 0))
                except:
                    continue
                
                if not ticker or price == 0:
                    continue
                
                # الفلترة الملكية المطلوبة: السعر بين 0.30$ و 10$ + فوليوم تداول قوي
                if 0.30 <= price <= 10.00 and change_percent > 1.0 and volume > 50000:
                    scanned_count += 1
                    alert_text = f"⚡ *رادار رعد: اقتناص إنفجاري حقيقي* ⚡\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي الحالي:** `${price:.2f}`\n" \
                                 f"📈 **نسبة الصعود المباشر:** `+{change_percent:.2f}%`\n" \
                                 f"📊 **حجم التداول (Volume):** `{volume:,}`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الحالة:* حركة اختراق صاعدة صريحة من قلب الماركت!"
                    send_msg(alert_text)
                    time.sleep(1.5)
            
            logging.info(f"🔄 تم فحص السوق بنجاح واكتشاف {scanned_count} أسهم مطابقة للفلتر.")
        else:
            logging.warning(f"السورس مشغول، رمز الاستجابة: {response.status_code}")
    except Exception as e:
        logging.error(f"خطأ أثناء قراءة الماركت الشامل: {e}")

send_msg("🚀 *تم إطلاق النسخة الرادارية النهائية الشاملة بدون حظر!* \n\nالرادار يفحص الآن كل أسهم أمريكا الصاعدة تحت الـ 10$ بأعلى استقرار بالماركت.")

while True:
    scan_all_us_market_final()
    time.sleep(90) # دورة فحص مستقرة كل دقيقة ونصف
