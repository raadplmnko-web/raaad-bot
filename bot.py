import logging
import yfinance as yf
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def analyze_raad_v54_all_hours(ticker):
    try:
        ticker = ticker.upper().strip()
        # إضافة prepost=True لضمان جلب بيانات ما قبل وما بعد السوق
        df = yf.Ticker(ticker).history(period="1d", interval="5m", prepost=True)
        
        if df.empty or len(df) < 2: 
            return f"⚠️ {ticker}: لا توجد بيانات تداول حالياً (خارج ساعات العمل بالكامل)."
        
        current = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        momentum = ((current - prev) / prev) * 100
        
        tp = current * 1.008
        sl = current * 0.995
        status = "🔥 صعود" if momentum > 0 else "📉 هبوط"
        
        return (f"📊 رادار رعد (شامل الوقت): {ticker}\n"
                f"💰 السعر: {current:.2f}\n"
                f"⚡ الزخم: {momentum:.2f}%\n"
                f"🎯 هدف: {tp:.2f}\n"
                f"🛑 وقف: {sl:.2f}\n"
                f"⚙️ الحالة: {status}")
                
    except Exception as e:
        return f"❌ خطأ تقني."

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v54_all_hours(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
