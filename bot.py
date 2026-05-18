import os
import time
import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import yfinance as yf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPyd1dzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        return requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        logging.error(f"خطأ إرسال تلجرام: {e}")

# دالة الجلب الذكي فائقة الأمان (حل مشكلة الـ 0 سهم)
def fetch_stock_data_safe(symbol):
    try:
        # المحاولة الأولى: فاصل 15 دقيقة المعتاد
        df = yf.download(symbol, period="3d", interval="15m", prepost=True, progress=False, group_by='ticker')
        if df is not None and not df.empty and len(df) >= 10:
            if 'Close' in df.columns and not pd.isna(df['Close'].iloc[-1]):
                return df, "15m"
        
        # المحاولة الثانية (خط الدفاع): تحويل الفاصل ليومي إذا كان السهم ضعيف السيولة لحظياً
        df_daily = yf.download(symbol, period="5d", interval="1d", progress=False, group_by='ticker')
        if df_daily is not None and not df_daily.empty and len(df_daily) >= 3:
            if 'Close' in df_daily.columns and not pd.isna(df_daily['Close'].iloc[-1]):
                return df_daily, "1d"
    except:
        return None, None
    return None, None

def get_active_market_stocks():
    return ["GOVX", "AUUD", "SPAI", "HCAI", "DGXX", "LBAT", "AIIO", "SIRI", "SOUN", "BBAI", "LCID", "NIO", "MARA", "RIOT"]

logging.info("🛡️ تشغيل رادار رعد الفولاذي V27 - نظام الحماية المزدوجة نشط...")

while True:
    try:
        tz_ny = pytz.timezone('America/New_York')
        current_time_ny = datetime.now(tz_ny)
        if current_time_ny.strftime('%A') in ['Saturday', 'Sunday']:
            time.sleep(60)
            continue
            
        active_stocks = get_active_market_stocks()
        scanned_count = 0  
        
        for s in active_stocks:
            try:
                df, timeframe = fetch_stock_data_safe(s)
                if df is None:
                    continue
                    
                last_price = float(df['Close'].iloc[-1])
                prev_price = float(df['Close'].iloc[-2])
                
                if last_price < 1.0 or last_price > 10.0:
                    continue
                
                scanned_count += 1
                
                # الحسابات الفنية الأساسية السريعة للفلترة
                df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
                res_val = df['High'].shift(1).rolling(window=3 if timeframe=="1d" else 15).max().iloc[-1]
                
                if pd.isna(res_val): continue
                
                # شرط اختراق مبسط وقوي جداً للمراقبة السريعة
                if last_price > res_val:
                    alert_text = f"⚡ *إشارة رادار رعد الفولاذي* ⚡\n\n" \
                                 f"🔹 *السهم المكتشف:* `{s}` (فريم: {timeframe})\n" \
                                 f"🟢 **سعر الدخول الحالي:** `${last_price:.2f}`\n" \
                                 f"📈 السهم يخترق المقاومة اللحظية بنجاح!"
                    send_msg(alert_text)
                    
            except:
                continue
                
        logging.info(f"🔄 بنجاح فحص وتحليل {scanned_count} سهم بدون أي تصفير أو توقف...")
        time.sleep(60)
    except Exception as e:
        time.sleep(10)
