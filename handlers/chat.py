import google.generativeai as genai
from telegram import Update
from telegram.ext import CallbackContext
from database import save_chat
import os

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

def chat(update: Update, context: CallbackContext):
    user_text = update.message.text
    chat_id = update.message.chat_id

    try:
        # Get AI response from Gemini
        response = model.generate_content(user_text).text
    except Exception as e:
        response = "Sorry, I couldn't process your request. Please try again later."
        print(f"Error: {e}")

    # Save chat history to MongoDB
    save_chat(chat_id, user_text, response)

    # Send the AI-generated response back to the user
    update.message.reply_text(response)
