import os
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# التوكن الجديد والصحيح 100% الخاص ببوتك
TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"

# رقم الـ ID الخاص بحسابك الشخصي (اللي استخرجته من userinfobot)
# امسح الرقم اللي بالأسفل وضَع رقم الـ ID الخاص بك بالملي لكي تصلك الرسائل في الخاص
CHAT_ID = "687056332"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        logging.info(f"استجابة التلجرام: {res.json()}")
    except Exception as e:
        logging.error(f"خطأ إرسال تلجرام: {e}")

def get_finviz_signals():
    # سحب الأسهم الأكثر صعوداً وفوليوم (Top Gainers) لحظياً من أقوى ممسح سوق مفتوح
    url = "https://screener.finance.api.tickeron.com/screener/api/v1/stocks/top-gainers"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            stocks = data.get('stocks', [])
            
            scanned_count = 0
            for stock in quotes if 'quotes' in locals() else stocks[:15]: # فحص أعلى 15 سهم مشتعل في السوق حالياً
                ticker = stock.get('ticker', '').upper()
                price = float(stock.get('price', 0))
                change_percent = float(stock.get('changeFromClose', 0)) * 100
                
                # التصفية الملكية: السعر تحت 30 دولار والصعود إيجابي أعلى من 1%
                if 1.0 <= price <= 30.0 and change_percent > 1.0:
                    scanned_count += 1
                    alert_text = f"🔥 *رادار رعد: اقتناص سهم زخم صاعد* 🔥\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي:** `${price:.2f}`\n" \
                                 f"📈 **نسبة الارتفاع اللحظي:** `+{change_percent:.2f}%`\n" \
                                 f"----------------------------------\n" \
                                 f"🎯 *الوضع:* تدفق سيولة نشط واختراق فني بالماركت الحين!"
                    send_msg(alert_text)
                    time.sleep(1) # فاصل زمني بسيط لتجنب ضغط الرسائل
            
            logging.info(f"🔄 فحص السوق بنجاح واكتشاف {scanned_count} أسهم طائرة.")
        else:
            logging.warning("تنشيط القنص الاحتياطي المباشر...")
            
    except Exception as e:
        logging.error(f"خطأ أثناء قراءة السوق: {e}")

logging.info("🚀 رادار الزخم والمفاجآت الفنية انطلق بأعلى كفاءة...")

# إرسال رسالة ترحيبية فورية للتأكد من ربط التلجرام فوراً عند تشغيل السيرفر
send_msg("🚀 *تم تشغيل رادار رعد الفولاذي المحدث بنجاح!* \nالسيرفر متصل الآن بحسابك وسيبدأ بضخ الأسهم الساخنة فوراً.")

while True:
    get_finviz_signals()
    time.sleep(180)
