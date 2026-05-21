import logging
import yfinance as yf
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def analyze_raad_v53_stable(ticker):
    try:
        ticker = ticker.upper().strip()
        # نطلب بيانات 5 أيام على فريم 5 دقائق لضمان توفر البيانات دائماً
        df = yf.Ticker(ticker).history(period="5d", interval="5m")
        
        if df.empty or len(df) < 2: 
            return f"⚠️ {ticker}: جاري تحديث البيانات، حاول مجدداً بعد لحظات."
        
        current = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        momentum = ((current - prev) / prev) * 100
        
        # أهداف ووقف مضاربي
        tp = current * 1.008
        sl = current * 0.995
        
        # رسالة مباشرة بدون فلاتر تمنعك
        status = "🔥 صعود" if momentum > 0 else "📉 هبوط"
        
        return (f"📊 رادار رعد (5 دقائق): {ticker}\n"
                f"💰 السعر: {current:.2f}\n"
                f"⚡ الزخم: {momentum:.2f}%\n"
                f"🎯 هدف: {tp:.2f}\n"
                f"🛑 وقف: {sl:.2f}\n"
                f"⚙️ الحالة: {status}")
                
    except Exception as e:
        return f"❌ خطأ تقني، تأكد من كتابة الرمز صحيحاً."

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v53_stable(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
