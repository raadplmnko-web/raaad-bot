import logging
import os
import yfinance as yf
from telegram.ext import ApplicationBuilder, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN: TOKEN = "8809048554:AAEidzYK2Ktvd1xDAdnEoAAb1WnfWQeHn1w"

def analyze_raad_v26(ticker):
    try:
        # تحميل البيانات
        ticker = ticker.upper()
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        
        # التأكد من وجود بيانات
        if df is None or df.empty: 
            return f"❌ عذراً، لم أجد بيانات للرمز: {ticker}. تأكد من صحة الرمز."
        
        # تصحيح المشكلة: التأكد من تحويل القيمة إلى رقم (float) بشكل صريح
        # .item() تحول القيمة المفردة من Series إلى رقم
        close = float(df['Close'].iloc[-1].item() if hasattr(df['Close'].iloc[-1], 'item') else df['Close'].iloc[-1])
        sma30 = float(df['Close'].rolling(window=30).mean().iloc[-1].item() if hasattr(df['Close'].iloc[-1], 'item') else df['Close'].rolling(window=30).mean().iloc[-1])
        resVal = float(df['High'].rolling(window=30).max().iloc[-1].item() if hasattr(df['High'].iloc[-1], 'item') else df['High'].rolling(window=30).max().iloc[-1])
        
        decision = "🔥 اختراق إيجابي" if close >= resVal else "⚓ منطقة انتظار"
        
        return f"⚡ تحليل {ticker}\nالقرار: {decision}\n💰 السعر الحالي: {close:.2f}\n📈 المقاومة: {resVal:.2f}\n📊 متوسط 30 يوم: {sma30:.2f}"
