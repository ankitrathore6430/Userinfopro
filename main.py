from flask import Flask
import threading

import telebot
import os

BOT_TOKEN = '7618558615:AAFO5kgrM5ru_Unp-ESwchCerQFE9eDisQk'
ADMIN_ID = 745211839  # User-provided admin ID
USER_IDS_FILE = 'user_ids.txt'

bot = telebot.TeleBot(BOT_TOKEN)

def load_user_ids():
    user_data = {}
    if os.path.exists(USER_IDS_FILE):
        with open(USER_IDS_FILE, 'r') as f:
            for line in f:
                try:
                    parts = line.strip().split(',', 1)
                    user_id = int(parts[0])
                    user_name = parts[1] if len(parts) > 1 else "N/A"
                    user_data[user_id] = user_name
                except ValueError:
                    continue
    return user_data

def save_user_id(user_id, username=None, first_name=None, last_name=None):
    user_data = load_user_ids()
    display_name = ""
    if username:
        display_name = f"@{username}"
    elif first_name:
        display_name = first_name
        if last_name:
            display_name += f" {last_name}"
    user_data[user_id] = display_name

    with open(USER_IDS_FILE, 'w') as f:
        for uid, name in user_data.items():
            f.write(f"{uid},{name}\n")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    save_user_id(user.id, user.username, user.first_name, user.last_name)
    info = f"👤 Your Info:\n\n🆔 ID: `{user.id}`\n👤 First Name: {user.first_name}"
    if user.last_name:
        info += f"\n👤 Last Name: {user.last_name}"
    if user.username:
        info += f"\n🔗 Username: @{user.username}"
    bot.reply_to(message, info, parse_mode='Markdown')

# Minimal Flask server for uptime checks
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()