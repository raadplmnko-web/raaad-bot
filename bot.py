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

def scan_us_market_lightning():
    # استخدام سورس خفيف ومباشر ومفتوح جلب أعلى الأسهم صعوداً وحركة بالماركت
    url = "https://query1.finance.yahoo.com/v1/finance/scrumb/screener/tokens/day_gainers?size=40"
    
    # إضافة حماية ذكية دورية ومحاكاة تصفح كاملة بالثانية لمنع الحظر
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://finance.yahoo.com/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # إذا واجه ضغط مؤقت، نجعله ينتظر ثواني ويعيد المحاولة بسلاسة بدون توقف
        if response.status_code == 500 or response.status_code == 429:
            logging.warning("السيرفر يطلب تهدئة الطلبات.. جاري الانتظار والتحديث...")
            time.sleep(5)
            return
            
        if response.status_code == 200:
            data = response.json()
            quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
            
            scanned_count = 0
            for stock in quotes:
                ticker = stock.get('symbol', '').upper()
                
                # قراءة الأسعار الحية الحالية بالسوق المفتوح
                price = stock.get('regularMarketPrice')
                change_percent = stock.get('regularMarketChangePercent')
                volume = stock.get('regularMarketVolume', 0)
                
                if not ticker or price is None or change_percent is None:
                    continue
                
                # الفلترة الملكية اللحظية الحين: السعر بين 0.30$ و 10$ + فوليوم تداول فوق 50 ألف
                if 0.30 <= price <= 10.00 and change_percent > 1.0 and volume > 50000:
                    scanned_count += 1
                    alert_text = f"🚨 *رادار رعد: اقتناص حركة حية بالماركت* 🚨\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي الحالي:** `${price:.2f}`\n" \
                                 f"📈 **نسبة الصعود المباشر:** `+{change_percent:.2f}%`\n" \
                                 f"📊 **حجم التداول (Volume):** `{volume:,}`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الحالة:* اختراق وزخم سيولة نشط في السوق المفتوح الحين!"
                    send_msg(alert_text)
                    time.sleep(1.5)
            
            logging.info(f"🔄 تم فحص السوق بنجاح واكتشاف {scanned_count} أسهم متطابقة للفلتر.")
    except Exception as e:
        logging.error(f"خطأ أثناء قراءة الماركت: {e}")

send_msg("🚀 *تم إطلاق النسخة الرادارية الفولاذية والبرق السريع!* \n\nالرادار يفحص الآن الماركت الأمريكي المفتوح بالكامل تحت الـ 10$ وبأعلى ثبات واستقرار دائم.")

while True:
    scan_us_market_lightning()
    time.sleep(60) # فحص مستمر وجديد كل 60 ثانية لسرعة اصطياد الفرص المشتعلة
