"""FastAPI route tests using TestClient. Each test module gets its own
temp SQLite DB (env vars set before importing app.main, since it reads
them once at module import time) so these never touch the real
data/app.db used for the manual demo.
"""

import os
import tempfile

import pytest

_tmp_dir = tempfile.mkdtemp()
os.environ["RAI_DB_PATH"] = os.path.join(_tmp_dir, "test_web.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def as_admin(client):
    client.post("/login", data={"chosen_role": "admin"}, follow_redirects=False)


def as_student(client):
    client.post("/login", data={"chosen_role": "student"}, follow_redirects=False)


def test_root_redirects_to_dashboard(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"] == "/dashboard"


def test_dashboard_shows_seeded_catalog(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert "200 total types" in resp.text


def test_new_request_page_loads(client):
    resp = client.get("/new-request")
    assert resp.status_code == 200
    assert "Submit Request" in resp.text


def test_component_search_returns_matches(client):
    resp = client.get("/components/search", params={"q": "Arduino"})
    assert resp.status_code == 200
    assert "Arduino" in resp.text


def test_component_search_empty_query_returns_nothing(client):
    resp = client.get("/components/search", params={"q": ""})
    assert "result-item" not in resp.text


def test_submit_request_reserves_and_redirects_to_status(client):
    resp = client.post(
        "/requests",
        data={
            "project_name": "Web Test Bot",
            "student_name": "Tester",
            "group": "G1",
            "pick_up_date": "2026-12-01",
            "student_email": "",
            "item_types": ["Control"],
            "item_names": ["Arduino Uno R3"],
            "item_quantities": ["1"],
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    location = resp.headers["location"]
    assert location.startswith("/requests/P")

    status_resp = client.get(location)
    assert status_resp.status_code == 200
    assert "Reserved" in status_resp.text


def test_submit_request_without_items_rejected(client):
    resp = client.post(
        "/requests",
        data={
            "project_name": "No Items",
            "student_name": "Tester",
            "group": "G1",
            "pick_up_date": "2026-12-01",
        },
    )
    assert resp.status_code == 400


def test_unknown_request_status_404(client):
    resp = client.get("/requests/P9999")
    assert resp.status_code == 404


def test_student_cannot_confirm_handover(client):
    as_student(client)
    resp = client.post("/reserved/P0001/handover")
    assert resp.status_code == 403


def test_full_borrow_return_pending_flow_via_http(client):
    as_admin(client)

    # Two requests compete for the same scarce item.
    r1 = client.post(
        "/requests",
        data={
            "project_name": "Winner", "student_name": "A", "group": "G1",
            "pick_up_date": "2026-11-01",
            "item_types": ["Sensor"], "item_names": ["IR Obstacle Sensor"], "item_quantities": ["1"],
        },
        follow_redirects=False,
    )
    winner_id = r1.headers["location"].split("/")[-1]

    r2 = client.post(
        "/requests",
        data={
            "project_name": "Loser", "student_name": "B", "group": "G1",
            "pick_up_date": "2026-11-02",
            "item_types": ["Sensor"], "item_names": ["IR Obstacle Sensor"], "item_quantities": ["999"],
        },
        follow_redirects=False,
    )
    loser_id = r2.headers["location"].split("/")[-1]

    assert "Reserved" in client.get(f"/requests/{winner_id}").text
    assert "Pending" in client.get(f"/requests/{loser_id}").text

    pending_page = client.get("/pending")
    assert loser_id in pending_page.text

    handover = client.post(f"/reserved/{winner_id}/handover", follow_redirects=False)
    assert handover.status_code == 303

    borrowed_page = client.get("/borrowed")
    assert winner_id in borrowed_page.text

    ret = client.post(
        f"/returns/{winner_id}",
        data={
            "item_types": ["Sensor"],
            "item_names": ["IR Obstacle Sensor"],
            "good_quantities": ["1"],
            "damaged_quantities": ["0"],
            "notes": [""],
        },
        follow_redirects=False,
    )
    assert ret.status_code == 303

    damaged_page = client.get("/damaged")
    assert damaged_page.status_code == 200


def test_admin_view_lists_requests(client):
    as_admin(client)
    resp = client.get("/admin")
    assert resp.status_code == 200
    assert "Admin Priority View" in resp.text


def test_inventory_search_by_query(client):
    resp = client.get("/inventory", params={"q": "Relay"})
    assert resp.status_code == 200
    assert "Relay" in resp.text
