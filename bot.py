import logging
import os
import yfinance as yf
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

# محاولة قراءة التوكن من Railway (الطريقة الرسمية)
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# إذا لم يجد التوكن، سنضع التوكن مباشرة هنا كـ "خطة طوارئ" (هذا سيحل المشكلة فوراً)
if not TOKEN:
    TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"
    logging.warning("تم استخدام التوكن من الكود مباشرة (خطة الطوارئ)!")
else:
    logging.info("تم العثور على التوكن من متغيرات النظام بنجاح!")

def analyze_raad_v26(ticker):
    try:
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if df.empty: return "لم يتم العثور على بيانات لهذا الرمز."
        close = float(df['Close'].iloc[-1])
        sma30 = df['Close'].rolling(window=30).mean().iloc[-1]
        resVal = df['High'].rolling(window=30).max().iloc[-1]
        decision = "🔥 اختراق إيجابي" if close >= resVal else "⚓ منطقة انتظار"
        return f"⚡ تحليل {ticker}\nالقرار: {decision}\n💰 السعر الحالي: {close:.2f}\n📈 المقاومة: {resVal:.2f}\n📊 متوسط 30 يوم: {sma30:.2f}"
    except Exception as e:
        return f"خطأ في التحليل: {e}"

async def handle_message(update, context):
    ticker = update.message.text.upper().strip()
    result = analyze_raad_v26(ticker)
    await update.message.reply_text(result)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    logging.info("البوت يعمل الآن ومتصل!")
    app.run_polling()
