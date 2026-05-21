import logging
import yfinance as yf
import pandas as pd
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"

def analyze_raad_v26(ticker):
    try:
        # تحميل البيانات
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if df.empty: return None
        
        # حساب المؤشرات يدوياً (بدون pandas_ta)
        close = float(df['Close'].iloc[-1])
        # متوسط متحرك بسيط (بديلاً عن المؤشرات المعقدة)
        sma30 = df['Close'].rolling(window=30).mean().iloc[-1]
        resVal = df['High'].rolling(window=30).max().iloc[-1]
        
        # منطق التحليل
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
    app.run_polling()
