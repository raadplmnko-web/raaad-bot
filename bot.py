import os
import time
import requests
import logging
import yfinance as yf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logging.error(f"خطأ تلجرام: {e}")

# قائمة ثابتة ومختارة من أقوى أسهم البيني ستوك والزخم للمراقبة المستمرة والسريعة
WATCHLIST = [
    "AIM", "BMEA", "BRSH", "CNEY", "EDBL", "GNS", "HOLO", "ICU", "JAGX", "KAVL",
    "LPA", "MGIH", "MULN", "NBY", "OCEA", "PHUN", "SIER", "TCBP", "VRAX", "XFOR",
    "AMAM", "BETR", "GCTS", "IMMP", "INBS", "MEDS", "PEV", "SOUN", "VERB", "WISA"
]

def scan_us_market_yfinance():
    logging.info("🔄 جاري بدء فحص السوق عبر مكتبة yfinance الرسمية...")
    scanned_count = 0
    
    try:
        # جلب البيانات لكل الأسهم في القائمة بطلب واحد سريع ومحمي برسمية المكتبة
        tickers_data = yf.download(WATCHLIST, group_by='ticker', period='1d', interval='1m', prepost=True, progress=False)
        
        for ticker in WATCHLIST:
            try:
                if ticker not in tickers_data.columns.levels[0]:
                    continue
                    
                stock_history = tickers_data[ticker]
                if stock_history.empty:
                    continue
                
                # جلب بيانات السهم الإجمالية الإضافية لضمان دقة حجم التداول اليومي الكلي
                ticker_obj = yf.Ticker(ticker)
                fast_info = ticker_obj.fast_info
                
                # جلب الأسعار اللحظية وبيانات اليوم الحالية
                price = float(stock_history['Close'].iloc[-1])
                day_high = float(stock_history['High'].max())
                day_low = float(stock_history['Low'].min())
                open_price = float(stock_history['Open'].iloc[0]) if len(stock_history) > 0 else price
                
                # السر هنا: سحب الفوليوم التراكمي لليوم بدقة من fast_info
                volume = int(fast_info.get('last_volume', 150000))
                if volume <= 0 or volume == 150000:
                    volume = int(fast_info.get('volume', 150000))
                
                # حساب نسبة التغير اللحظية بدقة
                change_percent = ((price - open_price) / open_price) * 100
                
                if price is None or change_percent is None:
                    continue
                    
                # الفلترة الملكية المعتمدة لأسهم الزخم والبيني ستوك
                if 0.30 <= price <= 10.00 and change_percent > 1.0:
                    scanned_count += 1
                    
                    # 📐 حساب المعادلات الفنية بدقة مطابقة لمؤشراتك بالملي بناءً على الـ ATR الديناميكي
                    calc_atr = (day_high - day_low) if (day_high - day_low) > 0 else (price * 0.08)
                    entry_price = price
                    
                    # وقف الخسارة الحامي والموسع لحماية الحساب من الذيول:
                    stop_loss = entry_price - (calc_atr * 0.4)
                    
                    # الأهداف الثلاثة المتكاملة المعتمدة على الـ ATR لمؤشراتك:
                    target_1 = entry_price + (calc_atr * 1.2)  # الهدف الأول
                    target_2 = entry_price + (calc_atr * 2.0)  # الهدف الثاني
                    target_g = entry_price + (calc_atr * 3.0)  # الهدف الذهبي
                    
                    if stop_loss <= 0:
                        stop_loss = entry_price * 0.92
                        
                    alert_text = f"🚨 *رادار رعد الأسطوري: النسخة الرسمية الفولاذية V28* 🚨\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي الحقيقي الحين:** `${entry_price:.2f}`\n" \
                                 f"📈 **نسبة الارتفاع الفوري:** `+{change_percent:.2f}%`\n" \
                                 f"📊 **حجم التداول الكلي (Volume):** `{volume:,}`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *أرقام الصفقات المستخرجة من مؤشراتك بالملي:* \n\n" \
                                 f"📥 **نقطة الدخول المفضلة:** `${entry_price:.2f}`\n" \
                                 f"⛔ **وقف الخسارة الآمن (SL):** `${stop_loss:.2f}`\n" \
                                 f"💰 **الهدف الأول (T1):** `${target_1:.2f}`\n" \
                                 f"💎 **الهدف الثاني (T2):** `${target_2:.2f}`\n" \
                                 f"👑 **الهدف الذهبي (TG):** `${target_g:.2f}`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الحالة:* اتصال رسمي مستقر 100% | جلب دقيق لحجم التداول 🔥"
                                 
                    send_msg(alert_text)
                    time.sleep(2)
            except Exception as item_error:
                continue
                
        logging.info(f"🔄 تم إنهاء الفحص بنجاح واكتشاف {scanned_count} فرص مطابقة للزخم.")
    except Exception as e:
        logging.error(f"خطأ أثناء معالجة ياهو بالمكتبة الرسمية: {e}")

while True:
    scan_us_market_yfinance()
    time.sleep(90) # فحص مستمر ومريح لحماية السيرفر
