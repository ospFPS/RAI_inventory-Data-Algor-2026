"""Inventory catalog: the live/reserved/available quantities for every
RAI component, plus the two lookup paths the brief calls for:

  * O(1) average-case exact lookup by (type, item_name) via the
    hand-implemented HashTable -- used during the borrow/return workflow
    to check and adjust stock (section 6 of the brief).
  * O(log m) lookup via hand-implemented binary search over an array kept
    sorted by (type, item_name) -- used for the component search box
    while a student is building a request (section 5).

The catalog keeps both views in sync: every mutation (CSV import, single
item add) updates the hash table, then rebuilds the sorted array. The
rebuild itself uses merge_sort (also hand-implemented) rather than
Python's sorted(), and is O(m log m); it only runs on catalog changes,
not on every lookup.
"""

import csv
from pathlib import Path

from algo.binary_search import binary_search_exact, lower_bound, upper_bound
from algo.merge_sort import merge_sort
from ds.hashtable import HashTable
from app.models import InventoryItem


class InventoryCatalog:
    def __init__(self):
        self._table: HashTable[tuple[str, str], InventoryItem] = HashTable()
        self._sorted: list[InventoryItem] = []
        # type -> (start, end) half-open slice into self._sorted, so a
        # name-prefix search only has to binary-search within one type's
        # run instead of the whole array.
        self._type_ranges: dict[str, tuple[int, int]] = {}

    def __len__(self) -> int:
        return len(self._table)

    def all_items(self) -> list[InventoryItem]:
        return list(self._sorted)

    def types(self) -> list[str]:
        return sorted(self._type_ranges.keys())

    # -- mutation ----------------------------------------------------

    def upsert(self, item: InventoryItem) -> None:
        """Insert or replace an item, then re-sort. O(m log m); intended
        for bulk loads (see load_csv) or infrequent single edits, not the
        hot borrow/return path (that goes through get/adjust below)."""
        self._table.put(item.key, item)
        self._rebuild_sorted()

    def load_csv(self, path: str | Path, replace: bool = True) -> int:
        """Load rows of type,item_name,live_qty from a CSV file.

        Returns the number of rows loaded. With replace=True (default)
        this clears any existing catalog first, matching the "seeded
        CSV" default from section 13 of the brief.
        """
        if replace:
            self._table = HashTable()
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                item = InventoryItem(
                    type=row["type"].strip(),
                    item_name=row["item_name"].strip(),
                    live_qty=int(row["live_qty"]),
                    reserved_qty=int(row.get("reserved_qty") or 0),
                )
                self._table.put(item.key, item)
                count += 1
        self._rebuild_sorted()
        return count

    # -- exact lookup (hash table, O(1) average) ----------------------

    def get(self, type_: str, item_name: str) -> InventoryItem | None:
        return self._table.get((type_, item_name))

    def reserve(self, type_: str, item_name: str, qty: int) -> None:
        """Mark qty as reserved (available -= qty, live unchanged)."""
        item = self._require(type_, item_name)
        item.reserved_qty += qty

    def release_reservation(self, type_: str, item_name: str, qty: int) -> None:
        """Undo a reservation without touching live stock (available += qty)."""
        item = self._require(type_, item_name)
        item.reserved_qty = max(0, item.reserved_qty - qty)

    def issue(self, type_: str, item_name: str, qty: int) -> None:
        """Handover confirmed: live -= qty, and the matching reservation
        is cleared (it's no longer "reserved", it's gone from the shelf)."""
        item = self._require(type_, item_name)
        item.live_qty -= qty
        item.reserved_qty = max(0, item.reserved_qty - qty)

    def restock_good(self, type_: str, item_name: str, qty: int) -> None:
        """A good-condition return: back into live (and thus available)."""
        item = self._require(type_, item_name)
        item.live_qty += qty

    def _require(self, type_: str, item_name: str) -> InventoryItem:
        item = self._table.get((type_, item_name))
        if item is None:
            raise KeyError(f"no such inventory item: {type_}/{item_name}")
        return item

    # -- binary search lookup (sorted array, O(log m)) -----------------

    def find_exact(self, type_: str, item_name: str) -> InventoryItem | None:
        """Same result as get(), but demonstrates the binary-search path
        explicitly (used by tests/benchmarks to compare against the hash
        table and a naive linear scan)."""
        idx = binary_search_exact(self._sorted, (type_, item_name), key_func=lambda i: i.key)
        return None if idx == -1 else self._sorted[idx]

    def search_by_name_prefix(
        self, prefix: str, type_: str | None = None
    ) -> list[InventoryItem]:
        """Items whose item_name starts with prefix (case-insensitive).

        If type_ is given, searches only that type's contiguous run in
        O(log(m/t)). Otherwise searches every type's run in turn --
        O(t * log(m/t) + k) for t types and k matches, still far cheaper
        than an O(m) linear scan across the whole catalog for the
        m ~= 200 items in scope here.
        """
        prefix_lower = prefix.strip().lower()
        ranges = (
            [self._type_ranges[type_]] if type_ else list(self._type_ranges.values())
        )
        results: list[InventoryItem] = []
        for start, end in ranges:
            segment = self._sorted[start:end]
            if prefix_lower == "":
                results.extend(segment)
                continue
            lo = lower_bound(segment, prefix_lower, key_func=lambda i: i.item_name.lower())
            hi = upper_bound(
                segment, prefix_lower + "￿", key_func=lambda i: i.item_name.lower()
            )
            results.extend(segment[lo:hi])
        return results

    # -- internal ------------------------------------------------------

    def _rebuild_sorted(self) -> None:
        self._sorted = merge_sort(list(self._table.values()), key_func=lambda i: i.key)
        self._type_ranges = {}
        start = 0
        for i in range(1, len(self._sorted) + 1):
            at_end = i == len(self._sorted)
            if at_end or self._sorted[i].type != self._sorted[start].type:
                self._type_ranges[self._sorted[start].type] = (start, i)
                start = i
