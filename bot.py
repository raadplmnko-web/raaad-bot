import logging
import os
import yfinance as yf
import pandas as pd
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# =========================================================
# إعدادات البوت
# =========================================================
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("❌ ضع TELEGRAM_TOKEN في متغيرات البيئة")

# =========================================================
# حساب مؤشر السيولة MFI
# =========================================================
def calculate_mfi(df, period=14):

    typical_price = (
        df['High'] +
        df['Low'] +
        df['Close']
    ) / 3

    money_flow = typical_price * df['Volume']

    positive_flow = money_flow.where(
        typical_price > typical_price.shift(1),
        0
    )

    negative_flow = money_flow.where(
        typical_price < typical_price.shift(1),
        0
    )

    positive_mf = positive_flow.rolling(period).sum()

    negative_mf = negative_flow.rolling(period).sum()

    mfi = 100 - (
        100 / (1 + (positive_mf / negative_mf))
    )

    return float(mfi.iloc[-1])

# =========================================================
# حساب ATR الحقيقي
# =========================================================
def calculate_atr(df, period=14):

    high_low = df['High'] - df['Low']

    high_close = abs(
        df['High'] - df['Close'].shift()
    )

    low_close = abs(
        df['Low'] - df['Close'].shift()
    )

    tr = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    ).max(axis=1)

    atr = tr.rolling(period).mean()

    return float(atr.iloc[-1])

# =========================================================
# تحليل السهم
# =========================================================
def analyze_raad_v31(ticker):

    try:

        ticker = ticker.upper().strip()

        # =================================================
        # جلب البيانات
        # =================================================
        df = yf.Ticker(ticker).history(
            period="5d",
            interval="5m"
        )

        if df.empty:
            return "❌ لم أجد بيانات لهذا السهم."

        # =================================================
        # البيانات الأساسية
        # =================================================
        close = float(df['Close'].iloc[-1])

        volume = float(df['Volume'].iloc[-1])

        avg_volume = float(
            df['Volume'].rolling(20).mean().iloc[-1]
        )

        # =================================================
        # المؤشرات
        # =================================================
        mfi = calculate_mfi(df)

        atr = calculate_atr(df)

        ema9 = float(
            df['Close'].ewm(span=9).mean().iloc[-1]
        )

        ema20 = float(
            df['Close'].ewm(span=20).mean().iloc[-1]
        )

        # =================================================
        # الاتجاه
        # =================================================
        uptrend = close > ema9 > ema20

        sideways = (
            close > ema20 and
            close < ema9
        )

        downtrend = close < ema20

        # =================================================
        # الحجم
        # =================================================
        high_volume = volume > avg_volume * 1.5

        super_volume = volume > avg_volume * 3

        # =================================================
        # تصنيف الحجم
        # =================================================
        if super_volume:
            volume_text = "🚀 انفجار سيولة"

        elif high_volume:
            volume_text = "🔥 قوي"

        else:
            volume_text = "⚠️ ضعيف"

        # =================================================
        # فلترة الأسهم الخطيرة
        # =================================================
        if close < 0.20:

            return (
                f"⚠️ {ticker}\n\n"
                f"السهم منخفض جدًا.\n"
                f"🚫 لا تدخل"
            )

        if avg_volume < 500000:

            return (
                f"⚠️ {ticker}\n\n"
                f"السيولة اليومية ضعيفة.\n"
                f"🚫 لا تدخل"
            )

        # =================================================
        # نسبة الحركة اليومية
        # =================================================
        first_close = float(df['Close'].iloc[0])

        day_change = (
            (close - first_close)
            / first_close
        ) * 100

        # =================================================
        # نظام النقاط
        # =================================================
        score = 0

        if mfi > 55:
            score += 1

        if mfi > 70:
            score += 2

        if high_volume:
            score += 2

        if super_volume:
            score += 2

        if uptrend:
            score += 3

        if day_change > 5:
            score += 2

        # =================================================
        # تحديد الاتجاه
        # =================================================
        if uptrend:
            trend_text = "🟢 اتجاه صاعد"

        elif sideways:
            trend_text = "🟡 تذبذب"

        else:
            trend_text = "🔴 اتجاه هابط"

        # =================================================
        # القرار النهائي
        # =================================================
        if (
            uptrend and
            super_volume and
            mfi > 75 and
            day_change > 7
        ):

            decision = "🔥 دخول انفجار زخم"

        elif (
            uptrend and
            high_volume and
            mfi > 60
        ):

            decision = "⚡ دخول مؤكد"

        elif (
            uptrend and
            mfi > 50
        ):

            decision = "👀 مراقبة إيجابية"

        elif downtrend:

            decision = "🚫 لا تدخل"

        else:

            decision = "⏳ انتظر السيولة"

        # =================================================
        # سبب المنع
        # =================================================
        reason = ""

        if decision == "🚫 لا تدخل":

            reason = (
                "\n🚨 السبب:\n"
                "• الاتجاه هابط\n"
                "• الزخم غير مؤكد\n"
                "• لا يوجد اختراق قوي\n"
            )

        # =================================================
        # تقييم القوة
        # =================================================
        if score >= 10:
            strength = "🚀 انفجار زخم"

        elif score >= 7:
            strength = "🔥 قوي جدًا"

        elif score >= 5:
            strength = "⚡ متوسط"

        else:
            strength = "⚠️ ضعيف"

        # =================================================
        # الأهداف
        # =================================================
        target1 = close + (atr * 0.7)

        golden_target = close + (atr * 1.5)

        stop_loss = close - (atr * 1.0)

        # =================================================
        # إنشاء الرسالة
        # =================================================
        message = (
            f"⚡ رادار رعد الاحترافي V31\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"

            f"🏷️ السهم: {ticker}\n"

            f"💰 السعر: {close:.2f}\n\n"

            f"{trend_text}\n"

            f"📊 MFI: {mfi:.1f}\n"

            f"📈 الحجم: {volume_text}\n"

            f"🚀 الحركة اليومية: "
            f"{day_change:.2f}%\n\n"

            f"🎯 القرار:\n"
            f"{decision}\n\n"

            f"💪 القوة:\n"
            f"{strength}\n"

            f"⭐ السكور: {score}/12\n\n"

            f"🎯 الهدف الأول: "
            f"{target1:.2f}\n"

            f"🏆 الهدف الذهبي: "
            f"{golden_target:.2f}\n"

            f"🛑 وقف الخسارة: "
            f"{stop_loss:.2f}"
            f"{reason}\n"

            f"━━━━━━━━━━━━━━━━━━"
        )

        return message

    except Exception as e:

        return f"❌ خطأ:\n{str(e)[:120]}"

# =========================================================
# استقبال الرسائل
# =========================================================
async def handle_message(update, context):

    text = update.message.text

    result = analyze_raad_v31(text)

    await update.message.reply_text(result)

# =========================================================
# تشغيل البوت
# =========================================================
if __name__ == '__main__':

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & (~filters.COMMAND),
            handle_message
        )
    )

    print("✅ رادار رعد V31 يعمل الآن...")

    app.run_polling()
