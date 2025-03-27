from flask import Flask, request
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import TOKEN
from bot import get_random_log_and_delete
import asyncio
import os

bot = Bot(token=TOKEN)
app = Flask(__name__)
loop = asyncio.get_event_loop()

# Envoie le log au client
async def send_log(chat_id, log):
    await bot.send_message(chat_id=chat_id, text=f"✅ Paiement PayPal confirmé ! Voici ton log :\n{log}")

async def send_no_log(chat_id):
    await bot.send_message(chat_id=chat_id, text="❌ Cette offre est épuisée.")

# Génération dynamique du lien PayPal
def generate_paypal_link(chat_id, row, brand, type_commande, price):
    item_name = f"{brand} {type_commande}".replace(" ", "+")
    return (
        f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick"
        f"&business=lucasbruges4@gmail.com"
        f"&item_name={item_name}"
        f"&amount={price:.2f}"
        f"&currency_code=EUR"
        f"&notify_url=https://bot-production-608c.up.railway.app/paypal-ipn"
        f"&custom={chat_id}_{row}"
    )

# Route IPN PayPal
@app.route('/paypal-ipn', methods=['POST'])
def paypal_ipn():
    data = request.form or request.json

    custom = data.get("custom", "")
    if "_" not in custom:
        return {"error": "Paramètres manquants"}, 400

    try:
        chat_id, row = map(int, custom.split("_"))
    except:
        return {"error": "Custom mal formé"}, 400

    print("📥 Paiement reçu — chat_id:", chat_id, "row:", row)
    log = get_random_log_and_delete(row)
    if log:
        loop.create_task(send_log(chat_id, log))
    else:
        loop.create_task(send_no_log(chat_id))

    return {"status": "ok"}, 200

# Lancement du serveur Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))