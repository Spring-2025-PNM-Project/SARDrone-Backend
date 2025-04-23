from app.services.database import get_database, init_database
import asyncio

def test_get_db():
    db = get_database()
    assert db.name == "Backend"


def test_init_db():
    get_database()
    asyncio.run(init_database())