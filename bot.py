import logging
import yfinance as yf
import pandas_ta as ta
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# إعداد السجل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ضع التوكن الخاص بك هنا
TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"

def analyze_raad_v26(ticker):
    try:
        # جلب البيانات
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if df.empty: return None
        
        close = float(df['Close'].iloc[-1])
        # حساب المؤشرات
        atr = float(ta.atr(df['High'], df['Low'], df['Close'], length=14).iloc[-1])
        mfi = float(ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'], length=7).iloc[-1])
        resVal = float(df['High'].rolling(30).max().iloc[-2])
        
        is_breakout = close >= resVal
        decision = "🔥 مغامرة (اختراق)" if is_breakout else "⚓ انتظار (ارتداد)"
        
        return {
            "decision": decision,
            "entry": close,
            "t1": close + (atr * 1.2),
            "tg": close + (atr * 3.0),
            "sl": close - (atr * 0.4),
            "mfi": mfi
        }
    except Exception as e:
        logging.error(f"Error analyzing {ticker}: {e}")
        return None

async def silent_analyzer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ticker = update.message.text.upper().strip()
    data = analyze_raad_v26(ticker)
    
    if data:
        msg = f"⚡ *تحليل رادار رعد لـ {ticker}*\n\n" \
              f"القرار: {data['decision']}\n" \
              f"💰 الدخول: `{data['entry']:.2f}`\n" \
              f"💰 هدف 1: `{data['t1']:.2f}`\n" \
              f"👑 هدف ذهبي: `{data['tg']:.2f}`\n" \
              f"⛔ وقف خسارة: `{data['sl']:.2f}`\n" \
              f"📊 سيولة MFI: `{data['mfi']:.1f}%`"
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ لم أتمكن من تحليل هذا السهم، تأكد من الرمز.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), silent_analyzer))
    application.run_polling()
