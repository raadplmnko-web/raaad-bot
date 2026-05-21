import logging
import yfinance as yf
import pandas_ta as ta
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPydldzQZ5a2TQ205plJ3JKA"

# دالة تحليل مؤشر رعد V26 (محاكي لمنطقك)
def analyze_raad_v26(ticker):
    try:
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if df.empty: return None
        
        close = df['Close'].iloc[-1]
        atr = ta.atr(df['High'], df['Low'], df['Close'], length=14).iloc[-1]
        mfi = ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'], length=7).iloc[-1]
        resVal = df['High'].rolling(30).max().iloc[-2]
        
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
    except: return None

# البوت هنا "صامت" لا يعمل تلقائياً، فقط يستجيب لطلبك
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
        # رد هادئ في حال عدم وجود بيانات
        await update.message.reply_text("❌ لم أجد بيانات لهذا الرمز.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    # البوت لا يفعل أي شيء إلا إذا أرسلت له نصاً
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), silent_analyzer))
    application.run_polling()
