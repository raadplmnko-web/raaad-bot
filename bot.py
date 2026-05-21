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

def analyze_raad_v48(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="5d", interval="5m")
        if len(df) < 12: return "⚠️ سهم جديد / بيانات غير كافية."
        
        close = float(df['Close'].iloc[-1])
        vol = float(df['Volume'].iloc[-1])
        avg_vol = float(df['Volume'].rolling(20, min_periods=1).mean().iloc[-1])
        
        # تخفيف شرط السيولة للأسهم الطايرة
        if avg_vol < 15000: return f"❌ {ticker}: سيولة ميتة"
        
        momentum3 = ((close - float(df['Close'].iloc[-4])) / float(df['Close'].iloc[-4])) * 100
        momentum6 = ((close - float(df['Close'].iloc[-7])) / float(df['Close'].iloc[-7])) * 100
        
        # تخفيف شرط الخروج للأسهم الطايرة
        if momentum3 < -3.0: return f"⚠️ {ticker}: خروج طارئ (انهيار الزخم)"
        
        mfi = calculate_mfi(df)
        atr = calculate_atr(df)
        
        entry_score = 0
        
        # نقاط الصواريخ
        if momentum3 > 2.0: entry_score += 2 # زخم قوي جداً
        if vol > avg_vol * 2.0: entry_score += 2 # سيولة عالية
        if mfi > 60: entry_score += 1
        
        # منطق "السهم الطاير"
        is_rocket = momentum3 > 3.0 and vol > avg_vol * 1.5
        if is_rocket:
            decision = "🚀 سهم طاااااير! (ملاحقة)"
            entry_score += 3
        else:
            decision = "⚡ دخول سكالب" if entry_score >= 4 else "👀 مراقبة"

        if entry_score < 3 and not is_rocket:
            return f"👀 {ticker}: ضعيف (نقاط: {entry_score})"
            
        tp = close + (atr * 1.2) # هدف أوسع للأسهم الطايرة
        sl = close - (atr * 0.7)
            
        return (f"⚡ رادار رعد V48 (وضع الصواريخ)\n"
                f"🏷️ السهم: {ticker}\n"
                f"🔥 الحالة: {decision}\n"
                f"📊 قوة الزخم: {momentum3:.2f}%\n"
                f"🎯 هدف: {tp:.2f} | 🛑 وقف: {sl:.2f}")
                
    except Exception as e:
        return f"❌ خطأ: {str(e)[:30]}"

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v48(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
