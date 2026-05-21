import logging
import yfinance as yf
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def analyze_raad_v52_pure(ticker):
    try:
        ticker = ticker.upper().strip()
        # طلب بيانات 3 دقائق بدون أي قيود
        df = yf.Ticker(ticker).history(period="1d", interval="3m")
        
        if len(df) < 2: 
            return f"⚠️ {ticker}: لا توجد بيانات في آخر 3 دقائق."
        
        current = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        momentum = ((current - prev) / prev) * 100
        
        # أهداف ووقف ثابت (بدون شروط دخول)
        tp = current * 1.005
        sl = current * 0.995
        
        # عرض البيانات كما هي بدون تقييم (نفي المشكلة)
        return (f"📊 بيانات {ticker} المباشرة:\n"
                f"💰 السعر الحالي: {current:.2f}\n"
                f"⚡ الزخم اللحظي: {momentum:.2f}%\n"
                f"🎯 هدف مقترح: {tp:.2f}\n"
                f"🛑 وقف مقترح: {sl:.2f}\n"
                f"⚙️ البوت يعمل الآن بنمط: الواقع المجرد")
                
    except Exception as e:
        return f"❌ خطأ تقني في جلب البيانات."

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v52_pure(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
