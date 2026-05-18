import requests
import time

TELEGRAM_TOKEN = "8809048554:AAHFEB7U68hSPyd1dzQZ5a2TQ205plJ3JKA"
CHAT_ID = "687056332"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Error: {e}")

def get_hot_volume_stocks():
    # سحب الأسهم الأعلى فوليوم وزخم في السوق الأمريكي لحظياً عبر واجهة مجانية ومفتوحة
    url = "https://financialmodelingprep.com/api/v3/stock_market/actives?apikey=demo"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            stocks = response.json()
            for stock in stocks:
                ticker = stock.get('ticker')
                price = float(stock.get('price', 0))
                changes_percentage = float(stock.get('changesPercentage', 0))
                
                # تصفية الأسهم حسب شروطك المفضلة (السعر تحت 30 دولار وزخم صعود قوي)
                if 1.0 <= price <= 30.0 and changes_percentage > 5.0:
                    alert_text = f"🔥 *اكتشاف سهم فوليوم مفاجئ (رادار رعد)* 🔥\n\n" \
                                 f"🔹 *السهم المكتشف:* `{ticker}`\n" \
                                 f"🟢 **السعر اللحظي:** `${price:.2f}`\n" \
                                 f"📈 **نسبة الصعود الحالية:** `+{changes_percentage:.2f}%`\n" \
                                 f"🎯 السهم عليه تداول عالي جداً بالماركت الحين!"
                    send_msg(alert_text)
    except Exception as e:
        print(f"Error fetching data: {e}")

print("🚀 رادار الفوليوم المجاني نشط ويبحث عن الأسهم الانفجارية...")
while True:
    get_hot_volume_stocks()
    time.sleep(180) # يفحص السوق تلقائياً كل 3 دقائق بحثاً عن أي سهم جديد يدخله فوليوم ضخم
