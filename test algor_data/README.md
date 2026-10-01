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
