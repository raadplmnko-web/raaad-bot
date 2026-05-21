import logging
import os
import yfinance as yf
import pandas as pd
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# =========================================================
# إعدادات البوت
# =========================================================
logging.basicConfig(level=logging.INFO)
TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

# =========================================================
# الحسابات الفنية
# =========================================================
def calculate_mfi(df, period=14):
    typical = (df['High'] + df['Low'] + df['Close']) / 3
    flow = typical * df['Volume']
    pos = flow.where(typical > typical.shift(1), 0).rolling(period).sum()
    neg = flow.where(typical < typical.shift(1), 0).rolling(period).sum()
    if neg.iloc[-1] == 0: return 50.0 
    return float((100 - (100 / (1 + (pos / neg)))).iloc[-1])

def calculate_atr(df, period=14):
    tr = pd.concat([df['High']-df['Low'], abs(df['High']-df['Close'].shift()), abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    return float(tr.rolling(period).mean().fillna(0).iloc[-1])

# =========================================================
# تحليل السهم - V34 (مع مستوى المغامرة)
# =========================================================
def analyze_raad_v34(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="5d", interval="5m")
        if df.empty or len(df) < 4: return "⚠️ السهم قليل البيانات."
        
        close = float(df['Close'].iloc[-1])
        vol = float(df['Volume'].iloc[-1])
        avg_vol = float(df['Volume'].rolling(20).mean().fillna(vol).iloc[-1])
        
        prev_close_3 = float(df['Close'].shift(3).iloc[-1])
        momentum3 = ((close - prev_close_3) / prev_close_3) * 100
        
        mfi = calculate_mfi(df)
        atr = calculate_atr(df)
        
        high_vol = vol > avg_vol * 1.5
        super_vol = vol > avg_vol * 3
        
        # منطق القرار المحدث
        if momentum3 > 0.8 and super_vol:
            decision = "🚀 زخم انفجار (قناص سريع)"
        elif momentum3 > 0.4 and high_vol:
            decision = "⚡ زخم قوي (دخول مبكر)"
        elif mfi > 50 and mfi < 65 and momentum3 > 0.2:
            decision = "⚠️ مغامرة (خطر عالي - وسط النطاق)"
        elif mfi > 70 and high_vol:
            decision = "🔥 دخول مؤكد"
        elif mfi < 30:
            decision = "⚓ ارتداد محتمل"
        else:
            decision = "⏳ ترقب السيولة"
            
        return (f"⚡ رادار رعد V34\n"
                f"🏷️ السهم: {ticker}\n"
                f"💰 السعر: {close:.2f}\n"
                f"🚀 الزخم: {momentum3:.2f}%\n"
                f"📊 MFI: {mfi:.1f}\n"
                f"📈 الحجم: {'🚀 انفجار' if super_vol else '🔥 قوي' if high_vol else '⚠️ ضعيف'}\n"
                f"🎯 القرار: {decision}\n"
                f"🎯 هدف: {close + (atr * 0.7):.2f}\n"
                f"🛑 وقف: {close - (atr * 1.0):.2f}")
                
    except Exception as e:
        return f"❌ خطأ تقني: {str(e)[:30]}"

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v34(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
