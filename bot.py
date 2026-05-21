import logging
import os
import yfinance as yf
import pandas as pd
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# =========================================================
# إعدادات البوت
# =========================================================
logging.basicConfig(level=logging.INFO)

# تم تثبيت التوكن هنا لضمان عمل البوت فوراً في Railway
TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

if not TOKEN:
    raise ValueError("❌ خطأ: لم يتم العثور على التوكن")

# =========================================================
# حساب مؤشر السيولة MFI
# =========================================================
def calculate_mfi(df, period=14):
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    money_flow = typical_price * df['Volume']
    positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
    negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
    positive_mf = positive_flow.rolling(period).sum()
    negative_mf = negative_flow.rolling(period).sum()
    mfi = 100 - (100 / (1 + (positive_mf / negative_mf)))
    return float(mfi.iloc[-1])

# =========================================================
# حساب ATR الحقيقي
# =========================================================
def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return float(atr.iloc[-1])

# =========================================================
# تحليل السهم - رادار رعد V31
# =========================================================
def analyze_raad_v31(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="5d", interval="5m")
        if df.empty: return "❌ لم أجد بيانات لهذا السهم."
        
        close = float(df['Close'].iloc[-1])
        volume = float(df['Volume'].iloc[-1])
        avg_volume = float(df['Volume'].rolling(20).mean().iloc[-1])
        
        mfi = calculate_mfi(df)
        atr = calculate_atr(df)
        ema9 = float(df['Close'].ewm(span=9).mean().iloc[-1])
        ema20 = float(df['Close'].ewm(span=20).mean().iloc[-1])
        
        uptrend = close > ema9 > ema20
        downtrend = close < ema20
        high_volume = volume > avg_volume * 1.5
        super_volume = volume > avg_volume * 3
        
        # فلترة
        if close < 0.20 or avg_volume < 500000:
            return f"⚠️ {ticker}\nسهم غير مناسب للمضاربة (سيولة ضعيفة أو سعر متدني)."

        # السكور والقرار
        first_close = float(df['Close'].iloc[0])
        day_change = ((close - first_close) / first_close) * 100
        
        score = 0
        if mfi > 55: score += 1
        if mfi > 70: score += 2
        if high_volume: score += 2
        if super_volume: score += 2
        if uptrend: score += 3
        if day_change > 5: score += 2
        
        # المنطق النهائي
        if uptrend and super_volume and mfi > 75 and day_change > 7:
            decision = "🔥 دخول انفجار زخم"
        elif uptrend and high_volume and mfi > 60:
            decision = "⚡ دخول مؤكد"
        elif uptrend and mfi > 50:
            decision = "👀 مراقبة إيجابية"
        elif downtrend:
            decision = "🚫 لا تدخل (اتجاه هابط)"
        else:
            decision = "⏳ انتظر السيولة"
            
        strength = "🚀 انفجار" if score >= 10 else "🔥 قوي" if score >= 7 else "⚡ متوسط" if score >= 5 else "⚠️ ضعيف"
        
        return (f"⚡ رادار رعد الاحترافي V31\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🏷️ السهم: {ticker}\n"
                f"💰 السعر: {close:.2f}\n"
                f"📊 MFI: {mfi:.1f}\n"
                f"📈 الحجم: {'🚀 انفجار' if super_volume else '🔥 قوي' if high_volume else '⚠️ ضعيف'}\n"
                f"🚀 الحركة اليومية: {day_change:.2f}%\n"
                f"🎯 القرار: {decision}\n"
                f"💪 القوة: {strength} ({score}/12)\n"
                f"🎯 هدف 1: {close + (atr * 0.7):.2f}\n"
                f"🏆 هدف ذهبي: {close + (atr * 1.5):.2f}\n"
                f"🛑 وقف الخسارة: {close - (atr * 1.0):.2f}\n"
                f"━━━━━━━━━━━━━━━━━━")
    except Exception as e:
        return f"❌ خطأ: {str(e)[:50]}"

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v31(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("✅ رادار رعد V31 يعمل الآن...")
    app.run_polling()
