from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGODB_URL")

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB!")
except Exception as e:
    print("❌ Connection Error:", e)

print("Available Databases:", client.list_database_names())
db = client["PhisingData"]
print("Collections in DB:", db.list_collection_names())

collection = db["network_security"]
print(f"📦 Total Documents: {collection.count_documents({})}")
print("🔍 Sample Document:", collection.find_one())
