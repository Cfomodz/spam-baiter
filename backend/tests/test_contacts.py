def test_group_crud(client):
    resp = client.post(
        "/api/contacts/groups", json={"name": "IRS Scam", "notes": "callback list"}
    )
    assert resp.status_code == 200
    group = resp.json()
    assert group["name"] == "IRS Scam"
    assert group["phone_numbers"] == []

    resp = client.put(
        f"/api/contacts/groups/{group['id']}", json={"notes": "updated"}
    )
    assert resp.status_code == 200
    assert resp.json()["notes"] == "updated"

    resp = client.get("/api/contacts/groups")
    assert any(g["id"] == group["id"] for g in resp.json())

    resp = client.delete(f"/api/contacts/groups/{group['id']}")
    assert resp.status_code == 200

    assert client.put(
        f"/api/contacts/groups/{group['id']}", json={"name": "x"}
    ).status_code == 404
    assert client.delete(f"/api/contacts/groups/{group['id']}").status_code == 404


def test_numbers_sequence_within_group(client):
    group_id = client.post(
        "/api/contacts/groups", json={"name": "Tech Support"}
    ).json()["id"]

    first = client.post(
        "/api/contacts/numbers",
        json={"number": "5551110001", "group_id": group_id},
    ).json()
    second = client.post(
        "/api/contacts/numbers",
        json={"number": "5551110002", "group_id": group_id},
    ).json()
    assert first["sequence_num"] == 1
    assert second["sequence_num"] == 2

    ungrouped = client.post(
        "/api/contacts/numbers", json={"number": "5551110003"}
    ).json()
    assert ungrouped["group_id"] is None
    assert ungrouped["sequence_num"] is None

    resp = client.put(
        f"/api/contacts/numbers/{ungrouped['id']}/assign",
        json={"group_id": group_id},
    )
    assert resp.status_code == 200
    assert resp.json()["sequence_num"] == 3

    recent = client.get("/api/contacts/recent").json()
    recent_ids = [n["id"] for n in recent]
    assert first["id"] in recent_ids

    for number in (first, second, ungrouped):
        assert client.delete(
            f"/api/contacts/numbers/{number['id']}"
        ).status_code == 200
    client.delete(f"/api/contacts/groups/{group_id}")


def test_delete_missing_number_returns_404(client):
    assert client.delete("/api/contacts/numbers/999999").status_code == 404
