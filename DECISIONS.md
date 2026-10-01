# Decisions

This file records implementation decisions for the current `frontend/` + `backend/` architecture and explains where the implementation adds detail beyond the original requirement.

## 1. Application Stack

The project uses:

- **FastAPI** for the web backend/routes.
- **Jinja2 + HTMX-style server-rendered pages** for the frontend.
- **SQLite** for persistent storage.
- **openpyxl** to read the real RAI inventory workbook.

The project is intentionally kept as one Python application so the required Data Structures and Algorithms remain easy to inspect and explain.

## 2. Frontend / Backend Split

The repository is now organized as:

```text
frontend/
  templates/
  static/

backend/
  main.py
  allocator.py
  inventory.py
  models.py
  notifications.py
  algor/
  data_struct/
  db/
```

The old top-level `app/`, `algo/`, `ds/`, `data/`, and `benchmarks/` folders were removed after the new structure was verified.

## 3. DSA Source of Truth

The simple manual implementations in `test algor_data/` are the proof/demo versions used to show how each required structure and algorithm works.

The production files use the same core logic, with manual test code removed:

```text
test algor_data/Algorithms/min_heaps.py
    -> backend/data_struct/min_heap.py

test algor_data/Data_Structure/hashtable.py
    -> backend/data_struct/hash_table.py

test algor_data/Data_Structure/linked_list.py
    -> backend/data_struct/linked_list.py

test algor_data/Algorithms/binary_search.py
    -> backend/algor/binary_search.py

test algor_data/Algorithms/merge_sort.py
    -> backend/algor/merge_sort.py
```

The website does not import the manual test scripts directly because those scripts contain `input()`, `print()`, and mock data.

## 4. Priority Rule

Project priority is:

1. Earlier requested pickup date.
2. If pickup dates are equal, earlier submission/request order.

This rule is used by the Main Min-Heap and Pending Min-Heap.

## 5. Main and Pending Min-Heaps

Every new request enters the Main Min-Heap first.

The Main Min-Heap processes requests in priority order and performs an inventory readiness check. Requests then move to the Pending Min-Heap for admin handling.

When the admin views Pending requests, the backend checks them in priority order and identifies the highest-priority request that currently has enough stock.

A higher-priority request that is short on stock remains Pending; a lower-priority request may proceed only if it is the highest-priority request that can actually be fulfilled.

## 6. Admin Approval Is the Reservation Gate

The current website requires admin approval before stock is reserved.

Therefore:

```text
Submit
  -> Main Min-Heap
  -> Pending Min-Heap
  -> Admin approval
  -> Reserved
  -> Handover
  -> Borrowed
```

This is an implementation decision added to make physical stock control safer and easier to demonstrate. The original requirement describes automatic reservation more directly; the current application adds explicit admin approval before reservation.

## 7. Reservation Is All-or-Nothing

A project is only approved when all requested item quantities are available.

The system does not partially reserve a request. If any required item is short, the project remains Pending.

## 8. Min-Heap Implementation

`backend/data_struct/min_heap.py` uses an array-backed binary Min-Heap with the same straightforward logic demonstrated in the manual test version:

- `insert()`
- `_heapify_up()`
- `extract_min()`
- `remove_project()`
- `_heapify_down()`

`remove_project()` performs a linear search for the requested Project ID and then restores heap order. This is intentionally simpler and easier to explain than the previous position-map implementation.

## 9. Hash Table Implementation

`backend/data_struct/hash_table.py` uses **separate chaining**.

Each bucket stores linked `HashNode` objects:

```text
Bucket
  -> HashNode
  -> HashNode
  -> None
```

The hash function follows the same simple style as the manual test implementation:

```text
sum(ord(character) for character in str(key)) % table_size
```

The production table is generalized to store arbitrary `key -> value` pairs so the same structure can support:

- Inventory.
- Reserved projects.
- Borrowed projects.
- All requests.

## 10. Inventory Representation

Inventory records keep:

- Type.
- Item name.
- Live quantity.
- Reserved quantity.

Available quantity is:

```text
available = live_qty - reserved_qty
```

Exact workflow lookups use the custom Hash Table.

The student-facing search also keeps a sorted inventory list so Binary Search can be demonstrated and used.

## 11. Binary Search

`backend/algor/binary_search.py` contains the hand-written Binary Search logic used by inventory searching.

The code repeatedly divides the sorted search range in half using:

```text
middle = (left + right) // 2
```

The production file also contains lower/upper-bound helpers because the website supports prefix-style inventory search.

## 12. Merge Sort

`backend/algor/merge_sort.py` contains the hand-written recursive Merge Sort.

It is used for:

- Admin ordered project views.
- Sorted inventory rebuilding.
- Other ordered display lists where the application needs a deterministic order.

The application does not rely on Python `sorted()` for the required Merge Sort demonstration path.

## 13. Damaged Items

Damaged returns are not put back into usable stock.

They are appended to the custom Singly Linked List in:

```text
backend/data_struct/linked_list.py
```

Conceptually:

```text
HEAD -> DamageNode -> DamageNode -> NULL
```

A good return increases live inventory. A damaged return only creates a damage record.

## 14. Borrowed and Reserved Hash Tables

The original requirement directly calls for an Inventory Hash Table and Borrowed Hash Table.

The application also uses a Reserved Hash Table because there is a real workflow state between admin approval and physical handover.

Both are keyed by Project ID.

## 15. Return Is Processed Per Project

A return must account for exactly the quantities originally borrowed by that project before state is changed.

Returned units may be split into:

- Good quantity.
- Damaged quantity.

Good units return to inventory. Damaged units go to the Damage Linked List.

After a return, Pending requests are checked again because stock may now be available.

## 16. SQLite Persistence

SQLite is the durable copy of application state:

```text
backend/db/app.db
```

The custom Data Structures are the in-memory working structures. On application startup, the backend loads SQLite data and rebuilds:

- Pending Min-Heap.
- Reserved Hash Table.
- Borrowed Hash Table.
- All-request Hash Table.
- Damage Singly Linked List.

## 17. Real Inventory Source

The real inventory workbook is:

```text
backend/db/Database_inven_RAI.xlsx
```

The database currently contains the imported real inventory data.

## 18. Project IDs

Project IDs use a readable zero-padded sequence:

```text
P0001
P0002
P0003
```

The next sequence value is stored in SQLite so IDs continue correctly after restart.

## 19. Authentication Scope

The course/demo application uses two selectable roles:

- Student.
- Admin.

The role is stored using a simple cookie. This is not intended to be production-grade authentication.

## 20. Notifications

The backend supports:

- Console notifications for development/demo.
- SMTP notifications when email environment variables are configured.

The allocation workflow talks to the notifier interface rather than directly to SMTP.

## 21. Benchmarks Folder Removed

The old `benchmarks/` folder was removed during the architecture cleanup because the current project focus is the five required implementations plus the working web application.

The manual proof code remains in `test algor_data/`.
