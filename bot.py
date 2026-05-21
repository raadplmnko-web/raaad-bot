import logging
import os
import yfinance as yf
import pandas as pd
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN: TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def analyze_raad_v26(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="3mo")
        if df.empty: return "❌ لم أجد بيانات."
        
        # 1. الحسابات الأساسية (المنطق البرمجي للمؤشر)
        close = float(df['Close'].iloc[-1])
        high30 = float(df['High'].rolling(window=30).max().iloc[-1])
        low30 = float(df['Low'].rolling(window=30).min().iloc[-1])
        atr = float((df['High'] - df['Low']).rolling(window=14).mean().iloc[-1])
        
        # 2. الأهداف ووقف الخسارة (مطابق لمنطق Pine Script)
        target1 = close + (atr * 1.2)
        targetG = close + (atr * 3.0)
        stopLoss = low30 - (atr * 0.4)
        
        # 3. إشارة التحليل
        status = "🔥 إشارة مغامرة/اختراق" if close >= high30 else "⚓ منطقة انتظار (ارتداد)"
        
        return (f"⚡ رادار رعد الأسطوري V26 - {ticker}\n"
                f"--------------------------\n"
                f"💰 السعر الحالي: {close:.2f}\n"
                f"📈 المقاومة (الاختراق): {high30:.2f}\n"
                f"🛑 وقف الخسارة: {stopLoss:.2f}\n"
                f"🎯 هدف 1: {target1:.2f}\n"
                f"🏆 الهدف الذهبي: {targetG:.2f}\n"
                f"--------------------------\n"
                f"القرار: {status}")
                
    except Exception as e:
        return f"خطأ في معالجة الرادار: {str(e)[:30]}"

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v26(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
