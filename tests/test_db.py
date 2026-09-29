from datetime import date

import pytest

from app.allocator import Allocator
from app.db import Database
from app.inventory import InventoryCatalog
from app.models import (
    InventoryItem,
    ItemCondition,
    RequestLineItem,
    RequestStatus,
    ReturnLineItem,
)


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"


def test_schema_created_and_reopenable(db_path):
    db1 = Database(db_path)
    db1.close()
    db2 = Database(db_path)  # should not error on existing schema
    db2.close()


def test_inventory_round_trip(db_path):
    db = Database(db_path)
    db.save_inventory_items(
        [
            InventoryItem("Control", "Arduino Uno R3", live_qty=5, reserved_qty=1),
            InventoryItem("Sensor", "IR Sensor", live_qty=10),
        ]
    )
    loaded = {i.key: i for i in db.load_inventory_items()}
    assert loaded[("Control", "Arduino Uno R3")].live_qty == 5
    assert loaded[("Control", "Arduino Uno R3")].reserved_qty == 1
    assert loaded[("Sensor", "IR Sensor")].live_qty == 10
    db.close()


def test_request_round_trip_with_items(db_path):
    db = Database(db_path)
    catalog = InventoryCatalog()
    catalog.upsert(InventoryItem("Control", "Arduino Uno R3", live_qty=5))
    alloc = Allocator(catalog, db=db)
    req = alloc.submit_request(
        "Bot", "Student", "G1", date(2026, 5, 1),
        [RequestLineItem("Control", "Arduino Uno R3", 2)],
        student_email="a@b.com",
    )
    loaded = db.load_requests()
    assert len(loaded) == 1
    assert loaded[0].project_id == req.project_id
    assert loaded[0].status == RequestStatus.RESERVED
    assert loaded[0].pick_up_date == date(2026, 5, 1)
    assert loaded[0].items == [RequestLineItem("Control", "Arduino Uno R3", 2)]
    db.close()


def test_allocator_state_survives_restart_reserved_and_pending(db_path):
    db = Database(db_path)
    catalog = InventoryCatalog()
    catalog.upsert(InventoryItem("Sensor", "Scarce", live_qty=2))
    alloc = Allocator(catalog, db=db)

    winner = alloc.submit_request(
        "Winner", "A", "G1", date(2026, 1, 1), [RequestLineItem("Sensor", "Scarce", 2)]
    )
    loser = alloc.submit_request(
        "Loser", "B", "G1", date(2026, 1, 2), [RequestLineItem("Sensor", "Scarce", 2)]
    )
    db.close()

    db2 = Database(db_path)
    alloc2 = Allocator.from_db(db2)

    assert len(alloc2.catalog) == 1
    scarce = alloc2.catalog.get("Sensor", "Scarce")
    assert scarce.reserved_qty == 2  # winner's reservation survived

    assert winner.project_id in alloc2.reserved
    pending_ids = [r.project_id for r in alloc2.pending_heap.to_list()]
    assert loser.project_id in pending_ids
    assert len(alloc2.all_requests) == 2
    db2.close()


def test_allocator_state_survives_restart_borrowed_and_damaged(db_path):
    db = Database(db_path)
    catalog = InventoryCatalog()
    catalog.upsert(InventoryItem("Control", "Arduino Uno R3", live_qty=5))
    alloc = Allocator(catalog, db=db)
    req = alloc.submit_request(
        "Bot", "A", "G1", date(2026, 1, 1), [RequestLineItem("Control", "Arduino Uno R3", 2)]
    )
    alloc.confirm_handover(req.project_id)
    alloc.process_return(
        req.project_id,
        [
            ReturnLineItem("Control", "Arduino Uno R3", 1, ItemCondition.GOOD),
            ReturnLineItem("Control", "Arduino Uno R3", 1, ItemCondition.DAMAGED, note="broke"),
        ],
    )
    db.close()

    db2 = Database(db_path)
    alloc2 = Allocator.from_db(db2)

    item = alloc2.catalog.get("Control", "Arduino Uno R3")
    assert item.live_qty == 4  # 5 - 2 issued + 1 good return
    assert req.project_id not in alloc2.borrowed
    damage_log = list(alloc2.damaged)
    assert len(damage_log) == 1
    assert damage_log[0].project_id == req.project_id
    assert damage_log[0].note == "broke"
    reloaded_req = alloc2.all_requests.get(req.project_id)
    assert reloaded_req.status == RequestStatus.RETURNED
    db2.close()


def test_next_sequence_persists_across_restart(db_path):
    db = Database(db_path)
    catalog = InventoryCatalog()
    catalog.upsert(InventoryItem("Control", "A", live_qty=5))
    alloc = Allocator(catalog, db=db)
    req1 = alloc.submit_request("P1", "A", "G1", date(2026, 1, 1), [RequestLineItem("Control", "A", 1)])
    db.close()

    db2 = Database(db_path)
    alloc2 = Allocator.from_db(db2)
    req2 = alloc2.submit_request("P2", "A", "G1", date(2026, 1, 1), [RequestLineItem("Control", "A", 1)])
    assert req2.project_id != req1.project_id
    db2.close()
