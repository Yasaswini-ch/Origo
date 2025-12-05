import json
from datetime import datetime, timedelta
import app.services.file_service as file_service


def test_projects_list_and_delete_and_cleanup(client):
    # Create two projects via /generate
    payload = {
        "idea": "Notes",
        "target_users": "students",
        "features": "auth,notes",
        "stack": "react+fastapi",
    }
    pids = []
    for _ in range(2):
        r = client.post("/generate", json=payload)
        assert r.status_code == 200
        pids.append(r.json()["project_id"])

    # List projects
    lr = client.get("/projects")
    assert lr.status_code == 200
    listing = lr.json()
    assert all(pid in listing for pid in pids)

    # Make first project old by modifying its metadata created_at
    old_pid = pids[0]
    meta_path = file_service.BASE_STORAGE_DIR / old_pid / "project.json"
    meta = json.loads(meta_path.read_text())
    meta["created_at"] = (datetime.utcnow() - timedelta(days=10)).isoformat() + "Z"
    meta_path.write_text(json.dumps(meta), encoding="utf-8")

    # Cleanup (default 7 days)
    cr = client.post("/projects/cleanup")
    assert cr.status_code == 200
    result = cr.json()
    assert old_pid in result["deleted"]

    # Old project folder removed
    assert not (file_service.BASE_STORAGE_DIR / old_pid).exists()

    # Delete remaining project explicitly
    remaining_pid = pids[1]
    dr = client.delete(f"/projects/{remaining_pid}")
    assert dr.status_code == 200
    assert dr.json()["status"] == "deleted"

    # After delete, it should not appear in listing
    lr2 = client.get("/projects")
    assert lr2.status_code == 200
    listing2 = lr2.json()
    assert remaining_pid not in listing2
