from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


class ItemStatus(str, Enum):
    AVAILABLE = "Available"
    OUT_OF_STOCK = "Out of Stock"


@dataclass
class InventoryItem:
    type: str
    item_name: str
    live_qty: int
    reserved_qty: int = 0

    @property
    def available_qty(self) -> int:
        return self.live_qty - self.reserved_qty

    @property
    def status(self) -> ItemStatus:
        if self.available_qty <= 0:
            return ItemStatus.OUT_OF_STOCK
        return ItemStatus.AVAILABLE

    @property
    def key(self) -> tuple[str, str]:
        return (self.type, self.item_name)


@dataclass
class RequestLineItem:

    type: str
    item_name: str
    quantity: int


class RequestStatus(str, Enum):
    RESERVED = "Reserved"
    PENDING = "Pending"
    BORROWED = "Borrowed"
    RETURNED = "Returned"


@dataclass
class ProjectRequest:
    project_id: str
    project_name: str
    student_name: str
    group: str
    pick_up_date: date
    submitted_at: datetime
    items: list[RequestLineItem] = field(default_factory=list)
    status: RequestStatus = RequestStatus.PENDING
    student_email: str = ""
    student_id: str = ""
    pending_reason: str = ""

    @property
    def heap_key(self) -> tuple[date, datetime]:
        return (self.pick_up_date, self.submitted_at)


class ItemCondition(str, Enum):
    GOOD = "Good"
    DAMAGED = "Damaged"


@dataclass
class BorrowedRecord:
    project_id: str
    project_name: str
    group: str
    items: list[RequestLineItem]
    handed_over_at: datetime
    student_name: str = ""
    student_id: str = ""


@dataclass
class ReturnLineItem:

    type: str
    item_name: str
    quantity: int
    condition: ItemCondition
    note: str = ""


@dataclass
class DamageRecord:
    project_id: str
    type: str
    item_name: str
    quantity: int
    reported_at: datetime
    note: str = ""
