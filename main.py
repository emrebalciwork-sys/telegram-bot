import os
import re
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text})

def check_with_ai(message):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "google/gemini-2.5-flash",
                "messages": [
                    {"role": "system", "content": "Sana gelen metinde bir telefon numarası varsa SADECE o telefon numarasını yaz (Örn: 05xxxxxxxxx). Kesinlikle yoksa sadece 'YOK' yaz."},
                    {"role": "user", "content": message}
                ]
            }
        )
        result = response.json()['choices'][0]['message']['content'].strip()
        return None if "YOK" in result else result
    except:
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Gelen veriyi ham metin (string) olarak tamamen alıyoruz
        # Böylece SOCIFLY ne gönderirse göndersin sistem kaçırmayacak
        raw_data = request.get_data(as_text=True)
        print("Gelen Ham Veri:", raw_data) # Render loglarında görmek için
        
        # Metnin içinde herhangi bir yerde peş peşe rakamlar (telefon formatı) var mı?
        if any(char.isdigit() for char in raw_data):
            ai_result = check_with_ai(raw_data)
            if ai_result:
                bildirim = f"📱 Telefon Numarası Yakalandı!\n\n📞 Numara: {ai_result}\n💬 Gelen Detay: {raw_data[:300]}"
                send_telegram(bildirim)
    except Exception as e:
        print("Hata:", str(e))
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
