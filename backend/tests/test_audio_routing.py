def test_routing_roundtrip(client):
    resp = client.post(
        "/api/audio/routing",
        json={"source": "mic", "line_id": "line-1", "enabled": True},
    )
    assert resp.status_code == 200

    resp = client.get("/api/audio/routing")
    assert resp.status_code == 200
    body = resp.json()
    assert body["routes"]["mic"]["line-1"] is True


def test_mic_mute_endpoints(client):
    assert client.post("/api/audio/mic/mute").json() == {"mic_muted": True}
    assert client.post("/api/audio/mic/unmute").json() == {"mic_muted": False}
    assert client.post("/api/audio/mic/toggle").json() == {"mic_muted": True}
    assert client.get("/api/audio/routing").json()["mic_muted"] is True
