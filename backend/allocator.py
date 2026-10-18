from datetime import datetime

from backend.algor.merge_sort import merge_sort
from backend.db.database import Database
from backend.inventory import InventoryCatalog
from backend.models import (
    BorrowedRecord,
    DamageRecord,
    ItemCondition,
    ProjectRequest,
    RequestLineItem,
    RequestStatus,
    ReturnLineItem,
)
from backend.notifications import ConsoleNotifier, Notifier
from backend.data_struct.hash_table import HashTable
from backend.data_struct.min_heap import MinHeap
from backend.data_struct.linked_list import SinglyLinkedList


def _heap_key(req: ProjectRequest):
    return req.heap_key


def _project_id(req: ProjectRequest):
    return req.project_id


class Allocator:
    def __init__(
        self,
        catalog: InventoryCatalog,
        notifier: Notifier | None = None,
        db: Database | None = None,
    ):
        self.catalog = catalog
        self.notifier = notifier or ConsoleNotifier()
        self.db = db

        self.main_heap: MinHeap[ProjectRequest] = MinHeap(_heap_key, _project_id)
        self.pending_heap: MinHeap[ProjectRequest] = MinHeap(_heap_key, _project_id)
        self.reserved: HashTable[str, ProjectRequest] = HashTable()
        self.borrowed: HashTable[str, BorrowedRecord] = HashTable()
        self.damaged: SinglyLinkedList = SinglyLinkedList()
        self.all_requests: HashTable[str, ProjectRequest] = HashTable()

        self._next_seq = db.load_next_sequence() if db else 1

    @classmethod
    def from_db(cls, db: Database, notifier: Notifier | None = None) -> "Allocator":
        catalog = InventoryCatalog()
        catalog.bulk_load(db.load_inventory_items())
        allocator = cls(catalog, notifier=notifier, db=db)

        all_reqs = merge_sort(db.load_requests(), key_func=_project_id)
        for req in all_reqs:
            allocator.all_requests.insert(req.project_id, req)
            if req.status == RequestStatus.PENDING:
                allocator.pending_heap.insert(req)
            elif req.status == RequestStatus.RESERVED:
                allocator.reserved.insert(req.project_id, req)

        for record in db.load_borrowed():
            allocator.borrowed.insert(record.project_id, record)
        for damage in db.load_damage():
            allocator.damaged.append(damage)

        return allocator


    def _persist_item(self, type_: str, item_name: str) -> None:
        if self.db is None:
            return
        item = self.catalog.get(type_, item_name)
        if item is not None:
            self.db.save_inventory_item(item)

    def _persist_items(self, lines: list[RequestLineItem]) -> None:
        if self.db is None:
            return
        for line in lines:
            self._persist_item(line.type, line.item_name)


    def _generate_project_id(self) -> str:
        pid = f"P{self._next_seq:04d}"
        self._next_seq += 1
        if self.db is not None:
            self.db.save_next_sequence(self._next_seq)
        return pid

    def add_request(
        self,
        project_name: str,
        student_name: str,
        group: str,
        pick_up_date,
        items: list[RequestLineItem],
        student_email: str = "",
        student_id: str = "",
        submitted_at: datetime | None = None,
    ) -> ProjectRequest:
        req = ProjectRequest(
            project_id=self._generate_project_id(),
            project_name=project_name,
            student_name=student_name,
            group=group,
            pick_up_date=pick_up_date,
            submitted_at=submitted_at or datetime.now(),
            items=list(items),
            student_email=student_email,
            student_id=student_id,
        )
        self.all_requests.insert(req.project_id, req)
        self.main_heap.insert(req)
        if self.db is not None:
            self.db.save_request(req)
            self.db.log_activity(
                "REQUEST_SUBMITTED",
                req.project_id,
                f"{req.project_name} submitted by {req.student_name}"
                + (f" ({req.student_id})" if req.student_id else ""),
                event_at=req.submitted_at,
            )
        return req

    def submit_request(self, *args, **kwargs) -> ProjectRequest:
        req = self.add_request(*args, **kwargs)
        self.process_main_queue()
        return req


    def process_main_queue(self) -> None:
        while not self.main_heap.is_empty():
            req = self.main_heap.extract_min()
            shortages = self._find_shortages(req)
            req.status = RequestStatus.PENDING
            req.pending_reason = (
                "; ".join(shortages) if shortages else "Awaiting admin approval"
            )
            self.pending_heap.insert(req)
            if self.db is not None:
                self.db.save_request_status(req)
            if shortages:
                if self.db is not None:
                    self.db.log_activity(
                        "SHORTAGE_NOTICE",
                        req.project_id,
                        req.pending_reason,
                    )
                self.notifier.notify_pending(req)

    def _find_shortages(self, req: ProjectRequest) -> list[str]:
        totals: dict[tuple[str, str], int] = {}
        for line in req.items:
            key = (line.type, line.item_name)
            totals[key] = totals.get(key, 0) + line.quantity

        shortages = []
        for (type_, name), quantity in totals.items():
            item = self.catalog.get(type_, name)
            if item is None:
                shortages.append(f"{name}: not in catalog")
            elif item.available_qty < quantity:
                shortages.append(
                    f"{name}: need {quantity}, have {item.available_qty}"
                )
        return shortages

    def analyze_pending_priorities(
        self,
    ) -> tuple[ProjectRequest | None, list[tuple[ProjectRequest, list[str]]]]:
        if self.pending_heap.is_empty():
            return None, []

        work_heap = MinHeap.build(
            self.pending_heap.to_list(),
            key_func=_heap_key,
            id_func=_project_id,
        )
        analysis: list[tuple[ProjectRequest, list[str]]] = []
        recommended: ProjectRequest | None = None

        while not work_heap.is_empty():
            req = work_heap.extract_min()
            shortages = self._find_shortages(req)
            analysis.append((req, shortages))
            if recommended is None and not shortages:
                recommended = req

        return recommended, analysis

    def notify_stock_shortage(self, project_id: str) -> ProjectRequest:
        if project_id not in self.pending_heap:
            raise KeyError(f"project not in Pending state: {project_id}")

        req = self.all_requests.search(project_id)
        if req is None:
            raise KeyError(f"request not found: {project_id}")

        shortages = self._find_shortages(req)
        if not shortages:
            raise ValueError(f"project {project_id} currently has enough stock")

        req.pending_reason = "; ".join(shortages)
        if self.db is not None:
            self.db.save_request_status(req)
            self.db.log_activity(
                "SHORTAGE_NOTICE",
                req.project_id,
                req.pending_reason,
            )
        self.notifier.notify_pending(req)
        return req


    def approve_pending_request(self, project_id: str) -> ProjectRequest | None:
        if project_id not in self.pending_heap:
            raise KeyError(f"project not in Pending state: {project_id}")

        req = self.pending_heap.remove_project(project_id)
        shortages = self._find_shortages(req)
        if shortages:
            req.status = RequestStatus.PENDING
            req.pending_reason = "; ".join(shortages)
            self.pending_heap.insert(req)
            if self.db is not None:
                self.db.save_request_status(req)
            return None

        for line in req.items:
            self.catalog.reserve(line.type, line.item_name, line.quantity)
        req.status = RequestStatus.RESERVED
        req.pending_reason = ""
        self.reserved.insert(req.project_id, req)
        self._persist_items(req.items)
        if self.db is not None:
            self.db.save_request_status(req)
            self.db.log_activity(
                "RESERVATION_READY",
                req.project_id,
                f"{req.project_name}: approved by admin and reserved",
            )
        self.notifier.notify_ready(req)

        self.recheck_pending()
        return req

    def confirm_handover(self, project_id: str) -> BorrowedRecord:
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
            student_name=req.student_name,
            student_id=req.student_id,
        )
        self.borrowed.insert(project_id, record)
        req.status = RequestStatus.BORROWED
        self._persist_items(req.items)
        if self.db is not None:
            self.db.save_request_status(req)
            self.db.save_borrowed(record)
            total_units = sum(line.quantity for line in req.items)
            self.db.log_activity(
                "BORROW_CONFIRMED",
                req.project_id,
                f"{req.project_name}: {total_units} unit(s) across {len(req.items)} item type(s)",
                event_at=record.handed_over_at,
            )
        return record

    def release_reservation(self, project_id: str) -> ProjectRequest:
        if project_id not in self.reserved:
            raise KeyError(f"project not in Reserved state: {project_id}")
        req = self.reserved.delete(project_id)
        for line in req.items:
            self.catalog.release_reservation(line.type, line.item_name, line.quantity)
        req.status = RequestStatus.PENDING
        req.pending_reason = "Reservation manually released by admin"
        self.all_requests.insert(req.project_id, req)
        self.pending_heap.insert(req)
        self._persist_items(req.items)
        if self.db is not None:
            self.db.save_request_status(req)
        return req


    def process_return(
        self, project_id: str, return_items: list[ReturnLineItem]
    ) -> list[DamageRecord]:
        if project_id not in self.borrowed:
            raise KeyError(f"project not in Borrowed state: {project_id}")
        record = self.borrowed.search(project_id)
        self._validate_return_matches_borrowed(record, return_items)
        self.borrowed.delete(project_id)
        if self.db is not None:
            self.db.delete_borrowed(project_id)

        now = datetime.now()
        new_damage: list[DamageRecord] = []
        for line in return_items:
            if line.condition == ItemCondition.GOOD:
                self.catalog.restock_good(line.type, line.item_name, line.quantity)
                self._persist_item(line.type, line.item_name)
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
                if self.db is not None:
                    self.db.save_damage(damage)

        req = self.all_requests.search(project_id)
        if req is not None:
            req.status = RequestStatus.RETURNED
            if self.db is not None:
                self.db.save_request_status(req)

        if self.db is not None:
            good_units = sum(
                line.quantity for line in return_items if line.condition == ItemCondition.GOOD
            )
            damaged_units = sum(
                line.quantity for line in return_items if line.condition == ItemCondition.DAMAGED
            )
            self.db.log_activity(
                "RETURN_PROCESSED",
                project_id,
                f"Returned {good_units} good unit(s), {damaged_units} damaged unit(s)",
                event_at=now,
            )

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
        ordered = merge_sort(self.pending_heap.to_list(), key_func=_heap_key)
        for req in ordered:
            previous_reason = req.pending_reason
            shortages = self._find_shortages(req)
            req.pending_reason = (
                "; ".join(shortages) if shortages else "Awaiting admin approval"
            )
            if self.db is not None:
                self.db.save_request_status(req)

            if shortages and previous_reason == "Awaiting admin approval":
                if self.db is not None:
                    self.db.log_activity(
                        "SHORTAGE_NOTICE",
                        req.project_id,
                        req.pending_reason,
                    )
                self.notifier.notify_pending(req)


    def admin_ordered_view(self) -> list[ProjectRequest]:
        return merge_sort(list(self.all_requests.values()), key_func=_heap_key)


