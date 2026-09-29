from datetime import date, datetime, timedelta

import pytest

from app.allocator import Allocator
from app.inventory import InventoryCatalog
from app.models import InventoryItem, RequestLineItem, RequestStatus


def catalog_with(*items):
    c = InventoryCatalog()
    for item in items:
        c.upsert(item)
    return c


class RecordingNotifier:
    def __init__(self):
        self.ready = []
        self.pending = []

    def notify_ready(self, request):
        self.ready.append(request.project_id)

    def notify_pending(self, request):
        self.pending.append(request.project_id)


def test_submit_reserves_when_all_items_available():
    catalog = catalog_with(InventoryItem("Control", "Arduino Uno R3", live_qty=5))
    alloc = Allocator(catalog, notifier=RecordingNotifier())
    req = alloc.submit_request(
        project_name="Bot",
        student_name="A",
        group="G1",
        pick_up_date=date.today(),
        items=[RequestLineItem("Control", "Arduino Uno R3", 2)],
    )
    assert req.status == RequestStatus.RESERVED
    assert req.project_id in alloc.reserved
    item = catalog.get("Control", "Arduino Uno R3")
    assert item.reserved_qty == 2
    assert item.available_qty == 3
    assert alloc.notifier.ready == [req.project_id]


def test_submit_goes_pending_when_any_item_short_all_or_nothing():
    catalog = catalog_with(
        InventoryItem("Control", "Arduino Uno R3", live_qty=5),
        InventoryItem("Sensor", "IR Obstacle Sensor", live_qty=1),
    )
    alloc = Allocator(catalog, notifier=RecordingNotifier())
    req = alloc.submit_request(
        project_name="Bot",
        student_name="A",
        group="G1",
        pick_up_date=date.today(),
        items=[
            RequestLineItem("Control", "Arduino Uno R3", 2),
            RequestLineItem("Sensor", "IR Obstacle Sensor", 5),  # short
        ],
    )
    assert req.status == RequestStatus.PENDING
    assert req.project_id in [r.project_id for r in alloc.pending_heap.to_list()]
    # all-or-nothing: the Arduino must NOT be reserved even though it had stock
    arduino = catalog.get("Control", "Arduino Uno R3")
    assert arduino.reserved_qty == 0
    assert alloc.notifier.pending == [req.project_id]


def test_priority_processing_order_by_pickup_date_then_submission():
    catalog = catalog_with(InventoryItem("Sensor", "Scarce", live_qty=2))
    alloc = Allocator(catalog, notifier=RecordingNotifier())
    now = datetime(2026, 1, 1, 12, 0, 0)
    today = date(2026, 1, 5)

    # Later pick-up date but earlier submission -- should still lose to
    # the earlier pick-up date.
    late_pickup = alloc.add_request(
        "Late Pickup", "A", "G1", today + timedelta(days=5),
        [RequestLineItem("Sensor", "Scarce", 2)], submitted_at=now,
    )
    early_pickup = alloc.add_request(
        "Early Pickup", "B", "G1", today,
        [RequestLineItem("Sensor", "Scarce", 2)], submitted_at=now + timedelta(minutes=10),
    )
    alloc.process_main_queue()

    assert early_pickup.status == RequestStatus.RESERVED
    assert late_pickup.status == RequestStatus.PENDING


def test_submission_time_tie_break_when_pickup_dates_equal():
    catalog = catalog_with(InventoryItem("Sensor", "Scarce", live_qty=2))
    alloc = Allocator(catalog)
    today = date(2026, 1, 5)
    now = datetime(2026, 1, 1, 12, 0, 0)

    later_submit = alloc.add_request(
        "Later Submit", "A", "G1", today,
        [RequestLineItem("Sensor", "Scarce", 2)], submitted_at=now + timedelta(minutes=5),
    )
    earlier_submit = alloc.add_request(
        "Earlier Submit", "B", "G1", today,
        [RequestLineItem("Sensor", "Scarce", 2)], submitted_at=now,
    )
    alloc.process_main_queue()

    assert earlier_submit.status == RequestStatus.RESERVED
    assert later_submit.status == RequestStatus.PENDING


def test_confirm_handover_reduces_live_stock_and_moves_to_borrowed():
    catalog = catalog_with(InventoryItem("Control", "Arduino Uno R3", live_qty=5))
    alloc = Allocator(catalog)
    req = alloc.submit_request(
        "Bot", "A", "G1", date.today(), [RequestLineItem("Control", "Arduino Uno R3", 2)]
    )
    record = alloc.confirm_handover(req.project_id)
    assert record.project_id == req.project_id
    assert req.project_id not in alloc.reserved
    assert req.project_id in alloc.borrowed
    item = catalog.get("Control", "Arduino Uno R3")
    assert item.live_qty == 3
    assert item.reserved_qty == 0
    assert item.available_qty == 3
    assert req.status == RequestStatus.BORROWED


def test_confirm_handover_unknown_project_raises():
    catalog = catalog_with(InventoryItem("Control", "Arduino Uno R3", live_qty=5))
    alloc = Allocator(catalog)
    with pytest.raises(KeyError):
        alloc.confirm_handover("nope")


def test_release_reservation_returns_stock_and_reopens_pending():
    catalog = catalog_with(InventoryItem("Control", "Arduino Uno R3", live_qty=5))
    alloc = Allocator(catalog)
    req = alloc.submit_request(
        "Bot", "A", "G1", date.today(), [RequestLineItem("Control", "Arduino Uno R3", 2)]
    )
    alloc.release_reservation(req.project_id)
    item = catalog.get("Control", "Arduino Uno R3")
    assert item.reserved_qty == 0
    assert item.available_qty == 5
    assert req.status == RequestStatus.PENDING
    assert req.project_id not in alloc.reserved


def test_admin_ordered_view_is_stable_merge_sort():
    catalog = catalog_with(InventoryItem("Control", "Arduino Uno R3", live_qty=50))
    alloc = Allocator(catalog)
    today = date(2026, 1, 5)
    ids_in_submission_order = []
    for i in range(4):
        req = alloc.submit_request(
            f"Proj{i}", "A", "G1", today, [RequestLineItem("Control", "Arduino Uno R3", 1)],
            submitted_at=datetime(2026, 1, 1, 12, i, 0),
        )
        ids_in_submission_order.append(req.project_id)
    view = alloc.admin_ordered_view()
    assert [r.project_id for r in view] == ids_in_submission_order


def test_missing_catalog_item_counts_as_shortage():
    catalog = InventoryCatalog()
    alloc = Allocator(catalog)
    req = alloc.submit_request(
        "Bot", "A", "G1", date.today(), [RequestLineItem("Sensor", "Nonexistent", 1)]
    )
    assert req.status == RequestStatus.PENDING
    assert "not in catalog" in req.pending_reason
