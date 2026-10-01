# Current Implementation Update

This file contains the original project requirement together with the current implementation mapping for the reorganized repository.

## Current Architecture

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
    binary_search.py
    merge_sort.py

  data_struct/
    min_heap.py
    hash_table.py
    linked_list.py

  db/
    database.py
    app.db
    Database_inven_RAI.xlsx

test algor_data/
  manual proof/demo implementations
```

## Requirement-to-Code Mapping

| Requirement | Current implementation |
|---|---|
| Main Min-Heap | `backend/data_struct/min_heap.py` |
| Pending Min-Heap | `backend/data_struct/min_heap.py` |
| Inventory Hash Table | `backend/data_struct/hash_table.py` + `backend/inventory.py` |
| Borrowed Hash Table | `backend/data_struct/hash_table.py` + `backend/allocator.py` |
| Singly Linked List | `backend/data_struct/linked_list.py` |
| Binary Search | `backend/algor/binary_search.py` |
| Merge Sort | `backend/algor/merge_sort.py` |
| SQLite persistence | `backend/db/database.py` |
| Web routes | `backend/main.py` |
| Frontend | `frontend/templates/` + `frontend/static/` |

## Current Workflow Clarification

The current website adds an explicit **admin approval gate** before reservation:

```text
Student submits request
        |
        v
Main Min-Heap
        |
        v
Inventory readiness check
        |
        v
Pending Min-Heap
        |
        v
Admin selects highest-priority fulfillable request
        |
        v
Approve and reserve
        |
        v
Student collects
        |
        v
Borrowed Hash Table
        |
        v
Return
```

This keeps the original priority and inventory rules, but reservation is performed only after admin approval. This implementation choice is documented in `DECISIONS.md`.

The manual proof versions of all five required Data Structures and Algorithms are kept in `test algor_data/`.

---

# Original Project Requirement
# Data & Algorithm Mini Project

## Item Allocator for Student Projects

> **"(IFP) - Priorities always come first"**

---

## 1. Project Overview

### Project Name
**Item Allocator for Student Projects**

### Group
**Group ROW**

### Team Members

| Name | Student ID |
|---|---:|
| Thiradet Kurdsup | 68011516 |
| Sunhanat Panasjaroen | 68011526 |
| Siraphop William Wakeling | 68011571 |

### Main Idea

The project is a digital item allocation and inventory management system for RAI student projects.

The system is designed to replace manual project-component requests with a digital process that can:

- Receive project requests from students.
- Prioritize projects automatically.
- Search and check the inventory.
- Reserve available components.
- Move projects with unavailable items into a pending queue.
- Track borrowed components.
- Process returned components.
- Separate damaged components from usable inventory.
- Update inventory quantities automatically.
- Help administrators visualize and analyze project requests.

The main principle of the project is:

> **Priorities always come first.**

---

# 2. Problem

The current item-allocation process has several problems:

1. Allocating components and items for student projects is done manually.
2. Searching for items in the stock database is time-consuming.
3. The current system requires administrators to manually reduce stock quantities.
4. All student requests must be made by contacting the administrator directly.
5. The administrator must manually decide which student request should be handled first.

These processes create unnecessary manual work and can make inventory management slower and less consistent.

---

# 3. Proposed Solution

The proposed solution is a digital system that manages student component requests automatically.

The system will:

- Manage project requests digitally.
- Automatically prioritize projects.
- Check inventory availability.
- Reserve available items.
- Track borrowed items.
- Track returned items.
- Maintain a pending request queue.
- Update stock quantities.
- Separate damaged items.
- Provide useful information for administrators.

The goal is to make the overall item-request and inventory-management process more efficient.

---

# 4. Project Objectives

The project has four major objectives.

## 4.1 Organize Project Requirements

The system stores information related to each project, including:

- Project priority.
- Required components.
- Available resources.

This allows the system to understand what each project needs before allocating inventory.

---

## 4.2 Prioritize Projects Automatically

The system uses an algorithm to select the highest-priority project first.

The main priority criterion is:

- **Requested pick-up date**

If two projects have the same pick-up date, the earlier request receives higher priority.

---

## 4.3 Allocate Available Components

The system checks whether the requested components are available.

If enough stock is available, the system can:

- Reserve the components.
- Mark them as reserved.
- Inform the student.

If stock is unavailable, the request is moved to a pending list.

---

## 4.4 Generate Useful Results

The system provides useful information for administrators, including:

- Item readiness.
- Item shortages.
- Remaining stock.
- Borrowed items.
- Pending requests.
- Damaged items.

This information can help the administrator prepare items and analyze inventory status.

---

# 5. Project Scope

The project is designed for the RAI student environment.

The scope includes:

- Handling approximately **50โ€“75 project requests** from RAI students.
- Automatically prioritizing projects using the requested pick-up date.
- Checking requested components against the RAI inventory database.
- Providing a simple interface for students and administrators.
- Allowing users to add and view project requests.
- Allowing administrators to monitor inventory and project requests.

The project is intended as a university-scale item allocation system rather than a large industrial inventory platform.

---

# 6. System Concept

The main concept of the system is to replace a manual form-based system with an automated digital request system.

The system concept includes:

- Creating a digital request system instead of a manual form.
- Using algorithms and data structures for decision-making.
- Queueing projects using a priority list.
- Moving projects with unavailable items to a pending list.
- Creating an admin dashboard for visualization and analysis.
- Automatically reducing stock.
- Tracking borrowed items.
- Tracking returned items.
- Checking pending requests again when items are returned.

---

# 7. High-Level System Flow

```text
Student
  โ“
Search Inventory
  โ“
Create Project Request
  โ“
Insert Request into Main Priority Queue
  โ“
Extract Highest-Priority Project
  โ“
Check Requested Components
  โ“
Check Inventory
  โ”โ”€โ”€ Components Available
  โ”      โ“
  โ”    Reserve Components
  โ”      โ“
  โ”    Notify Student
  โ”      โ“
  โ”    Student Collects Items
  โ”      โ“
  โ”    Reduce Stock
  โ”      โ“
  โ”    Store Project in Borrowed List
  โ”
  โ””โ”€โ”€ Components Not Available
         โ“
       Identify Missing Items
         โ“
       Insert Project into Pending Queue
         โ“
       Notify Student
```

---

# 8. Borrowing Process

The borrowing process is one of the main workflows of the system.

## 8.1 Student Inputs Project Information

The student provides:

- Project name.
- Pick-up date.
- Components/tools needed.

Before creating the request, the student can search for components in the inventory.

The item catalog is searched using:

- **Binary Search**

---

## 8.2 Create Project Request

After entering the project information, the system creates a new project request.

The request contains information such as:

- Project ID.
- Project name.
- Pick-up date.
- Requested components.
- Request time.
- Project status.

---

## 8.3 Insert Project into Main Min-Heap

The project request is inserted into the main priority queue.

The selected data structure is:

- **Min-Heap**

The Min-Heap is used because the earliest pick-up date can be treated as the smallest key.

Example:

```text
Project A โ’ Pick-up date: 2 October
Project B โ’ Pick-up date: 5 October
Project C โ’ Pick-up date: 1 October
```

Priority order:

```text
Project C
Project A
Project B
```

---

## 8.4 Extract Highest-Priority Project

The system retrieves the project with the highest priority from the Main Min-Heap.

The highest-priority request is the project with the earliest pick-up date.

If two projects have the same pick-up date, the earlier request has higher priority.

Example:

```text
Project A
Pick-up date: 10 October
Request time: 09:00

Project B
Pick-up date: 10 October
Request time: 10:00
```

Project A receives priority because it was requested earlier.

---

## 8.5 Retrieve Requested Components

After selecting the highest-priority project, the system retrieves the list of requested components/tools.

Example:

```text
Project ID: P001

Requested Items:
- Arduino Uno ร— 2
- Servo Motor ร— 4
- Breadboard ร— 2
```

---

## 8.6 Check Inventory

The system checks inventory using a:

- **Hash Table**

The Hash Table stores and retrieves stock information.

Example:

```text
"Arduino Uno" โ’ 10
"Servo Motor" โ’ 3
"Breadboard" โ’ 15
```

The system compares requested quantity with available quantity.

---

# 9. Components Available Branch

If all required components are available:

```text
Components Available
        โ“
Reserve Components
        โ“
Mark as "Reserved"
        โ“
Notify Student by Email
```

---

## 9.1 Reserve Components

The requested quantity is reserved for the project.

Example:

```text
Stock:
Arduino Uno = 10

Project requests:
Arduino Uno = 2

Reserved:
2

Available for other projects:
8
```

---

## 9.2 Mark Components as Reserved

The system records that the components belong to a specific project request.

Possible status:

```text
AVAILABLE
RESERVED
BORROWED
DAMAGED
```

The presentation specifically describes the reserved state as:

> **"Reserved"**

---

## 9.3 Notify Student

The system sends an email informing the student that the requested components are ready.

Conceptually:

```text
Subject: Project Components Ready

Your requested components are available and have been reserved.
Please collect them according to the requested pick-up date.
```

---

# 10. Components Not Available Branch

If one or more components are unavailable:

```text
Components Not Available
        โ“
Identify Out-of-Stock Items
        โ“
Insert Project into Pending Min-Heap
        โ“
Notify Student
```

---

## 10.1 Identify Missing Items

The system identifies which requested items cannot be allocated.

Example:

```text
Requested:
Arduino Uno ร— 2
Servo Motor ร— 4

Inventory:
Arduino Uno = 10
Servo Motor = 3
```

Result:

```text
Arduino Uno โ’ Available
Servo Motor โ’ Short by 1
```

---

## 10.2 Insert Project into Pending Min-Heap

The project is moved into a:

- **Pending Min-Heap**

The pending queue stores projects that cannot currently receive all requested components.

The queue is still prioritized by pick-up date.

---

## 10.3 Notify Student About Missing Components

The system sends an email informing the student which requested items are unavailable.

Example:

```text
Your project request is currently pending.

Unavailable items:
- Servo Motor ร— 1

Your request will be checked again when inventory becomes available.
```

---

# 11. Project Collection Process

When components are ready, the student physically collects the items.

The system then performs the following actions:

```text
Student Collects Items
        โ“
Reduce Inventory
        โ“
Store Project in Borrowed List
```

---

## 11.1 Reduce Stock

Once the items are collected, the system reduces the item quantity in the inventory.

The inventory is managed using a Hash Table.

Example:

```text
Before Collection:
Arduino Uno = 10

Borrowed:
2

After Collection:
Arduino Uno = 8
```

This removes the need for an administrator to manually edit stock quantity.

---

## 11.2 Store Project in Borrowed List

The project is stored in the Borrowed List.

The Borrowed List is used to keep track of:

- Project ID.
- Project name.
- Student information.
- Borrowed components.
- Borrowed quantity.
- Borrow date.

The project can be found using:

- **Project ID**

Conceptually:

```text
Project ID โ’ Borrowed Project Information
```

Example:

```text
P001 โ’
{
    Project: "Robot Arm",
    Items: {
        "Arduino Uno": 2,
        "Servo Motor": 4
    }
}
```

---

# 12. Continue Processing Projects

After processing one project, the system checks whether more projects remain in the Main Min-Heap.

```text
Check Main Min-Heap
        โ“
More Projects?
       / \
     Yes  No
     โ“     โ“
Extract   Stop
Next
Project
```

This continues until there are no remaining projects to process.

---

# 13. Ordered Project List for Admin

The project uses:

- **Merge Sort**

to create an ordered project list for administrators.

The list is sorted from highest priority to lowest priority.

The admin can see information such as:

- Project name.
- Pick-up date.
- Required components.

Example:

| Priority | Project | Pick-up Date | Requested Items |
|---:|---|---|---|
| 1 | Project C | 1 Oct | Servo, Arduino |
| 2 | Project A | 2 Oct | Motor, Sensor |
| 3 | Project B | 5 Oct | Breadboard |

This helps the inventory manager prepare items in the correct order.

---

# 14. Returning Process

The returning process begins when the student physically returns borrowed components or tools.

The workflow is:

```text
Student Returns Borrowed Items
        โ“
Use Project ID
        โ“
Look Up Borrowed Items
        โ“
Admin Checks Returned Items
        โ“
Check Item Condition
       / \
     Good  Bad
     โ“      โ“
Return to  Add to
Inventory  Damage List
```

---

# 15. Look Up Borrowed Items

The administrator uses the Project ID to retrieve borrowed-item information.

Example:

```text
Input:
Project ID = P001

Output:
Arduino Uno ร— 2
Servo Motor ร— 4
Breadboard ร— 2
```

This lets the administrator verify what the student should return.

---

# 16. Admin Checks Returned Items

The administrator physically checks each returned component/tool.

Each item is classified as:

- Good condition.
- Bad condition / damaged.

---

# 17. Returned Item in Good Condition

If the item is still usable:

```text
Good Condition
      โ“
Add Quantity Back into Inventory
      โ“
Update Hash Table
```

Example:

```text
Current Stock:
Arduino Uno = 8

Student Returns:
Arduino Uno = 2

Updated Stock:
Arduino Uno = 10
```

---

# 18. Returned Item in Bad Condition

If an item is damaged or unusable:

```text
Bad Condition
      โ“
Cross Item Out from Return Checklist
      โ“
Insert Item into Damage List
      โ“
Singly Linked List
```

The damaged item is kept separate from usable inventory.

---

# 19. Damage List

The Damage List uses a:

- **Singly Linked List**

Example:

```text
HEAD
 โ“
Damaged Servo
 โ“
Broken Arduino
 โ“
Broken Multimeter
 โ“
NULL
```

Each node can store information such as:

```text
Item ID
Item Name
Project ID
Damage Description
Date Returned
Next Node
```

The purpose of the Damage List is to:

- Keep damaged items separate from usable stock.
- Record damaged components.
- Help administrators identify items that need repair.
- Help administrators identify items that need replacement.

---

# 20. Finish Returned Project

After all returned items have been checked:

```text
Delete Finished Project
        โ“
Remove from Project Heap
        โ“
Delete from Confirmed/Borrowed Project Hash Table
```

The project is no longer considered active after the return is completed.

---

# 21. Check Pending List After Return

After an item is returned, the system checks the Pending List.

This is important because the returned components may be required by another waiting project.

Workflow:

```text
Item Returned
      โ“
Inventory Updated
      โ“
Check Pending List
      โ“
Does a Pending Project Need This Item?
      / \
    Yes  No
    โ“     โ“
Return   Stop
to Stock
Checking
Process
```

If the returned item satisfies a pending request, the project can return to the normal borrowing process.

---

# 22. Process Selection and Reasoning

## 22.1 Priority Queueing

### Chosen Process

- Real-time priority queueing after students submit requests.
- Use pick-up date as the priority criterion.
- If projects have the same pick-up date, give priority to the earlier request.

### Rationale

- Eliminates manual queueing.
- Reduces human decision-making.
- Helps reduce possible bias.

---

## 22.2 Item Search

### Chosen Process

- Search for items in stock when students make requests.
- Display searched items.

### Rationale

- Students do not have to manually search through the stock database.

---

## 22.3 Ordered Project List

### Chosen Process

- Sort project requests from highest priority to lowest.
- Display:
  - Project name.
  - Pick-up date.
  - Requested items.

### Rationale

- Helps the inventory manager prepare items.
- Removes the need to manually inspect every request.

---

## 22.4 Pending Request List

### Chosen Process

- Move a project to another list when required items are unavailable.
- Sort the Pending List according to pick-up date.
- Give priority to the earliest pick-up date.

### Rationale

- Keeps track of projects that have not yet received their requested items.

---

## 22.5 Item-in-Stock Reduction

### Chosen Process

- Admin confirms the allocated items.
- The system reduces the number of items in stock.

### Rationale

- The database shows the exact number of items remaining.
- Removes manual stock editing.

---

## 22.6 Borrowed Item Tracking

### Chosen Process

- Admin confirms allocated items.
- The system stores the project and borrowed items in a separate list.

### Rationale

- Keeps track of currently borrowed items.
- Helps when items go missing.

---

## 22.7 Return Process

### Chosen Process

- Admin checks returned components/tools.
- Remove finished project from Borrowed List.
- Check the Pending List again.

### Rationale

- Keeps inventory quantity accurate.
- Reduces manual stock updates.
- Helps waiting projects receive returned items faster.

---

## 22.8 List of Damaged Components

### Chosen Process

- Admin checks each returned component/tool.
- Damaged or unusable items are crossed out.
- Damaged items are inserted into the Damage List using a Singly Linked List.

### Rationale

- Keeps damaged items separate from usable inventory.
- Helps administrators identify items needing repair or replacement.

---

# 23. Algorithm and Data Structure Selection

The project uses the following main data structures and algorithms.

## Data Structures

1. Min-Heap
2. Hash Table
3. Singly Linked List

## Algorithms

1. Binary Search
2. Merge Sort

---

# 24. Min-Heap

## Usage

The Min-Heap is used to:

- Insert project requests.
- Store project requests.
- Find the highest-priority project.
- Retrieve the highest-priority project.
- Delete projects that have returned borrowed items.
- Store pending projects.
- Insert pending projects.
- Delete pending projects.

---

## Why Min-Heap?

The main reason is time efficiency.

### Highest-Priority Item

Accessing the root of the Min-Heap:

```text
O(1)
```

### Insert

```text
O(log n)
```

### Extract/Delete

```text
O(log n)
```

This makes the heap suitable for project-priority management.

---

# 25. Min-Heap vs. Array Comparison

For approximately **75 requests**:

## Unsorted Array

Finding the highest-priority project:

```text
O(n)
```

Approximately:

```text
75 checks
```

---

## Sorted Array

Inserting a new project can require:

```text
O(n)
```

Approximately:

```text
75 shifts
```

---

## Heap

Heap insertion/extraction:

```text
O(log n)
```

For 75 projects:

```text
log2(75) โ 6.23
```

This is roughly around:

```text
7 operations
```

The presentation therefore compares:

```text
Unsorted Array โ’ up to 75 checks
Sorted Array   โ’ up to 75 shifts
Heap           โ’ about 7 operations
```

---

# 26. Hash Table

The Hash Table is another important structure in the system.

## Usage

The Hash Table is used for:

- Inventory quantity lookup.
- Stock reduction.
- Stock updates.
- Storing allocated project information.
- Tracking borrowed projects.
- Deleting completed borrowed projects.
- Looking up items quickly.

---

## Example Inventory Hash Table

```text
Key                   Value

"Arduino Uno"       โ’ 10
"Servo Motor"       โ’ 25
"Breadboard"        โ’ 15
"Ultrasonic Sensor" โ’ 8
```

---

## Example Borrowed Project Hash Table

```text
Project ID           Borrowed Information

P001              โ’ Project A Borrowed Items
P002              โ’ Project B Borrowed Items
P003              โ’ Project C Borrowed Items
```

---

## Hash Table Complexity

Average-case search:

```text
O(1)
```

Average-case insertion:

```text
O(1)
```

Average-case update:

```text
O(1)
```

Average-case deletion:

```text
O(1)
```

Worst case can become:

```text
O(m)
```

if many keys collide.

---

# 27. Hash Table vs. Array / Linked List

The presentation assumes up to approximately **200 inventory items**.

## Array / Linked List

Searching may require:

```text
O(m)
```

Worst case:

```text
200 checks
```

---

## Hash Table

Average case:

```text
O(1)
```

Approximately:

```text
1 operation
```

Worst case:

```text
O(m)
```

This worst case can happen if all keys collide, although the presentation notes that this is rare with a good hash function.

---

# 28. Singly Linked List

The Singly Linked List is used for storing damaged component/tool records.

## Usage

When returned items are found to be damaged or unusable, they are inserted into the damage list.

Example:

```text
HEAD
 โ“
[Damaged Item 1]
 โ“
[Damaged Item 2]
 โ“
[Damaged Item 3]
 โ“
NULL
```

---

## Reason

The presentation selects a Singly Linked List because:

- New damaged-item records can be added easily.
- The system does not need to move backward through the list.
- Damaged records can grow dynamically.

---

# 29. Binary Search

Binary Search is used during item search.

## Usage

The student searches for a requested component/tool using:

- Type.
- Item name.

The inventory is sorted alphabetically.

Example:

```text
Arduino Uno
Battery Holder
Breadboard
DC Motor
ESP32
Raspberry Pi
Servo Motor
Ultrasonic Sensor
```

Binary Search repeatedly divides the search area in half.

---

# 30. Binary Search vs. Linear Search

The project assumes approximately **200 items**.

## Linear Search

Worst case:

```text
O(m)
```

For 200 items:

```text
up to 200 checks
```

---

## Binary Search

Worst case:

```text
O(log m)
```

For 200 items:

```text
log2(200) โ 7.64
```

Approximately:

```text
8 checks
```

Comparison:

```text
Linear Search โ’ up to 200 checks
Binary Search โ’ about 8 checks
```

---

# 31. Merge Sort

Merge Sort is used to create an ordered project list for the administrator.

## Usage

The algorithm sorts project requests so the administrator can inspect them for component allocation and preparation.

Example output:

```text
1. Project C โ€” 1 Oct
2. Project A โ€” 2 Oct
3. Project D โ€” 3 Oct
4. Project B โ€” 5 Oct
```

---

## Reason

The presentation selects Merge Sort because:

- It works smoothly with larger datasets.
- It has consistent time complexity.
- Its time complexity is:

```text
O(n log n)
```

- It can also work well with linked-list-style data structures.

---

# 32. Merge Sort Comparison

The presentation compares:

- Selection Sort
- Bubble Sort
- Insertion Sort
- Quick Sort
- Merge Sort

---

## Selection Sort

Worst case:

```text
O(nยฒ)
```

---

## Bubble Sort

Worst case:

```text
O(nยฒ)
```

---

## Insertion Sort

Worst case:

```text
O(nยฒ)
```

---

## Quick Sort

Average case:

```text
O(n log n)
```

Worst case:

```text
O(nยฒ)
```

The worst case can occur when poor pivots are repeatedly selected.

---

## Merge Sort

Best case:

```text
O(n log n)
```

Average case:

```text
O(n log n)
```

Worst case:

```text
O(n log n)
```

---

# 33. Comparison for 75 Projects

The presentation gives the following comparison.

## Selection / Bubble / Insertion Sort

```text
O(nยฒ)
```

For 75 project requests:

```text
75ยฒ = 5,625
```

Presented as approximately:

```text
5,625 comparisons
```

---

## Quick Sort

Average:

```text
O(n log n)
```

Worst case:

```text
O(nยฒ)
```

---

## Merge Sort

```text
O(n log n)
```

The presentation states approximately:

```text
467 comparisons
```

for 75 projects.

---

# 34. Complexity Summary

| Operation | Selected Technique | Complexity |
|---|---|---|
| Access highest-priority project | Min-Heap | O(1) |
| Insert project | Min-Heap | O(log n) |
| Extract project | Min-Heap | O(log n) |
| Search inventory by hash key | Hash Table | O(1) average |
| Insert/update inventory | Hash Table | O(1) average |
| Search sorted item catalog | Binary Search | O(log m) |
| Sort project list | Merge Sort | O(n log n) |
| Add damaged item record | Singly Linked List | O(1) if inserting at known end/head |

---

# 35. Full Borrowing Workflow

```text
START
  โ“
Student enters:
- Project Name
- Pick-up Date
- Components/Tools Needed
  โ“
Search Component Catalog
[Binary Search]
  โ“
Create Project Request
  โ“
Insert into Main Min-Heap
  โ“
Extract Highest-Priority Project
  โ“
Retrieve Components/Tools Needed
  โ“
Check Stock Inventory
[Hash Table]
  โ“
Are Components Available?
  โ”โ”€โ”€ YES
  โ”    โ“
  โ”  Reserve Components
  โ”    โ“
  โ”  Mark as "Reserved"
  โ”    โ“
  โ”  Notify Student of Readiness
  โ”    โ“
  โ”  Student Collects Items
  โ”    โ“
  โ”  Reduce Stock
  โ”  [Hash Table]
  โ”    โ“
  โ”  Store Project in Borrowed List
  โ”  [Project ID / Hash Table]
  โ”    โ“
  โ”  Check for More Projects
  โ”
  โ””โ”€โ”€ NO
       โ“
     Identify Out-of-Stock Items
       โ“
     Insert Project into Pending Min-Heap
       โ“
     Notify Student of Missing Items
       โ“
     Check Next Main-Heap Project
```

---

# 36. Full Returning Workflow

```text
START
  โ“
Student Returns Borrowed Items
  โ“
Use Project ID
  โ“
Look Up Borrowed Items
  โ“
Admin Checks Returned Items
  โ“
Check Item Condition
  โ”โ”€โ”€ GOOD
  โ”    โ“
  โ”  Add Quantity Back to Inventory
  โ”  [Hash Table]
  โ”
  โ””โ”€โ”€ BAD
       โ“
     Cross Out Damaged Item
       โ“
     Insert into Damage List
     [Singly Linked List]
  โ“
Delete Finished Project
  โ“
Delete Project from Borrowed/Confirmed Project Records
  โ“
Check Pending List
  โ“
Are Returned Items Needed?
  โ”โ”€โ”€ YES
  โ”    โ“
  โ”  Return to Stock Checking Process
  โ”
  โ””โ”€โ”€ NO
       โ“
      STOP
```

---

# 37. Conceptual System Architecture

```text
                    โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                    โ”       STUDENT       โ”
                    โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                               โ”
                               โ–ผ
                    โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                    โ” Search Item Catalog โ”
                    โ”    Binary Search    โ”
                    โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                               โ”
                               โ–ผ
                    โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                    โ” Create Project      โ”
                    โ” Request             โ”
                    โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                               โ”
                               โ–ผ
                    โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                    โ”   MAIN MIN-HEAP     โ”
                    โ”   Priority Queue    โ”
                    โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                               โ”
                               โ–ผ
                    โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                    โ” Extract Highest     โ”
                    โ” Priority Project    โ”
                    โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                               โ”
                               โ–ผ
                    โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                    โ” Inventory Lookup    โ”
                    โ”     Hash Table      โ”
                    โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                               โ”
                   โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ดโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                   โ”                       โ”
                   โ–ผ                       โ–ผ
           โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”       โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
           โ”   AVAILABLE   โ”       โ” NOT AVAILABLE  โ”
           โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”       โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                   โ”                       โ”
                   โ–ผ                       โ–ผ
           โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”       โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
           โ” Reserve Items โ”       โ” Pending        โ”
           โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”       โ” Min-Heap       โ”
                   โ”               โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                   โ–ผ
           โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
           โ” Notify Studentโ”
           โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                   โ”
                   โ–ผ
           โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
           โ” Student       โ”
           โ” Collects      โ”
           โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                   โ”
                   โ–ผ
           โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
           โ” Reduce Stock  โ”
           โ” Hash Table    โ”
           โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                   โ”
                   โ–ผ
           โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
           โ” Borrowed List โ”
           โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                   โ”
                   โ–ผ
           โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
           โ” Student       โ”
           โ” Returns Items โ”
           โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                   โ”
                   โ–ผ
           โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
           โ” Admin Checks  โ”
           โ” Condition     โ”
           โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                   โ”
            โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”ดโ”€โ”€โ”€โ”€โ”€โ”€โ”
            โ”             โ”
            โ–ผ             โ–ผ
       โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”   โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
       โ”  GOOD   โ”   โ” DAMAGED  โ”
       โ””โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”   โ””โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”
            โ”             โ”
            โ–ผ             โ–ผ
      โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”  โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
      โ”Add Back toโ”  โ” Damage List  โ”
      โ” Inventory โ”  โ” Linked List  โ”
      โ””โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”  โ””โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
            โ”              โ”
            โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
                   โ”
                   โ–ผ
           โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
           โ” Check Pending โ”
           โ” Projects      โ”
           โ””โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
```

---

# 38. Example End-to-End Scenario

Assume the inventory contains:

```text
Arduino Uno = 5
Servo Motor = 4
Breadboard = 10
Ultrasonic Sensor = 3
```

Two projects are submitted.

## Project A

```text
Pick-up Date: 10 October
Request Time: 09:00

Requested:
Arduino Uno ร— 2
Servo Motor ร— 2
```

## Project B

```text
Pick-up Date: 8 October
Request Time: 11:00

Requested:
Arduino Uno ร— 4
```

---

## Step 1: Priority

Project B has the earlier pick-up date.

Main Min-Heap priority:

```text
1. Project B
2. Project A
```

---

## Step 2: Process Project B

Requested:

```text
Arduino Uno ร— 4
```

Inventory:

```text
Arduino Uno = 5
```

The item is available.

The system reserves:

```text
Arduino Uno ร— 4
```

After collection:

```text
Arduino Uno = 1
```

Project B is stored in the Borrowed List.

---

## Step 3: Process Project A

Project A requests:

```text
Arduino Uno ร— 2
Servo Motor ร— 2
```

Current inventory:

```text
Arduino Uno = 1
Servo Motor = 4
```

Servo Motor is available, but Arduino Uno is not sufficient.

Project A is moved to:

```text
Pending Min-Heap
```

The student is notified that Arduino Uno is unavailable.

---

## Step 4: Project B Returns Items

Project B returns:

```text
Arduino Uno ร— 4
```

Assume all four are in good condition.

Inventory becomes:

```text
Arduino Uno = 5
```

The system checks the Pending Min-Heap.

Project A requires:

```text
Arduino Uno ร— 2
```

The item is now available.

Project A can return to the allocation process.

---

# 39. Admin Dashboard Information

Based on the project concept, the admin dashboard should be able to display information such as:

## Inventory

```text
Total Inventory Items
Available Items
Reserved Items
Borrowed Items
Damaged Items
```

## Project Status

```text
Total Project Requests
Waiting Projects
Ready Projects
Borrowed Projects
Pending Projects
Finished Projects
```

## Priority Queue

```text
Project Name
Pick-up Date
Priority
Items Needed
Status
```

## Pending Projects

```text
Project Name
Pick-up Date
Unavailable Item
Required Quantity
Current Stock
```

## Borrowed Items

```text
Project ID
Project Name
Item
Quantity
Borrow Date
```

## Damaged Items

```text
Item Name
Project ID
Damage Description
Return Date
```

---

# 40. Suggested Project Statuses

The presentation does not provide a complete formal status enum, but the workflows imply statuses similar to:

```text
REQUESTED
QUEUED
PENDING
RESERVED
READY
BORROWED
RETURNED
COMPLETED
```

Possible item states implied by the process include:

```text
AVAILABLE
RESERVED
BORROWED
DAMAGED
```

These are implementation-oriented interpretations of the workflow rather than an explicit status list from the slides.

---

# 41. Summary of Algorithms and Data Structures

## Data Structures

### Min-Heap

Purpose:

- Find the project with highest priority.
- Prioritize using pick-up date.
- Retrieve the highest-priority request.
- Store pending requests.

---

### Hash Table

Purpose:

- Store inventory information.
- Update inventory quantities.
- Search stock quickly.
- Store borrowed-project information.
- Confirm borrowed-project information.

---

### Singly Linked List

Purpose:

- Store damaged item records.
- Add new damaged-item records dynamically.

---

## Algorithms

### Binary Search

Purpose:

- Search for components/tools in an alphabetically sorted inventory.

---

### Merge Sort

Purpose:

- Sort project requests.
- Produce an ordered list for administrators.
- Support item preparation and analysis.

---

# 42. Final System Summary

The complete system can be summarized as:

```text
STUDENT REQUEST
      โ“
BINARY SEARCH
Find Items
      โ“
MIN-HEAP
Prioritize Project
      โ“
HASH TABLE
Check Inventory
      โ“
 โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
 โ” Available   โ” Unavailable โ”
 โ“             โ“
Reserve      Pending Heap
 โ“
Student Collects
 โ“
HASH TABLE
Reduce Stock
 โ“
Borrowed Project Tracking
 โ“
Student Returns
 โ“
Admin Inspects
 โ“
 โ”โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”ฌโ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”€โ”
 โ” Good     โ” Damaged  โ”
 โ“          โ“
Hash Table  Singly Linked List
Update      Damage List
Inventory
      โ“
Check Pending Projects
      โ“
Repeat Allocation if Items Become Available
```

---

# 43. Important Consistency Notes from the Original Presentation

The following points should be kept in mind because the presentation contains some inconsistent terminology.

## 43.1 Min-Heap vs. Max-Heap

Most of the presentation identifies the priority structure as:

> **Min-Heap**

However, the algorithm-comparison page contains the text:

> **"Max-Heap (ours)"**

The workflow, final summary, and other Min-Heap slides indicate that the intended project structure is a **Min-Heap**.

This is especially consistent with using an earlier pick-up date as a smaller key.

For example:

```text
2026-10-01 < 2026-10-05
```

Therefore the earlier date naturally rises toward the root of a Min-Heap.

This note records the inconsistency rather than silently changing the original presentation.

---

## 43.2 Singly Linked List Classification

The final summary slide places **Singly Linked List** under the Algorithm side of the slide.

Technically, and according to the earlier dedicated slide, the Singly Linked List is used as a **data structure** for damaged-item records.

Therefore the project content is best understood as:

```text
DATA STRUCTURES
- Min-Heap
- Hash Table
- Singly Linked List

ALGORITHMS
- Binary Search
- Merge Sort
```

Again, this note documents the inconsistency in the source rather than silently changing it.

---

# 44. Final Project Structure

```text
Item Allocator for Student Projects
โ”
โ”โ”€โ”€ Student Request System
โ”   โ”โ”€โ”€ Search Inventory
โ”   โ”   โ””โ”€โ”€ Binary Search
โ”   โ”
โ”   โ”โ”€โ”€ Create Project Request
โ”   โ”
โ”   โ””โ”€โ”€ Priority Queue
โ”       โ””โ”€โ”€ Main Min-Heap
โ”
โ”โ”€โ”€ Inventory Management
โ”   โ”โ”€โ”€ Inventory Hash Table
โ”   โ”โ”€โ”€ Reserve Items
โ”   โ”โ”€โ”€ Reduce Stock
โ”   โ””โ”€โ”€ Return Stock
โ”
โ”โ”€โ”€ Pending Request System
โ”   โ””โ”€โ”€ Pending Min-Heap
โ”
โ”โ”€โ”€ Borrowed Item Tracking
โ”   โ””โ”€โ”€ Project ID / Hash Table
โ”
โ”โ”€โ”€ Return System
โ”   โ”โ”€โ”€ Good Item
โ”   โ”   โ””โ”€โ”€ Return to Inventory
โ”   โ”
โ”   โ””โ”€โ”€ Damaged Item
โ”       โ””โ”€โ”€ Singly Linked List
โ”
โ”โ”€โ”€ Admin View
โ”   โ””โ”€โ”€ Merge Sort
โ”       โ””โ”€โ”€ Ordered Project List
โ”
โ””โ”€โ”€ Notifications
    โ”โ”€โ”€ Components Ready
    โ””โ”€โ”€ Components Unavailable
```

---

# 45. One-Line Project Description

> **A digital system for RAI student project component requests that automatically prioritizes projects, checks and reserves inventory, tracks borrowed and returned items, manages pending requests, records damaged components, and supports administrators using Min-Heaps, Hash Tables, Binary Search, Singly Linked Lists, and Merge Sort.**

