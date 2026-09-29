# Decisions

Choices that fill in the brief's open questions (section 13) or otherwise
deviate from / add detail beyond a literal reading of it.

## Stack (section 10)
Confirmed with the team at the start: **FastAPI + SQLite + Jinja2/HTMX**
(not the React/Vite alternative also suggested in the brief) — one language,
simpler to build and demo, keeps the DSA logic front-and-center rather than
behind a JSON API split across two dev servers.

## Section 13 open questions — used the stated defaults
- Priority: pick-up date, then submission time (tie-break) only.
- Reservation is all-or-nothing; a request with *any* short item goes
  entirely to Pending — nothing is partially reserved.
- An uncollected reservation is released manually by the admin (no
  automatic expiry).
- Inventory source is the seeded CSV (`data/inventory_seed.csv`).
- Auth is two hard-coded roles (Student/Admin) selectable at login, via a
  plain cookie — no passwords, no real session security. Admin-only
  mutations (confirm handover, release reservation, process return) are
  enforced server-side (403 for students), not just hidden in the UI.

## A third hash table for "Reserved, awaiting handover"
The brief names a Main heap, a Pending heap, an Inventory hash table, and a
Borrowed hash table, but the borrow workflow (section 6.1) has a state in
between "reserved" and "handed over" that needs to be listed and searched
by the admin before confirming pickup. Rather than inventing a sixth
structure, `Allocator.reserved` reuses the same hand-implemented
`HashTable`, keyed by Project ID — the same pattern as `borrowed`.

## Return is all-at-once per project
`process_return()` requires the returned line items to sum to *exactly*
what that project borrowed (validated before any state changes). The brief
describes a student physically returning items and the admin looking the
project up once in the Borrowed table (section 6.2); it doesn't describe a
partial/staged return spread across multiple confirmations, so we didn't
build one. A rejected return (quantity mismatch) leaves Borrowed state and
inventory untouched.

## Low-stock threshold and admin priority labels
Not specified anywhere in the brief. `InventoryItem.status` treats an item
as **Low Stock** once `available_qty <= max(2, live_qty * 0.2)` (see
`app/models.py`). The Admin View's High/Medium/Low priority badge is based
on days until pick-up: High `<= 1` day, Medium `<= 3` days, Low otherwise
(`app/main.py:priority_label`). Both are simple, documented, easy to change.

## Hash function
`ds/hashtable.py` uses a hand-rolled FNV-1a over `repr(key)`, not Python's
built-in `hash()` — the brief asks the structures to be hand-implemented
end to end, and a hash table built on the language's own hash function
would leave the one property (`comparisons/shifts/probes`, section 11)
that's actually being graded implemented by someone else.

## Baseline algorithms for the benchmarks (section 11) are not graded DSA
`benchmarks/baselines.py` has simple unsorted/sorted-array helpers and
bubble/selection/insertion/quicksort — these exist purely so the four
required comparisons have something to compare against, and are never used
by the app itself. `algo/` only contains the two algorithms the brief
actually requires (binary search, merge sort).

## Project ID format
`P0001`, `P0002`, ... — a zero-padded sequence counter persisted in SQLite
(`next_sequence` table) so IDs stay stable and readable across restarts,
well within the 50–75 request scope.
