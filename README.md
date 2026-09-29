# RAI Student Project Item Allocator (IFP)

> "Priorities always come first"
> KMITL Robotics and AI Engineering (RAI) — data structures & algorithms course project
> Team ROW: Thiradet Kurdsup, Sunhanat Panasjaroen, Siraphop William Wakeling

A web app that replaces the manual process RAI students use to request electronic
components and tools. Students submit a project request; the system prioritizes
requests by pick-up date, checks and reserves stock, tracks borrowed items and
returns, tracks damaged items, and gives the admin a dashboard.

This is a DSA course project: the core structures — a min-heap, a hash table with
chaining, a singly linked list, binary search, and merge sort — are all
hand-implemented in [`ds/`](ds/) and [`algo/`](algo/), framework-free. Built-ins
(`heapq`, `dict`, `sorted()`) are used only inside `tests/` as a correctness
oracle to check the hand-implemented versions against.

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

## Running the web app

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 — it redirects to `/login`, where you pick **Student**
or **Admin** (a cookie remembers the choice; there's no real authentication, per
the course scope). On first run it seeds the ~200-item catalog from
[`data/inventory_seed.csv`](data/inventory_seed.csv) into `data/app.db` (SQLite);
on every later run it rebuilds the in-memory heaps/hash tables/linked list from
that database. Delete `data/app.db` to reset to a fresh seeded state.

Student flow: **New Request** → search for components (binary search over the
sorted catalog) → add items → submit. The request is reserved immediately if
stock allows, or queued as Pending otherwise, and the student can check status
at the URL shown (`/requests/<Project ID>`).

Admin flow: **Borrowed** to confirm a handover (moves Reserved → Borrowed,
reduces live stock) or release an unclaimed reservation; **Returns** to search a
Project ID and record each item's returned quantity and condition (good stock is
restocked, damaged stock is logged and never reused, and any now-satisfiable
Pending requests are automatically promoted); **Admin View** for the full
merge-sort priority listing; **Damaged Items** for the append-only damage log.

### Email notifications

Console/log fallback by default (prints `[NOTIFY] ...` lines to the terminal
running uvicorn). To send real email instead, set:

```bash
export RAI_SMTP_HOST=smtp.example.com
export RAI_SMTP_PORT=587            # optional, defaults to 587
export RAI_SMTP_USERNAME=...        # optional
export RAI_SMTP_PASSWORD=...        # optional
export RAI_SMTP_FROM=rai@kmitl.ac.th   # optional, defaults to username
export RAI_SMTP_USE_TLS=false       # optional, defaults to true
```

## CLI demo (no web server)

```bash
python cli_demo.py
```

Walks through the borrow/return workflow end-to-end in the terminal: loads the
seeded inventory, submits three requests (two of which compete for the same
scarce item, resolved by pick-up date then submission-time tie-break), drains
the Main Min-Heap, shows the Reserved/Pending split and the merge-sorted admin
view, confirms a handover, then processes a return (one good, one damaged) and
shows the previously-Pending request get satisfied.

## Tests

```bash
pytest
```

105 tests across `tests/`: heap ordering/tie-break/delete-by-id/build,
hash table collisions/resize/randomized-vs-`dict` oracle, linked list,
binary search hits/misses/edges, merge sort stability, the inventory
catalog, the full borrow/return allocator workflow (including a pending
project getting satisfied after a return, and damaged items never
re-entering stock), SQLite persistence and startup rebuild, email
notifications, and FastAPI route tests via `TestClient`.

## Benchmarks

```bash
python -m benchmarks.run_benchmarks
```

Reproduces the four complexity comparisons from the project brief, counting
real operations (comparisons / array shifts / hash probes) rather than just
wall-clock time — see [`benchmarks/counters.py`](benchmarks/counters.py) for
how (a value wrapper that ticks a shared counter on every comparison, so the
*actual* `ds/`/`algo/` code gets measured with no instrumentation added to the
graded algorithms themselves). Prints a table and saves a bar chart per
comparison to `benchmarks/output/` (git-ignored, regenerated each run):

1. **Min-Heap vs unsorted array vs sorted array**, n=75 — insert cost and
   find-highest-priority cost for each.
2. **Hash Table vs array/linked-list lookup**, m=200.
3. **Binary Search vs Linear Search**, m=200.
4. **Merge Sort vs Bubble/Selection/Insertion/Quick Sort**, n=75, random input.

## Project layout

```
ds/                  hand-implemented data structures (no framework deps)
  heap.py              MinHeap: array-backed binary min-heap + O(log n) delete-by-id
  hashtable.py         HashTable: separate chaining, FNV-1a hash, load-factor resize
  linkedlist.py        SinglyLinkedList: O(1) append, O(n) traverse
algo/                hand-implemented algorithms (no framework deps)
  binary_search.py     binary_search_exact / lower_bound / upper_bound / prefix_search
  merge_sort.py         stable O(n log n) merge sort
app/                 the application built on top of ds/ and algo/
  models.py             plain dataclasses (InventoryItem, ProjectRequest, ...)
  inventory.py          InventoryCatalog: hash-table + sorted-array views of stock
  allocator.py           Allocator: the borrow/return workflow (section 6 of the brief)
  notifications.py       Notifier interface: console fallback + SMTP
  db.py                  SQLite persistence: write-through + rebuild-on-startup
  main.py                FastAPI app and routes
  templates/, static/    Jinja2 + HTMX UI
benchmarks/          operation-counting benchmarks + charts (section 11)
tests/               pytest suite (105 tests)
data/                inventory_seed.csv (~200 items) and app.db (git-ignored)
cli_demo.py          terminal walkthrough of the borrow/return workflow
```

See [`DECISIONS.md`](DECISIONS.md) for choices that fill in the brief's open
questions or otherwise deviate from a literal reading of it.
