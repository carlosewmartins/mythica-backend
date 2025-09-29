from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]

users_list = db["users"]
personagens_list = db["personagens"]
campanhas_list = db["campanhas"]