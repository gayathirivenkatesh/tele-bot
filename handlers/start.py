from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from database import save_user

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    chat_id = user.id

    # Check if user exists in database
    if not save_user(user.first_name, user.username, chat_id):
        update.message.reply_text("You're already registered!")
        return

    # Ask for phone number using contact button
    contact_keyboard = [[KeyboardButton("Share Contact", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(contact_keyboard, one_time_keyboard=True)

    update.message.reply_text("Please share your phone number:", reply_markup=reply_markup)

def save_phone(update: Update, context: CallbackContext):
    if update.message.contact:
        phone_number = update.message.contact.phone_number
        chat_id = update.message.chat_id
        update.message.reply_text(f"Phone number saved: {phone_number}")
        save_user(phone_number=phone_number, chat_id=chat_id)
