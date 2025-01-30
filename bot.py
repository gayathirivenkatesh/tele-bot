import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from handlers.image_analysis import analyze_image_with_blip  
from pymongo import MongoClient
import datetime
import google.generativeai as genai
from textblob import TextBlob 

# Load environment variables
load_dotenv()

# Telegram & Gemini API Keys
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  

# MongoDB Connection Setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client["my_bot"]

# Function to save user data in MongoDB
def save_user(first_name, username, chat_id, phone_number=None):
    if db.users.find_one({"chat_id": chat_id}):
        return False  # User already exists

    db.users.insert_one({
        "first_name": first_name,
        "username": username,
        "chat_id": chat_id,
        "phone_number": phone_number
    })
    return True

# Function to save chat messages
def save_chat(chat_id, user_message, bot_response):
    db.chats.insert_one({
        "chat_id": chat_id,
        "user_message": user_message,
        "bot_response": bot_response,
        "timestamp": datetime.datetime.utcnow()  # Add timestamp for the chat
    })

# Function to save image data
def save_image(chat_id, file_path, description):
    db.files.insert_one({
        "chat_id": chat_id,
        "file_path": file_path,
        "description": description,
        "timestamp": datetime.datetime.utcnow()  # Add timestamp for the file upload
    })

# Function to perform sentiment analysis on the user's message
def analyze_sentiment(user_message):
    # Create a TextBlob object
    blob = TextBlob(user_message)
    
    # Get the sentiment polarity of the message
    sentiment_score = blob.sentiment.polarity
    
    # Determine sentiment based on the polarity score
    if sentiment_score > 0:
        return "positive"
    elif sentiment_score < 0:
        return "negative"
    else:
        return "neutral"

# Command handler to start the bot
async def start(update: Update, context):
    contact_keyboard = [[KeyboardButton("Share Contact", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(contact_keyboard, one_time_keyboard=True)

    # Save the user when they start the conversation
    user = update.message.from_user
    first_name = user.first_name
    username = user.username
    chat_id = update.message.chat_id
    phone_number = update.message.contact.phone_number if update.message.contact else None

    user_saved = save_user(first_name, username, chat_id, phone_number)
    if user_saved:
        await update.message.reply_text(
            "Welcome! 🤖 I am your AI assistant. Feel free to ask me anything!\n\nPlease share your contact to continue.",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("You are already registered. 😊")

# AI-powered chat using Gemini with sentiment analysis
async def chat(update: Update, context):
    user_message = update.message.text
    chat_id = update.message.chat_id

    try:
        # Analyze sentiment of the user's message
        sentiment = analyze_sentiment(user_message)
        
        # Generate AI response using Gemini
        response = model.generate_content(user_message)
        ai_reply = response.text if response else "Sorry, I couldn't generate a response."

        # Customize the response based on sentiment
        if sentiment == "positive":
            sentiment_reply = "😊 I'm happy to hear you're in a good mood!"
        elif sentiment == "negative":
            sentiment_reply = "😞 I'm sorry you're feeling that way. How can I help?"
        else:
            sentiment_reply = "😐 Let's talk! How can I assist you?"

        # Combine the AI response and sentiment-based reply
        full_reply = f"{ai_reply}\n\nSentiment: {sentiment_reply}"

        # Save the chat message and response in MongoDB
        save_chat(chat_id, user_message, full_reply)

    except Exception as e:
        full_reply = f"❌ Error: {str(e)}"

    await update.message.reply_text(full_reply)

# Image analysis using BLIP
async def analyze_image(update: Update, context):
    try:
        # Get the image sent by the user
        file = await update.message.photo[-1].get_file()
        file_path = f"downloads/{file.file_unique_id}.jpg"
        await file.download_to_drive(custom_path=file_path)

        await update.message.reply_text("📷 Image received. Processing...")

        # Call the function from image_analysis.py
        caption = analyze_image_with_blip(file_path)

        # Save the image data in MongoDB
        save_image(update.message.chat_id, file_path, caption)

        await update.message.reply_text(caption)

    except Exception as e:
        await update.message.reply_text(f"❌ Error analyzing image: {str(e)}")

# Handler to process contact sharing
async def handle_contact(update: Update, context):
    contact = update.message.contact
    user_name = contact.first_name
    await update.message.reply_text(f"Thanks for sharing your contact, {user_name}! 📞")

# Main function to set up the bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))  # AI-powered chat
    application.add_handler(MessageHandler(filters.PHOTO, analyze_image))  # Image captioning with BLIP
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))  # Handle contact sharing

    application.run_polling()

if __name__ == "__main__":
    main()
