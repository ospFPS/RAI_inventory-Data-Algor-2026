"""Plain domain dataclasses shared across the inventory, allocator, and
web layers. No framework dependencies here on purpose -- these mirror the
SQLite schema and are what the hand-implemented ds/ structures store.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


class ItemStatus(str, Enum):
    AVAILABLE = "Available"
    LOW_STOCK = "Low Stock"
    OUT_OF_STOCK = "Out of Stock"


# An item counts as "low stock" once available_qty drops to or below this
# fraction of live_qty (with a floor, so small counts still warn early).
LOW_STOCK_RATIO = 0.2
LOW_STOCK_FLOOR = 2


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
        threshold = max(LOW_STOCK_FLOOR, int(self.live_qty * LOW_STOCK_RATIO))
        if self.available_qty <= threshold:
            return ItemStatus.LOW_STOCK
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


@dataclass
class DamageRecord:
    project_id: str
    type: str
    item_name: str
    quantity: int
    reported_at: datetime
    note: str = ""
