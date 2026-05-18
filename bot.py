import os
import logging
from flask import Flask, request, jsonify
import requests

# إعدادات المراقبة اللحظية للسجل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# بيانات التلجرام المعتمدة والنشطة للرادار
TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPyd1dzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        return res.json()
    except Exception as e:
        logging.error(f"خطأ في إرسال رسالة التلجرام: {e}")
        return None

@app.route('/')
def home():
    return "⚡ سيرفر رادار رعد لاستقبال الـ Webhooks يعمل بنجاح ومستعد للقنص اللحظي! ⚡", 200

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    try:
        # استقبال البيانات القادمة من المنصة
        data = request.json
        
        # إذا أرسلت المنصة البيانات كنص عادي (Plain Text) وليس JSON
        if not data:
            data_text = request.data.decode('utf-8')
            logging.info(f"📩 تنبيه نصي قادم: {data_text}")
            send_telegram_message(data_text)
            return jsonify({"status": "success", "message": "Text notification processed"}), 200

        logging.info(f"📩 إشارة Webhook جديدة مستلمة بنجاح: {data}")
        
        # استخراج تفاصيل السهم من التنبيه التلقائي
        ticker = data.get('ticker', 'UNKNOWN').upper()
        price = data.get('price', '0.00')
        signal = data.get('signal', 'مغامرة زخم 🔥')
        action = data.get('action', 'دخول فوري')
        
        # صياغة الرسالة الملكية لرادار رعد لتظهر في التلجرام بشكل منظم جداً
        alert_text = f"💥 *إشارة رادار رعد الفورية (Webhook)* 💥\n\n" \
                     f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                     f"🟢 **سعر الدخول الفوري:** `${price}`\n" \
                     f"📊 **نوع الإشارة الفنية:** `{signal}`\n" \
                     f"🎯 **الإجراء المطلوب:** `{action}`\n" \
                     f"----------------------------------\n" \
                     f"📈 *وضع الاستقبال:* متصل ونشط ومؤمن 100%"
                     
        send_telegram_message(alert_text)
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logging.error(f"خطأ أثناء معالجة الـ Webhook المستلم: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # تشغيل محلي احتياطي
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
