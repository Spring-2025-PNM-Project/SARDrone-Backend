from fastapi import APIRouter, HTTPException
from app.schemas.user import UserLogin, LoginResponse
from app.services.database import get_database
from bcrypt import checkpw


router = APIRouter(
    prefix="/login",
    tags=["User"]
)

db = get_database()


@router.post("/", response_model=LoginResponse)
async def login(login: UserLogin):
    user = db["users"].find_one({"username": login.username})
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not checkpw(login.password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return LoginResponse(status="success", token="dummy_token")