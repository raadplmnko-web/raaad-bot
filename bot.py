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

def scan_us_market_safe():
    # استخدام رابط خفيف ومستقر جداً لتجنب الخطأ 500 نهائياً
    url = "https://query1.finance.yahoo.com/v1/finance/scrumb/screener/tokens/day_gainers?size=40"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
            
            scanned_count = 0
            for stock in quotes:
                ticker = stock.get('symbol', '').upper()
                
                # جلب السعر ونسبة الصعود اللحظية بدقة
                price = stock.get('regularMarketPrice') or stock.get('postMarketPrice') or stock.get('preMarketPrice')
                change_percent = stock.get('regularMarketChangePercent') or stock.get('postMarketChangePercent') or stock.get('preMarketChangePercent')
                volume = stock.get('regularMarketVolume', 0)
                
                if not ticker or price is None or change_percent is None:
                    continue
                
                # الفلترة الملكية الدقيقة: السعر تحت 10 دولار
                if 0.30 <= price <= 10.00 and change_percent > 1.0 and volume > 50000:
                    scanned_count += 1
                    alert_text = f"⚡ *رادار رعد: اقتناص سهم صاعد* ⚡\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي:** `${price:.2f}`\n" \
                                 f"📈 **نسبة الارتفاع المباشر:** `+{change_percent:.2f}%`\n" \
                                 f"📊 **حجم التداول (Volume):** `{volume:,}`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الحالة:* اختراق وزخم سيولة نشط بالماركت الحين!"
                    send_msg(alert_text)
                    time.sleep(1.5)
            
            logging.info(f"🔄 تم فحص السوق بنجاح واكتشاف {scanned_count} أسهم مطابقة للفلتر.")
        else:
            logging.warning(f"السيرفر مشغول، رمز الاستجابة: {response.status_code}. سيتم إعادة المحاولة تلقائياً...")
    except Exception as e:
        logging.error(f"خطأ أثناء قراءة الماركت: {e}")

send_msg("🚀 *تم تحديث الرادار للنسخة الآمنة والمستقرة ضد الحظر!* \n\nجاري بدء المسح الفوري لأسهم الماركت تحت 10$...")

while True:
    scan_us_market_safe()
    time.sleep(90) # تحديث كل دقيقة ونصف للحفاظ على استقرار الاتصال
