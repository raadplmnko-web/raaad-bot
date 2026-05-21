import logging
import yfinance as yf
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def analyze_raad_v51_sniper(ticker):
    try:
        ticker = ticker.upper().strip()
        # جلب بيانات فريم 3 دقائق (طلب 5 أيام لضمان توفر البيانات دائماً)
        df = yf.Ticker(ticker).history(period="5d", interval="3m")
        
        if len(df) < 2: 
            return f"⚠️ {ticker}: لا توجد بيانات كافية حالياً."
        
        current = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        momentum = ((current - prev) / prev) * 100
        vol = float(df['Volume'].iloc[-1])
        
        # أهداف سكالبينج (هدف 0.6% ووقف 0.4%)
        tp = current * 1.006
        sl = current * 0.996
        
        # منطق القناص (بدون فلاتر معقدة)
        if momentum > 0.3:
            return (f"🎯 قناص: {ticker}\n"
                    f"🚀 اتجاه: صعود (زخم {momentum:.2f}%)\n"
                    f"💰 دخول: {current:.2f}\n"
                    f"🎯 هدف: {tp:.2f}\n"
                    f"🛑 وقف: {sl:.2f}\n"
                    f"⚠️ مغامرة: سكالب سريع جداً")
        
        elif momentum < -0.3:
            return (f"⚠️ {ticker}: إشارة ضعف\n"
                    f"📉 زخم: {momentum:.2f}%\n"
                    f"💰 السعر الحالي: {current:.2f}")
        
        else:
            return f"👀 {ticker}: سهم هادئ (مراقبة.. السعر: {current:.2f})"
                
    except Exception as e:
        return f"❌ حدث خطأ تقني، تأكد من رمز السهم."

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v51_sniper(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
