
import telebot

BOT_TOKEN = '7618558615:AAFO5kgrM5ru_Unp-ESwchCerQFE9eDisQk'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    info = f"👤 Your Info:\n\n🆔 ID: `{user.id}`\n👤 First Name: {user.first_name}"
    if user.last_name:
        info += f"\n👤 Last Name: {user.last_name}"
    if user.username:
        info += f"\n🔗 Username: @{user.username}"
    bot.reply_to(message, info, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text.startswith('@'))
def get_user_info(message):
    bot.reply_to(message, "❌ Telegram does not allow bots to access another user's info using @username directly unless they message the bot first.")

@bot.message_handler(func=lambda message: True)
def fallback(message):
    bot.reply_to(message, "Send /start to get your own user info.")


@bot.message_handler(commands=['admin'])
def show_admin_commands(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "🚫 You are not authorized.")
    
    text = (
        "🔧 Admin Commands:\n"
        "/broadcast <message>\n"
        "/show_users\n"
        "/sendto <user_id> <message>\n"
        "/reload_users\n"
        "/admin"
    )
    bot.reply_to(message, text)


@bot.message_handler(commands=['reload_users'])
def reload_users(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "🚫 You are not authorized.")
    try:
        load_users()  # Just reloads from file
        bot.reply_to(message, "✅ User list reloaded from file.")
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to reload users: {e}")



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


bot.infinity_polling()
