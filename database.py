from datetime import datetime
from pymongo import MongoClient
import os

# Initialize MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["my_bot"]

# Function to save user data
def save_user(first_name, username, chat_id, phone_number=None):
    # Check if the user already exists
    if db.users.find_one({"chat_id": chat_id}):
        return False  # User already exists

    # Insert new user into the database
    db.users.insert_one({
        "first_name": first_name,
        "username": username,
        "chat_id": chat_id,
        "phone_number": phone_number
    })
    return True

# Function to save chat messages (both user and bot messages)
def save_chat(chat_id, user_message, bot_response):
    # Insert user message and bot response into the database
    db.chats.insert_one({
        "chat_id": chat_id,
        "user_message": user_message,
        "bot_response": bot_response,
        "timestamp": datetime.datetime.utcnow()  # Optionally, include a timestamp
    })

# Function to save image data and its description
def save_image(chat_id, file_path, description):
    # Insert file path and description into the database
    db.files.insert_one({
        "chat_id": chat_id,
        "file_path": file_path,
        "description": description,
        "timestamp": datetime.datetime.utcnow()  # Optional timestamp
    })
