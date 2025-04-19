from app.services.database import get_database
from app.schemas.user import User
from bcrypt import hashpw, gensalt


USERNAME = "user1"
PASSWORD = "password"
READ_DRONES = ["1"]
WRITE_DRONES = []


db = get_database()


def create_user():
    hashed_password = hashpw(PASSWORD.encode('utf-8'), gensalt())

    user = User(
        username=USERNAME,
        password=hashed_password.decode('utf-8'),
        read_drones=READ_DRONES,
        write_drones=WRITE_DRONES
    )

    try:
        db["users"].insert_one(user.model_dump())
        print("User created successfully!")
    except Exception as e:
        print("Error creating user:", e)

if __name__ == "__main__":
    create_user()
