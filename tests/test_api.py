import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "Financial ETL API"
    assert data["status"] == "running"
    assert data["version"] == "1.0.0"