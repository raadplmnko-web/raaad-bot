import os
import time
import requests
import logging
import yfinance as yf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

# قاموس ذكي لحفظ عدّاد التنبيهات المستقل لكل سهم على حدة
ticker_counters = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logging.error(f"خطأ تلجرام: {e}")

def scan_full_us_market_v32():
    global ticker_counters
    logging.info("🔄 جاري سحب قائمة الأسهم الأكثر اشتعالاً في السوق الأمريكي كاملاً...")
    scanned_count = 0
    
    try:
        # 1. جلب قائمة أكبر الأسهم الرابحة والمتحركة في السوق بالكامل تلقائياً
        gainers_tickers = []
        try:
            screener = yf.Screen(key='day_gainers')
            gainers_tickers = [quote['symbol'] for quote in screener.quotes]
        except Exception as screener_err:
            logging.error(f"خطأ في جلب القائمة التلقائية، جاري استخدام القائمة البديلة: {screener_err}")
            gainers_tickers = [
                "AIM", "BMEA", "BRSH", "CNEY", "EDBL", "GNS", "HOLO", "ICU", "JAGX", "KAVL",
                "LPA", "MGIH", "MULN", "NBY", "OCEA", "PHUN", "SIER", "TCBP", "VRAX", "XFOR",
                "AMAM", "BETR", "GCTS", "IMMP", "INBS", "MEDS", "PEV", "SOUN", "VERB", "WISA",
                "AEI", "AKAN", "AMPX", "AURA", "AVPR", "BAOS", "CCTG", "CXAI", "HUBC", "INVO",
                "KORK", "MRAI", "OPTT", "PEGY", "SINT", "SLNA", "TPET", "VREO", "WETG", "ZVSA",
                "NVD", "SISI", "REVB", "MNDR", "LIPO", "NKGN", "LGVN", "MDAI", "AGBA", "GWAV"
            ]

        if not gainers_tickers:
            return

        # تنظيف الرموز من أي نقاط أو شرطات غير مدعومة
        clean_watchlist = [t for t in gainers_tickers if "." not in t and "-" not in t]

        # 2. جلب البيانات اللحظية المجمعة بشكل رسمي ومستقر 100%
        tickers_data = yf.download(clean_watchlist, group_by='ticker', period='1d', interval='1m', prepost=True, progress=False)
        
        for ticker in clean_watchlist:
            try:
                if ticker not in tickers_data.columns.levels[0]:
                    continue
                    
                stock_history = tickers_data[ticker]
                if stock_history.empty:
                    continue
                
                ticker_obj = yf.Ticker(ticker)
                fast_info = ticker_obj.fast_info
                
                # جلب الأسعار اللحظية وبيانات اليوم الحالية
                price = float(stock_history['Close'].iloc[-1])
                open_price = float(stock_history['Open'].iloc[0]) if len(stock_history) > 0 else price
                
                # سحب الفوليوم التراكمي لليوم بدقة
                volume = int(fast_info.get('last_volume', 150000))
                if volume <= 0 or volume == 150000:
                    volume = int(fast_info.get('volume', 150000))
                
                # حساب نسبة التغير اللحظية بدقة
                change_percent = ((price - open_price) / open_price) * 100
                
                if price is None or change_percent is None:
                    continue
                    
                # 🎯 الفلترة الملكية: من 5$ وتحت + صعود إيجابي ممتاز وتدفق سيولة
                if 0.30 <= price <= 5.00 and change_percent > 1.5 and volume > 100000:
                    scanned_count += 1
                    
                    # 🔥 الحسبة الذكية هنا: تحديث عدّاد التنبيهات الخاص بهذا السهم بالتحديد
                    if ticker not in ticker_counters:
                        ticker_counters[ticker] = 1
                    else:
                        ticker_counters[ticker] += 1
                        
                    current_ticker_alert = ticker_counters[ticker]
                    entry_price = price
                    
                    # 📐 أهداف منطقية وقريبة جداً وسريعة التحقق بنسب مئوية مدروسة ومحسنة:
                    stop_loss = entry_price * 0.965  # وقف خسارة حامي وقريب عند -3.5%
                    target_1 = entry_price * 1.03    # هدف أول سريع عند +3%
                    target_2 = entry_price * 1.055   # هدف ثاني لتأمين الأرباح عند +5.5%
                    target_g = entry_price * 1.085   # هدف ذهبي ممتاز عند +8.5%
                    
                    alert_text = f"🚨 *رادار رعد الأسطوري: المسح الشامل للماركت* 🚨\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🔢 **تنبيه رقم لهذا السهم:** `#{current_ticker_alert}`\n\n" \
                                 f"🟢 **السعر اللحظي الحقيقي:** `${entry_price:.2f}`\n" \
                                 f"📈 **نسبة الارتفاع الفوري:** `+{change_percent:.2f}%`\n" \
                                 f"📊 **حجم التداول الكلي (Volume):** `{volume:,}`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *أرقام صفقات منطقية وسريعة التحقق:* \n\n" \
                                 f"📥 **نقطة الدخول المفضلة:** `${entry_price:.2f}`\n" \
                                 f"⛔ **وقف الخسارة الآمن (SL):** `${stop_loss:.2f}`\n" \
                                 f"💰 **الهدف الأول (T1):** `${target_1:.2f}`\n" \
                                 f"💎 **الهدف الثاني (T2):** `${target_2:.2f}`\n" \
                                 f"👑 **الهدف الذهبي (TG):** `${target_g:.2f}`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الحالة:* عدّاد تنبيهات مخصص ومنفصل لكل سهم تحت 5$! 🔥"
                                 
                    send_msg(alert_text)
                    time.sleep(2)
            except Exception as item_error:
                continue
                
        logging.info(f"🔄 تم إنهاء مسح الماركت بنجاح واكتشاف {scanned_count} فرص.")
    except Exception as e:
        logging.error(f"خطأ أثناء معالجة ياهو الشامل: {e}")

while True:
    scan_full_us_market_v32()
    time.sleep(90) # فحص مستمر ومريح لحماية السيرفر
