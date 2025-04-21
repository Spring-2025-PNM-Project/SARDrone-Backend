import jwt
from fastapi import Request, HTTPException
from datetime import datetime, timezone
from typing import Optional
import os
from dotenv import load_dotenv
from jwt import ExpiredSignatureError, PyJWTError


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


def verify_token(require_drone: bool = False, access_type: str = "read"):
    async def _verify(
        request: Request,
        drone_id: Optional[str] = None
    ):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid Authorization Header")

        token = auth_header.split(" ", 1)[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            if "exp" in payload:
                exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
                if exp < datetime.now(timezone.utc):
                    raise HTTPException(status_code=401, detail="Token has expired")

            user_info = {
                "username": payload.get("sub"),
                "read_drones": payload.get("read_drones", []),
                "write_drones": payload.get("write_drones", [])
            }

            if require_drone and drone_id:
                access_list = user_info[f"{access_type}_drones"]
                if drone_id not in access_list:
                    raise HTTPException(
                        status_code=403,
                        detail=f"No {access_type} access to drone {drone_id}"
                    )

            return user_info
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    return _verify
