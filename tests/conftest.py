import pytest
from app import create_app, db as _db
from app.config import TestingConfig
from sqlalchemy import event
from sqlalchemy.engine import Engine


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if dbapi_connection.__class__.__module__ == 'sqlite3':
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@pytest.fixture(scope='session')
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        yield app


@pytest.fixture(scope='session')
def db(app):
    _db.app = app
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(scope='function', autouse=True)
def session(db):
    db.session.begin_nested()

    yield db.session

    db.session.rollback()


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()
