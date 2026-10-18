# System Architecture

```text
                              STUDENT
                                 |
                                 V
                        Select Components
                                 |
                                 V
                          Binary Search
                        Search Inventory
                                 |
                                 V
                           Submit Request
                                 |
                                 V
                       -------------------
                       |   Main Min-Heap |
                       -------------------
                                 |
                                 V
                    Priority by Pickup Date
                    Same Date -> Request Order
                                 |
                                 V
                      Check Actual Inventory
                         using Hash Table
                                 |
                    -------------+-------------
                    |                           |
                    V                           V
               Enough Stock               Not Enough Stock
                    |                           |
                    |                           V
                    |                   -------------------
                    |                   | Pending Min-Heap|
                    |                   -------------------
                    |                           |
                    |                           |
                    +-------------+-------------+
                                  |
                                  V
                              ADMIN
                                  |
                                  V
                       Re-check Pending Heap
                                  |
                                  V
                  Highest-Priority Fulfillable
                              Project
                                  |
                                  V
                         Admin Approves
                                  |
                                  V
                        Reserve Inventory
                        using Hash Table
                                  |
                                  V
                       -------------------
                       |     RESERVED    |
                       -------------------
                                  |
                                  V
                       Student Collects Items
                                  |
                                  V
                         Reduce Live Stock
                                  |
                                  V
                        Borrowed Hash Table
                                  |
                                  V
                               RETURN
                                  |
                      ------------+------------
                      |                         |
                      V                         V
                 Good Condition           Damaged Condition
                      |                         |
                      V                         V
              Increase Inventory       Singly Linked List
                 Hash Table              Damage List
                      |                         |
                      +------------+------------+
                                   |
                                   V
                         Delete Project from
                         Borrowed Hash Table
                                   |
                                   V
                         Re-check Pending Heap
                                   |
                                   V
                    Newly Available Project?
                           /             \
                         Yes              No
                          |                |
                          V                V
                   Admin Can Approve    Stay Pending
```

## Admin Ordered Project View

```text
All Project Requests
        |
        V
    Merge Sort
        |
        V
Ordered by:
1. Pickup Date
2. Request Order / Submission Order
        |
        V
   Admin Dashboard
```

## Data Structures and Algorithms Used

```text
DATA STRUCTURES

1. Min-Heap
   - Main Min-Heap
   - Pending Min-Heap
   - Earlier pickup date = higher priority
   - Same pickup date = earlier request first

2. Hash Table
   - Inventory lookup
   - Inventory quantity / reservation
   - Borrowed projects
   - Search by Project ID
   - Delete returned project

3. Singly Linked List
   - Stores damaged returned items
   - HEAD -> Damage Node -> Damage Node -> NULL


ALGORITHMS

1. Binary Search
   - Search component/tool inventory
   - Inventory is searched from sorted item data

2. Merge Sort
   - Creates ordered project list for Admin
   - Sorts by pickup date and request order
```

## Full Workflow

```text
Student searches item
        |
        V
Binary Search
        |
        V
Submit Project Request
        |
        V
Main Min-Heap
        |
        V
Hash Table checks inventory
        |
        V
Pending Min-Heap / Ready for approval
        |
        V
Admin selects highest-priority fulfillable project
        |
        V
Reserve inventory
        |
        V
Student collects items
        |
        V
Borrowed Hash Table
        |
        V
Return items
   /          \
Good         Damaged
 |              |
 V              V
Inventory    Singly Linked List
   \          /
    \        /
     V      V
 Re-check Pending Min-Heap
        |
        V
 Continue allocation

Admin project list -> Merge Sort -> Ordered view
```

## Excel-backed Mock Data (Manual Algorithm Demos)

The standalone demos in this folder now build their **mock inventory in memory** from the real
`backend/db/Database_inven_RAI.xlsx` workbook, via `mock_data.py`. This loader reuses the
application's `InventoryCatalog.load_xlsx()` import logic, including the inventory quantities.
The workbook is read-only and the demos never access or modify `backend/db/app.db`.

- **Real from Excel:** Component/tool names, types, and starting stock quantities.
- **Mock only:** Student/project names, student IDs, requested amounts, damage events, and
  simulated stock replenishment. The demonstrations do not represent real student loans.
- **Binary Search:** Runs against all imported inventory records (not just a few examples).
- **Merge Sort, Min-Heaps, Hash Table, Linked List:** Use actual Excel item names; the
  inventory quantity demonstrations use values loaded from that workbook.

These standalone scripts are for explaining each algorithm/data structure. In particular,
`Algorithms/min_heaps.py` illustrates a simplified queue-and-stock simulation; the **live
website** separately requires an admin to approve reservations and confirm handover.

To run all verification tests from the repository root (Windows PowerShell):

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s "test algor_data" -p "test_*.py" -v
```

For the interactive search demonstration:

```powershell
.\.venv\Scripts\python.exe "test algor_data\Algorithms\binary_search.py"
```

Try `Tool` and `Screw driver set`, or any valid type/item name in the workbook.
