import telebot
import json
import os
from flask import Flask, request
import threading
import time

TOKEN = os.getenv("BOT_TOKEN")  # Use environment variable for security
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))  # Replace with your actual Telegram ID or set as env var

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

users_file = "users.json"
auto_message = ""
auto_interval = 0
auto_thread = None
auto_running = False

# Load or initialize user data
def load_users():
    if not os.path.exists(users_file):
        return []
    with open(users_file, "r") as f:
        return json.load(f)

def save_users(users):
    with open(users_file, "w") as f:
        json.dump(users, f)

def add_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user = message.from_user
    add_user(user.id)
    bot.reply_to(message, f"👋 Hello {user.first_name}! You have been registered.")

@bot.message_handler(commands=['ping'])
def handle_ping(message):
    bot.reply_to(message, "✅ Bot is online!")

# Admin only command
def is_admin(message):
    return message.from_user.id == ADMIN_ID

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    if is_admin(message):
        bot.reply_to(message, "🔐 You are an admin.")
    else:
        bot.reply_to(message, "❌ You are not authorized.")

@bot.message_handler(commands=['show_users'])
def show_users(message):
    if not is_admin(message):
        return
    users = load_users()
    bot.reply_to(message, f"📊 Total users: {len(users)}\n" + "\n".join(str(uid) for uid in users))

@bot.message_handler(commands=['reload_users'])
def reload_users(message):
    if not is_admin(message):
        return
    save_users(load_users())
    bot.reply_to(message, "✅ Users reloaded.")

@bot.message_handler(commands=['set_auto'])
def set_auto(message):
    if not is_admin(message):
        return
    try:
        parts = message.text.split(" ", 2)
        global auto_interval, auto_message, auto_running, auto_thread
        auto_interval = int(parts[1])
        auto_message = parts[2]
        if auto_running:
            auto_running = False
            time.sleep(1)
        auto_running = True
        auto_thread = threading.Thread(target=auto_broadcast)
        auto_thread.start()
        bot.reply_to(message, f"✅ Auto message started every {auto_interval} seconds.")
    except:
        bot.reply_to(message, "⚠️ Usage: /set_auto <seconds> <message>")

@bot.message_handler(commands=['stop_auto'])
def stop_auto(message):
    global auto_running
    if not is_admin(message):
        return
    auto_running = False
    bot.reply_to(message, "🛑 Auto message stopped.")

def auto_broadcast():
    global auto_running
    while auto_running:
        users = load_users()
        for uid in users:
            try:
                bot.send_message(uid, auto_message)
            except:
                pass
        time.sleep(auto_interval)

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK"

@app.route('/')
def home():
    return "🤖 Bot is running."

# Set webhook automatically (use for Render deployment)
def set_webhook():
    url = os.getenv("WEBHOOK_URL")
    if url:
        bot.remove_webhook()
        bot.set_webhook(url=f"{url}/{TOKEN}")

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
