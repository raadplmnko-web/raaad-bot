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

def calculate_macd(df):
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd.iloc[-1] > signal.iloc[-1] # إشارة إيجابية أم لا

def analyze_raad_v26(ticker):
    try:
        ticker = ticker.upper().strip()
        df = yf.Ticker(ticker).history(period="3mo")
        if df.empty: return "❌ لم أجد بيانات."
        
        close = float(df['Close'].iloc[-1])
        resVal = float(df['High'].rolling(window=30).max().iloc[-1])
        atr = float((df['High'] - df['Low']).rolling(window=14).mean().iloc[-1])
        
        mfi = calculate_mfi(df)
        is_macd_bullish = calculate_macd(df)
        
        # --- منطق القرار الأسطوري (دمج MFI و MACD) ---
        if close >= resVal and is_macd_bullish:
            decision = "⚡ دخول مؤكد (اختراق + زخم)"
        elif mfi > 65 and is_macd_bullish:
            decision = "🔥 مغامرة (زخم عالي)"
        elif mfi < 30:
            decision = "⚓ ارتداد (فرصة شراء)"
        else:
            decision = "⚖️ انتظار (سيولة متوازنة)"
            
        return (f"⚡ رادار رعد الأسطوري V26 - {ticker}\n"
                f"--------------------------\n"
                f"💰 السعر: {close:.2f}\n"
                f"📊 MFI: {mfi:.1f} | MACD: {'إيجابي' if is_macd_bullish else 'سلبي'}\n"
                f"🎯 قرار الرادار: {decision}\n"
                f"📈 هدف 1: {close + (atr*1.2):.2f}\n"
                f"🛑 وقف الخسارة: {close - (atr*1.5):.2f}\n"
                f"--------------------------")
    except Exception as e:
        return f"خطأ: {str(e)[:30]}"

async def handle_message(update, context):
    await update.message.reply_text(analyze_raad_v26(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
