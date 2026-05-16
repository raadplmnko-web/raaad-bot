import os
import time
import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import yfinance as yf

# إعدادات الـ Logging لمراقبة عمل السيرفر
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# بيانات التلجرام الخاصة بك
TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPyd1dzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        return res
    except Exception as e:
        logging.error(f"خطأ في إرسال رسالة التلجرام: {e}")

def calculate_mfi(df, period=7):
    """ حساب مؤشر تدفق الأموال MFI """
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    money_flow = typical_price * df['Volume']
    
    positive_flow = pd.Series(0.0, index=df.index)
    negative_flow = pd.Series(0.0, index=df.index)
    
    price_diff = typical_price.diff()
    positive_flow.loc[price_diff > 0] = money_flow.loc[price_diff > 0]
    negative_flow.loc[price_diff < 0] = money_flow.loc[price_diff < 0]
    
    pos_mf = positive_flow.rolling(window=period).sum()
    neg_mf = negative_flow.rolling(window=period).sum()
    
    neg_mf = neg_mf.replace(0, np.nan)
    mfi = 100 - (100 / (1 + (pos_mf / neg_mf)))
    mfi = mfi.fillna(50)
    return mfi

def calculate_atr(df, period=14):
    """ حساب مؤشر ATR الموزون (RMA) كما في TradingView """
    high_low = df['High'] - df['Low']
    high_cp = (df['High'] - df['Close'].shift(1)).abs()
    low_cp = (df['Low'] - df['Close'].shift(1)).abs()
    
    tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    return atr

def get_active_market_stocks():
    """ جلب الأسهم الأكثر نشاطاً في السوق الأمريكي تحت 10$ وبفاليوم حي """
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=false&screenerId=most_actives&count=100"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).json()
        
        discovered_stocks = []
        quotes = response.get('finance', {}).get('result', [{}])[0].get('quotes', [])
        
        for q in quotes:
            symbol = q.get('symbol')
            price = q.get('regularMarketPrice', 100)
            volume = q.get('regularMarketVolume', 0)
            
            # فلترة أولية: السعر تحت 10$ وحجم تداول يومي أعلى من نصف مليون
            if symbol and price < 10.0 and volume > 500000:
                if "^" not in symbol and "=" not in symbol:
                    discovered_stocks.append(symbol)
                    
        return list(set(discovered_stocks))
    except Exception as e:
        logging.error(f"خطأ في جلب قائمة السوق النشطة: {e}")
        return []

logging.info("🚀 رادار رعد الأسطوري V24 يعمل بنمط (إشارة دخول رعد ⚡ فقط) على مدار الساعة...")

while True:
    try:
        # تحديد الوقت بتوقيت نيويورك لمعرفة فترات السوق
        tz_ny = pytz.timezone('America/New_York')
        current_time_ny = datetime.now(tz_ny)
        current_day = current_time_ny.strftime('%A')
        current_hour = current_time_ny.hour
        current_minute = current_time_ny.minute
        
        time_float = current_hour + (current_minute / 60.0)
        
        market_phase = "السوق الرسمي 🟢"
        if time_float < 9.5:
            market_phase = "ما قبل السوق (Pre-Market) 🌅"
        elif time_float > 16.0:
            market_phase = "ما بعد السوق (After-Hours) 🌙"
            
        # إيقاف مؤقت في الويكند لتوفير جهد السيرفر
        if current_day in ['Saturday', 'Sunday']:
            logging.info(f"السوق مغلق عطلة نهاية الأسبوع ({current_day})...")
            time.sleep(300)
            continue
            
        active_stocks = get_active_market_stocks()
        logging.info(f"🔄 جاري مسح السوق وفحص إشارة (دخول رعد ⚡) لـ {len(active_stocks)} سهم...")
        
        for s in active_stocks:
            try:
                ticker = yf.Ticker(s)
                # جلب البيانات شاملة خارج أوقات العمل الرسمية
                df = ticker.history(period="5d", interval="1h", include_prepost=True)
                if df.empty or len(df) < 32: continue
                
                # الحسابات الفنية لـ V24
                df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
                df['MFI7'] = calculate_mfi(df, period=7)
                df['ATR14'] = calculate_atr(df, period=14)
                
                # مستويات المقاومة والدعم لآخر 30 شمعة و 10 شموع للوقف
                df['Res30'] = df['High'].shift(1).rolling(window=30).max()
                df['Sup30'] = df['Low'].shift(1).rolling(window=30).min()
                df['Low10'] = df['Low'].rolling(window=10).min()
                
                # القيم الحالية
                last_price = df['Close'].iloc[-1]
                ema9_val = df['EMA9'].iloc[-1]
                mfi_val = df['MFI7'].iloc[-1]
                res_val = df['Res30'].iloc[-1]
                sup_val = df['Sup30'].iloc[-1]
                atr_val = df['ATR14'].iloc[-1]
                low10_val = df['Low10'].iloc[-1]
                
                # القيم السابقة لتأكيد الاختراق المتقاطع
                prev_price = df['Close'].iloc[-2]
                prev_ema9 = df['EMA9'].iloc[-2]
                
                if pd.isna(res_val) or pd.isna(mfi_val) or pd.isna(atr_val): continue
                
                # معادلة "دخول رعد ⚡" الأصلية من مؤشرك:
                is_crossover = prev_price <= prev_ema9 and last_price > ema9_val
                is_near_res = last_price > (res_val * 0.98)
                is_high_mfi = mfi_val > 50
                
                if last_price < 10.0 and is_crossover and is_near_res and is_high_mfi:
                    
                    # حساب الوقف والأهداف طبق الأصل من التايم فيو
                    stop_loss = min(sup_val, low10_val) - (atr_val * 0.5)
                    target1 = last_price + (atr_val * 1.2)
                    target_gold = last_price + (atr_val * 3.0)
                    
                    alert_text = (
                        f"⚡ *إشارة: دخول رعد ⚡*\n\n"
                        f"🔹 *السهم:* `{s}`\n"
                        f"⏰ *الفترة:* {market_phase}\n"
                        f"📊 *السيولة MFI:* `{round(mfi_val)}%`\n"
                        f"----------------------------------\n"
                        f"🟢 **سعر الدخول:** `${last_price:.2f}`\n"
                        f"🛑 **وقف الخسارة:** `${stop_loss:.2f}`\n"
                        f"🎯 **الهدف الأول:** `${target1:.2f}`\n"
                        f"🏆 **الهدف الذهبي:** `${target_gold:.2f}`\n"
                        f"----------------------------------\n"
                        f"📈 *الرادار:* مستوفي الشروط، ومطابق للشاشة تماماً!"
                    )
                    send_msg(alert_text)
                    logging.info(f"✅ تم قنص وإرسال إشارة دخول رعد للسهم: {s}")
                    
            except Exception as e:
                continue
                
    except Exception as e:
        logging.error(f"خطأ في الدورة الرئيسية: {e}")
        
    time.sleep(300)
