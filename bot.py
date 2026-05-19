import os
import time
import requests
import logging
import yfinance as yf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

ticker_counters = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logging.error(f"خطأ تلجرام: {e}")

def scan_momentum_market_v33():
    global ticker_counters
    logging.info("🚀 جاري صيد أسهم الزخم الانفجاري...")
    
    try:
        # مسح السوق بحثاً عن الأسهم الأكثر نشاطاً في التداول (Most Active) وليس فقط الرابحة
        screener = yf.Screen(key='most_active')
        tickers = [quote['symbol'] for quote in screener.quotes]
        
        # فلترة مبدئية لسرعة الأداء
        clean_watchlist = [t for t in tickers if "." not in t and "-" not in t][:50]
        tickers_data = yf.download(clean_watchlist, group_by='ticker', period='2d', interval='1m', progress=False)
        
        for ticker in clean_watchlist:
            try:
                stock_history = tickers_data[ticker]
                if len(stock_history) < 2: continue
                
                # بيانات لحظية
                curr_price = float(stock_history['Close'].iloc[-1])
                prev_volume = float(stock_history['Volume'].iloc[-2]) # فوليوم الدقيقة السابقة
                curr_volume = float(stock_history['Volume'].iloc[-1]) # فوليوم الدقيقة الحالية
                
                # فلتر الزخم: سعر تحت 5$ + انفجار في الفوليوم (الدقيقة الحالية > 3 أضعاف السابقة)
                if 0.30 <= curr_price <= 5.00 and curr_volume > (prev_volume * 3) and curr_volume > 200000:
                    
                    if ticker not in ticker_counters: ticker_counters[ticker] = 1
                    else: ticker_counters[ticker] += 1
                    
                    entry_price = curr_price
                    alert_text = f"⚡ *رادار الزخم الانفجاري: صيد جديد!* ⚡\n\n" \
                                 f"🔹 *الرمز:* `{ticker}`\n" \
                                 f"🔢 *تنبيه رقم:* `#{ticker_counters[ticker]}`\n" \
                                 f"💰 *السعر اللحظي:* `${entry_price:.2f}`\n" \
                                 f"📊 *انفجار الفوليوم (Volume):* `{int(curr_volume):,}`\n" \
                                 f"----------------------------------\n" \
                                 f"📥 *نقطة الدخول:* `${entry_price:.2f}`\n" \
                                 f"⛔ *وقف الخسارة:* `${entry_price*0.96:.2f}`\n" \
                                 f"💎 *الأهداف:* T1:`{entry_price*1.04:.2f}` | T2:`{entry_price*1.07:.2f}`\n" \
                                 f"----------------------------------\n" \
                                 f"🚀 *الحالة:* هذا السهم يملك سيولة انفجارية لحظية الآن!"
                                 
                    send_msg(alert_text)
                    time.sleep(2)
            except: continue
    except Exception as e:
        logging.error(f"خطأ في مسح الزخم: {e}")

while True:
    scan_momentum_market_v33()
    time.sleep(60) # فحص كل دقيقة لصيد الزخم اللحظي
