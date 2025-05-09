import jwt
import os

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user import UserLogin, LoginResponse, UserResponse
from app.middleware.drone import verify_token
from app.services.database import get_database
from bcrypt import checkpw


router = APIRouter(
    prefix="/login",
    tags=["User"]
)

db = get_database()
load_dotenv()


@router.post("", response_model=LoginResponse)
async def login(login: UserLogin):
    users = db["users"]
    user = await users.find_one({"username": login.username})
    
    if not user or not checkpw(login.password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    payload = {
        "sub": user["username"],
        "read_drones": user["read_drones"],
        "write_drones": user["write_drones"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60*24)
    }

    token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")

    return LoginResponse(status="success", token=token)

@router.get("/drones", response_model=UserResponse)
async def get_drones(user_info: dict = Depends(verify_token())):
    return user_info
