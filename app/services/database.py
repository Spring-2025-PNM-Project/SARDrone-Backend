import os
import asyncio

from pymongo import AsyncMongoClient
from dotenv import load_dotenv

load_dotenv()

client = AsyncMongoClient(os.getenv("MONGODB_URL"))
db = client["Backend"]

async def init_database():
    logs = db["logs"]
<<<<<<< HEAD
    logs.create_index([("drone_id", 1), ("timestamp", -1)])
#  # db["logs"].create_index("timestamp", expireAfterSeconds = 600) 
=======
    await logs.create_index([("drone_id", 1), ("timestamp", -1)])
    await db["logs"].create_index("timestamp", expireAfterSeconds = 600) 
>>>>>>> main

    users = db["users"]
    await users.create_index("username", unique=True)

def get_database():
    return db

if __name__=="__main__":
    asyncio.run(init_database())
    