import os
import time
import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import yfinance as yf

# إعدادات الـ Logging لمراقبة عمل السيرفر والعمليات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# بيانات التلجرام المعتمدة والنشطة لك
TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPyd1dzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        return res
    except Exception as e:
        logging.error(f"خطأ في إرسال رسالة التلجرام: {e}")

# ============================================================
# حسابات مؤشرات رادار رعد الفنية الفائقة المترجمة من Pine Script
# ============================================================

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
        return mfi.fillna(50)
    except:
        return pd.Series(50.0, index=df.index)

def calculate_atr(df, period=14):
    try:
        high_low = df['High'] - df['Low']
        high_cp = (df['High'] - df['Close'].shift(1)).abs()
        low_cp = (df['Low'] - df['Close'].shift(1)).abs()
        tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        return tr.ewm(alpha=1/period, adjust=False).mean()
    except:
        return pd.Series(0.1, index=df.index)

def calculate_rsi(df, period=14):
    try:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, np.nan)
        return (100 - (100 / (1 + rs))).fillna(50)
    except:
        return pd.Series(50.0, index=df.index)

def calculate_adx(df, period=7):
    """ حساب مؤشر ADX والـ DMI لفترة مقلصة للزخم السريع """
    try:
        plus_dm = df['High'].diff()
        minus_dm = df['Low'].diff()
        
        plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
        minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0.0)
        
        high_low = df['High'] - df['Low']
        high_cp = (df['High'] - df['Close'].shift(1)).abs()
        low_cp = (df['Low'] - df['Close'].shift(1)).abs()
        tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        
        tr_smooth = pd.Series(tr).rolling(window=period).sum()
        plus_dm_smooth = pd.Series(plus_dm, index=df.index).rolling(window=period).sum()
        minus_dm_smooth = pd.Series(minus_dm, index=df.index).rolling(window=period).sum()
        
        di_plus = (plus_dm_smooth / tr_smooth * 100).fillna(0)
        di_minus = (minus_dm_smooth / tr_smooth * 100).fillna(0)
        
        di_sum = di_plus + di_minus
        di_sum = di_sum.replace(0, np.nan)
        dx = (abs(di_plus - di_minus) / di_sum * 100).fillna(0)
        adx = dx.rolling(window=period).mean().fillna(20)
        return adx
    except:
        return pd.Series(20.0, index=df.index)

def get_active_market_stocks():
    """ القائمة الذهبية المنقحة المكونة من 39 سهم مضاربي """
    return [
        "SIRI", "SOUN", "BBAI", "PLTR", "LCID", "NIO", "MARA", "RIOT", "CLSK", "WULF", 
        "HIVE", "BITF", "GOEV", "MULN", "XPEV", "LI", "FFIE", "LAZR", "WKHS", "PLUG", 
        "FCEL", "RUN", "BLNK", "AMC", "GME", "BB", "TLRY", "SNDL", "CGC", "SOFI", 
        "HOOD", "NU", "UPST", "AFRM", "OPEN", "DNA", "RNXT", "NUGT", "NKLA"
    ]

logging.info("🚀 رادار رعد الأسطوري (الإصدار الاحترافي V26) بدأ الفحص التكاملي الحجمي...")

while True:
    try:
        tz_ny = pytz.timezone('America/New_York')
        current_time_ny = datetime.now(tz_ny)
        current_day = current_time_ny.strftime('%A')
        current_hour = current_time_ny.hour
        current_minute = current_time_ny.minute
        
        time_float = current_hour + (current_minute / 60.0)
        
        if current_day in ['Saturday', 'Sunday']:
            logging.info(f"السوق مغلق عطلة نهاية الأسبوع ({current_day})...")
            time.sleep(60)
            continue
            
        market_phase = "السوق الرسمي 🟢"
        if time_float < 9.5:
            market_phase = "ما قبل السوق (Pre-Market) 🌅"
        elif time_float > 16.0:
            market_phase = "ما بعد السوق (After-Hours) 🌙"
            
        active_stocks = get_active_market_stocks()
        logging.info(f"🔄 [{market_phase}] جاري مسح السوق فنيّاً لـ {len(active_stocks)} سهم طبقاً لشروط V26...")
        
        for s in active_stocks:
            try:
                ticker = yf.Ticker(s)
                df = ticker.history(period="4d", interval="15m", include_prepost=True)
                if df.empty or len(df) < 25: 
                    continue
                
                last_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2]
                
                # تصفية الأسهم السعرية
                if last_price is None or last_price >= 30.0 or last_price <= 0.1:
                    continue
                
                # حساب الأساسيات الفنية V26
                df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
                df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
                df['MFI7'] = calculate_mfi(df, period=7)
                df['ATR14'] = calculate_atr(df, period=14)
                df['RSI14'] = calculate_rsi(df, period=14)
                df['ADX7'] = calculate_adx(df, period=7)
                
                # ROC حساب معدل سرعة السعر
                df['ROC10'] = df['Close'].pct_change(periods=10) * 100
                
                # مستويات الدعم والمقاومة مقلصة لفترة 15 شمعة
                df['Res15'] = df['High'].shift(1).rolling(window=15).max()
                df['Sup15'] = df['Low'].shift(1).rolling(window=15).min()
                df['Low10'] = df['Low'].rolling(window=10).min()
                
                # القيم الحالية (الشمعة الأخيرة المنفذة)
                ema9_val  = df['EMA9'].iloc[-1]
                ema21_val = df['EMA21'].iloc[-1]
                mfi_val   = df['MFI7'].iloc[-1]
                atr_val   = df['ATR14'].iloc[-1]
                rsi_val   = df['RSI14'].iloc[-1]
                adx_val   = df['ADX7'].iloc[-1]
                roc_val   = df['ROC10'].iloc[-1]
                res_val   = df['Res15'].iloc[-1]
                sup_val   = df['Sup15'].iloc[-1]
                low10_val = df['Low10'].iloc[-1]
                
                prev_ema9 = df['EMA9'].iloc[-2]
                
                if pd.isna(res_val) or pd.isna(mfi_val) or pd.isna(atr_val) or pd.isna(roc_val): 
                    continue
                
                # تحليل وفحص الحجم (الفاليوم)
                avg_vol = df['Volume'].rolling(window=20).mean().iloc[-1]
                current_vol = df['Volume'].iloc[-1]
                is_high_vol = current_vol > (avg_vol * 2.0)
                is_mega_vol = current_vol > (avg_vol * 3.5)
                
                # الشروط الفنية المبنية بالـ Pine Script
                is_roc_strong = roc_val > 2.0
                trend_strong  = adx_val > 25
                trend_weak    = adx_val < 20
                is_breakout   = (prev_price <= res_val and last_price > res_val) and is_high_vol
                
                # تحديد نوع وقوة إشارة الصيد ⚡
                signal_type = ""
                alert_emoji = ""
                
                # 💥 1. انفجار زخم مدمر
                if is_mega_vol and is_roc_strong and last_price > res_val and mfi_val > 60 and trend_strong:
                    signal_type = "انفجار زخم 💥"
                    alert_emoji = "💥💥"
                # ⚡ 2. دخول رعد النموذجي
                elif (prev_price <= prev_ema9 and last_price > ema9_val) and last_price > (res_val * 0.98) and mfi_val > 50 and trend_strong and is_roc_strong:
                    signal_type = "دخول رعد ⚡"
                    alert_emoji = "⚡⚡"
                # 🔥 3. صفقة مغامرة وسرعة
                elif (is_breakout or (is_mega_vol and df['Close'].iloc[-1] > df['Open'].iloc[-1])) and mfi_val > 45 and not trend_weak and is_roc_strong:
                    signal_type = "مغامرة زخم 🔥"
                    alert_emoji = "🔥🔥"
                # ⚓ 4. ارتداد سفلي من القاع
                elif df['Low'].iloc[-1] <= (sup_val * 1.01) and (min(df['Open'].iloc[-1], last_price) - df['Low'].iloc[-1]) > abs(last_price - df['Open'].iloc[-1]) * 0.6 and rsi_val < 45:
                    signal_type = "ارت
