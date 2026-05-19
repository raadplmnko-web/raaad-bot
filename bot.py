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

def scan_all_us_market_gainers():
    # الاتصال بأقوى ممسح سوق مفتوح لفحص أفضل 100 سهم مشتعل في أمريكا حالياً
    url = "https://query2.finance.yahoo.com/v1/finance/scrumb/screener/tokens/day_gainers?count=100"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            data = response.json()
            quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
            
            scanned_count = 0
            for stock in quotes:
                ticker = stock.get('symbol', '').upper()
                
                # جلب السعر ونسبة الصعود بدقة فترات الماركت المختلفة
                price = stock.get('regularMarketPrice') or stock.get('postMarketPrice') or stock.get('preMarketPrice')
                change_percent = stock.get('regularMarketChangePercent') or stock.get('postMarketChangePercent') or stock.get('preMarketChangePercent')
                volume = stock.get('regularMarketVolume', 0)
                
                if not ticker or price is None or change_percent is None:
                    continue
                
                # الفلترة الملكية الصارمة المطلوبة:
                # سعر من 0.30$ إلى 10$ + صعود إيجابي ممتاز + فوليوم تداول حقيقي لتجنب الأسهم الوهمية
                if 0.30 <= price <= 10.00 and change_percent > 1.0 and volume > 50000:
                    scanned_count += 1
                    alert_text = f"⚡ *رادار رعد: اقتناص إنفجاري في السوق* ⚡\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي:** `${price:.2f}`\n" \
                                 f"📈 **نسبة الارتفاع المباشر:** `+{change_percent:.2f}%`\n" \
                                 f"📊 **حجم التداول (Volume):** `{volume:,}`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الحالة:* حركة اختراق صاعدة وسيولة حية بالماركت الحين!"
                    send_msg(alert_text)
                    time.sleep(1.5) # فاصل زمني بسيط لمنع حظر الرسائل
            
            logging.info(f"🔄 تم فحص السوق بالكامل واكتشاف {scanned_count} أسهم متطابقة للفلتر.")
        else:
            logging.warning(f"فشل جلب البيانات، رمز الاستجابة: {response.status_code}")
    except Exception as e:
        logging.error(f"خطأ أثناء قراءة الماركت الشامل: {e}")

send_msg("🚀 *تم إطلاق النسخة الرادارية الشاملة لكل أسهم أمريكا!* \n\nالرادار يفحص الآن أفضل 100 سهم متحرك تحت الـ 10$ بالثانية الحين وبدون لستة ثابتة.")

while True:
    scan_all_us_market_gainers()
    time.sleep(90) # تحديث مستمر كل دقيقة ونصف لملاحقة الأسهم الجديدة
