from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_health():
    response = client.get("/health", headers={"ip_address": "127.1.10.1"})
    assert response.status_code == 200
    assert response.json() == {"message": "Application is healthy"}


def test_token_bucket_rate_limit():
    """
    Bucket limit = 8 tokens. Fire 9 rapid requests for the same IP.
    Requests 1-8 must succeed (200); request 9 must be rate-limited (429).
    """
    ip = "127.9.9.9"
    headers = {"ip_address": ip}

    allowed = []
    for _ in range(9):
        r = client.get("/health", headers=headers)
        allowed.append(r.status_code)

    print("Status codes:", allowed)

    # First 8 should pass
    assert all(s == 200 for s in allowed[:8]), f"Expected 200s, got: {allowed[:8]}"
    # 9th must be rejected
    assert allowed[8] == 429, f"Expected 429 on 9th request, got: {allowed[8]}"