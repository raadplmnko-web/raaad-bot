import logging
import yfinance as yf
import pandas as pd
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

# ... الدوال الحسابية (MFI, ATR) تبقى كما هي ...

def analyze_raad_v46(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="5d", interval="5m")
        if len(df) < 12: return "⚠️ بيانات غير كافية."
        
        close = float(df['Close'].iloc[-1])
        vol = float(df['Volume'].iloc[-1])
        avg_vol = float(df['Volume'].rolling(20, min_periods=1).mean().iloc[-1])
        
        if avg_vol < 30000: return f"❌ {ticker}: سيولة ضعيفة"
        
        # الزخم (3, 6, 12 شمعة)
        momentum3 = ((close - float(df['Close'].iloc[-4])) / float(df['Close'].iloc[-4])) * 100
        momentum6 = ((close - float(df['Close'].iloc[-7])) / float(df['Close'].iloc[-7])) * 100
        momentum12 = ((close - float(df['Close'].iloc[-10])) / float(df['Close'].iloc[-10])) * 100
        
        # فلتر الخروج والسرعة
        if momentum3 < -1.5: return f"⚠️ {ticker}: ضعف قوي"
        if abs(momentum3) < 0.4: return f"❌ {ticker}: حركة ضعيفة"
        
        mfi = calculate_mfi(df)
        atr = calculate_atr(df)
        
        # نظام النقاط V46
        entry_score = 0
        
        # 1. قوة الاتجاه والتسارع
        trend_strength = momentum3 - momentum6
        if trend_strength > 0.3: entry_score += 1
        elif trend_strength < -0.3: entry_score -= 1
        
        acceleration = momentum3 - momentum12
        if acceleration > 0.3: entry_score += 1
        
        # 2. الاختراق المطور (Breakout)
        breakout = (vol > avg_vol * 2.5) and (momentum3 > 1.5) and (mfi > 55)
        if breakout:
            entry_score += 1
            if vol > avg_vol * 3: entry_score += 1 # مكافأة إضافية لحجم ضخم
            
        # 3. تقييم MFI
        if 50 < mfi < 70: entry_score += 1
        elif mfi >= 70: entry_score += 2
        
        # الفلتر النهائي
        if entry_score < 4:
            return f"❌ {ticker}: لا توجد فرصة (نقاط: {entry_score})"
            
        decision = "🚀 دخول انفجار" if entry_score >= 6 else "⚡ دخول سكالب"
        tp = close + (atr * 0.9)
        sl = close - (atr * 0.6)
            
        return (f"⚡ رادار رعد V46\n"
                f"🏷️ السهم: {ticker}\n"
                f"📊 قوة الصفقة: {entry_score}\n"
                f"🎯 القرار: {decision}\n"
                f"🎯 هدف: {tp:.2f} | 🛑 وقف: {sl:.2f}")
                
    except Exception as e:
        return f"❌ خطأ: {str(e)[:30]}"

# ... بقية الكود (async, main) ...
