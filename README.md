# RAI Student Project Item Allocator (IFP)

> "Priorities always come first"
>
> KMITL Robotics and AI Engineering (RAI) - Data Structures & Algorithms project

A web application for RAI student project component and tool requests. Students search the real inventory, submit a project request, and check request status. The backend prioritizes projects, checks stock, handles admin approval, reservation, borrowing, returns, damaged items, and persistent storage.

## Current Project Structure

```text
RAI_inventory/
|
|-- frontend/
|   |-- templates/                 Jinja2/HTMX pages
|   `-- static/                    CSS and images
|
|-- backend/
|   |-- main.py                    FastAPI routes
|   |-- allocator.py               request / reserve / borrow / return workflow
|   |-- inventory.py               inventory operations and search
|   |-- models.py                  domain models
|   |-- notifications.py           console / SMTP notifications
|   |
|   |-- algor/
|   |   |-- binary_search.py       Binary Search
|   |   `-- merge_sort.py          Merge Sort
|   |
|   |-- data_struct/
|   |   |-- min_heap.py            Main + Pending Min-Heap
|   |   |-- hash_table.py          separate-chaining Hash Table
|   |   `-- linked_list.py         damage Singly Linked List
|   |
|   `-- db/
|       |-- database.py            SQLite persistence
|       |-- app.db                 application database
|       `-- Database_inven_RAI.xlsx real RAI inventory source
|
|-- test algor_data/               manual proof/demo versions of all required DSA
|-- requirement.md                 project requirement + implementation update
|-- DECISIONS.md                   implementation decisions
|-- pyproject.toml                 project configuration
|-- requirements.txt               Python dependencies
`-- README.md                      this file
```

## Required Data Structures and Algorithms

### Data Structures

1. **Min-Heap**
   - Main request queue.
   - Pending request queue.
   - Earlier pickup date has higher priority.
   - Same pickup date uses earlier submission/request order.

2. **Hash Table**
   - Inventory lookup.
   - Reserved project lookup.
   - Borrowed project lookup.
   - All-request lookup by Project ID.

3. **Singly Linked List**
   - Stores damaged returned-item records.

### Algorithms

1. **Binary Search**
   - Searches the sorted inventory catalog.

2. **Merge Sort**
   - Creates ordered project/admin views.
   - Also rebuilds the sorted inventory view without using Python `sorted()`.

## Backend Workflow

```text
Student
  |
  v
Search inventory
  |
  v
Binary Search
  |
  v
Submit request
  |
  v
Main Min-Heap
  |
  v
Inventory check using Hash Table
  |
  v
Pending Min-Heap
  |
  v
Admin selects highest-priority fulfillable request
  |
  v
Approve and reserve inventory
  |
  v
RESERVED
  |
  v
Student collects items
  |
  v
Reduce live stock
  |
  v
Borrowed Hash Table
  |
  v
Return
  |-----------------------|
  v                       v
Good                    Damaged
  |                       |
  v                       v
Increase inventory     Singly Linked List
  |                       |
  `-----------+-----------'
              |
              v
      Re-check Pending Heap
```

The admin ordered project view uses **Merge Sort**.

## Priority Rule

Requests are prioritized by:

1. Earlier requested pickup date.
2. If pickup dates are equal, earlier submission time/request order.

A higher-priority request that does not currently have enough stock stays Pending. The system can continue to the next highest-priority request that can actually be fulfilled.

## Database

The application uses SQLite for persistent storage:

```text
backend/db/app.db
```

The real RAI inventory source is:

```text
backend/db/Database_inven_RAI.xlsx
```

SQLite stores persistent state. On startup, the application rebuilds its working Min-Heaps, Hash Tables, and Singly Linked List from the stored data.

## Setup

From the repository root:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Or install the project and development dependencies with:

```bash
pip install -e ".[dev]"
```

## Run the Website

From the repository root:

```bash
uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Manual DSA Proof

The `test algor_data/` folder contains simple manual implementations that are easy to run and explain during presentation.

```text
test algor_data/
|-- Algorithms/
|   |-- min_heaps.py
|   |-- binary_search.py
|   `-- merge_sort.py
|-- Data_Structure/
|   |-- hashtable.py
|   `-- linked_list.py
`-- Models/
```

The production versions in `backend/algor/` and `backend/data_struct/` use the same core approach, but remove the manual `input()`, `print()`, and mock test data.

## Important Files

- `requirement.md` - original project requirement plus a current implementation mapping.
- `DECISIONS.md` - explains implementation choices and deviations.
- `test algor_data/README.md` - complete system architecture diagram for the DSA workflow.
