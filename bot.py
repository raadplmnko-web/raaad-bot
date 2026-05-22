import logging
import yfinance as yf
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def analyze_raad_v59_final(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="5d", interval="5m", prepost=True)
        
        if df.empty or len(df) < 20: return f"⚠️ {ticker}: بيانات غير كافية."
        
        current = float(df['Close'].iloc[-1])
        vol = float(df['Volume'].iloc[-1])
        avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
        vol_ratio = vol / avg_vol
        
        # تشخيص السيولة بدقة
        if vol_ratio > 2.0:
            vol_text = "انفجار 🔥 (سيولة عالية جداً)"
        elif vol_ratio > 1.0:
            vol_text = "متوسط 📈 (حركة طبيعية)"
        elif vol_ratio > 0.4:
            vol_text = "ضعيف 📉 (يحتاج مراقبة)"
        else:
            vol_text = "ميت ⛔ (سيولة معدومة)"
            
        momentum = ((current - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        
        # تقييم الدخول بناءً على السيولة
        if vol_ratio < 0.4:
            type_call = "⛔ ممنوع الدخول (سيولة ميتة)"
        elif momentum > 0.5 and vol_ratio > 1.0:
            type_call = "✅ دخول مؤكد"
        else:
            type_call = "⚠️ مغامرة"
        
        atr = (df['High'] - df['Low']).mean()
        target1 = current + (atr * 1.0)
        target_mid = current + (atr * 2.5)
        target_gold = current + (atr * 4.0)
        stop_loss = current - (atr * 1.5)
        
        return (f"⚡ رادار رعد V59\n"
                f"🏷️ السهم: {ticker}\n"
                f"💰 السعر: {current:.2f}\n"
                f"⚡ الزخم: {momentum:.2f}%\n"
                f"📊 الفاليوم: {vol_text}\n"
                f"⚖️ الحالة: {type_call}\n"
                f"--------------------------\n"
                f"🎯 هدف أول: {target1:.2f}\n"
                f"🎯 هدف وسط: {target_mid:.2f}\n"
                f"🏆 هدف ذهبي: {target_gold:.2f}\n"
                f"🛑 وقف الخسارة: {stop_loss:.2f}")
                
    except Exception as e:
        return f"❌ خطأ في النظام."

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v59_final(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
