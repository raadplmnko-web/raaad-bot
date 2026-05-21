import logging
import os
import yfinance as yf
import pandas as pd
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN: TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def calculate_mfi(df, period=14):
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    money_flow = typical_price * df['Volume']
    positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(period).sum()
    negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(period).sum()
    mfi = 100 - (100 / (1 + positive_flow / negative_flow))
    return mfi.iloc[-1]

def analyze_raad_v26(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="3mo")
        if df.empty: return f"❌ لم أجد بيانات لـ {ticker}."
        
        close = float(df['Close'].iloc[-1])
        atr = float((df['High'] - df['Low']).rolling(window=14).mean().iloc[-1])
        mfi = calculate_mfi(df)
        
        # الأهداف
        target1 = close + (atr * 1.2)
        targetG = close + (atr * 3.0)
        stopLoss = close - (atr * 1.5)
        
        # حالة التشبع
        if mfi > 80: status_mfi = "🚨 تشبع شرائي (خطر!)"
        elif mfi < 20: status_mfi = "💎 تشبع بيعي (فرصة!)"
        else: status_mfi = "⚖️ سيولة متوازنة"
        
        return (f"⚡ رادار رعد الأسطوري V26 - {ticker}\n"
                f"--------------------------\n"
                f"💰 السعر الحالي: {close:.2f}\n"
                f"📊 مؤشر السيولة (MFI): {mfi:.1f} ({status_mfi})\n"
                f"🎯 هدف 1: {target1:.2f}\n"
                f"🏆 الهدف الذهبي: {targetG:.2f}\n"
                f"🛑 وقف الخسارة: {stopLoss:.2f}\n"
                f"--------------------------")
                
    except Exception as e:
        return f"خطأ في التحليل: {str(e)[:40]}"

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v26(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
