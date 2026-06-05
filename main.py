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
                    {"role": "system", "content": "Sana gelen mesajda bir telefon numarası varsa SADECE o telefon numarası formatını yaz (Örn: 05xxxxxxxxx). Mesajda telefon numarası kesinlikle yoksa sadece 'YOK' yaz. Başka hiçbir şey yazma."},
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
        data = request.json
        if not data:
            return 'No Data', 400
            
        message_text = data.get('message', {}).get('text', '') or data.get('text', '') or str(data)
        sender_name = data.get('sender', {}).get('name', '') or data.get('username', 'Bir Kullanıcı')
        
        if any(char.isdigit() for char in message_text):
            ai_result = check_with_ai(message_text)
            if ai_result:
                bildirim = f"📱 [Ücretsiz Sistem] Telefon Numarası Yakalandı!\n\n👤 Müşteri: {sender_name}\n📞 Numara: {ai_result}\n💬 Mesaj: {message_text}"
                send_telegram(bildirim)
    except Exception as e:
        print("Hata:", str(e))
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
