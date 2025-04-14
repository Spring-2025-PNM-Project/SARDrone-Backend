from app.services.database import get_database, init_database


def test_get_db():
    db = get_database()
    assert db.name == "Backend"


def test_init_db():
    get_database()
    init_database()