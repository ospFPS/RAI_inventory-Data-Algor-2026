from datetime import date, timedelta

import pytest

from app.allocator import Allocator
from app.inventory import InventoryCatalog
from app.models import (
    InventoryItem,
    ItemCondition,
    RequestLineItem,
    RequestStatus,
    ReturnLineItem,
)


def catalog_with(*items):
    c = InventoryCatalog()
    for item in items:
        c.upsert(item)
    return c


def borrow(alloc, name, pick_up_date, items):
    req = alloc.submit_request(name, "Student", "G1", pick_up_date, items)
    assert req.status == RequestStatus.RESERVED, f"{name} did not reserve: {req.pending_reason}"
    alloc.confirm_handover(req.project_id)
    return req


def test_return_all_good_restocks_live_qty():
    catalog = catalog_with(InventoryItem("Control", "Arduino Uno R3", live_qty=5))
    alloc = Allocator(catalog)
    req = borrow(alloc, "Bot", date.today(), [RequestLineItem("Control", "Arduino Uno R3", 2)])
    item = catalog.get("Control", "Arduino Uno R3")
    assert item.live_qty == 3

    damage = alloc.process_return(
        req.project_id,
        [ReturnLineItem("Control", "Arduino Uno R3", 2, ItemCondition.GOOD)],
    )
    assert damage == []
    assert item.live_qty == 5
    assert req.project_id not in alloc.borrowed
    assert req.status == RequestStatus.RETURNED


def test_return_damaged_items_are_not_restocked_and_are_logged():
    catalog = catalog_with(InventoryItem("Control", "Arduino Uno R3", live_qty=5))
    alloc = Allocator(catalog)
    req = borrow(alloc, "Bot", date.today(), [RequestLineItem("Control", "Arduino Uno R3", 2)])
    item = catalog.get("Control", "Arduino Uno R3")
    assert item.live_qty == 3

    damage = alloc.process_return(
        req.project_id,
        [ReturnLineItem("Control", "Arduino Uno R3", 2, ItemCondition.DAMAGED, note="cracked")],
    )
    assert item.live_qty == 3  # unchanged -- damaged items never re-enter stock
    assert len(damage) == 1
    assert damage[0].quantity == 2
    assert damage[0].note == "cracked"
    assert [d.project_id for d in alloc.damaged] == [req.project_id]


def test_return_mixed_good_and_damaged_split():
    catalog = catalog_with(InventoryItem("Control", "Arduino Uno R3", live_qty=10))
    alloc = Allocator(catalog)
    req = borrow(alloc, "Bot", date.today(), [RequestLineItem("Control", "Arduino Uno R3", 5)])
    item = catalog.get("Control", "Arduino Uno R3")
    assert item.live_qty == 5

    alloc.process_return(
        req.project_id,
        [
            ReturnLineItem("Control", "Arduino Uno R3", 3, ItemCondition.GOOD),
            ReturnLineItem("Control", "Arduino Uno R3", 2, ItemCondition.DAMAGED),
        ],
    )
    assert item.live_qty == 8  # 5 + 3 good, 2 damaged excluded
    assert len(list(alloc.damaged)) == 1
    assert list(alloc.damaged)[0].quantity == 2


def test_return_unknown_project_raises():
    catalog = catalog_with(InventoryItem("Control", "Arduino Uno R3", live_qty=5))
    alloc = Allocator(catalog)
    with pytest.raises(KeyError):
        alloc.process_return("nope", [])


def test_return_quantity_mismatch_raises_and_does_not_mutate_stock():
    catalog = catalog_with(InventoryItem("Control", "Arduino Uno R3", live_qty=5))
    alloc = Allocator(catalog)
    req = borrow(alloc, "Bot", date.today(), [RequestLineItem("Control", "Arduino Uno R3", 2)])
    with pytest.raises(ValueError):
        alloc.process_return(
            req.project_id,
            [ReturnLineItem("Control", "Arduino Uno R3", 1, ItemCondition.GOOD)],  # only 1 of 2
        )
    # a rejected return must not mutate state: still borrowed, stock untouched
    assert req.project_id in alloc.borrowed
    assert catalog.get("Control", "Arduino Uno R3").live_qty == 3


def test_pending_project_satisfied_after_return_frees_stock():
    catalog = catalog_with(InventoryItem("Sensor", "Scarce", live_qty=2))
    alloc = Allocator(catalog)
    today = date.today()

    winner = alloc.submit_request(
        "Winner", "A", "G1", today, [RequestLineItem("Sensor", "Scarce", 2)]
    )
    loser = alloc.submit_request(
        "Loser", "B", "G1", today + timedelta(days=1), [RequestLineItem("Sensor", "Scarce", 2)]
    )
    assert winner.status == RequestStatus.RESERVED
    assert loser.status == RequestStatus.PENDING
    assert len(alloc.pending_heap) == 1

    alloc.confirm_handover(winner.project_id)
    alloc.process_return(
        winner.project_id, [ReturnLineItem("Sensor", "Scarce", 2, ItemCondition.GOOD)]
    )

    assert loser.status == RequestStatus.RESERVED
    assert loser.project_id in alloc.reserved
    assert len(alloc.pending_heap) == 0


def test_pending_project_stays_pending_if_return_is_damaged():
    catalog = catalog_with(InventoryItem("Sensor", "Scarce", live_qty=2))
    alloc = Allocator(catalog)
    today = date.today()

    winner = alloc.submit_request(
        "Winner", "A", "G1", today, [RequestLineItem("Sensor", "Scarce", 2)]
    )
    loser = alloc.submit_request(
        "Loser", "B", "G1", today + timedelta(days=1), [RequestLineItem("Sensor", "Scarce", 2)]
    )
    alloc.confirm_handover(winner.project_id)
    alloc.process_return(
        winner.project_id, [ReturnLineItem("Sensor", "Scarce", 2, ItemCondition.DAMAGED)]
    )

    # damaged items never re-enter stock, so the pending project is still short
    assert loser.status == RequestStatus.PENDING
    assert len(alloc.pending_heap) == 1


def test_multiple_returns_accumulate_in_damage_log_in_order():
    catalog = catalog_with(
        InventoryItem("Control", "A", live_qty=5),
        InventoryItem("Control", "B", live_qty=5),
    )
    alloc = Allocator(catalog)
    req1 = borrow(alloc, "P1", date.today(), [RequestLineItem("Control", "A", 1)])
    req2 = borrow(alloc, "P2", date.today(), [RequestLineItem("Control", "B", 1)])

    alloc.process_return(req1.project_id, [ReturnLineItem("Control", "A", 1, ItemCondition.DAMAGED)])
    alloc.process_return(req2.project_id, [ReturnLineItem("Control", "B", 1, ItemCondition.DAMAGED)])

    log = list(alloc.damaged)
    assert [d.project_id for d in log] == [req1.project_id, req2.project_id]
