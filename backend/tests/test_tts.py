def test_voices_returns_503_without_api_key(client):
    resp = client.get("/api/tts/voices")
    assert resp.status_code == 503
    assert "ELEVENLABS_API_KEY" in resp.json()["detail"]


def test_generate_returns_503_without_api_key(client):
    resp = client.post(
        "/api/tts/generate", json={"text": "hello", "voice_id": "abc"}
    )
    assert resp.status_code == 503
    assert "ELEVENLABS_API_KEY" in resp.json()["detail"]


def test_generate_rejects_empty_text(client):
    resp = client.post(
        "/api/tts/generate", json={"text": "   ", "voice_id": "abc"}
    )
    assert resp.status_code == 400
