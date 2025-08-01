
import telebot
import json
import threading
import time
from flask import Flask

API_TOKEN = '7618558615:AAFO5kgrM5ru_Unp-ESwchCerQFE9eDisQk'
ADMIN_ID = 745211839

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

users_file = "users.json"

def load_users():
    try:
        with open(users_file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(users_file, "w") as f:
        json.dump(users, f, indent=2)

auto_message_config = {"enabled": False, "interval": 0, "message": ""}
auto_thread = None

def auto_broadcast_loop():
    while auto_message_config["enabled"]:
        time.sleep(auto_message_config["interval"] * 60)
        if not auto_message_config["enabled"]:
            break
        users = load_users()
        for user_id in users:
            try:
                bot.send_message(user_id, auto_message_config["message"])
            except:
                continue

@bot.message_handler(commands=['start'])
def send_user_info(message):
    user = message.from_user
    user_info = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username
    }
    users = load_users()
    users[str(user.id)] = user_info
    save_users(users)
    bot.reply_to(message, f"👋 Hello {user.first_name}!
Your Telegram ID: `{user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "🚫 You are not authorized.")
    text = message.text.split(' ', 1)
    if len(text) < 2:
        return bot.reply_to(message, "❗ Usage: /broadcast <message>")
    users = load_users()
    for uid in users:
        try:
            bot.send_message(uid, text[1])
        except:
            continue
    bot.reply_to(message, "📢 Broadcast sent.")

@bot.message_handler(commands=['show_users'])
def show_users(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "🚫 You are not authorized.")
    users = load_users()
    msg = "👥 Registered Users:\n\n"
    for uid, info in users.items():
        name = f"{info.get('first_name', '')} {info.get('last_name', '')}".strip()
        username = f"@{info['username']}" if info.get("username") else "N/A"
        msg += f"ID: `{uid}` - {name} ({username})\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "🚫 You are not authorized.")
    bot.reply_to(message, """
👑 *Admin Commands:*
/broadcast <msg> - Send to all users
/show_users - List all users
/set_auto <minutes> <msg> - Auto-message
/stop_auto - Stop auto-message
/reload_users - Reload user list
/ping - Check bot status
""", parse_mode="Markdown")

@bot.message_handler(commands=['reload_users'])
def reload_users(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "🚫 You are not authorized.")
    load_users()
    bot.reply_to(message, "✅ Users reloaded from file.")

@bot.message_handler(commands=['set_auto'])
def set_auto_message(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "🚫 You are not authorized.")
    args = message.text.split(maxsplit=2)
    if len(args) < 3 or not args[1].isdigit():
        return bot.reply_to(message, "❗ Usage: /set_auto <minutes> <message>")
    interval = int(args[1])
    auto_message_config["interval"] = interval
    auto_message_config["message"] = args[2]
    auto_message_config["enabled"] = True
    global auto_thread
    if auto_thread and auto_thread.is_alive():
        pass
    else:
        auto_thread = threading.Thread(target=auto_broadcast_loop)
        auto_thread.daemon = True
        auto_thread.start()
    bot.reply_to(message, f"🔁 Auto message set every {interval} minutes.")

@bot.message_handler(commands=['stop_auto'])
def stop_auto_message(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "🚫 You are not authorized.")
    auto_message_config["enabled"] = False
    bot.reply_to(message, "🛑 Auto message stopped.")

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "✅ Bot is running!")

@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.reply_to(message, "Send /start to get your own user info.")

@app.route('/ping')
def flask_ping():
    return "Bot is alive!"

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()
    bot.infinity_polling()
