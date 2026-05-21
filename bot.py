import logging
import yfinance as yf
import pandas as pd
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

# الدوال الحسابية
def calculate_mfi(df, period=14):
    typical = (df['High'] + df['Low'] + df['Close']) / 3
    flow = typical * df['Volume']
    pos = flow.where(typical > typical.shift(1), 0).rolling(period, min_periods=1).sum()
    neg = flow.where(typical < typical.shift(1), 0).rolling(period, min_periods=1).sum()
    if neg.iloc[-1] == 0: return 50.0 
    return float((100 - (100 / (1 + (pos / neg)))).iloc[-1])

def calculate_atr(df, period=14):
    tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    return float(tr.rolling(period, min_periods=1).mean().iloc[-1])

def analyze_raad_v43(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="5d", interval="5m")
        
        # شرط بياناتك المحدث
        if len(df) < 6: return "⚠️ بيانات غير كافية للمضاربة"
        
        close = float(df['Close'].iloc[-1])
        vol = float(df['Volume'].iloc[-1])
        avg_vol = float(df['Volume'].rolling(20, min_periods=1).mean().iloc[-1])
        
        if avg_vol < 30000: return f"❌ {ticker}: سيولة ضعيفة"
        
        # استخدام إضافتك لـ prev_close_3
        prev_close_3 = float(df['Close'].iloc[-4])
        momentum3 = ((close - prev_close_3) / prev_close_3) * 100
        
        # شروط الخروج والسرعة الصارمة
        if momentum3 < -1.5: return f"⚠️ {ticker}: ضعف قوي / خروج"
        speed = abs(momentum3)
        if speed < 0.4: return f"❌ {ticker}: حركة ضعيفة (غير سكالب)"
        
        mfi = calculate_mfi(df)
        atr = calculate_atr(df)
        
        # نظام النقاط
        strength = 0
        if vol > avg_vol * 3: strength += 2
        elif vol > avg_vol * 1.5: strength += 1
        if momentum3 > 1: strength += 2
        elif momentum3 > 0.5: strength += 1
        if 50 < mfi < 65: strength += 1
        elif mfi > 70: strength += 2
        
        entry_score = strength
        if momentum3 > 2: entry_score += 2
        if speed > 1: entry_score += 1
        
        # الفلتر النهائي
        if entry_score < 4:
            return f"❌ {ticker}: لا توجد فرصة سكالب (النقاط: {entry_score})"
            
        # تحديد الأهداف
        if entry_score >= 6:
            decision, tp, sl = "🚀 دخول انفجار", close + (atr * 1.0), close - (atr * 0.5)
        else:
            decision, tp, sl = "⚡ دخول سكالب", close + (atr * 0.8), close - (atr * 0.6)
            
        return (f"⚡ رادار رعد V43 (المطور)\n"
                f"🏷️ السهم: {ticker}\n"
                f"📊 النقاط: {entry_score}\n"
                f"🎯 القرار: {decision}\n"
                f"🎯 هدف: {tp:.2f} | 🛑 وقف: {sl:.2f}")
                
    except Exception as e:
        return f"❌ خطأ تقني: {str(e)[:30]}"

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v43(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
