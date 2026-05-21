import logging
import yfinance as yf
import pandas as pd
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

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

def analyze_raad_v45(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="5d", interval="5m")
        if len(df) < 7: return "⚠️ بيانات غير كافية."
        
        close = float(df['Close'].iloc[-1])
        vol = float(df['Volume'].iloc[-1])
        avg_vol = float(df['Volume'].rolling(20, min_periods=1).mean().iloc[-1])
        
        if avg_vol < 30000: return f"❌ {ticker}: سيولة ضعيفة"
        
        momentum3 = ((close - float(df['Close'].iloc[-4])) / float(df['Close'].iloc[-4])) * 100
        momentum6 = ((close - float(df['Close'].iloc[-7])) / float(df['Close'].iloc[-7])) * 100
        
        if momentum3 < -1.5: return f"⚠️ {ticker}: ضعف قوي"
        if abs(momentum3) < 0.4: return f"❌ {ticker}: حركة ضعيفة"
        
        mfi = calculate_mfi(df)
        atr = calculate_atr(df)
        
        # نظام النقاط المتطور جداً
        entry_score = 0
        
        # 1. قوة الاتجاه (إضافتك)
        trend_strength = momentum3 - momentum6
        if trend_strength > 0.2: entry_score += 1
        else: entry_score -= 1
        
        # 2. تقييم MFI
        if 50 < mfi < 70: entry_score += 1
        elif mfi >= 70: entry_score += 2
        
        # 3. الاختراق (Breakout)
        breakout = (vol > avg_vol * 2.5) and (momentum3 > 1.5) and (mfi > 55)
        if breakout: entry_score += 2
        
        # الفلتر النهائي
        if entry_score < 4:
            return f"❌ {ticker}: لا توجد فرصة (نقاط: {entry_score})"
            
        decision = "🚀 دخول انفجار" if entry_score >= 6 else "⚡ دخول سكالب"
        tp = close + (atr * 0.9)
        sl = close - (atr * 0.6)
            
        return (f"⚡ رادار رعد V45 (النظام المتطور)\n"
                f"🏷️ السهم: {ticker}\n"
                f"📊 قوة الصفقة: {entry_score}\n"
                f"🎯 القرار: {decision}\n"
                f"🎯 هدف: {tp:.2f} | 🛑 وقف: {sl:.2f}")
                
    except Exception as e:
        return f"❌ خطأ: {str(e)[:30]}"

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v45(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
