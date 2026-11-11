from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
TEST_SITE = "pytest.example"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_report_for_unknown_site_returns_full_score():
    response = client.get("/report/site-that-was-never-scanned.example")
    assert response.status_code == 200
    body = response.json()
    assert body["trust_score"] == 100 and body["label"] == "No data yet"


def test_feedback_rejects_incomplete_request():
    response = client.post("/feedback", json={"correct": False})
    assert response.status_code == 422


def test_scan_returns_detections_with_legal_clauses():
    payload = {
        "url": TEST_SITE,
        "dom_text": "Hurry! Offer ends in 05:32. Only 3 left in stock.",
        "dom_structure": [],
    }
    response = client.post("/scan", json=payload)
    assert response.status_code == 200
    detections = response.json()["detections"]
    categories = {d["category"] for d in detections}
    assert {"fake_urgency", "scarcity_claim"} <= categories
    assert all(d["law_name"] for d in detections)


def test_report_for_scanned_site_has_lower_score():
    response = client.get("/report/" + TEST_SITE)
    assert response.status_code == 200
    assert response.json()["trust_score"] < 100