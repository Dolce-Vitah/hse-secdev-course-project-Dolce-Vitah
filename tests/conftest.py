import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from src.adapters import database
from src.app.main import app
from src.app.security import create_access_token, get_current_user
from src.domain.models import User

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite://")

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    database.engine = engine

    database.init_db()
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def session():
    with Session(engine) as session:
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.exec(table.delete())
        session.commit()

        yield session

        session.rollback()


@pytest.fixture()
def client(session):
    def override_get_session():
        yield session

    app.dependency_overrides[database.get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def create_user(session):
    def _create_user(username: str, password: str = "password123", role: str = "user"):
        user = User(username=username, password_hash=password, role=role)
        session.add(user)
        session.commit()
        session.refresh(user)
        token = create_access_token({"sub": str(user.id)})
        return {"user": user, "token": token}

    return _create_user


@pytest.fixture
def test_user(create_user):
    username = f"testuser_{uuid.uuid4().hex[:6]}"
    return create_user(username)


@pytest.fixture
def another_user(create_user):
    username = f"anotheruser_{uuid.uuid4().hex[:6]}"
    return create_user(username)


@pytest.fixture
def client_with_user(client, test_user):
    app.dependency_overrides[get_current_user] = lambda: test_user["user"]
    yield client
    app.dependency_overrides.clear()
