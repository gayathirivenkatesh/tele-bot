from telegram import Update
from telegram.ext import CallbackContext
from web_scraper import search_web  # Ensure this function is implemented

def web_search(update: Update, context: CallbackContext):
    query = update.message.text.replace("/websearch", "").strip()

    if not query:
        update.message.reply_text("Please enter a search query.")
        return

    results = search_web(query)  # Ensure search_web() is properly defined
    update.message.reply_text(results)
