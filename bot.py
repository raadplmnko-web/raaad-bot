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

def analyze_raad_v40(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="5d", interval="5m")
        if df.empty or len(df) < 4: return "⚠️ السهم قليل البيانات."
        
        close = float(df['Close'].iloc[-1])
        vol = float(df['Volume'].iloc[-1])
        avg_vol = float(df['Volume'].rolling(20, min_periods=1).mean().iloc[-1])
        
        if avg_vol < 50000: return f"❌ {ticker}: سيولة ضعيفة"
        
        prev_close_3 = float(df['Close'].shift(3).iloc[-1])
        momentum3 = ((close - prev_close_3) / prev_close_3) * 100
        
        # فلتر السرعة (إضافتك)
        speed = abs(momentum3)
        if speed < 0.3: return f"❌ {ticker}: بطيء (غير صالح للسكالبينج)"
        if momentum3 < 0: return f"⚠️ {ticker}: خروج فوري / ضعف زخم"
        
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
        
        # منطق السكالبينج المدمج
        if strength >= 4 and momentum3 > 1 and vol > avg_vol * 2:
            decision = "🚀 دخول سكالب سريع"
            tp, sl = close + (atr * 0.5), close - (atr * 0.4)
        elif strength >= 3:
            decision = "⚡ دخول محتمل"
            tp, sl = close + (atr * 1.0), close - (atr * 1.0)
        else:
            decision = "⚠️ مراقبة"
            tp, sl = close + (atr * 0.6), close - (atr * 1.2)
            
        return (f"⚡ رادار رعد V40 (سكالبينج)\n"
                f"🏷️ السهم: {ticker}\n"
                f"🚀 الزخم: {momentum3:.2f}%\n"
                f"🎯 القرار: {decision}\n"
                f"🎯 هدف: {tp:.2f} | 🛑 وقف: {sl:.2f}")
                
    except Exception as e:
        return f"❌ خطأ: {str(e)[:30]}"

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v40(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
