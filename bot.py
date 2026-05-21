import logging
import os
import yfinance as yf
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def analyze_raad_v26(ticker):
    try:
        ticker = ticker.upper().strip()
        # تحميل البيانات لآخر شهر
        data = yf.Ticker(ticker)
        df = data.history(period="1mo")
        
        if df.empty:
            return f"❌ لم أجد بيانات للرمز: {ticker}."
        
        # استخراج القيم والتأكد من أنها أرقام
        # نستخدم .iloc[-1] للحصول على آخر صف، ثم نأخذ القيمة ونحولها لـ float
        close_val = float(df['Close'].iloc[-1])
        # حساب المتوسط والمقاومة (استخدام .mean() و .max() يعيد قيمة مفردة)
        sma30 = float(df['Close'].rolling(window=30).mean().iloc[-1])
        resVal = float(df['High'].rolling(window=30).max().iloc[-1])
        
        decision = "🔥 اختراق إيجابي" if close_val >= resVal else "⚓ منطقة انتظار"
        
        return (f"⚡ تحليل {ticker}\n"
                f"القرار: {decision}\n"
                f"💰 السعر الحالي: {close_val:.2f}\n"
                f"📈 المقاومة: {resVal:.2f}\n"
                f"📊 متوسط 30 يوم: {sma30:.2f}")
                
    except Exception as e:
        return f"خطأ في معالجة البيانات. (التفاصيل: {str(e)[:40]})"

async def handle_message(update, context):
    ticker = update.message.text.upper().strip()
    if ticker.startswith('/'): return
    result = analyze_raad_v26(ticker)
    await update.message.reply_text(result)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    logging.info("البوت يعمل الآن!")
    app.run_polling()
