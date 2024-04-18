from typing import final
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import sqlite3

TOKEN: final = "7022439090:AAGIJo3K-o85isgUL-1CkzNwwSzFYyjMD8U"
BOT_USERNAME = "@baPredictionBot"

# Database setup
conn = sqlite3.connect('prediction_bot.db')
cursor = conn.cursor()

# Create users table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER,
        username TEXT,
        selected_game TEXT,
        prediction_status INTEGER,
        free_predictions INTEGER,
        subscription_status INTEGER
    )
''')
conn.commit()

# Custom filter for registration-related messages
class RegistrationFilter:
    def filter(self, message):
        # Check if the message contains the /register command
        games =['tennis', 'football', 'basketball']
        if str(message.text).lower() in games:
            return True  # Allow messages with /register command for registration
        else:
            return False  # Exclude messages without /register command

# Add the custom filter
filters.REGISTRATION = RegistrationFilter()

# COMMANDS
# -----------------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.full_name
    response = f"""Hello, {user_name}\! 👋

Welcome to *jba prediction bot*\. Thanks for chatting with me\. 😊

I can help you with various tasks, such as predicting the outcome of a live match in Tennis, Basketball, and Football\.

To get started, you can type /help to see a list of available commands
"""
    await update.message.reply_text(response, parse_mode='MarkdownV2')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = """
    Here are the available commands:

    */start* \- Start the bot and receive a welcome message\.
    */help* \- Get help and see a list of available commands\.
    */selectgame *\- Select a game for predictions \(Tennis, Basketball, or Football\)\.
    */startprediction* \- Start continuous predictions for the selected game\.
    */stopprediction* \- Stop continuous predictions for the selected game\.
    */register* \- Register to the bot and get 10 free predictions\.
    */subscribe* \- Subscribe to get more predictions \(coming soon\)\.
    */status* \- Get information about your account, including subscription status, free predictions, selected game, and prediction status\.
    """
    await update.message.reply_text(response, parse_mode='MarkdownV2')

async def selectGame_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Tennis"), KeyboardButton("Basketball"), KeyboardButton("Football")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    response = "Select a game: Tennis, Basketball, or Football"
    await update.message.reply_text(response, reply_markup=reply_markup)

async def handle_selected_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    selected_game = update.message.text

    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (user_id,))
    user_info = cursor.fetchone()

    if user_info:
        if filters.REGISTRATION.filter(update.message):
            cursor.execute('UPDATE users SET selected_game = ? WHERE telegram_id = ?', (selected_game, user_id))
            conn.commit()
            response = f"You have selected {selected_game}."
            await update.message.reply_text(response)
        else:
            message_type: str = update.message.chat.type
            text: str = update.message.text

            print(f"user: {update.message.chat.id} in {message_type}: '{text}'")

            if message_type == 'group':
                if BOT_USERNAME in text:
                    new_text: str = text.replace(BOT_USERNAME, "").strip()
                    response = await handle_responses(new_text)
                else:
                    return
            else:
                response = await handle_responses(text)

            print(f"Bot: {response}")
            await update.message.reply_text(response, parse_mode='MarkdownV2')
    else:
        response = "You are not registered. Please use the /register command."

        await update.message.reply_text(response)

async def startPrediction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (user_id,))
    user_info = cursor.fetchone()

    if user_info and not filters.REGISTRATION.filter(update.message):
        # Logic for starting predictions (add your specific implementation here)
        response = "Starting prediction."
    else:
        response = "You are not registered. Please use the /register command."

    await update.message.reply_text(response)

async def stopPrediction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (user_id,))
    user_info = cursor.fetchone()

    if user_info and not filters.REGISTRATION.filter(update.message):
        # Logic for stopping predictions (add your specific implementation here)
        response = "Stopping prediction."
    else:
        response = "You are not registered. Please use the /register command."

    await update.message.reply_text(response)

async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    full_name = update.message.from_user.full_name

    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        response = "You are already registered\."
    else:
        cursor.execute('''
            INSERT INTO users (telegram_id, username, selected_game, prediction_status, free_predictions, subscription_status)
            VALUES (?, ?, NULL, 0, 10, 0)
        ''', (user_id, full_name))
        conn.commit()
        response = f"Registration successful\, {full_name}\! You now have 10 free predictions\."

    await update.message.reply_text(response, parse_mode='MarkdownV2')

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (user_id,))
    user_info = cursor.fetchone()

    if user_info and not filters.REGISTRATION.filter(update.message):
        # Placeholder for subscription command
        response = "Subscription feature coming soon\!"
    else:
        response = "You are not registered\. Please use the /register command\."

    await update.message.reply_text(response, parse_mode='MarkdownV2')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (user_id,))
    user_info = cursor.fetchone()

    if user_info:
        username = user_info[2]
        selected_game = user_info[3] if user_info[3] else "None"
        prediction_status = "Active" if user_info[4] else "Inactive"
        free_predictions = user_info[5]
        subscription_status = "Subscribed" if user_info[6] else "Not Subscribed"

        response = f"""
        *USER INFO:*

        *Name:* _{username}_
        *Subscription Status:* _{subscription_status}_
        *Free Predictions:* _{free_predictions}_
        *Selected Game:* _{selected_game}_
        *Prediction Status:* _{prediction_status}_
        """
    else:
        response = "You are not registered\. Please use the /register command\."

    await update.message.reply_text(response, parse_mode='MarkdownV2')

# RESPONSES
# ------------------
async def handle_responses(text: str) -> str:
    processed: str = text.lower()

    greetings = ["hello", "hi", "hey"]
    farewells = ["bye", "goodbye"]
    how_are_you = ["how are you", "how's it going", "how do you do"]
    thank_you = ["thank you", "thanks"]
    default_response = "Sorry\! I do not understand your message\."

    if any(greeting in processed for greeting in greetings):
        return "Hi\!"

    if any(farewell in processed for farewell in farewells):
        return "Goodbye\!"

    if any(how in processed for how in how_are_you):
        return "I'm doing well, thank you for asking\!"

    if any(thanks in processed for thanks in thank_you):
        return "You're welcome\!"

    return default_response

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error: {context.error}")
    pass

if __name__ == '__main__':
    print('starting bot...')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("selectgame", selectGame_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_selected_game), group=1)
    app.add_handler(CommandHandler("startprediction", startPrediction_command))
    app.add_handler(CommandHandler("stopprediction", stopPrediction_command))
    app.add_handler(CommandHandler("register", register_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("status", status_command))

    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=3)
