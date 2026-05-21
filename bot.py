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
        ticker = ticker.upper()
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if df is None or df.empty:
            return f"❌ لم أجد بيانات لـ {ticker}."
        
        close = float(df['Close'].iloc[-1])
        sma30 = float(df['Close'].rolling(window=30).mean().iloc[-1])
        resVal = float(df['High'].rolling(window=30).max().iloc[-1])
        
        decision = "🔥 اختراق إيجابي" if close >= resVal else "⚓ منطقة انتظار"
        
        return f"⚡ تحليل {ticker}\nالقرار: {decision}\n💰 السعر الحالي: {close:.2f}\n📈 المقاومة: {resVal:.2f}\n📊 متوسط 30 يوم: {sma30:.2f}"
    except Exception as e:
        return f"خطأ: {str(e)}"

async def handle_message(update, context):
    ticker = update.message.text.upper().strip()
    result = analyze_raad_v26(ticker)
    await update.message.reply_text(result)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
