import logging
import os
import yfinance as yf
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

# قراءة التوكن (أولوية لـ Railway، ثم التوكن المباشر كخطة طوارئ)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def analyze_raad_v26(ticker):
    try:
        ticker = ticker.upper().strip()
        # تحميل البيانات
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        
        # التأكد من وجود بيانات
        if df is None or df.empty:
            return f"❌ لم أجد بيانات للرمز: {ticker}. تأكد من صحة الرمز."
        
        # استخراج القيم وتحويلها إلى رقم (float) مباشرة لتجنب خطأ الـ Series
        # نستخدم .iloc[-1] للحصول على آخر قيمة ثم نحولها لرقم
        close_val = float(df['Close'].iloc[-1])
        sma30_val = float(df['Close'].rolling(window=30).mean().iloc[-1])
        resVal_val = float(df['High'].rolling(window=30).max().iloc[-1])
        
        # منطق التحليل
        decision = "🔥 اختراق إيجابي" if close_val >= resVal_val else "⚓ منطقة انتظار"
        
        return (f"⚡ تحليل {ticker}\n"
                f"القرار: {decision}\n"
                f"💰 السعر الحالي: {close_val:.2f}\n"
                f"📈 المقاومة: {resVal_val:.2f}\n"
                f"📊 متوسط 30 يوم: {sma30_val:.2f}")
                
    except Exception as e:
        return f"خطأ في التحليل: ربما الرمز غير دقيق. التفاصيل: {str(e)[:50]}"

async def handle_message(update, context):
    ticker = update.message.text.upper().strip()
    # التحقق من أن الرسالة ليست أمراً (مثل /start)
    if ticker.startswith('/'):
        return
    result = analyze_raad_v26(ticker)
    await update.message.reply_text(result)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    logging.info("البوت يعمل الآن وبانتظار طلباتك...")
    app.run_polling()
