import telebot
import os
from flask import Flask
import threading

# Load the bot token from environment variable for safety
BOT_TOKEN = os.getenv("BOT_TOKEN", "7618558615:AAFO5kgrM5ru_Unp-ESwchCerQFE9eDisQk")
ADMIN_ID = 745211839
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

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    text_to_broadcast = message.text.replace("/broadcast", "").strip()
    if not text_to_broadcast:
        bot.reply_to(message, "Please provide a message to broadcast.")
        return

    user_data = load_user_ids()
    success_count = 0
    failed_count = 0

    for user_id in user_data.keys():
        # Do not send the broadcast message to the admin
        if user_id == ADMIN_ID:
            continue
        try:
            bot.send_message(user_id, text_to_broadcast)
            success_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Could not send message to {user_id}: {e}")
            
    report_message = (
        f"📢 Broadcast Finished!\n\n"
        f"✅ Messages Sent: {success_count}\n"
        f"❌ Failed to Send: {failed_count}"
    )
    bot.reply_to(message, report_message)

@bot.message_handler(commands=['showusers'])
def show_users(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    users_info = "Registered Users:\n"
    user_data = load_user_ids()
    if user_data:
        for user_id, user_name in user_data.items():
            users_info += f"- ID: `{user_id}`, Name: {user_name}\n"
    else:
        users_info += "No users registered yet."
    bot.reply_to(message, users_info, parse_mode='Markdown')

# ---- NEW FEATURE: Get user info from a forwarded post ----
@bot.message_handler(func=lambda message: message.forward_from or message.forward_sender_name)
def get_forwarded_user_info(message):
    if message.forward_from:
        user = message.forward_from
        # Save the user's info to the list
        save_user_id(user.id, user.username, user.first_name, user.last_name)

        # Prepare the info message
        info = f"👤 **Forwarded User Info**:\n\n"
        info += f"**ID**: `{user.id}`\n"
        info += f"**First Name**: {user.first_name}\n"
        if user.last_name:
            info += f"**Last Name**: {user.last_name}\n"
        if user.username:
            info += f"**Username**: @{user.username}\n"
        info += f"**Is Bot**: {'Yes' if user.is_bot else 'No'}"
        bot.reply_to(message, info, parse_mode='Markdown')
    else:
        # This handles cases where the user has privacy settings on
        info = "Could not retrieve user details. The original sender has hidden their account due to their privacy settings."
        bot.reply_to(message, info)

@bot.message_handler(func=lambda message: message.text.startswith('@'))
def get_user_info(message):
    bot.reply_to(message, "❌ Telegram does not allow bots to access another user's info using @username directly unless they message the bot first. Please forward a message from that user instead.")

@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.reply_to(message, "Send /start to get your own user info, or forward a message from another user to get their info.")


# ---- Flask server for Render + UptimeRobot ----
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
