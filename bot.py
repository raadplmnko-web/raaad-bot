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
    """ باقة الأسهم المنقحة والمطهرة تماماً من الرموز المعطلة كـ BTCM """
    clean_stocks = [
        "SIRI", "SOUN", "BBAI", "PLTR", "LCID", "NIO", "MARA", "RIOT", "CLSK", "WULF", 
        "HIVE", "BITF", "GOEV", "MULN", "XPEV", "LI", "FFIE", "LAZR", "WKHS", "PLUG", 
        "FCEL", "RUN", "BLNK", "AMC", "GME", "BB", "TLRY", "SNDL", "CGC", "SOFI", 
        "HOOD", "NU", "UPST", "AFRM", "OPEN", "DNA", "RNXT", "NUGT", "NKLA",
        "RUM", "CRDO", "PATH", "AI", "VERI", "CXAI", "SAVE", "JBLU", "CIFR", "ANY", 
        "SDG", "CAN", "IREN", "GNE", "AMPS", "BE", "CHPT", "EVGO", "SOLO", 
        "NVAX", "OCGN", "TNXP", "GNS", "XELA", "COSM", "CEI", "IMPP", "HUSA", "INDO", 
        "SNAP", "PTON", "GRWG", "ACB", "OGI", "FUBO", "RIG", "VALE", "AAL"
    ]
    return list(set(clean_stocks))

logging.info("🚀 رادار رعد الأسطوري V26 (إصلاح شامل لجلب أسعار البني ستوكس في البري ماركت)...")

while True:
    try:
        tz_ny = pytz.timezone('America/New_York')
        current_time_ny = datetime.now(tz_ny)
        current_day = current_time_ny.strftime('%A')
        current_hour = current_time_ny.hour
        current_minute = current_time_ny.minute
        
        time_float = current_hour + (current_minute / 60.0)
        
        if current_day in ['Saturday', 'Sunday']:
            logging.info(f"💤 السوق مغلق حالياً عطلة نهاية الأسبوع ({current_day})...")
            time.sleep(60)
            continue
            
        market_phase = "السوق الرسمي 🟢"
        if time_float < 9.5:
            market_phase = "ما قبل السوق (Pre-Market) 🌅"
        elif time_float > 16.0:
            market_phase = "ما بعد السوق (After-Hours) 🌙"
            
        active_stocks = get_active_market_stocks()
        scanned_count = 0  
        
        for s in active_stocks:
            try:
                ticker = yf.Ticker(s)
                df = ticker.history(period="3d", interval="15m", include_prepost=True)
                
                if df.empty or len(df) < 10: 
                    continue
                
                # تأمين قراءة السعر الأخير في شاشات الـ Pre-Market لتجنب الـ NaN
                last_price = df['Close'].iloc[-1]
                if pd.isna(last_price) or last_price is None:
                    last_price = df['Open'].iloc[-1] # تراجع ذكي في حال لم تنفذ شمعة إغلاق
                    
                prev_price = df['Close'].iloc[-2]
                if pd.isna(prev_price) or prev_price is None:
                    prev_price = df['Open'].iloc[-2]
                
                # التحقق النهائي الآمن من الأسعار ومطابقتها لشرط 10$ وتحت
                if pd.isna(last_price) or last_price >= 10.0 or last_price <= 0.1:
                    continue
                
                # إضافة السهم للعداد بنجاح بعد تجاوز فحص السعر
                scanned_count += 1
                
                # حساب الأساسيات الفنية V26 للرادار
                df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
                df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
                df['MFI7'] = calculate_mfi(df, period=7)
                df['ATR14'] = calculate_atr(df, period=14)
                df['RSI14'] = calculate_rsi(df, period=14)
                df['ADX7'] = calculate_adx(df, period=7)
                df['ROC10'] = df['Close'].pct_change(periods=10) * 100
                
                df['Res15'] = df['High'].shift(1).rolling(window=15).max()
                df['Sup15'] = df['Low'].shift(1).rolling(window=15).min()
                df['Low10'] = df['Low'].rolling(window=10).min()
                
                ema9_val  = df['EMA9'].iloc[-1]
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
                
                avg_vol = df['Volume'].rolling(window=20).mean().iloc[-1]
                current_vol = df['Volume'].iloc[-1]
                is_high_vol = current_vol > (avg_vol * 1.5)
                is_mega_vol = current_vol > (avg_vol * 2.8)
                
                is_roc_strong = roc_val > 1.5
                trend_strong  = adx_val > 22
                trend_weak    = adx_val < 18
                is_breakout   = (prev_price <= res_val and last_price > res_val) and is_high_vol
                
                signal_type = ""
                alert_emoji = ""
                
                if is_mega_vol and is_roc_strong and last_price > res_val and mfi_val > 55 and trend_strong:
                    signal_type = "انفجار زخم 💥"
                    alert_emoji = "💥💥"
                elif (prev_price <= prev_ema9 and last_price > ema9_val) and last_price > (res_val * 0.97) and mfi_val > 45 and trend_strong:
                    signal_type = "دخول رعد ⚡"
                    alert_emoji = "⚡⚡"
                elif (is_breakout or (is_mega_vol and df['Close'].iloc[-1] > df['Open'].iloc[-1])) and mfi_val > 40 and not trend_weak:
                    signal_type = "مغامرة زخم 🔥"
                    alert_emoji = "🔥🔥"
                elif df['Low'].iloc[-1] <= (sup_val * 1.01) and rsi_val < 40:
                    signal_type = "ارتداد قاع ⚓"
                    alert_emoji = "⚓⚓"

                if signal_type != "":
                    stop_loss = min(sup_val, low10_val) - (atr_val * 0.2)
                    target1 = last_price + (atr_val * 1.0)
                    target2 = last_price + (atr_val * 2.0)
                    target_gold = last_price + (atr_val * 3.2)
                    
                    alert_text = (
                        f"{alert_emoji} *إشارة: {signal_type}* {alert_emoji}\n\n"
                        f"🔹 *السهم المكتشف:* `{s}`\n"
                        f"⏰ *توقيت ومرحلة السوق:* {market_phase}\n"
                        f"📊 *سرعة صعود السعر ROC:* `{roc_val:.1f}%`\n"
                        f"🌊 *سيولة التدفق MFI:* `{mfi_val:.0f}%`\n"
                        f"🎯 *قوة مؤشر الـ RSI:* `{rsi_val:.0f}`\n"
                        f"💪 *قوة الترند ADX:* `{adx_val:.0f}`\n"
                        f"----------------------------------\n"
                        f"🟢 **سعر الدخول الفوري:** `${last_price:.2f}`\n"
                        f"🛑 **وقف الخسارة الجسداني:** `${stop_loss:.2f}`\n"
                        f"🎯 **الهدف السريع الأول:** `${target1:.2f}`\n"
                        f"🎯 **الهدف الإستراتيجي الثاني:** `${target2:.2f}`\n"
                        f"🏆 **الهدف الذهبي البعيد:** `${target_gold:.2f}`\n"
                        f"----------------------------------\n"
                        f"📈 *رادار رعد V26:* فحص نشط ومؤمن لأسهم تحت 10$!"
                    )
                    send_msg(alert_text)
                    logging.info(f"✅ [تم الإرسال] قنص إشارة {signal_type} للسهم: {s}")
                    
            except Exception as e:
                continue
                
        logging.info(f"🔄 [{market_phase}] بنجاح فحص وتحليل {scanned_count} سهم نشط حالياً...")
        time.sleep(60)
        
    except Exception as e:
        logging.error(f"خطأ في الدورة الرئيسية: {e}")
        time.sleep(10)
