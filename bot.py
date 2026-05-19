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

def scan_us_market_final_hybrid():
    # 1. جلب قائمة الأسهم الأكثر نشاطاً كرموز فقط لتفادي الضغط
    list_url = "https://query1.finance.yahoo.com/v1/finance/scrumb/screener/tokens/day_gainers?size=30"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://finance.yahoo.com/'
    }
    
    try:
        response = requests.get(list_url, headers=headers, timeout=10)
        if response.status_code != 200:
            logging.warning(f"جاري انتظار استقرار السيرفر، رمز الاستجابة: {response.status_code}")
            return
            
        data = response.json()
        quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
        
        scanned_count = 0
        for stock in quotes:
            ticker = stock.get('symbol', '').upper()
            if not ticker or "." in ticker or "-" in ticker:
                continue
                
            # 2. الاستعلام عن البيانات اللحظية الكاملة لكل سهم بشكل منفصل ومضمون 100%
            quote_url = f"https://query1.finance.yahoo.com/v7/finance/options/{ticker}"
            res = requests.get(quote_url, headers=headers, timeout=5)
            if res.status_code != 200:
                continue
                
            res_data = res.json()
            result = res_data.get('optionChain', {}).get('result', [{}])
            if not result:
                continue
                
            quote_info = result[0].get('quote', {})
            
            # سحب البيانات الفورية واللحظية بالثانية الحين
            price = quote_info.get('regularMarketPrice')
            change_percent = quote_info.get('regularMarketChangePercent')
            volume = quote_info.get('regularMarketVolume', 0)
            day_high = quote_info.get('regularMarketDayHigh')
            day_low = quote_info.get('regularMarketDayLow')
            
            if price is None or change_percent is None or day_high is None or day_low is None:
                continue
                
            # الفلترة الملكية المعتمدة: السعر بين 0.30$ و 10$ + صعود إيجابي ممتاز + سيولة
            if 0.30 <= price <= 10.00 and change_percent > 1.5 and volume > 100000:
                scanned_count += 1
                
                # 📐 تطبيق معادلات مؤشرات رادار رعد الفنية بالملي
                calc_atr = (day_high - day_low) if (day_high - day_low) > 0 else (price * 0.08)
                entry_price = price
                
                # وقف الخسارة من النسخة الشاملة لضمان حماية الحساب:
                stop_loss = entry_price - (calc_atr * 0.4)
                
                # حساب الأهداف الثلاثة بناءً على قيم الـ ATR لمؤشراتك:
                target_1 = entry_price + (calc_atr * 1.2)  # الهدف الأول
                target_2 = entry_price + (calc_atr * 2.0)  # الهدف الثاني (تأمين منتصف الطريق)
                target_g = entry_price + (calc_atr * 3.0)  # الهدف الذهبي
                
                if stop_loss <= 0:
                    stop_loss = entry_price * 0.92
                    
                alert_text = f"🚨 *رادار رعد الأسطوري: الخلطة الملكية الهجينة* 🚨\n\n" \
                             f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                             f"🟢 **السعر اللحظي الحقيقي الحين:** `${entry_price:.2f}`\n" \
                             f"📈 **نسبة الارتفاع الفوري:** `+{change_percent:.2f}%`\n" \
                             f"📊 **حجم التداول (Volume):** `{volume:,}`\n" \
                             f"----------------------------------\n" \
                             f"🎯 *أرقام الصفقات المستخرجة من مؤشراتك بالملي:* \n\n" \
                             f"📥 **نقطة الدخول المفضلة:** `${entry_price:.2f}`\n" \
                             f"⛔ **وقف الخسارة الآمن (SL):** `${stop_loss:.2f}`\n" \
                             f"💰 **الهدف الأول (T1):** `${target_1:.2f}`\n" \
                             f"💎 **الهدف الثاني (T2):** `${target_2:.2f}`\n" \
                             f"👑 **الهدف الذهبي (TG):** `${target_g:.2f}`\n" \
                             f"----------------------------------\n" \
                             f"🎯 *الحالة:* حركة اختراق صاعدة صريحة ومحمية بالكامل!"
                             
                send_msg(alert_text)
                time.sleep(2) # فاصل زمني لحماية الطلبات من الحظر وتنسيق الرسائل
                
        logging.info(f"🔄 تم فحص الماركت بنجاح واكتشاف {scanned_count} أسهم صاعدة بالأسعار اللحظية.")
    except Exception as e:
        logging.error(f"خطأ أثناء فحص السوق المطور: {e}")

send_msg("🔥 *تم إطلاق النسخة المستقرة النهائية لرادار رعد الهجين!* 🔥\n\n- جلب الأسعار اللحظية الحقيقية من السيرفر المباشر ⚡\n- حساب الأهداف والوقف بدقة كاملة ومطابقة لمؤشراتك الشامل والزخم 📊")

while True:
    scan_us_market_final_hybrid()
    time.sleep(90) # دورة فحص مريحة ومستمرة لمنع أي حظر
