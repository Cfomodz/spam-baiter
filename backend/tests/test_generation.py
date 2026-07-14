import time

import pytest

from app.config import settings
from app.services.tts_service import tts_service


@pytest.fixture()
def fake_tts(monkeypatch):
    """Pretend TTS is configured and synthesis instantly returns audio."""
    calls: list[tuple[str, str]] = []

    async def fake_synthesize(text: str, voice_id: str) -> bytes:
        calls.append((text, voice_id))
        return b"fake-mp3-bytes"

    async def fake_get_voice_name(voice_id: str) -> str | None:
        return None

    monkeypatch.setattr(settings, "elevenlabs_api_key", "test-key")
    monkeypatch.setattr(tts_service, "synthesize", fake_synthesize)
    monkeypatch.setattr(tts_service, "get_voice_name", fake_get_voice_name)
    return calls


def _wait_for_clips(client, module_id: int, expected: int, timeout: float = 5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        detail = client.get(f"/api/modules/{module_id}").json()
        if len(detail["clips"]) >= expected:
            return detail
        time.sleep(0.05)
    raise AssertionError(
        f"module {module_id} never reached {expected} clips"
    )


def test_list_templates(client):
    templates = client.get("/api/templates").json()
    assert any(t["key"] == "google-listing" for t in templates)
    tpl = next(t for t in templates if t["key"] == "google-listing")
    assert tpl["script_count"] == 19
    assert tpl["filler_count"] == 18


def test_generate_requires_api_key(client):
    resp = client.post(
        "/api/modules/generate",
        json={
            "name": "Roger",
            "voice_id": "v123",
            "template_key": "google-listing",
        },
    )
    assert resp.status_code == 503


def test_generate_from_template(client, fake_tts):
    resp = client.post(
        "/api/modules/generate",
        json={
            "name": "Roger (google-listing)",
            "voice_id": "voice-abc",
            "template_key": "google-listing",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_lines"] == 37
    module_id = body["module"]["id"]

    detail = _wait_for_clips(client, module_id, 37)
    script = sorted(
        (c for c in detail["clips"] if c["kind"] == "script"),
        key=lambda c: c["position"],
    )
    fillers = [c for c in detail["clips"] if c["kind"] == "filler"]

    assert len(script) == 19
    assert script[0]["label"].startswith("Oh, that sounds fantastic")
    assert script[0]["expected_duration"] == 37.5
    assert all(c["file_path"].startswith("/audio/modules/") for c in script)
    assert {c["tier"] for c in fillers} == {1, 2, 3}

    # Every line was synthesized with the requested voice
    assert len(fake_tts) == 37
    assert all(voice == "voice-abc" for _, voice in fake_tts)
    # Spoken-form text is used, not the display label
    texts = [text for text, _ in fake_tts]
    assert "Sixteen Seventy Goldcliff Circle." in texts

    client.delete(f"/api/modules/{module_id}")


def test_generate_from_existing_module(client, fake_tts):
    source = client.post(
        "/api/modules", json={"name": "Source Persona"}
    ).json()
    # Reuse the seeded Test Persona instead: it has clips
    modules = client.get("/api/modules").json()
    seeded = next(m for m in modules if m["name"] == "Test Persona")

    resp = client.post(
        "/api/modules/generate",
        json={
            "name": "Test Persona (new voice)",
            "voice_id": "voice-xyz",
            "source_module_id": seeded["id"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_lines"] == 2

    detail = _wait_for_clips(client, body["module"]["id"], 2)
    labels = {c["label"] for c in detail["clips"]}
    assert labels == {"Hello there", "Yes"}

    client.delete(f"/api/modules/{body['module']['id']}")
    client.delete(f"/api/modules/{source['id']}")


def test_generate_validation(client, fake_tts):
    both = client.post(
        "/api/modules/generate",
        json={
            "name": "X",
            "voice_id": "v",
            "template_key": "google-listing",
            "source_module_id": 1,
        },
    )
    assert both.status_code == 400

    neither = client.post(
        "/api/modules/generate", json={"name": "X", "voice_id": "v"}
    )
    assert neither.status_code == 400

    unknown = client.post(
        "/api/modules/generate",
        json={"name": "X", "voice_id": "v", "template_key": "nope"},
    )
    assert unknown.status_code == 404

    empty_source = client.post("/api/modules", json={"name": "Empty Src"}).json()
    no_lines = client.post(
        "/api/modules/generate",
        json={
            "name": "X",
            "voice_id": "v",
            "source_module_id": empty_source["id"],
        },
    )
    assert no_lines.status_code == 400
    client.delete(f"/api/modules/{empty_source['id']}")


def test_generation_broadcasts_progress(client, fake_tts):
    with client.websocket_connect("/ws") as ws:
        resp = client.post(
            "/api/modules/generate",
            json={
                "name": "WS Progress Persona",
                "voice_id": "voice-ws",
                "template_key": "google-listing",
            },
        )
        module_id = resp.json()["module"]["id"]

        final = None
        for _ in range(200):
            msg = ws.receive_json()
            if msg["type"] != "module_generation":
                continue
            assert msg["payload"]["module_id"] == module_id
            if msg["payload"]["status"] == "complete":
                final = msg["payload"]
                break
        assert final is not None
        assert final["done"] == 37
        assert final["failed"] == 0

    client.delete(f"/api/modules/{module_id}")
