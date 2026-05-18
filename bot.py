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
    try:
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
    except:
        return pd.Series(50.0, index=df.index)

def calculate_atr(df, period=14):
    try:
        high_low = df['High'] - df['Low']
        high_cp = (df['High'] - df['Close'].shift(1)).abs()
        low_cp = (df['Low'] - df['Close'].shift(1)).abs()
        
        tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
        return atr
    except:
        return pd.Series(0.1, index=df.index)

def get_active_market_stocks():
    """ جلب ديناميكي شامل لأكثر الأسهم حركة ونشاطاً تغطي فترة ما قبل السوق والسوق الرسمي """
    discovered_stocks = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 1. جلب الأكثر نشاطاً بحجم التداول
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=false&screenerId=most_actives&count=50"
        res = requests.get(url, headers=headers).json()
        quotes = res.get('finance', {}).get('result', [{}])[0].get('quotes', [])
        for q in quotes:
            symbol = q.get('symbol')
            if symbol and "^" not in symbol and "=" not in symbol:
                discovered_stocks.append(symbol)
    except:
        pass

    # 2. جلب الأسهم الأكثر صعوداً لاقتناص طفرات الصباح
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=false&screenerId=day_gainers&count=50"
        res = requests.get(url, headers=headers).json()
        quotes = res.get('finance', {}).get('result', [{}])[0].get('quotes', [])
        for q in quotes:
            symbol = q.get('symbol')
            if symbol and "^" not in symbol and "=" not in symbol:
                discovered_stocks.append(symbol)
    except:
        pass

    return list(set(discovered_stocks))

logging.info("🚀 رادار رعد الأسطوري المطور (فحص على مدار الساعة) بدأ العمل بنجاح...")

while True:
    try:
        tz_ny = pytz.timezone('America/New_York')
        current_time_ny = datetime.now(tz_ny)
        current_day = current_time_ny.strftime('%A')
        current_hour = current_time_ny.hour
        current_minute = current_time_ny.minute
        
        time_float = current_hour + (current_minute / 60.0)
        
        # حماية عطلة نهاية الأسبوع فقط
        if current_day in ['Saturday', 'Sunday']:
            logging.info(f"السوق مغلق عطلة نهاية الأسبوع ({current_day})...")
            time.sleep(60)
            continue
            
        # تحديد اسم الفترة بشكل توضيحي فقط دون تعطيل المسح
        market_phase = "السوق الرسمي 🟢"
        if time_float < 9.5:
            market_phase = "ما قبل السوق (Pre-Market) 🌅"
        elif time_float > 16.0:
            market_phase = "ما بعد السوق (After-Hours) 🌙"
            
        active_stocks = get_active_market_stocks()
        logging.info(f"🔄 [{market_phase}] جاري مسح السوق وفحص إشارة رعد لـ {len(active_stocks)} سهم حركي...")
        
        for s in active_stocks:
            try:
                ticker = yf.Ticker(s)
                # سحب داتا حية شاملة لفترات ما قبل السوق
                df = ticker.history(period="3d", interval="15m", include_prepost=True)
                if df.empty or len(df) < 20: continue
                
                # قراءة السعر الحالي اللحظي بدقة
                info = ticker.fast_info
                last_price = info.get('lastPrice') if info.get('lastPrice') else df['Close'].iloc[-1]
                
                # التصفية السعرية: أسهم تحت الـ 10 دولار
                if last_price is None or last_price >= 10.0 or last_price <= 0.1:
                    continue
                
                df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
                df['MFI7'] = calculate_mfi(df, period=7)
                df['ATR14'] = calculate_atr(df, period=14)
                
                df['Res30'] = df['High'].shift(1).rolling(window=30).max()
                df['Sup30'] = df['Low'].shift(1).rolling(window=30).min()
                df['Low10'] = df['Low'].rolling(window=10).min()
                
                ema9_val = df['EMA9'].iloc[-1]
                mfi_val = df['MFI7'].iloc[-1]
                res_val = df['Res30'].iloc[-1]
                sup_val = df['Sup30'].iloc[-1]
                atr_val = df['ATR14'].iloc[-1]
                low10_val = df['Low10'].iloc[-1]
                
                prev_price = df['Close'].iloc[-2]
                prev_ema9 = df['EMA9'].iloc[-2]
                
                if pd.isna(res_val) or pd.isna(mfi_val) or pd.isna(atr_val): 
                    continue
                
                # تطبيق استراتيجية "دخول رعد" الفنية
                is_crossover = prev_price <= prev_ema9 and last_price > ema9_val
                is_near_res = last_price > (res_val * 0.96)
                is_high_mfi = mfi_val > 45
                
                if is_crossover and is_near_res and is_high_mfi:
                    stop_loss = min(sup_val, low10_val) - (atr_val * 0.5)
                    target1 = last_price + (atr_val * 1.2)
                    target_gold = last_price + (atr_val * 3.0)
                    
                    mfi_display = int(mfi_val)
                    
                    alert_text = (
                        f"⚡ *إشارة: دخول رعد ⚡*\n\n"
                        f"🔹 *السهم:* `{s}`\n"
                        f"⏰ *الفترة:* {market_phase}\n"
                        f"📊 *السيولة MFI:* `{mfi_display}%`\n"
                        f"----------------------------------\n"
                        f"🟢 **سعر الدخول الحاضر:** `${last_price:.2f}`\n"
                        f"🛑 **وقف الخسارة:** `${stop_loss:.2f}`\n"
                        f"🎯 **الهدف الأول:** `${target1:.2f}`\n"
                        f"🏆 **الهدف الذهبي:** `${target_gold:.2f}`\n"
                        f"----------------------------------\n"
                        f"📈 *الرادار:* مستوفي الشروط، وجاهز للقنص الفوري!"
                    )
                    send_msg(alert_text)
                    logging.info(f"✅ تم قنص وإرسال إشارة دخول رعد للسهم: {s}")
                    
            except Exception as e:
                continue
                
    except Exception as e:
        logging.error(f"خطأ في الدورة الرئيسية: {e}")
        
    # فحص سريع ومستمر كل دقيقة واحدة لمواكبة سرعة فترات التداول
    time.sleep(60)
