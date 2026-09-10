from fastapi.testclient import TestClient
from app.main import app

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200

def test_freight_prediction():
    with TestClient(app) as client:
        response = client.post("/predict/freight", json={"dollars":18500,"quantity":500,"vendor_number":105})
        assert response.status_code == 200
        assert "predicted_freight" in response.json()

def test_anomaly_prediction():
    with TestClient(app) as client:
        response = client.post("/predict/anomaly", json={"dollars":18500,"quantity":500,"freight":100,"total_quantity":500,"total_dollars":18500})
        assert response.status_code == 200
        assert "is_anomaly" in response.json()
