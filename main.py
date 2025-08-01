
import telebot
import os

BOT_TOKEN = '1233674761:AAHjXGim4mRXy41AdSWlrvqd9mCY4QOCqRc'
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
                    continue # Skip malformed lines
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
    for user_id in user_data.keys():
        try:
            if user_id != ADMIN_ID: # Don't send broadcast to admin itself
                bot.send_message(user_id, text_to_broadcast)
        except Exception as e:
            print(f"Could not send message to {user_id}: {e}")
    bot.reply_to(message, "Broadcast sent to all users.")

@bot.message_handler(commands=['show_users'])
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

@bot.message_handler(func=lambda message: message.text.startswith('@'))
def get_user_info(message):
    bot.reply_to(message, "❌ Telegram does not allow bots to access another user's info using @username directly unless they message the bot first.")

@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.reply_to(message, "Send /start to get your own user info.")

bot.infinity_polling()


