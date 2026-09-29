"""Command-line walkthrough of the borrow workflow (milestone 3).

Run:
    python cli_demo.py

Loads the seeded inventory, submits a batch of project requests
(including two that compete for the same scarce item, to show the
Main Min-Heap picking a winner by pick-up date / submission time and
sending the loser to the Pending heap), then confirms a handover.
"""

from datetime import date, datetime, timedelta

from algo.merge_sort import merge_sort
from app.allocator import Allocator
from app.inventory import InventoryCatalog
from app.models import ItemCondition, RequestLineItem, ReturnLineItem


def line(*parts):
    print(" ".join(str(p) for p in parts))


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main():
    catalog = InventoryCatalog()
    n = catalog.load_csv("data/inventory_seed.csv")
    section(f"Loaded inventory: {n} items")

    allocator = Allocator(catalog)
    today = date.today()
    now = datetime.now()

    # Deliberately push the scarce sensor's stock down to 2 so two
    # requests for 2 units each cannot both be satisfied.
    scarce_type, scarce_name = "Sensor", "Ultrasonic Sensor HC-SR04"
    scarce_item = catalog.get(scarce_type, scarce_name)
    scarce_item.live_qty = 2
    line(f"(demo setup) {scarce_name} live_qty forced to 2 for this run")

    section("Submitting a batch of requests (added, not yet processed)")

    allocator.add_request(
        project_name="Line-Following Bot",
        student_name="Nan",
        group="ROW",
        pick_up_date=today + timedelta(days=3),
        items=[
            RequestLineItem("Control", "Arduino Uno R3", 1),
            RequestLineItem(scarce_type, scarce_name, 2),
        ],
        student_email="nan@example.kmitl.ac.th",
        submitted_at=now - timedelta(minutes=5),
    )
    line("Added P0001: Line-Following Bot, pick-up +3d, submitted -5min")

    allocator.add_request(
        project_name="Obstacle Avoider",
        student_name="Ploy",
        group="ROW",
        pick_up_date=today + timedelta(days=3),
        items=[
            RequestLineItem(scarce_type, scarce_name, 2),
        ],
        student_email="ploy@example.kmitl.ac.th",
        submitted_at=now - timedelta(minutes=2),
    )
    line("Added P0002: Obstacle Avoider, pick-up +3d (same day), submitted -2min")
    line("  -> same pick-up date as P0001 but submitted later: loses the tie-break")

    allocator.add_request(
        project_name="Weather Station",
        student_name="Beam",
        group="ROW",
        pick_up_date=today + timedelta(days=1),
        items=[
            RequestLineItem("Sensor", "Temperature & Humidity Sensor DHT22", 1),
        ],
        student_email="beam@example.kmitl.ac.th",
        submitted_at=now,
    )
    line("Added P0003: Weather Station, pick-up +1d (earliest) -> highest priority")

    section("Draining the Main Min-Heap in priority order")
    allocator.process_main_queue()

    section("Reserved (awaiting pickup)")
    for req in allocator.reserved.values():
        line(f"  {req.project_id} {req.project_name!r} -> RESERVED")

    section("Pending (waiting on stock)")
    pending_ordered = merge_sort(allocator.pending_heap.to_list(), key_func=lambda r: r.heap_key)
    for req in pending_ordered:
        line(f"  {req.project_id} {req.project_name!r} -> PENDING: {req.pending_reason}")

    section("Admin ordered view (merge sort, by pick-up date then submission)")
    for req in allocator.admin_ordered_view():
        line(
            f"  {req.project_id:6s} {req.pick_up_date}  {req.status.value:9s} "
            f"{req.project_name}"
        )

    section("Confirming handover for the project holding the scarce sensor")
    # P0001 (Line-Following Bot) is the one holding the scarce sensor;
    # P0003 has the earlier pick-up date but doesn't touch that item.
    holder = next(
        r for r in allocator.reserved.values()
        if any(i.type == scarce_type and i.item_name == scarce_name for i in r.items)
    )
    target = holder.project_id
    record = allocator.confirm_handover(target)
    line(f"  Handed over {record.project_id} ({record.project_name}) at {record.handed_over_at}")

    section("Inventory after handover")
    item = catalog.get(scarce_type, scarce_name)
    line(f"  {scarce_name}: live={item.live_qty} reserved={item.reserved_qty} available={item.available_qty} status={item.status.value}")

    section("Borrowed table")
    for pid, record in allocator.borrowed.items():
        line(f"  {pid}: {record.project_name} handed over {record.handed_over_at}")

    section(f"Returning {target}: 1 good, 1 damaged")
    damage_records = allocator.process_return(
        target,
        [
            ReturnLineItem("Control", "Arduino Uno R3", 1, ItemCondition.GOOD),
            ReturnLineItem(scarce_type, scarce_name, 1, ItemCondition.GOOD),
            ReturnLineItem(scarce_type, scarce_name, 1, ItemCondition.DAMAGED, note="cracked housing"),
        ],
    )
    line(f"  Logged {len(damage_records)} damage record(s) to the linked list")

    section("Pending after return (partial restock: only 1 unit came back good)")
    pending_ordered = merge_sort(allocator.pending_heap.to_list(), key_func=lambda r: r.heap_key)
    if pending_ordered:
        for req in pending_ordered:
            line(f"  {req.project_id} {req.project_name!r} -> still PENDING: {req.pending_reason}")
    else:
        for req in allocator.reserved.values():
            line(f"  {req.project_id} {req.project_name!r} -> now RESERVED (stock freed by the return)")

    section("Damaged items log (Singly Linked List, append-only)")
    for record in allocator.damaged:
        line(f"  {record.project_id}: {record.quantity}x {record.item_name} ({record.note})")

    item = catalog.get(scarce_type, scarce_name)
    line()
    line(
        f"Final {scarce_name}: live={item.live_qty} reserved={item.reserved_qty} "
        f"available={item.available_qty} status={item.status.value}"
    )


if __name__ == "__main__":
    main()
