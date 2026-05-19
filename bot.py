import os
import time
import requests
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logging.error(f"خطأ تلجرام: {e}")

# قائمة وكلاء متغيرة لمحاكاة متصفحات حقيقية ومختلفة تماماً في كل دورة لمنع الرصد
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
]

def scan_us_market_anti_ban():
    # استخدام رابط خفيف ومستقل تماماً لياهو
    list_url = "https://query2.finance.yahoo.com/v1/finance/trending/US"
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://finance.yahoo.com',
        'Referer': 'https://finance.yahoo.com/'
    }
    
    try:
        response = requests.get(list_url, headers=headers, timeout=12)
        
        # إذا تم رصد حظر الـ IP القديم من ياهو
        if response.status_code == 429 or response.status_code == 500:
            logging.warning(f"تنبيه: الـ IP الخاص بالسيرفر يخضع للتهدئة حالياً. رمز الاستجابة: {response.status_code}")
            return
            
        if response.status_code == 200:
            data = response.json()
            trending_quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
            
            tickers = [stock.get('symbol', '').upper() for stock in trending_quotes if stock.get('symbol')]
            if not tickers:
                return
                
            # جلب البيانات اللحظية المجمعة في طلب واحد واقتصادي جداً
            symbols_str = ",".join(tickers)
            quote_url = f"https://query2.finance.yahoo.com/v7/finance/quote?symbols={symbols_str}"
            
            headers['User-Agent'] = random.choice(USER_AGENTS)
            res = requests.get(quote_url, headers=headers, timeout=12)
            if res.status_code != 200:
                return
                
            res_data = res.json()
            quotes = res_data.get('quoteResponse', {}).get('result', [])
            
            scanned_count = 0
            for quote_info in quotes:
                ticker = quote_info.get('symbol', '').upper()
                if not ticker or "." in ticker or "-" in ticker:
                    continue
                    
                # سحب الأسعار الحية الحقيقية الآن بالثانية
                price = quote_info.get('regularMarketPrice')
                change_percent = quote_info.get('regularMarketChangePercent')
                volume = quote_info.get('regularMarketVolume', 0)
                day_high = quote_info.get('regularMarketDayHigh')
                day_low = quote_info.get('regularMarketDayLow')
                
                if price is None or change_percent is None or day_high is None or day_low is None:
                    continue
                    
                # الفلترة الملكية: سعر مابين 0.30$ و 10$ + فوليوم وزخم قوي
                if 0.30 <= price <= 10.00 and change_percent > 1.0 and volume > 50000:
                    scanned_count += 1
                    
                    # 📐 حساب المعادلات المستخرجة بالملي من كود مؤشراتك المدمجة (V26)
                    calc_atr = (day_high - day_low) if (day_high - day_low) > 0 else (price * 0.08)
                    entry_price = price
                    
                    # الوقف الآمن والموسع لحماية الحساب من الذيول:
                    stop_loss = entry_price - (calc_atr * 0.4)
                    
                    # الأهداف الثلاثة المتكاملة المعتمدة على الـ ATR لمؤشراتك:
                    target_1 = entry_price + (calc_atr * 1.2)  # الهدف الأول
                    target_2 = entry_price + (calc_atr * 2.0)  # الهدف الثاني
                    target_g = entry_price + (calc_atr * 3.0)  # الهدف الذهبي
                    
                    if stop_loss <= 0:
                        stop_loss = entry_price * 0.92
                        
                    alert_text = f"🚨 *رادار رعد الأسطوري: النسخة الملكية V27* 🚨\n\n" \
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
                                 f"🎯 *الحالة:* اتصال لحظي متجدد وبأعلى حماية متوفرة!"
                                 
                    send_msg(alert_text)
                    time.sleep(2)
                    
            logging.info(f"🔄 تم فحص الماركت بنجاح واكتشاف {scanned_count} صفقات حية.")
    except Exception as e:
        logging.error(f"خطأ أثناء معالجة البيانات: {e}")

send_msg("🛡️ *تم تفعيل رادار رعد الأسطوري النسخة الملكية V27 بنجاح!* 🛡️\n\n- نظام دمج وفلترة متطور مقاوم للحظر ⚡\n- الأسعار حية ولحظية بالثانية مع أهداف ووقف مؤشراتك بالملي 📊")

while True:
    scan_us_market_anti_ban()
    time.sleep(120) # وضع فاصل زمني آمن ومريح جداً مدته دقيقتين لمنع إجهاد الـ IP
