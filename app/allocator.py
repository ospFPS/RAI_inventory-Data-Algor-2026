"""The Allocator ties the hand-implemented data structures together into
the borrow/return workflow described in section 6 of the brief:

    Main Min-Heap      -- queued requests not yet processed, keyed by
                           (pick_up_date, submitted_at)
    Pending Min-Heap    -- requests processed but missing stock, same key
    reserved (HashTable) -- requests fully reserved, awaiting physical
                             handover, keyed by Project ID
    borrowed (HashTable) -- handed-over projects, keyed by Project ID
    damaged (SinglyLinkedList) -- append-only damage log (return workflow)
    all_requests (HashTable) -- every request ever submitted, keyed by
                                 Project ID, for the admin merge-sort view
                                 and general lookup regardless of state

Reservation is all-or-nothing (section 13 default): a request only
reserves stock if every line item has enough available quantity;
otherwise nothing is reserved and the whole request goes to Pending.
"""

from datetime import datetime

from algo.merge_sort import merge_sort
from app.inventory import InventoryCatalog
from app.models import (
    BorrowedRecord,
    DamageRecord,
    ItemCondition,
    ProjectRequest,
    RequestLineItem,
    RequestStatus,
    ReturnLineItem,
)
from app.notifications import ConsoleNotifier, Notifier
from ds.hashtable import HashTable
from ds.heap import MinHeap
from ds.linkedlist import SinglyLinkedList


def _heap_key(req: ProjectRequest):
    return req.heap_key


def _project_id(req: ProjectRequest):
    return req.project_id


class Allocator:
    def __init__(self, catalog: InventoryCatalog, notifier: Notifier | None = None):
        self.catalog = catalog
        self.notifier = notifier or ConsoleNotifier()

        self.main_heap: MinHeap[ProjectRequest] = MinHeap(_heap_key, _project_id)
        self.pending_heap: MinHeap[ProjectRequest] = MinHeap(_heap_key, _project_id)
        self.reserved: HashTable[str, ProjectRequest] = HashTable()
        self.borrowed: HashTable[str, BorrowedRecord] = HashTable()
        self.damaged: SinglyLinkedList = SinglyLinkedList()
        self.all_requests: HashTable[str, ProjectRequest] = HashTable()

        self._next_seq = 1

    # -- request intake --------------------------------------------------

    def _generate_project_id(self) -> str:
        pid = f"P{self._next_seq:04d}"
        self._next_seq += 1
        return pid

    def add_request(
        self,
        project_name: str,
        student_name: str,
        group: str,
        pick_up_date,
        items: list[RequestLineItem],
        student_email: str = "",
        submitted_at: datetime | None = None,
    ) -> ProjectRequest:
        """Create a request and push it onto the Main Min-Heap, without
        processing it yet. Useful for batch-loading several requests
        before a single process_main_queue() call, e.g. in the CLI demo,
        so priority ordering actually has multiple candidates to pick
        between."""
        req = ProjectRequest(
            project_id=self._generate_project_id(),
            project_name=project_name,
            student_name=student_name,
            group=group,
            pick_up_date=pick_up_date,
            submitted_at=submitted_at or datetime.now(),
            items=list(items),
            student_email=student_email,
        )
        self.all_requests.put(req.project_id, req)
        self.main_heap.push(req)
        return req

    def submit_request(self, *args, **kwargs) -> ProjectRequest:
        """add_request() followed immediately by draining the Main heap,
        matching the brief's step-by-step borrow workflow (section 6.1)."""
        req = self.add_request(*args, **kwargs)
        self.process_main_queue()
        return req

    # -- main queue processing -------------------------------------------

    def process_main_queue(self) -> None:
        """Extract every project from the Main Min-Heap in priority
        order (earliest pick-up date, then earliest submission), and for
        each one either reserve its items or move it to Pending."""
        while not self.main_heap.is_empty():
            req = self.main_heap.pop()
            self._try_reserve_or_pend(req)

    def _try_reserve_or_pend(self, req: ProjectRequest) -> None:
        shortages = self._find_shortages(req)
        if not shortages:
            for line in req.items:
                self.catalog.reserve(line.type, line.item_name, line.quantity)
            req.status = RequestStatus.RESERVED
            req.pending_reason = ""
            self.reserved.put(req.project_id, req)
            self.notifier.notify_ready(req)
        else:
            req.status = RequestStatus.PENDING
            req.pending_reason = "; ".join(shortages)
            self.pending_heap.push(req)
            self.notifier.notify_pending(req)

    def _find_shortages(self, req: ProjectRequest) -> list[str]:
        shortages = []
        for line in req.items:
            item = self.catalog.get(line.type, line.item_name)
            if item is None:
                shortages.append(f"{line.item_name}: not in catalog")
            elif item.available_qty < line.quantity:
                shortages.append(
                    f"{line.item_name}: need {line.quantity}, have {item.available_qty}"
                )
        return shortages

    # -- handover ----------------------------------------------------------

    def confirm_handover(self, project_id: str) -> BorrowedRecord:
        """Admin confirms the student physically collected a Reserved
        project: reduce live stock and move it into the Borrowed table."""
        if project_id not in self.reserved:
            raise KeyError(f"project not in Reserved state: {project_id}")
        req = self.reserved.delete(project_id)
        for line in req.items:
            self.catalog.issue(line.type, line.item_name, line.quantity)
        record = BorrowedRecord(
            project_id=req.project_id,
            project_name=req.project_name,
            group=req.group,
            items=req.items,
            handed_over_at=datetime.now(),
        )
        self.borrowed.put(project_id, record)
        req.status = RequestStatus.BORROWED
        return record

    def release_reservation(self, project_id: str) -> ProjectRequest:
        """Admin manually releases a Reserved project that was never
        collected (section 13 default for uncollected reservations)."""
        if project_id not in self.reserved:
            raise KeyError(f"project not in Reserved state: {project_id}")
        req = self.reserved.delete(project_id)
        for line in req.items:
            self.catalog.release_reservation(line.type, line.item_name, line.quantity)
        req.status = RequestStatus.PENDING
        req.pending_reason = "Reservation manually released by admin"
        self.all_requests.put(req.project_id, req)
        return req

    # -- returns ---------------------------------------------------------

    def process_return(
        self, project_id: str, return_items: list[ReturnLineItem]
    ) -> list[DamageRecord]:
        """Return workflow (section 6.2): validate the return accounts
        for exactly what was borrowed, restock good-condition items,
        log damaged ones to the Damage linked list (never restocked),
        remove the project from Borrowed, then re-check the Pending
        heap since stock just changed."""
        if project_id not in self.borrowed:
            raise KeyError(f"project not in Borrowed state: {project_id}")
        record = self.borrowed.get(project_id)
        self._validate_return_matches_borrowed(record, return_items)
        self.borrowed.delete(project_id)

        now = datetime.now()
        new_damage: list[DamageRecord] = []
        for line in return_items:
            if line.condition == ItemCondition.GOOD:
                self.catalog.restock_good(line.type, line.item_name, line.quantity)
            else:
                damage = DamageRecord(
                    project_id=project_id,
                    type=line.type,
                    item_name=line.item_name,
                    quantity=line.quantity,
                    reported_at=now,
                    note=line.note,
                )
                self.damaged.append(damage)
                new_damage.append(damage)

        req = self.all_requests.get(project_id)
        if req is not None:
            req.status = RequestStatus.RETURNED

        self.recheck_pending()
        return new_damage

    @staticmethod
    def _validate_return_matches_borrowed(
        record: BorrowedRecord, return_items: list[ReturnLineItem]
    ) -> None:
        borrowed_totals: dict[tuple[str, str], int] = {}
        for line in record.items:
            key = (line.type, line.item_name)
            borrowed_totals[key] = borrowed_totals.get(key, 0) + line.quantity

        returned_totals: dict[tuple[str, str], int] = {}
        for line in return_items:
            key = (line.type, line.item_name)
            returned_totals[key] = returned_totals.get(key, 0) + line.quantity

        if borrowed_totals != returned_totals:
            raise ValueError(
                f"return for {record.project_id} does not match what was "
                f"borrowed: borrowed={borrowed_totals} returned={returned_totals}"
            )

    def recheck_pending(self) -> None:
        """Re-run every Pending project against current stock, in
        priority order, after a return frees up inventory. Items that
        still can't be fully satisfied go back onto a fresh Pending
        heap (draining and refilling the same heap in place would risk
        re-popping an item we just re-pushed within this same pass)."""
        still_pending_snapshot = self.pending_heap.to_list()
        self.pending_heap = MinHeap(_heap_key, _project_id)
        ordered = merge_sort(still_pending_snapshot, key_func=_heap_key)
        for req in ordered:
            self._try_reserve_or_pend(req)

    # -- admin view ----------------------------------------------------

    def admin_ordered_view(self) -> list[ProjectRequest]:
        """Every known request, merge-sorted by (pick_up_date,
        submitted_at) -- the stable O(n log n) admin priority view."""
        return merge_sort(list(self.all_requests.values()), key_func=_heap_key)
