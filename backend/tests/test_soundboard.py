def test_clips_list(client):
    resp = client.get("/api/soundboard/clips")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_legacy_clips_scanned_from_soundboard_dir(client):
    resp = client.get("/api/soundboard/legacy")
    assert resp.status_code == 200
    clips = resp.json()

    labels = {c["label"] for c in clips}
    assert "Hello there" in labels
    assert "Yes" in labels

    by_label = {c["label"]: c for c in clips}
    assert by_label["Hello there"]["persona"] == "Test Persona"
    assert by_label["Hello there"]["category"] == "main"
    assert by_label["Yes"]["category"] == "tier_1"


def test_pin_missing_clip_returns_404(client):
    resp = client.post("/api/soundboard/clips/does-not-exist/pin")
    assert resp.status_code == 404
