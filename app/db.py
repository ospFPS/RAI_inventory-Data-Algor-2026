"""SQLite persistence (section 10 of the brief): the hand-implemented
ds/ structures (heap, hash table, linked list) are the in-memory working
structures used for every algorithmic operation; SQLite is only the
durable copy they are rebuilt from on startup and written through to on
every change, so the app survives a restart without re-deriving state
from anywhere else.
"""

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

from app.models import (
    BorrowedRecord,
    DamageRecord,
    InventoryItem,
    ProjectRequest,
    RequestLineItem,
    RequestStatus,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS inventory_items (
    type TEXT NOT NULL,
    item_name TEXT NOT NULL,
    live_qty INTEGER NOT NULL,
    reserved_qty INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (type, item_name)
);

CREATE TABLE IF NOT EXISTS requests (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    student_name TEXT NOT NULL,
    group_name TEXT NOT NULL,
    pick_up_date TEXT NOT NULL,
    submitted_at TEXT NOT NULL,
    status TEXT NOT NULL,
    student_email TEXT NOT NULL DEFAULT '',
    pending_reason TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS request_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL REFERENCES requests(project_id),
    type TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_request_items_project ON request_items(project_id);

CREATE TABLE IF NOT EXISTS borrowed (
    project_id TEXT PRIMARY KEY REFERENCES requests(project_id),
    handed_over_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS damage_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    type TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    reported_at TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS next_sequence (
    name TEXT PRIMARY KEY,
    value INTEGER NOT NULL
);
"""


class Database:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    @contextmanager
    def _cursor(self):
        cur = self._conn.cursor()
        try:
            yield cur
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()

    # -- inventory -------------------------------------------------------

    def save_inventory_item(self, item: InventoryItem) -> None:
        with self._cursor() as cur:
            cur.execute(
                """INSERT INTO inventory_items (type, item_name, live_qty, reserved_qty)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(type, item_name) DO UPDATE SET
                       live_qty = excluded.live_qty,
                       reserved_qty = excluded.reserved_qty""",
                (item.type, item.item_name, item.live_qty, item.reserved_qty),
            )

    def save_inventory_items(self, items: list[InventoryItem]) -> None:
        with self._cursor() as cur:
            cur.executemany(
                """INSERT INTO inventory_items (type, item_name, live_qty, reserved_qty)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(type, item_name) DO UPDATE SET
                       live_qty = excluded.live_qty,
                       reserved_qty = excluded.reserved_qty""",
                [(i.type, i.item_name, i.live_qty, i.reserved_qty) for i in items],
            )

    def load_inventory_items(self) -> list[InventoryItem]:
        rows = self._conn.execute(
            "SELECT type, item_name, live_qty, reserved_qty FROM inventory_items"
        ).fetchall()
        return [
            InventoryItem(r["type"], r["item_name"], r["live_qty"], r["reserved_qty"])
            for r in rows
        ]

    # -- requests ----------------------------------------------------------

    def save_request(self, req: ProjectRequest) -> None:
        with self._cursor() as cur:
            cur.execute(
                """INSERT INTO requests
                       (project_id, project_name, student_name, group_name,
                        pick_up_date, submitted_at, status, student_email, pending_reason)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(project_id) DO UPDATE SET
                       status = excluded.status,
                       pending_reason = excluded.pending_reason""",
                (
                    req.project_id,
                    req.project_name,
                    req.student_name,
                    req.group,
                    req.pick_up_date.isoformat(),
                    req.submitted_at.isoformat(),
                    req.status.value,
                    req.student_email,
                    req.pending_reason,
                ),
            )
            cur.execute("DELETE FROM request_items WHERE project_id = ?", (req.project_id,))
            cur.executemany(
                "INSERT INTO request_items (project_id, type, item_name, quantity) VALUES (?, ?, ?, ?)",
                [(req.project_id, i.type, i.item_name, i.quantity) for i in req.items],
            )

    def save_request_status(self, req: ProjectRequest) -> None:
        """Cheaper than save_request() when only status/pending_reason
        changed and the line items are unchanged."""
        with self._cursor() as cur:
            cur.execute(
                "UPDATE requests SET status = ?, pending_reason = ? WHERE project_id = ?",
                (req.status.value, req.pending_reason, req.project_id),
            )

    def load_requests(self) -> list[ProjectRequest]:
        rows = self._conn.execute(
            """SELECT project_id, project_name, student_name, group_name, pick_up_date,
                      submitted_at, status, student_email, pending_reason
               FROM requests"""
        ).fetchall()
        item_rows = self._conn.execute(
            "SELECT project_id, type, item_name, quantity FROM request_items"
        ).fetchall()
        items_by_project: dict[str, list[RequestLineItem]] = {}
        for r in item_rows:
            items_by_project.setdefault(r["project_id"], []).append(
                RequestLineItem(r["type"], r["item_name"], r["quantity"])
            )
        requests = []
        for r in rows:
            requests.append(
                ProjectRequest(
                    project_id=r["project_id"],
                    project_name=r["project_name"],
                    student_name=r["student_name"],
                    group=r["group_name"],
                    pick_up_date=date.fromisoformat(r["pick_up_date"]),
                    submitted_at=datetime.fromisoformat(r["submitted_at"]),
                    items=items_by_project.get(r["project_id"], []),
                    status=RequestStatus(r["status"]),
                    student_email=r["student_email"],
                    pending_reason=r["pending_reason"],
                )
            )
        return requests

    # -- borrowed ------------------------------------------------------

    def save_borrowed(self, record: BorrowedRecord) -> None:
        with self._cursor() as cur:
            cur.execute(
                """INSERT INTO borrowed (project_id, handed_over_at) VALUES (?, ?)
                   ON CONFLICT(project_id) DO UPDATE SET handed_over_at = excluded.handed_over_at""",
                (record.project_id, record.handed_over_at.isoformat()),
            )

    def delete_borrowed(self, project_id: str) -> None:
        with self._cursor() as cur:
            cur.execute("DELETE FROM borrowed WHERE project_id = ?", (project_id,))

    def load_borrowed(self) -> list[BorrowedRecord]:
        rows = self._conn.execute(
            """SELECT b.project_id, b.handed_over_at, r.project_name, r.group_name
               FROM borrowed b JOIN requests r ON r.project_id = b.project_id"""
        ).fetchall()
        item_rows = self._conn.execute(
            "SELECT project_id, type, item_name, quantity FROM request_items"
        ).fetchall()
        items_by_project: dict[str, list[RequestLineItem]] = {}
        for r in item_rows:
            items_by_project.setdefault(r["project_id"], []).append(
                RequestLineItem(r["type"], r["item_name"], r["quantity"])
            )
        return [
            BorrowedRecord(
                project_id=r["project_id"],
                project_name=r["project_name"],
                group=r["group_name"],
                items=items_by_project.get(r["project_id"], []),
                handed_over_at=datetime.fromisoformat(r["handed_over_at"]),
            )
            for r in rows
        ]

    # -- damage ----------------------------------------------------------

    def save_damage(self, record: DamageRecord) -> None:
        with self._cursor() as cur:
            cur.execute(
                """INSERT INTO damage_records
                       (project_id, type, item_name, quantity, reported_at, note)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    record.project_id,
                    record.type,
                    record.item_name,
                    record.quantity,
                    record.reported_at.isoformat(),
                    record.note,
                ),
            )

    def load_damage(self) -> list[DamageRecord]:
        rows = self._conn.execute(
            """SELECT project_id, type, item_name, quantity, reported_at, note
               FROM damage_records ORDER BY id ASC"""
        ).fetchall()
        return [
            DamageRecord(
                project_id=r["project_id"],
                type=r["type"],
                item_name=r["item_name"],
                quantity=r["quantity"],
                reported_at=datetime.fromisoformat(r["reported_at"]),
                note=r["note"],
            )
            for r in rows
        ]

    # -- sequence counter (Project ID generator) --------------------------

    def load_next_sequence(self) -> int:
        row = self._conn.execute(
            "SELECT value FROM next_sequence WHERE name = 'project_id'"
        ).fetchone()
        return row["value"] if row else 1

    def save_next_sequence(self, value: int) -> None:
        with self._cursor() as cur:
            cur.execute(
                """INSERT INTO next_sequence (name, value) VALUES ('project_id', ?)
                   ON CONFLICT(name) DO UPDATE SET value = excluded.value""",
                (value,),
            )
