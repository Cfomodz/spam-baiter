import io


def _create(client, name="My Persona", description=None) -> dict:
    resp = client.post(
        "/api/modules", json={"name": name, "description": description}
    )
    assert resp.status_code == 200
    return resp.json()


def _upload(client, module_id, filename="clip.wav", **fields) -> dict:
    resp = client.post(
        f"/api/modules/{module_id}/clips",
        files={"file": (filename, io.BytesIO(b"RIFF-fake-wav"), "audio/wav")},
        data=fields,
    )
    return resp.json() if resp.status_code == 200 else resp


def test_seeded_module_from_soundboard(client):
    modules = client.get("/api/modules").json()
    seeded = next((m for m in modules if m["name"] == "Test Persona"), None)
    assert seeded is not None
    assert seeded["script_count"] == 1
    assert seeded["filler_count"] == 1

    detail = client.get(f"/api/modules/{seeded['id']}").json()
    clips = detail["clips"]
    script = [c for c in clips if c["kind"] == "script"]
    fillers = [c for c in clips if c["kind"] == "filler"]

    assert script[0]["label"] == "Hello there"
    assert script[0]["file_path"] == (
        "/soundboard-files/Test Persona/Hello there.wav"
    )
    assert fillers[0]["label"] == "Yes"
    assert fillers[0]["tier"] == 1


def test_module_crud(client):
    module = _create(client, "IRS Agent", "tax scam persona")
    assert module["clips"] == []

    resp = client.put(
        f"/api/modules/{module['id']}", json={"description": "updated"}
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "updated"

    dup = client.post("/api/modules", json={"name": "IRS Agent"})
    assert dup.status_code == 409

    blank = client.post("/api/modules", json={"name": "   "})
    assert blank.status_code == 400

    assert client.delete(f"/api/modules/{module['id']}").json() == {"ok": True}
    assert client.get(f"/api/modules/{module['id']}").status_code == 404


def test_upload_and_delete_clips(client):
    module = _create(client, "Upload Persona")

    step = _upload(
        client, module["id"], "Greeting.wav", kind="script", expected_duration="12.5"
    )
    assert step["kind"] == "script"
    assert step["label"] == "Greeting"
    assert step["expected_duration"] == 12.5
    assert step["position"] == 0
    assert step["file_path"].startswith("/audio/modules/")

    second = _upload(client, module["id"], "Follow up.wav", kind="script")
    assert second["position"] == 1

    filler = _upload(client, module["id"], "Mmhmm.wav", kind="filler", tier="2")
    assert filler["tier"] == 2
    assert filler["position"] == 0  # positions are tracked per kind

    bad_kind = _upload(client, module["id"], "x.wav", kind="banana")
    assert bad_kind.status_code == 400
    bad_ext = _upload(client, module["id"], "notes.txt", kind="script")
    assert bad_ext.status_code == 400
    bad_tier = _upload(client, module["id"], "x.wav", kind="filler", tier="7")
    assert bad_tier.status_code == 400

    resp = client.delete(f"/api/modules/{module['id']}/clips/{step['id']}")
    assert resp.json() == {"ok": True}
    detail = client.get(f"/api/modules/{module['id']}").json()
    assert {c["id"] for c in detail["clips"]} == {second["id"], filler["id"]}

    client.delete(f"/api/modules/{module['id']}")


def test_update_and_reorder_clips(client):
    module = _create(client, "Reorder Persona")
    a = _upload(client, module["id"], "a.wav", kind="script")
    b = _upload(client, module["id"], "b.wav", kind="script")
    c = _upload(client, module["id"], "c.wav", kind="script")

    resp = client.put(
        f"/api/modules/{module['id']}/clips/{a['id']}",
        json={"label": "renamed", "expected_duration": 30},
    )
    assert resp.status_code == 200
    assert resp.json()["label"] == "renamed"
    assert resp.json()["expected_duration"] == 30

    tier_on_script = client.put(
        f"/api/modules/{module['id']}/clips/{a['id']}", json={"tier": 2}
    )
    assert tier_on_script.status_code == 400

    resp = client.post(
        f"/api/modules/{module['id']}/reorder",
        json={"kind": "script", "clip_ids": [c["id"], a["id"], b["id"]]},
    )
    assert resp.status_code == 200
    ordered = [cl["id"] for cl in resp.json()["clips"] if cl["kind"] == "script"]
    assert ordered == [c["id"], a["id"], b["id"]]

    foreign = client.post(
        f"/api/modules/{module['id']}/reorder",
        json={"kind": "script", "clip_ids": [999999]},
    )
    assert foreign.status_code == 400

    client.delete(f"/api/modules/{module['id']}")
