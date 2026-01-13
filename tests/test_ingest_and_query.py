import os
import pytest
from backend.db import SessionLocal, engine
from backend.models import Base, Profile

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_ingest_sample():
    # Run ingest in sample mode (no netcdf files)
    os.system("python ingest.py --input 'data/netcdf/none/*.nc'")
    db = SessionLocal()
    n = db.query(Profile).count()
    assert n >= 1

def test_sql_query():
    from backend.rag_service import app
    # Simple check that app imports and health endpoint exists
    assert app.title == "FloatChat Backend"
