import logging
import yfinance as yf
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def analyze_raad_v50_3min(ticker):
    try:
        ticker = ticker.upper().strip()
        # جلب بيانات فريم 3 دقائق
        df = yf.Ticker(ticker).history(period="1d", interval="3m")
        if len(df) < 3: return "⚠️ سهم جديد / غير متاح."
        
        current = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        momentum = ((current - prev) / prev) * 100
        vol = float(df['Volume'].iloc[-1])
        
        # أهداف سكالبينج لفريم الـ 3 دقائق (أسرع وأدق)
        tp = current * 1.006  # هدف 0.6%
        sl = current * 0.995  # وقف 0.5%
        
        # كاشف الانفجار السريع
        if momentum > 0.5 and vol > 2000:
            return (f"⚡ رادار 3 دقائق: {ticker}\n"
                    f"🚀 زخم: {momentum:.2f}%\n"
                    f"💰 دخول: {current:.2f}\n"
                    f"🎯 هدف: {tp:.2f}\n"
                    f"🛑 وقف: {sl:.2f}\n"
                    f"🔥 الحالة: انفجار لحظي")
        
        elif momentum < -0.4:
            return f"⚠️ {ticker}: ضعف لحظي (خروج: {momentum:.2f}%)"
            
        else:
            return f"👀 {ticker}: وضع الانتظار على 3 دقائق"
                
    except Exception as e:
        return f"❌ خطأ تقني."

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v50_3min(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
