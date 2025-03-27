from flask import Flask, request
from telegram import Bot
from config import TOKEN
from bot import get_random_log_and_delete
import asyncio

bot = Bot(token=TOKEN)
app = Flask(__name__)
loop = asyncio.get_event_loop()

async def send_log(chat_id, log):
    await bot.send_message(chat_id=chat_id, text=f"✅ Paiement PayPal confirmé ! Voici ton log :\n{log}")

async def send_no_log(chat_id):
    await bot.send_message(chat_id=chat_id, text="❌ Cette offre est épuisée.")

@app.route('/paypal-ipn', methods=['POST'])
def paypal_ipn():
    data = request.json
    chat_id = int(data.get("chat_id"))
    row = int(data.get("row"))

    print("📥 Requête reçue pour chat_id:", chat_id, "row:", row)

    log = get_random_log_and_delete(row)
    print("🎯 Log récupéré :", log)

    if log:
        loop.create_task(send_log(chat_id, log))
        print("✅ Message Telegram envoyé.")
    else:
        loop.create_task(send_no_log(chat_id))
        print("❌ Aucun log disponible pour cette ligne.")

    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

@app.route('/crypto-webhook', methods=['POST'])
def crypto_webhook():
    data = request.json  # attend un JSON : {"chat_id": ..., "row": ...}
    chat_id = int(data.get("chat_id"))
    row = int(data.get("row"))

    log = get_random_log_and_delete(row)
    if log:
        bot.send_message(chat_id=chat_id, text=f"✅ Paiement crypto confirmé ! Voici ton log :\n{log}")
    else:
        bot.send_message(chat_id=chat_id, text="❌ Cette offre est épuisée.")
    return {"status": "ok"}, 200

@app.route('/test', methods=['GET'])
def test():
    test_chat_id = 1666355951  # remplace par ton ID Telegram pour test
    bot.send_message(chat_id=test_chat_id, text="🚀 Test réussi depuis le serveur Flask !")
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)