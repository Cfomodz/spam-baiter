def _dial(client, number: str) -> dict:
    resp = client.post("/api/lines/dial", json={"number": number})
    assert resp.status_code == 200
    return resp.json()


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_lines_start_empty(client):
    resp = client.get("/api/lines")
    assert resp.status_code == 200
    assert resp.json() == []


def test_dial_and_hangup(client):
    line = _dial(client, "5551234567")
    assert line["status"] == "dialing"
    assert line["number"] == "5551234567"

    resp = client.get("/api/lines")
    assert [l["line_id"] for l in resp.json()] == [line["line_id"]]

    resp = client.post(f"/api/lines/{line['line_id']}/hangup")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

    assert client.get("/api/lines").json() == []


def test_hold_and_unhold_are_safe_while_dialing(client):
    line = _dial(client, "5550000001")

    # Hold only applies to active lines; on a dialing line it must be a
    # harmless no-op rather than an error.
    assert client.post(f"/api/lines/{line['line_id']}/hold").status_code == 200
    assert client.post(f"/api/lines/{line['line_id']}/unhold").status_code == 200

    status = client.get("/api/lines").json()[0]["status"]
    assert status == "dialing"

    client.post(f"/api/lines/{line['line_id']}/hangup")


def test_merge_two_lines(client):
    first = _dial(client, "5551111111")
    second = _dial(client, "5552222222")

    resp = client.post(
        "/api/lines/merge",
        json={"line_ids": [first["line_id"], second["line_id"]]},
    )
    assert resp.status_code == 200
    merged = resp.json()
    assert merged["status"] == "active"
    assert set(merged["merged_with"]) == {first["line_id"], second["line_id"]}

    lines = {l["line_id"]: l for l in client.get("/api/lines").json()}
    assert lines[first["line_id"]]["status"] == "merged"
    assert lines[second["line_id"]]["status"] == "merged"
    assert merged["line_id"] in lines


def test_dial_broadcasts_line_update(client):
    with client.websocket_connect("/ws") as ws:
        line = _dial(client, "5559998888")
        msg = ws.receive_json()
        assert msg["type"] == "line_update"
        assert msg["payload"]["line_id"] == line["line_id"]
        assert msg["payload"]["number"] == "5559998888"
        client.post(f"/api/lines/{line['line_id']}/hangup")
