import logging
import os
import yfinance as yf
import pandas as pd
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN: TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def calculate_mfi(df, period=14):
    typical = (df['High'] + df['Low'] + df['Close']) / 3
    flow = typical * df['Volume']
    pos = flow.where(typical > typical.shift(1), 0).rolling(period).sum()
    neg = flow.where(typical < typical.shift(1), 0).rolling(period).sum()
    return (100 - (100 / (1 + pos / neg))).iloc[-1]

def analyze_raad_v26(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="5d", interval="5m")
        if df.empty: return "❌ لم أجد بيانات لحظية."
        
        close = float(df['Close'].iloc[-1])
        volume = float(df['Volume'].iloc[-1])
        avg_vol = float(df['Volume'].rolling(window=20).mean().iloc[-1])
        atr = float((df['High'] - df['Low']).rolling(window=14).mean().iloc[-1])
        mfi = calculate_mfi(df)
        
        is_high_volume = volume > avg_vol
        
        # الأهداف ووقف الخسارة
        target1 = close + (atr * 0.5)
        targetG = close + (atr * 1.0)
        stopLoss = close - (atr * 0.8)
        
        # منطق القرار
        if mfi > 70 and is_high_volume:
            decision = "🔥 مغامرة (زخم عالي)"
        elif mfi < 30:
            decision = "⚓ ارتداد (فرصة شراء)"
        else:
            decision = "⚡ دخول (سيولة متوازنة)"
            
        return (f"⚡ رادار رعد (قناص الزخم) - {ticker}\n"
                f"--------------------------\n"
                f"💰 السعر: {close:.2f}\n"
                f"📊 السيولة (MFI): {mfi:.1f}\n"
                f"📈 الحجم: {'عالي' if is_high_volume else 'منخفض'}\n"
                f"🎯 قرار الرادار: {decision}\n"
                f"📈 هدف 1: {target1:.2f}\n"
                f"🏆 الهدف الذهبي: {targetG:.2f}\n"
                f"🛑 وقف الخسارة: {stopLoss:.2f}\n"
                f"--------------------------")
    except Exception as e:
        return f"خطأ: {str(e)[:30]}"

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v26(update.message.text))

if name == 'main':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
