import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration for the bot and external APIs
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# You can add more configuration variables here as needed
