import os

from pymongo import AsyncMongoClient
from dotenv import load_dotenv

load_dotenv()

client = AsyncMongoClient(os.getenv("MONGODB_URL"))
db = client["Backend"]

def init_database():
    logs = db["logs"]
    logs.create_index([("drone_id", 1), ("timestamp", -1)])
    db["logs"].create_index("timestamp", expireAfterSeconds = 600) 

    users = db["users"]
    users.create_index("username", unique=True)

def get_database():
    return db

if __name__=="__main__":
    init_database()