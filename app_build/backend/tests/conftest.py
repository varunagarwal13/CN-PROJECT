import sys
from pathlib import Path

# Ensure workspace root is in sys.path
workspace_root = Path(__file__).resolve().parent.parent.parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app_build.backend.db import Base, get_db
from app_build.backend.main import app
from app_build.backend import models

# Use in-memory SQLite for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db(monkeypatch):
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr("app_build.backend.db.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr("app_build.backend.event_bus.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr("app_build.backend.orchestration.lab_runner.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr("app_build.backend.routes.SessionLocal", TestingSessionLocal)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
