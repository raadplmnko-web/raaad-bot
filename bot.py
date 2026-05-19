import os
import time
import requests
import logging
import yfinance as yf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

# متغير لحفظ عدد التنبيهات تصاعدياً
alert_counter = 0

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logging.error(f"خطأ تلجرام: {e}")

# قائمة الـ 50 سهماً من أقوى أسهم البيني ستوك والزخم لمراقبتها باستمرار
WATCHLIST = [
    "AIM", "BMEA", "BRSH", "CNEY", "EDBL", "GNS", "HOLO", "ICU", "JAGX", "KAVL",
    "LPA", "MGIH", "MULN", "NBY", "OCEA", "PHUN", "SIER", "TCBP", "VRAX", "XFOR",
    "AMAM", "BETR", "GCTS", "IMMP", "INBS", "MEDS", "PEV", "SOUN", "VERB", "WISA",
    "AEI", "AKAN", "AMPX", "AURA", "AVPR", "BAOS", "CCTG", "CXAI", "HUBC", "INVO",
    "KORK", "MRAI", "OPTT", "PEGY", "SINT", "SLNA", "TPET", "VREO", "WETG", "ZVSA"
]

def scan_us_market_v30():
    global alert_counter
    logging.info("🔄 جاري بدء فحص السوق للأسهم تحت 5$ بالمعادلات المنطقية...")
    scanned_count = 0
    
    try:
        # جلب البيانات المجمعة بطلب رسمي آمن ومستقر 100%
        tickers_data = yf.download(WATCHLIST, group_by='ticker', period='1d', interval='1m', prepost=True, progress=False)
        
        for ticker in WATCHLIST:
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
                
                # حساب نسبة Tغير اللحظية بدقة
                change_percent = ((price - open_price) / open_price) * 100
                
                if price is None or change_percent is None:
                    continue
                    
                # 🎯 السر هنا: الفلترة الملكية المحدثة حصرياً للأسهم من 5$ وتحت فقط!
                if 0.30 <= price <= 5.00 and change_percent > 1.0:
                    scanned_count += 1
                    alert_counter += 1  # زيادة عداد التنبيهات
                    
                    entry_price = price
                    
                    # 📐 أهداف منطقية وقريبة وسريعة التحقق بنسب مئوية مدروسة:
                    stop_loss = entry_price * 0.965  # وقف خسارة حامي وقريب عند -3.5%
                    target_1 = entry_price * 1.03    # هدف أول سريع عند +3%
                    target_2 = entry_price * 1.055   # هدف ثاني لتأمين الأرباح عند +5.5%
                    target_g = entry_price * 1.085   # هدف ذهبي ممتاز عند +8.5%
                    
                    alert_text = f"🚨 *رادار رعد الأسطوري: الأسهم تحت 5$ فقط* 🚨\n" \
                                 f"🔢 **تنبيه رقم:** `#{alert_counter}`\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي الحقيقي الحين:** `${entry_price:.2f}`\n" \
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
                                 f"🎯 *الحالة:* الفلتر مخصص للأسهم من 5$ وتحت | أهداف قريبة وواقعية! 🔥"
                                 
                    send_msg(alert_text)
                    time.sleep(2)
            except Exception as item_error:
                continue
                
        logging.info(f"🔄 تم إنهاء الفحص بنجاح واكتشاف {scanned_count} فرص مطابقة للزخم تحت 5$.")
    except Exception as e:
        logging.error(f"خطأ أثناء معالجة ياهو بالمكتبة الرسمية: {e}")

while True:
    scan_us_market_v30()
    time.sleep(90) # فحص دوري مستمر ومريح
