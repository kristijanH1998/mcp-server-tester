async def test_experiment_persistence(client):
    # Register server
    server = await client.post(
        "/servers",
        json={"url": "http://127.0.0.1:8001"}
    )
    server_id = server.json()["id"]

    # Run experiment
    exp = await client.post(
        "/experiments",
        json={
            "server_id": server_id,
            "tool": "echo",
            "arguments": {"message": "hello"},
            "iterations": 2
        }
    )

    assert exp.status_code == 200
    exp_id = exp.json()["experiment_id"]

    # Retrieve experiment
    fetch = await client.get(f"/experiments/{exp_id}")
    assert fetch.status_code == 200
    assert fetch.json()["experiment_id"] == exp_id
