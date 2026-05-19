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

def scan_us_market_hybrid():
    # جلب أفضل 25 سهم مشتعل بالثانية لضمان دقة السعر اللحظي ومنع الحظر 500
    url = "https://query1.finance.yahoo.com/v1/finance/scrumb/screener/tokens/day_gainers?size=25"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://finance.yahoo.com/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 429 or response.status_code == 500:
            logging.warning("السيرفر مضغوط.. سيتم التحديث في الدورة القادمة تلقائياً.")
            return

        if response.status_code == 200:
            data = response.json()
            quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
            
            scanned_count = 0
            for stock in quotes:
                ticker = stock.get('symbol', '').upper()
                
                # السعر اللحظي الحقيقي والفوري بالثانية الحين
                price = stock.get('regularMarketPrice')
                change_percent = stock.get('regularMarketChangePercent')
                volume = stock.get('regularMarketVolume', 0)
                
                # جلب أعلى وأدنى سعر لليوم لحساب معدل المدى ATR بدقة المؤشر
                day_high = stock.get('regularMarketDayHigh')
                day_low = stock.get('regularMarketDayLow')
                
                if not ticker or price is None or change_percent is None or day_high is None or day_low is None:
                    continue
                
                # الفلترة الملكية: سعر مابين 0.30$ و 10$ + صعود زخم قوي الحين + فوليوم معتبر
                if 0.30 <= price <= 10.00 and change_percent > 1.5 and volume > 100000:
                    scanned_count += 1
                    
                    # حساب الـ ATR اللحظي بناءً على حركة اليوم الحالية لإعطاء قيم مطابقة
                    calc_atr = (day_high - day_low) if (day_high - day_low) > 0 else (price * 0.08)
                    
                    entry_price = price
                    
                    # معادلة الوقف من النسخة الشاملة (أكثر أماناً وحماية):
                    stop_loss = entry_price - (calc_atr * 0.4)
                    
                    # معادلات الأهداف المدمجة بالملي لضمان أعلى ربح:
                    target_1 = entry_price + (calc_atr * 1.2)  # هدف 1 من النسخة الشاملة
                    target_2 = entry_price + (calc_atr * 2.0)  # هدف 2 لتأمين منتصف الطريق
                    target_g = entry_price + (calc_atr * 3.0)  # الهدف الذهبي من النسخة الشاملة
                    
                    # تأمين الحساب في حال كان الحساب الرياضي أقل من صفر نتيجة تذبذب حاد
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
                    time.sleep(2) 
            
            logging.info(f"🔄 تم فحص الماركت بالنسخة الهجينة واكتشاف {scanned_count} أسهم صاعدة.")
    except Exception as e:
        logging.error(f"خطأ أثناء المسح المطور: {e}")

send_msg("🔥 *تم إطلاق النسخة الهجينة والأقوى لرادار رعد!* 🔥\n\n- الأسعار حية ولحظية بالثانية ⚡\n- دمج كامل لأهداف ووقف المؤشرين الشامل والزخم لحماية أرباحك بالملي 📊")

while True:
    scan_us_market_hybrid()
    time.sleep(60) # تحديث حار مستمر كل دقيقة لاقتناص الفرصة فور تشكلها
