import pytest
from fastapi.testclient import TestClient

from ci_cd.api import CLASSES, app
from ci_cd.train import train

SETOSA = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2,
}


@pytest.fixture(scope="module")
def client():
    # Train and save a model, for the API to load when it starts.
    train()
    with TestClient(app) as client:
        yield client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict(client):
    response = client.post("/predict", json=SETOSA)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "setosa"
    assert set(data["probabilities"]) == set(CLASSES)
    assert sum(data["probabilities"].values()) == pytest.approx(1.0)
