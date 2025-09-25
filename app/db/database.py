from pymongo import MongoClient
from app.core.config import settings

URI = settings.MONGODB_URL
client = MongoClient(URI)

print(client)