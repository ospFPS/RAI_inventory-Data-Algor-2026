"""Plain domain dataclasses shared across the inventory, allocator, and
web layers. No framework dependencies here on purpose -- these mirror the
SQLite schema and are what the hand-implemented ds/ structures store.
"""

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
        # We only classify states the real inventory data can determine
        # objectively. A positive quantity is Available; zero is Out of Stock.
        if self.available_qty <= 0:
            return ItemStatus.OUT_OF_STOCK
        return ItemStatus.AVAILABLE

    @property
    def key(self) -> tuple[str, str]:
        """Hash table / binary search key: (type, item_name)."""
        return (self.type, self.item_name)


@dataclass
class RequestLineItem:
    """One requested component/tool line within a ProjectRequest."""

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
        """(pick_up_date, submitted_at) -- earliest date wins; ties broken
        by earlier submission time, per section 5/13 of the brief."""
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
    """One line of a return: how much of one borrowed item came back in
    a given condition. A single borrowed item can be split across two
    ReturnLineItems (e.g. 3 good + 2 damaged out of 5 borrowed)."""

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
